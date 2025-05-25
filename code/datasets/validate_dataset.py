import pandas as pd
import os
import asyncio
import json
import openai


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


# === OpenAI client com OpenRouter ===
client = openai.AsyncOpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)


async def ask_openrouter_async(prompt):
    try:
        response = await client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na validação com OpenRouter: {e}"


async def main(dataset_path):
    try:
        dataset = pd.read_csv(dataset_path, sep=';', skiprows=1)
        file_name = os.path.basename(dataset_path)

        validate_dataset_structure(dataset, file_name)
        prompts = []
        questions = []

        for index, row in dataset.iterrows():
            question = row['Question']
            options = f"A: {row['Option A']}, B: {row['Option B']}, C: {row['Option C']}, D: {row['Option D']}"
            correct_answer = row['Correct Answer']

            prompt = (
                f"You are a cybersecurity expert. Please review the following multiple choice question and assess if the given correct option is truly correct.\n"
                f"Question: {question}\n"
                f"Options: {options}\n"
                f"The answer marked as correct is: {correct_answer}\n"
                f"Is this the correct answer? If yes, explain why briefly. If no, identify the correct one and explain why.\n"
                f"Only respond with:  Correct: [explanation] or  Incorrect. Correct option: [X] - [explanation]"
            )

            prompts.append(prompt)
            questions.append(question)

        # Execução assíncrona dos prompts
        tasks = [ask_openrouter_async(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)

        # Mostrar os resultados
        print(f"\n###### Resultados para {file_name}: #######\n")
        for i, result in enumerate(results):
            print(f"Pergunta {i + 1}:\n{questions[i]}\nValidação: {result}\n")

    except Exception as e:
        print(f"Erro ao processar o arquivo {dataset_path}: {e}")


if __name__ == "__main__":
    dataset_path = "./digital_forensics.csv"
    asyncio.run(main(dataset_path))
