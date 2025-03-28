import requests
import pandas as pd
import os
import asyncio
import json


class DatasetValidationError(Exception):
    pass


def validate_dataset_structure(dataset, file_name):
    if dataset.isnull().any().any():
        raise DatasetValidationError(f"O dataset '{file_name}' contém valores ausentes.")

    required_columns = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer", "Explanation",
                        "Difficulty", "Domain"]
    for col in required_columns:
        if col not in dataset.columns.str.strip():
            raise DatasetValidationError(f"O dataset '{file_name}' está com a coluna obrigatória ausente: {col}")

    if not dataset['Correct Answer'].str.strip().isin(['A', 'B', 'C', 'D']).all():
        raise DatasetValidationError(
            f"O dataset '{file_name}' contém valores inválidos na coluna 'Correct Answer'. Apenas 'A', 'B', 'C' ou 'D' são permitidos."
        )


def ask_fireworks(prompt):
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
        "model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
        "max_tokens": 500,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer fw_3ZjJEBdGSgYneU2XaMMeFn2w"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Verifica se houve erro na chamada
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Erro ao validar com Fireworks LLM: {e}"


async def ask_fireworks_async(prompt):
    # Executa a função síncrona em um thread separado
    return await asyncio.to_thread(ask_fireworks, prompt)


async def main():
    file_paths = {
        "applications_security": "../datasets/applications_security.csv",
        "cloud_security": "../datasets/cloud_security.csv",
        "cryptography": "../datasets/cryptography.csv",
        "digital_forensics": "../datasets/digital_forensics.csv",
        "iam": "../datasets/iam.csv",
        "network_security": "../datasets/network_security.csv",
        "operating_systems_security": "../datasets/operating_systems_security.csv"
    }

    for category, file_path in file_paths.items():
        try:
            dataset = pd.read_csv(file_path, sep=';', skiprows=1)
            file_name = os.path.basename(file_path)

            # Validate dataset structure
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
                    f"Responda com 'CORRETO' se a pergunta estiver bem formulada e a resposta correta for adequada, ou 'INCORRETO' caso contrário."
                )

                prompts.append(prompt)

            # Asynchronous execution for all prompts
            tasks = [ask_fireworks_async(prompt) for prompt in prompts]
            results = await asyncio.gather(*tasks)

            # Display results for the current dataset
            print(f"\n###### Resultados para {file_name}: #######\n")
            for i, result in enumerate(results):
                print(f"Pergunta {i + 1}: {result}")

        except Exception as e:
            print(f"Erro ao processar o arquivo {category}.csv: {e}")


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
