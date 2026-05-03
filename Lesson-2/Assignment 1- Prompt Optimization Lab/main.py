from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

from prompts import basic_prompt, refined_prompt, cot_prompt
from test_cases import test_cases

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

prompts = {
    "basic": basic_prompt,
    "refined": refined_prompt,
    "cot": cot_prompt
}


def get_response(system_prompt, user_input):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content


@app.get("/run-tests")
def run_tests():

    results = []
    for case in test_cases:
        case_result = {
            "user_input": case
        }
        for prompt_name, prompt_text in prompts.items():

            output = get_response(prompt_text, case)

            case_result[prompt_name] = output

        results.append(case_result)

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    return results