import time
import os
import statistics
import openai
import pandas as pd
from google import genai
from google.genai import types
import matplotlib.pyplot as plt
import seaborn as sns

# ==== CONFIG ====
GOOGLE_API_KEY = "AIzaSyCPNA1pu7JueWEAmIUYgXlZa-apeKwqvRI"
OPENROUTER_API_KEY = "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"
CSV_PATH = "C:\ISEL\Tese\git\code\datasets\honeypots.csv"
CSV_RESULTS_PATH = "latency_results.csv"

# Vertex AI config (project & region)
VERTEX_PROJECT = "tese-438022"
VERTEX_LOCATION = "global"


# ==== LOAD AND FORMAT PROMPTS ====
def load_honeypot_prompts(csv_path):
    df = pd.read_csv(csv_path, sep=";", skiprows=1)
    prompts = []

    for _, row in df.iterrows():
        prompt = (
            f"You are a cybersecurity expert. Your task is to select the correct answer to the multiple-choice question below.\n"
            f"Respond with the letter corresponding to the correct option (A, B, C, or D). Do not add explanations. Do not write anything else.\n"
            f"Strictly follow the response format provided below.\n\n"
            f"Question:\n{row['Question']}\n\n"
            f"Options:\n"
            f"A: {row['Option A']}\n"
            f"B: {row['Option B']}\n"
            f"C: {row['Option C']}\n"
            f"D: {row['Option D']}\n\n"
            f"### Response Format:\n"
            f"Answer: <Correct answer letter (A, B, C, or D)>\n\n"
            f"### Example Response:\n"
            f"Answer: C"
        )
        prompts.append(prompt)
    return prompts


# ==== VERTEX AI (Google Cloud) ====
def query_vertex_gemini(prompt):
    client = genai.Client(
        vertexai=True,
        project=VERTEX_PROJECT,
        location=VERTEX_LOCATION
    )

    model = "gemini-2.5-pro"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
    )

    start = time.time()
    chunks = client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    response_text = "".join(chunk.text for chunk in chunks if chunk.text is not None)
    duration = time.time() - start
    return response_text.strip(), duration


# ==== GOOGLE AI STUDIO ====
def query_google_gemini(prompt):
    os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY
    client = genai.Client(api_key=GOOGLE_API_KEY)
    model = "gemini-2.5-pro"

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
    )

    start = time.time()
    chunks = client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    response_text = "".join(chunk.text for chunk in chunks if chunk.text is not None)
    duration = time.time() - start
    return response_text.strip(), duration


# ==== OPENROUTER ====
def query_openrouter_gemini(prompt):
    client = openai.OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    start = time.time()
    response = client.chat.completions.create(
        model="google/gemini-2.5-pro",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20000,
    )
    duration = time.time() - start
    content = response.choices[0].message.content.strip()
    return content, duration


# ==== VISUALIZATION FUNCTIONS ====
def plot_average_latency_bar_chart(df):
    plt.figure(figsize=(8, 5))

    avg_df = df.groupby("platform", as_index=False)["latency_seconds"].mean().sort_values("latency_seconds")
    sns.barplot(data=avg_df, x="platform", y="latency_seconds", hue="platform", palette="Set3", legend=False)

    plt.ylabel("Average Latency (seconds)")
    plt.title("Average Latency per Platform")
    plt.tight_layout()
    plt.show()


def plot_latency_box_plot(df):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="platform", y="latency_seconds", data=df, hue="platform", palette="Set2", legend=False)
    sns.stripplot(x="platform", y="latency_seconds", data=df, color='black', alpha=0.6, jitter=0.1)
    plt.title("Latency Distribution per Platform (Boxplot)")
    plt.ylabel("Latency (seconds)")
    plt.tight_layout()
    plt.show()


# ==== LATENCY SUMMARY ====
def summarize_latencies(name, durations):
    print(f"\n📊 {name} Latency Stats (seconds):")
    print(f"  - Média:         {statistics.mean(durations):.2f}")
    print(f"  - Variância:     {statistics.variance(durations):.4f}")
    print(f"  - Desvio Padrão: {statistics.stdev(durations):.4f}")
    print(f"  - Mínimo:        {min(durations):.2f}")
    print(f"  - Máximo:        {max(durations):.2f}")


# ==== MAIN ====
def main():
    if os.path.exists(CSV_RESULTS_PATH):
        df = pd.read_csv(CSV_RESULTS_PATH)
        print(f"✅ Ficheiro com resultados encontrado: {CSV_RESULTS_PATH}")
    else:
        prompts = load_honeypot_prompts(CSV_PATH)
        results = []
        print(f"🔁 Testing {len(prompts)} Honeypots questions...\n")

        for i, prompt in enumerate(prompts):
            print(f"🧪 Prompt {i + 1}/{len(prompts)}")

            # Vertex
            vertex_output, v_time = query_vertex_gemini(prompt)
            print(f"  ✅ Vertex AI:      {v_time:.2f}s | {vertex_output[:100]}...")
            results.append({"prompt_index": i + 1, "platform": "Vertex AI", "latency_seconds": round(v_time, 4)})

            # Google Studio
            google_output, g_time = query_google_gemini(prompt)
            print(f"  ✅ Google Studio:  {g_time:.2f}s | {google_output[:100]}...")
            results.append({"prompt_index": i + 1, "platform": "Google AI Studio", "latency_seconds": round(g_time, 4)})

            # OpenRouter
            openrouter_output, o_time = query_openrouter_gemini(prompt)
            print(f"  ✅ OpenRouter:     {o_time:.2f}s | {openrouter_output[:100]}...\n")
            results.append({"prompt_index": i + 1, "platform": "OpenRouter", "latency_seconds": round(o_time, 4)})

        # Save
        df = pd.DataFrame(results)
        df.to_csv(CSV_RESULTS_PATH, index=False)
        print(f"✅ Results saved in '{CSV_RESULTS_PATH}'")

        # Summary
        for platform in ["Vertex AI", "Google AI Studio", "OpenRouter"]:
            subset = df[df["platform"] == platform]["latency_seconds"].tolist()
            summarize_latencies(platform, subset)

    # Plot
    plot_average_latency_bar_chart(df)
    plot_latency_box_plot(df)


if __name__ == "__main__":
    main()