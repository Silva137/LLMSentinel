import asyncio

import openai
from openai import AsyncOpenAI
import requests
import json

# Configuração da API do LLM
TOKEN = "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"
endpoint = "https://models.inference.ai.azure.com"

client = AsyncOpenAI(
    base_url=endpoint,
    api_key=TOKEN,
)


async def test_gpt():
    try:
        # Preparar a mensagem para o modelo
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": "Qual é a capital da França?"}
            ],
            temperature=0.7,
            max_tokens=50
        )

        content = response.choices[0].message.content.strip()
        print("Resposta do GPT:", content)

    except Exception as e:
        print(f"Erro ao conectar-se ao GPT: {str(e)}")


def query_llm_fireworks():
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    model = "accounts/fireworks/models/llama-v3p1-8b-instruct"
    payload = {
        "model": model,
        "max_tokens": 500,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {"role": "user", "content": "Que paises fazem parte da peninsula ibérica?"}
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer fw_3ZjJEBdGSgYneU2XaMMeFn2w"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Erro ao validar com Fireworks LLM: {e}"


def get_fireworks_models():
    url = "https://api.fireworks.ai/v1/accounts/fireworks/models"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer fw_3ZjJEBdGSgYneU2XaMMeFn2w"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model["name"] for model in models]
    except requests.exceptions.RequestException as e:
        return f"Erro ao recuperar modelos do Fireworks LLM: {e}"


def query_llm_openrouter():
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    data = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": [{"role": "user", "content": "Que paises fazem parte da peninsula ibérica?"}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Erro ao perguntar ao modelo: {e}"


def get_openrouter_models():
    client = openai.OpenAI(
        api_key="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",
        base_url="https://openrouter.ai/api/v1"
    )

    try:
        response = client.models.list()
        models = response.data
        return [model.id for model in models]

    except openai.OpenAIError as e:
        print(f"Error fetching LLM models from OpenRouter: {e}")


def get_api_key_limits(api_key):
    url = "https://openrouter.ai/api/v1/auth/key"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        limits = response.json()
        print(json.dumps(limits, indent=2))
        return limits
    except requests.exceptions.RequestException as e:
        print(f"Error fetching API key limits: {e}")
        return None


if __name__ == "__main__":
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # asyncio.run(test_gpt())
    # print(query_llm_fireworks())
    # print(get_fireworks_models())
    #print(query_llm_openrouter())
    #print(get_openrouter_models())
    api_key = "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"
    get_api_key_limits(api_key)
