from django.core.management.base import BaseCommand

from api.models import Test
from api.models import QuestionResult
from statsmodels.stats.proportion import proportion_confint


class Command(BaseCommand):
    help = 'Calcula e guarda os intervalos de confiança (IC) nos testes já existentes'

    def handle(self, *args, **kwargs):
        tests = Test.objects.all()
        for test in tests:
            results = QuestionResult.objects.filter(test=test)
            y_true = [res.question.correct_option for res in results if res.answer != "X"]
            y_pred = [res.answer for res in results if res.answer != "X"]

            total = len(y_true)
            correct = sum(1 for i in range(total) if y_true[i] == y_pred[i])

            if total > 0:
                ci_low, ci_high = proportion_confint(correct, total, alpha=0.05, method='wilson')
                test.confidence_interval_low = ci_low * 100
                test.confidence_interval_high = ci_high * 100
            else:
                test.confidence_interval_low = 0.0
                test.confidence_interval_high = 0.0

            test.save(update_fields=["confidence_interval_low", "confidence_interval_high"])

        self.stdout.write(self.style.SUCCESS(f"Recalculadas métricas para {tests.count()} testes."))
