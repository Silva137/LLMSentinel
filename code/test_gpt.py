import asyncio
from openai import AsyncOpenAI

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


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_gpt())
