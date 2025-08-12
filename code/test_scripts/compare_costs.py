import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import textwrap


def analyze_and_plot_costs_per_1000_questions():
    """
    Calcula o custo estimado para 1000 perguntas para cada modelo e gera um gráfico de barras.
    """

    # --- 1. Definição dos Dados ---

    # Preços por 1 MILHÃO de tokens (Input, Output)
    prices = {
        'Gemini 2.5 Pro': {'input': 1.25, 'output': 10.00},
        'Gemini 2.0 Flash': {'input': 0.10, 'output': 0.40},
        'Claude 3.5 Haiku': {'input': 0.80, 'output': 4.00},
        'Claude 3.7 Sonnet': {'input': 3.00, 'output': 15.00},
        'Grok 3 Beta': {'input': 3.00, 'output': 15.00},
        'Grok 3 Mini Beta': {'input': 0.30, 'output': 0.50},
        'Mistral Large 2411': {'input': 2.00, 'output': 6.00},
        'Mistral Small 3.1 24B': {'input': 0.05, 'output': 0.10},
        'OpenAI: GPT-4o': {'input': 2.50, 'output': 10.00},
        'OpenAI: GPT-4o-mini': {'input': 0.15, 'output': 0.60},
    }

    # Parâmetros da simulação
    NUM_QUESTIONS = 1000
    TOKENS_PER_INFERENCE_INPUT = 200
    TOKENS_PER_INFERENCE_OUTPUT = 10

    # --- 2. Cálculo dos Custos ---

    total_tokens_input = NUM_QUESTIONS * TOKENS_PER_INFERENCE_INPUT
    total_tokens_output = NUM_QUESTIONS * TOKENS_PER_INFERENCE_OUTPUT

    cost_data = []
    for model_name, price_info in prices.items():
        cost_input = (total_tokens_input / 1_000_000) * price_info['input']
        cost_output = (total_tokens_output / 1_000_000) * price_info['output']
        total_cost = cost_input + cost_output
        cost_data.append({'Model': model_name, 'Cost per 1000 Questions (USD)': total_cost})

    # Criar e ordenar o DataFrame
    df_costs = pd.DataFrame(cost_data)
    df_costs = df_costs.sort_values('Cost per 1000 Questions (USD)', ascending=True)

    print("Custo Estimado por 1000 Perguntas:")
    print(df_costs.to_string(index=False))

    # --- 3. Geração do Gráfico ---

    output_dir = "cost_analysis_charts"
    os.makedirs(output_dir, exist_ok=True)

    # Gráfico de Barras Horizontal
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")

    # Usar nomes mais curtos para o gráfico
    model_name_map = {
        'Gemini 2.5 Pro': 'Gemini 2.5 Pro',
        'Gemini 2.0 Flash': 'Gemini 2.0 Flash',
        'Claude 3.5 Haiku': 'Claude 3.5 Haiku',
        'Claude 3.7 Sonnet': 'Claude 3.7 Sonnet',
        'Grok 3 Beta': 'Grok 3 Beta',
        'Grok 3 Mini Beta': 'Grok 3 Mini Beta',
        'Mistral Large 2411': 'Mistral Large 2411',
        'Mistral Small 3.1 24B': 'Mistral Small 3.1',
        'OpenAI: GPT-4o': 'GPT-4o',
        'OpenAI: GPT-4o-mini': 'GPT-4o-mini',
    }
    df_costs['Short Model Name'] = df_costs['Model'].map(model_name_map)
    df_costs['Short Model Name'] = df_costs['Short Model Name'].apply(lambda x: textwrap.fill(x, 25))

    ax = sns.barplot(
        data=df_costs,
        y='Short Model Name',
        x='Cost per 1000 Questions (USD)',
        hue='Short Model Name',
        palette='plasma',
        dodge=False,
        orient='h',
    )

    plt.xlabel('Custo (USD)', fontsize=18)
    plt.ylabel('Modelo', fontsize=18)
    plt.legend([], [], frameon=False)  # Esconder a legenda

    # Adicionar os valores de custo no final de cada barra
    for p in ax.patches:
        width = p.get_width()
        plt.text(width + 0.005,
                 p.get_y() + p.get_height() / 2,
                 f'${width:.4f}',
                 va='center',
                 ha='left',
                 fontsize=14)

    ax.tick_params(axis='y', labelsize=14)

    # Ajustar o limite do eixo X para dar espaço às anotações
    plt.xlim(0, df_costs['Cost per 1000 Questions (USD)'].max() * 1.2)

    plt.tight_layout()
    output_path = os.path.join(output_dir, "cost_per_1000_questions.png")
    plt.savefig(output_path)
    plt.close()

    print(f"\n✅ Gráfico de Custo por 1000 Perguntas salvo em '{output_path}'")


# --- Executar a análise ---
if __name__ == "__main__":
    analyze_and_plot_costs_per_1000_questions()