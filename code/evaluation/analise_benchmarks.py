import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

DATASET_TO_BENCH = {
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


def analyze_benchmarks_performance(csv_path="evaluation_results.csv"):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Erro: Ficheiro '{csv_path}' não encontrado.")
        return

    df['accuracy'] = pd.to_numeric(df.get('accuracy'), errors='coerce')
    if 'duration_seconds' in df.columns:
        df['duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce')
    df = df.dropna(subset=['accuracy'])

    if 'dataset_name' not in df.columns:
        print("Erro: coluna 'dataset_name' não encontrada no CSV.")
        return

    df['benchmark'] = df['dataset_name'].map(DATASET_TO_BENCH)
    if df['benchmark'].isna().any():
        missing = sorted(df.loc[df['benchmark'].isna(), 'dataset_name'].unique().tolist())
        print("Aviso: sem mapeamento para os seguintes datasets:", missing)
        df = df.dropna(subset=['benchmark'])

    has_ci = {'confidence_interval_low', 'confidence_interval_high'}.issubset(df.columns)
    if has_ci:
        df['confidence_interval_low'] = pd.to_numeric(df['confidence_interval_low'], errors='coerce')
        df['confidence_interval_high'] = pd.to_numeric(df['confidence_interval_high'], errors='coerce')
        df['lower_gap'] = (df['accuracy'] - df['confidence_interval_low']).clip(lower=0)
        df['upper_gap'] = (df['confidence_interval_high'] - df['accuracy']).clip(lower=0)

    output_dir = "benchmark_analysis_charts"
    os.makedirs(output_dir, exist_ok=True)
    sns.set_style("whitegrid")

    base = df.groupby('benchmark')['accuracy'].agg(['mean', 'std', 'count']).reset_index()
    base.rename(columns={'mean': 'average_precision', 'std': 'precision_std_dev', 'count': 'n'}, inplace=True)

    if has_ci:
        ci_asym = (
            df.groupby('benchmark')[['lower_gap', 'upper_gap']]
            .mean()
            .reset_index()
            .rename(columns={'lower_gap': 'avg_lower_err', 'upper_gap': 'avg_upper_err'})
        )
        stats = base.merge(ci_asym, on='benchmark', how='left')
    else:
        stats = base.copy()
        stats['avg_lower_err'] = np.nan
        stats['avg_upper_err'] = np.nan

    print("Estatísticas Agregadas por Benchmark:")
    print(stats.to_string(index=False))

    plot_precision_std_dev_per_benchmark(stats.copy(), output_dir)
    plot_precision_with_confidence_intervals(stats.copy(), output_dir, has_ci)


def plot_precision_std_dev_per_benchmark(df_stats, output_dir):
    """Gera um gráfico de barras do desvio padrão da precisão por benchmark com fontes maiores."""
    df_sorted = df_stats.sort_values('precision_std_dev', ascending=False)

    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")

    sns.set_context("talk", font_scale=1.1)

    ax = sns.barplot(
        data=df_sorted,
        x='precision_std_dev', y='benchmark',
        hue='benchmark', palette='viridis',
        dodge=False, legend=False, orient='h'
    )
    plt.xlabel('Desvio Padrão da Precisão (pp)', fontsize=18)
    plt.ylabel('Benchmark', fontsize=18)

    for p in ax.patches:
        width = p.get_width()
        plt.text(width + 0.1, p.get_y() + p.get_height() / 2, f'{width:.2f}', va='center', fontsize=18)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "benchmark_precision_std_dev.png"))
    plt.close()

    sns.set_context("notebook")

    print(f"✅ Gráfico de Desvio-Padrão da Precisão salvo em '{output_dir}/'")


def plot_precision_with_confidence_intervals(df_stats, output_dir, has_ci: bool):
    """Gera um gráfico de barras com intervalos de confiança e fontes maiores."""
    df = df_stats.copy().sort_values('average_precision', ascending=False).reset_index(drop=True)

    if has_ci and df[['avg_lower_err', 'avg_upper_err']].notna().all(axis=None):
        df['lower_err'] = df['avg_lower_err'].clip(lower=0)
        df['upper_err'] = df['avg_upper_err'].clip(lower=0)
    else:
        sem = (df['precision_std_dev'] / np.sqrt(df['n'].clip(lower=1))).fillna(0)
        df['lower_err'] = (1.96 * sem).clip(lower=0)
        df['upper_err'] = (1.96 * sem).clip(lower=0)

    df['low'] = (df['average_precision'] - df['lower_err']).clip(lower=0)
    df['high'] = (df['average_precision'] + df['upper_err']).clip(upper=100)

    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")

    sns.set_context("talk", font_scale=1.1)

    ax = sns.barplot(
        data=df,
        x='average_precision', y='benchmark',
        hue='benchmark', palette='coolwarm',
        dodge=False, legend=False, orient='h'
    )
    plt.xlabel('Precisão Média (%)', fontsize=18)
    plt.ylabel('Benchmark', fontsize=18)
    plt.xlim(0, 100)
    y_positions = np.arange(len(df))
    offset = -0.18

    for i, row in df.iterrows():
        y = y_positions[i] + offset
        ax.hlines(y, row['low'], row['high'], color='black', linewidth=2, zorder=3, clip_on=False)
        ax.vlines(row['low'], y - 0.08, y + 0.08, color='black', linewidth=2, zorder=3, clip_on=False)
        ax.vlines(row['high'], y - 0.08, y + 0.08, color='black', linewidth=2, zorder=3, clip_on=False)

    for p, (_, row) in zip(ax.patches, df.iterrows()):
        mean = row['average_precision']
        lo = row['lower_err']
        up = row['upper_err']
        y = p.get_y() + p.get_height() / 2
        plt.text(mean + max(0.8, up / 2), y, f'{mean:.1f}%  −{lo:.1f}/+{up:.1f}', va='center', fontsize=18)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "benchmark_precision_with_ci.png"))
    plt.close()

    # Resetar o contexto
    sns.set_context("notebook")

    print(f"✅ Gráfico de Precisão com IC 95% (assimétrico) salvo em '{output_dir}/'")


if __name__ == "__main__":
    analyze_benchmarks_performance()