import pandas as pd
import os
import asyncio
from openai import AsyncOpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Configuração da API do LLM
TOKEN = "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"
endpoint = "https://models.inference.ai.azure.com"

client = AsyncOpenAI(base_url=endpoint, api_key=TOKEN)
client_azure = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(TOKEN))


class DatasetValidationError(Exception):
    pass


def validate_dataset_structure(dataset, file_name):
    # Verificar valores ausentes
    if dataset.isnull().any().any():
        raise DatasetValidationError(f"O dataset '{file_name}' contém valores ausentes.")

    # Verificar se todas as colunas obrigatórias estão presentes
    required_columns = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer", "Explanation",
                        "Difficulty", "Domain"]
    for col in required_columns:
        if col not in dataset.columns.str.strip():
            raise DatasetValidationError(f"O dataset '{file_name}' está com a coluna obrigatória ausente: {col}")

    # Verificar se 'Correct Answer' contém apenas valores válidos (A, B, C, D)
    if not dataset['Correct Answer'].str.strip().isin(['A', 'B', 'C', 'D']).all():
        raise DatasetValidationError(
            f"O dataset '{file_name}' contém valores inválidos na coluna 'Correct Answer'. Apenas 'A', 'B', 'C' ou 'D' são permitidos.")


async def ask_gpt_async(prompt):
    try:
        response = await client.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um especialista em cibersegurança."},
                      {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500,
            model="gpt-4o"
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Erro ao validar com LLM: {e}"


def ask_Llama(prompt):
    try:
        response = client_azure.complete(
            messages=[
                SystemMessage(content="Você é um especialista em cibersegurança."),
                UserMessage(content=prompt),
            ],
            temperature=1.0,
            max_tokens=500,
            model="Meta-Llama-3.1-8B-Instruct"
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Erro ao validar com Azure LLM: {e}"


async def ask_Llama_async(prompt):
    # Run the synchronous ask_Llama function in a thread
    return await asyncio.to_thread(ask_Llama, prompt)


async def main():
    # Caminho para o arquivo CSV
    file_path = './datasets/cryptography.csv'
    # Carregar o dataset
    dataset = pd.read_csv(file_path, sep=';', skiprows=1)
    file_name = os.path.basename(file_path)

    try:
        # Validar a estrutura do dataset
        validate_dataset_structure(dataset, file_name)

        prompts = []

        for index, row in dataset.iterrows():
            question = row['Question']
            options = f"A: {row['Option A']}, B: {row['Option B']}, C: {row['Option C']}, D: {row['Option D']}"
            correct_answer = row['Correct Answer']

            prompt = (
                f"Você é um especialista em cibersegurança. Analise a seguinte pergunta de múltipla escolha:\n"
                f"Pergunta: {question}\n"
                f"Opções: {options}\n"
                f"Resposta correta esperada: {correct_answer}\n"
                f"Responda com 'CORRETO' se a pergunta estiver bem formulada e a resposta correta for adequada, ou 'INCORRETO' caso contrário. Explique brevemente sua análise."
            )

            prompts.append(prompt)

        results = []

        # tasks = [ask_gpt_async(prompt) for prompt in prompts]  ## OpenAI - async
        # tasks = [ask_Llama_async(prompt) for prompt in prompts]  ## Azure - Meta Llama - async

        for prompt in prompts:  ## for sync call - Llama
            result = ask_Llama(prompt)
            results.append(result)

        # results = await asyncio.gather(*tasks) ## for async call

        for i, result in enumerate(results):
            print(f"\nResultado da validação da pergunta {i + 1}:", result)

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_name}: {e}")


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
