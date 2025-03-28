import json
import os

import pandas as pd


def parse_input(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Extract the question (remove the "Question:" prefix if present)
    if lines and lines[0].lower().startswith("question:"):
        question = lines[0][len("question:"):].strip()
    else:
        question = lines[0] if lines else ""

    # Initialize options with empty strings
    option_a = option_b = option_c = option_d = ""

    # Process subsequent lines for options
    for line in lines[1:]:
        if line.startswith("A."):
            option_a = line[len("A."):].strip()
        elif line.startswith("B."):
            option_b = line[len("B."):].strip()
        elif line.startswith("C."):
            option_c = line[len("C."):].strip()
        elif line.startswith("D."):
            option_d = line[len("D."):].strip()

    return question, option_a, option_b, option_c, option_d


def format_CyberBench_datasets(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    # Extract the question, options, and correct answer
    questions_data = []
    for index, row in df.iterrows():
        question, option_a, option_b, option_c, option_d = parse_input(row["input"])
        questions_data.append({
            "Question": question,
            "Option A": option_a,
            "Option B": option_b,
            "Option C": option_c,
            "Option D": option_d,
            "Correct Answer": row["output"]
        })

    df_final = pd.DataFrame(questions_data)
    df_final.to_csv(output_csv, sep=';', index=False, encoding='utf-8')


def split_csv_by_dataset_CyberBench():
    input_csv = "../datasets/cyberbench.csv"

    df = pd.read_csv(input_csv)

    filtered_df = df[df['task'] == 'mc']

    # Split by dataset value and save each to a separate file
    for dataset_name, group in filtered_df.groupby('dataset'):
        output_csv = os.path.join("../datasets/", f"{dataset_name}.csv")
        group.to_csv(output_csv, index=False)
        print(f"Saved: {output_csv}")


def json_to_csv_SecEval():
    input_json_file = "../datasets/SecEval.json"  # Change this to your JSON file name
    output_csv_file = "../datasets/SecEval.csv"

    with open(input_json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    questions_data = []
    count = 0
    for item in data:
        if count >= 250:  # Limit to 250 questions
            break

        choices = item.get("choices", [])

        correct_answer = item["answer"].strip().upper()
        domain = ", ".join(item.get("topics", []))

        if len(domain) == 0:
            domain = "Unknown"

        if len(correct_answer) != 1:
            continue

        questions_data.append({
            "Question": item["question"],
            "Option A": choices[0].split(": ", 1)[-1],  # Extracting the answer text after "A: "
            "Option B": choices[1].split(": ", 1)[-1],
            "Option C": choices[2].split(": ", 1)[-1],
            "Option D": choices[3].split(": ", 1)[-1],
            "Correct Answer": correct_answer,
            "Domain": domain
        })

        count += 1

    # Create DataFrame
    df = pd.DataFrame(questions_data)

    # Save to CSV with ; as separator
    df.to_csv(output_csv_file, sep=';', index=False, encoding='utf-8')


def json_to_csv():
    input_json_file = "../datasets/CyberMetric-80-v1.json"  # Change this to your JSON file name
    output_csv_file = "../datasets/CyberMetric_80.csv"

    with open(input_json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Process questions into a structured format
    questions_data = []

    for item in data["questions"]:
        questions_data.append({
            "Question": item["question"],
            "Option A": item["answers"]["A"],
            "Option B": item["answers"]["B"],
            "Option C": item["answers"]["C"],
            "Option D": item["answers"]["D"],
            "Correct Answer": item["solution"]
        })

    # Create DataFrame
    df = pd.DataFrame(questions_data)

    # Save to CSV with ; as separator
    df.to_csv(output_csv_file, sep=';', index=False, encoding='utf-8')


def convert_secqa_format(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    # Rename and reorder columns to match SecQA v1 format
    df.rename(columns={
        "Question": "Question",
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D",
        "Answer": "Correct Answer",
        "Explanation": "Explanation"
    }, inplace=True)

    df.to_csv(output_csv, sep=';', index=False, encoding='utf-8')

    print(f"Converted file saved as: {output_csv}")



if __name__ == "__main__":
    #change_sep()
    #json_to_csv()
    #json_to_csv_SecEval()
    #split_csv_by_dataset_CyberBench()
    #format_CyberBench_datasets("../datasets/cyquiz.csv", "../datasets/cyquiz-final.csv")
    #format_CyberBench_datasets("../datasets/secmmlu.csv", "../datasets/secmmlu-final.csv")
    convert_secqa_format("../datasets/secqa_v2_test.csv", "../datasets/secqa_v2.csv")
