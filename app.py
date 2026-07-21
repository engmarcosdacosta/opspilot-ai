import json
import os
from pathlib import Path

from openai import OpenAI

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")
client = OpenAI()


def build_plan(procedure: str) -> dict:
    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "You are OpsPilot AI. Transform technical procedures into a safe, "
                    "reviewable operations plan. Return valid JSON with keys: objective, "
                    "prerequisites, checklist, risks, verification, escalation. "
                    "Do not invent unavailable facts. Mark uncertainties for human review."
                ),
            },
            {
                "role": "user",
                "content": procedure,
            },
        ],
    )
    return json.loads(response.output_text)


if __name__ == "__main__":
    procedure_path = Path("example_procedure.md")
    procedure = procedure_path.read_text(encoding="utf-8")
    plan = build_plan(procedure)
    print(json.dumps(plan, indent=2, ensure_ascii=False))
