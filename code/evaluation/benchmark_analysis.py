
import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

def pareto_frontier(points):
    pts = sorted(points)  # sort by duration asc, then accuracy desc (because -acc used)
    frontier = []
    best_acc = -np.inf
    for d, neg_acc, m in pts:
        acc = -neg_acc
        if acc > best_acc:
            frontier.append((d, acc, m))
            best_acc = acc
    return frontier

def count_upsets_factory(global_rank):
    def count_upsets(group):
        # group contains only ["model_id", "mean_accuracy"]
        models = group["model_id"].tolist()
        accs = dict(zip(group["model_id"], group["mean_accuracy"]))
        upsets = 0
        pairs = 0
        for a, b in combinations(models, 2):
            pairs += 1
            ga = global_rank.get(a, 1e9)
            gb = global_rank.get(b, 1e9)
            if ga < gb and accs.get(a, -1) < accs.get(b, -1):
                upsets += 1
            elif gb < ga and accs.get(b, -1) < accs.get(a, -1):
                upsets += 1
        return pd.Series({"upsets": upsets, "pairs": pairs, "upset_rate": upsets / pairs if pairs else np.nan})
    return count_upsets

def main(input_csv, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(input_csv)

    dataset_to_benchmark = {
        "Ctf": "CSLU",
        "Honeypots": "CSLU",
        "Malware": "CSLU",
        "Applications Security": "CyberDomain",
        "Cloud Security": "CyberDomain",
        "Cryptography": "CyberDomain",
        "Digital Forensics": "CyberDomain",
        "Iam": "CyberDomain",
        "Network Security": "CyberDomain",
        "Operating Systems Security": "CyberDomain",
        "Secmmlu": "CyberBench",
        "Cyquiz": "CyberBench",
        "Secqa V1": "SecQA",
        "Secqa V2": "SecQA",
    }
    df["benchmark"] = df["dataset_name"].map(dataset_to_benchmark)

    # model identifier
    df["model_id"] = (df["model"] if "model" in df.columns else df["model_name"]).astype(str)

    # Ensure numeric
    for col in ["accuracy", "duration_seconds", "confidence_interval_low", "confidence_interval_high", "number_of_executions"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Compute CI width per run (better than mean high/low difference after aggregation)
    if {"confidence_interval_low", "confidence_interval_high"} <= set(df.columns):
        df["ci_width"] = df["confidence_interval_high"] - df["confidence_interval_low"]
    else:
        df["ci_width"] = np.nan

    # Per-dataset aggregation
    per_dataset = (
        df.groupby(["benchmark", "dataset_name", "model_id"], as_index=False)
          .agg(mean_accuracy=("accuracy", "mean"),
               mean_duration_s=("duration_seconds", "mean"),
               mean_ci_width=("ci_width", "mean"),
               ci_low=("confidence_interval_low", "mean"),
               ci_high=("confidence_interval_high", "mean"),
               runs=("number_of_executions", "max"))
    )
    per_dataset["rank_in_dataset"] = per_dataset.groupby(["benchmark", "dataset_name"])["mean_accuracy"].rank(ascending=False, method="min")
    per_dataset.to_csv(os.path.join(out_dir, "per_dataset_model_summary.csv"), index=False)

    # Per-benchmark aggregation
    per_benchmark_model = (
        per_dataset.groupby(["benchmark", "model_id"], as_index=False)
                   .agg(mean_accuracy=("mean_accuracy", "mean"),
                        median_accuracy=("mean_accuracy", "median"),
                        iqr_accuracy=("mean_accuracy", lambda s: np.percentile(s, 75) - np.percentile(s, 25)),
                        mean_duration_s=("mean_duration_s", "mean"),
                        avg_ci_width=("mean_ci_width", "mean"))
    )
    per_benchmark_model.to_csv(os.path.join(out_dir, "per_benchmark_model_summary.csv"), index=False)

    # KPI por benchmark
    difficulty = per_benchmark_model.groupby("benchmark")["mean_accuracy"].mean().rename("difficulty_(1-acc)").rsub(1.0) * 100.0
    discrimination = per_benchmark_model.groupby("benchmark")["mean_accuracy"].apply(lambda s: np.percentile(s, 75) - np.percentile(s, 25)).rename("discrimination_IQR")
    ci_width = per_benchmark_model.groupby("benchmark")["avg_ci_width"].mean().rename("avg_ci_width")

    # Global rank para cálculo de upsets
    global_model_order = (
        per_benchmark_model.groupby("model_id")["mean_accuracy"].mean()
                           .sort_values(ascending=False)
                           .index.tolist()
    )
    global_rank = {m: i for i, m in enumerate(global_model_order)}
    count_upsets = count_upsets_factory(global_rank)

    # FIX: avoid pandas deprecation warning by selecting columns before apply
    upsets_by_benchmark = (
        per_benchmark_model.groupby("benchmark", group_keys=False)[["model_id", "mean_accuracy"]]
        .apply(count_upsets)
        .reset_index()
    )

    benchmark_summary = pd.concat([difficulty, discrimination, ci_width], axis=1).reset_index()
    benchmark_summary = benchmark_summary.merge(upsets_by_benchmark, on="benchmark", how="left")
    benchmark_summary.to_csv(os.path.join(out_dir, "benchmark_summary.csv"), index=False)

    # Rank correlations
    benchmarks = sorted(per_benchmark_model["benchmark"].unique().tolist())
    models = sorted(per_benchmark_model["model_id"].unique().tolist())
    rank_df = pd.DataFrame(index=models, columns=benchmarks, dtype=float)

    for b in benchmarks:
        tmp = per_benchmark_model[per_benchmark_model["benchmark"] == b].sort_values("mean_accuracy", ascending=False)
        ranks = {m: r for r, m in enumerate(tmp["model_id"].tolist(), start=1)}
        for m in models:
            rank_df.loc[m, b] = ranks.get(m, np.nan)

    spearman_corr = rank_df.corr(method="spearman")
    kendall_corr = rank_df.corr(method="kendall")
    spearman_corr.to_csv(os.path.join(out_dir, "rank_corr_spearman.csv"))
    kendall_corr.to_csv(os.path.join(out_dir, "rank_corr_kendall.csv"))

    # Figures
    plt.figure(figsize=(6,5))
    plt.imshow(spearman_corr, interpolation="nearest")
    plt.xticks(range(len(benchmarks)), benchmarks, rotation=45, ha="right")
    plt.yticks(range(len(benchmarks)), benchmarks)
    plt.title("Rank correlation (Spearman) across benchmarks")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "heatmap_spearman.png"))
    plt.close()

    plt.figure(figsize=(6,5))
    plt.imshow(kendall_corr, interpolation="nearest")
    plt.xticks(range(len(benchmarks)), benchmarks, rotation=45, ha="right")
    plt.yticks(range(len(benchmarks)), benchmarks)
    plt.title("Rank correlation (Kendall) across benchmarks")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "heatmap_kendall.png"))
    plt.close()

    tmp_sum = benchmark_summary.copy()
    plt.figure(figsize=(6,5))
    plt.scatter(tmp_sum["difficulty_(1-acc)"], tmp_sum["discrimination_IQR"])
    for _, row in tmp_sum.iterrows():
        plt.annotate(row["benchmark"], (row["difficulty_(1-acc)"], row["discrimination_IQR"]), xytext=(5,5), textcoords="offset points", fontsize=9)
    plt.xlabel("Dificuldade (1 - precisão média) [%]")
    plt.ylabel("Discriminação (IQR das precisões entre modelos)")
    plt.title("Dificuldade vs Discriminação por benchmark")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "difficulty_vs_discrimination.png"))
    plt.close()

    plt.figure(figsize=(6,4))
    plt.bar(benchmark_summary["benchmark"], benchmark_summary["upset_rate"])
    plt.ylabel("Taxa de upsets (inversões)")
    plt.title("Upsets vs ranking global por benchmark")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "upset_rate.png"))
    plt.close()

    # Pareto per benchmark
    pareto_tables = []
    for b in benchmarks:
        sub = per_benchmark_model[per_benchmark_model["benchmark"] == b].dropna(subset=["mean_duration_s", "mean_accuracy"])
        pts = list(zip(sub["mean_duration_s"].tolist(), (-sub["mean_accuracy"]).tolist(), sub["model_id"].tolist()))
        front = pareto_frontier(pts)
        pareto_df = pd.DataFrame(front, columns=["duration_s", "accuracy", "model_id"])
        pareto_df["benchmark"] = b
        pareto_tables.append(pareto_df)

        # Scatter + frontier
        plt.figure(figsize=(6,5))
        plt.scatter(sub["mean_duration_s"], sub["mean_accuracy"])
        for _, row in sub.iterrows():
            plt.annotate(row["model_id"], (row["mean_duration_s"], row["mean_accuracy"]), xytext=(5,5), textcoords="offset points", fontsize=8)
        if len(front) > 0:
            front_df = pd.DataFrame(front, columns=["duration_s", "accuracy", "model_id"])
            plt.plot(front_df["duration_s"], front_df["accuracy"], marker="o")
        plt.xlabel("Duração média por pergunta (s)")
        plt.ylabel("Precisão média (%)")
        plt.title(f"Eficiência: precisão vs latência — {b}")
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"pareto_{b}.png"))
        plt.close()

    pareto_all = pd.concat(pareto_tables, ignore_index=True)
    pareto_all.to_csv(os.path.join(out_dir, "pareto_frontiers.csv"), index=False)

    # Leaderboards per benchmark
    for b in benchmarks:
        lead = per_benchmark_model[per_benchmark_model["benchmark"] == b][["benchmark","model_id","mean_accuracy","mean_duration_s","avg_ci_width"]].copy()
        lead = lead.sort_values("mean_accuracy", ascending=False).reset_index(drop=True)
        lead.to_csv(os.path.join(out_dir, f"leaderboard_{b}.csv"), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comparative analysis of LLM cybersecurity benchmarks.")
    parser.add_argument("--input", type=str, required=True, help="Path to evaluation_results.csv")
    parser.add_argument("--outdir", type=str, default="analysis_outputs", help="Directory to write outputs")
    args = parser.parse_args()
    main(args.input, args.outdir)
