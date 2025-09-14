import asyncio
import statistics
import time
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.auth import get_user_model

from api.models import Test, QuestionResult, Dataset, LLMModel
from api.views import test_views as tv
from api.views.test_views import evaluate_llm, get_openrouter_client_for_user


def percentile(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[int(k)]
    d0 = values[f] * (c - k)
    d1 = values[c] * (k - f)
    return d0 + d1


class Command(BaseCommand):
    help = "Benchmark real do limite de concorrência (SEMAPHORE_UNITS) usando OpenRouter no dataset cyquiz."

    def add_arguments(self, parser):
        parser.add_argument(
            "--units",
            type=str,
            default="10,20,30,50",
            help="Lista de limites de concorrência, separada por vírgulas (ex.: 10,20,30,50)",
        )
        parser.add_argument(
            "--repetitions",
            type=int,
            default=1,
            help="Número de repetições por valor",
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Mantém os Test criados em vez de apagá-los no fim",
        )

    def handle(self, *args, **options):
        units_list = [int(x.strip()) for x in options["units"].split(",") if x.strip()]
        repetitions = options["repetitions"]
        keep = options["keep"]

        # Resolve dataset cyquiz
        try:
            dataset = Dataset.objects.get(name="Cyquiz")
        except Dataset.DoesNotExist:
            raise CommandError("Dataset 'Cyquiz' não encontrado. Verifica as fixtures.")

        # Resolve modelo Mistral Small 3.1 24B
        try:
            llm_model = LLMModel.objects.get(name="Mistral: Mistral Small 3.1 24B")
        except LLMModel.DoesNotExist:
            raise CommandError("Modelo 'Mistral Small 3.1 24B' não encontrado na tabela LLMModel.")

        # Resolve user newuser
        User = get_user_model()
        try:
            user = User.objects.get(username="newuser")
        except User.DoesNotExist:
            raise CommandError("Utilizador 'newuser' não encontrado.")

        # Cria cliente OpenRouter para esse user
        client = get_openrouter_client_for_user(user)

        questions = list(dataset.questions.all().order_by("id"))
        if not questions:
            raise CommandError("Dataset 'cyquiz' não tem perguntas.")

        self.stdout.write(self.style.NOTICE(
            f"Início do benchmark @ {datetime.now().isoformat()} | "
            f"unidades={units_list} | total_perguntas={len(questions)} | reps={repetitions} | modelo={llm_model.name} | user={user.username}"
        ))

        results = []
        for units in units_list:
            run_stats = []
            for rep in range(1, repetitions + 1):
                stats = self._run_once(units, dataset, llm_model, user, client, questions, keep)
                run_stats.append(stats)
                self._print_single_stats(units, rep, stats)

            agg = self._aggregate_runs(run_stats)
            results.append((units, agg))

        self._print_summary(results)

    def _run_once(self, units, dataset, llm_model, user, client, questions, keep):
        # Cria Test temporário
        test = Test.objects.create(
            user=user,
            dataset=dataset,
            llm_model=llm_model,
            started_at=None,
            completed_at=None,
        )

        # Monkeypatch SEMAPHORE_UNITS
        original_units = getattr(tv, "SEMAPHORE_UNITS", None)
        setattr(tv, "SEMAPHORE_UNITS", int(units))

        t0 = time.perf_counter()
        try:
            test.started_at = timezone.now()
            test.save(update_fields=["started_at"])

            asyncio.run(evaluate_llm(test=test, questions=questions, client=client))

            test.completed_at = timezone.now()
            test.save(update_fields=["completed_at"])
        finally:
            if original_units is not None:
                setattr(tv, "SEMAPHORE_UNITS", original_units)

        t1 = time.perf_counter()

        # Métricas
        qrs = list(QuestionResult.objects.filter(test=test))
        total = len(qrs)
        failures = sum(1 for r in qrs if r.answer == "X")
        latencies = [r.response_time for r in qrs if r.response_time and r.response_time > 0]
        mean_latency = statistics.mean(latencies) if latencies else 0.0
        p95_latency = percentile(latencies, 95) if latencies else 0.0
        elapsed = t1 - t0
        throughput_qps = total / elapsed if elapsed > 0 else 0.0

        stats = {
            "units": units,
            "total": total,
            "failures": failures,
            "failure_rate": failures / total if total else 0.0,
            "elapsed_s": elapsed,
            "throughput_qps": throughput_qps,
            "mean_latency_s": mean_latency,
            "p95_latency_s": p95_latency,
            "test_id": test.id,
        }

        if not keep:
            Test.objects.filter(id=test.id).delete()

        return stats

    def _print_single_stats(self, units, rep, s):
        self.stdout.write(
            f"[units={units:>3}] rep {rep}: "
            f"elapsed={s['elapsed_s']:.2f}s | qps={s['throughput_qps']:.2f} | "
            f"fail={s['failure_rate']*100:.1f}% | mean={s['mean_latency_s']:.2f}s | p95={s['p95_latency_s']:.2f}s"
        )

    def _aggregate_runs(self, runs):
        def avg(key):
            vals = [r[key] for r in runs]
            return sum(vals) / len(vals) if vals else 0.0

        return {
            "n": len(runs),
            "elapsed_s_avg": avg("elapsed_s"),
            "throughput_qps_avg": avg("throughput_qps"),
            "failure_rate_avg": avg("failure_rate"),
            "mean_latency_s_avg": avg("mean_latency_s"),
            "p95_latency_s_avg": avg("p95_latency_s"),
        }

    def _print_summary(self, results):
        self.stdout.write(self.style.SUCCESS("\n=== SUMÁRIO ==="))
        self.stdout.write(
            f"{'units':>7} | {'elapsed_avg(s)':>14} | {'qps_avg':>8} | {'fail_avg%':>9} | {'mean_lat(s)':>11} | {'p95_lat(s)':>10}"
        )
        self.stdout.write("-" * 72)
        for units, agg in results:
            self.stdout.write(
                f"{units:>7} | {agg['elapsed_s_avg']:>14.2f} | {agg['throughput_qps_avg']:>8.2f} | "
                f"{agg['failure_rate_avg']*100:>9.2f} | {agg['mean_latency_s_avg']:>11.2f} | {agg['p95_latency_s_avg']:>10.2f}"
            )
