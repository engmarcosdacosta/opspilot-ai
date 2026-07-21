# OpsPilot AI

OpsPilot AI is a prototype that transforms technical procedures, maintenance notes, and operational incidents into clear action plans, checklists, risks, and escalation points.

Built for OpenAI Build Week.

## Why it matters

Operational knowledge is often trapped in long documents and scattered notes. OpsPilot AI turns that context into a practical next-step plan while keeping a human reviewer in control.

## What the prototype does

- Accepts a technical procedure or incident description.
- Extracts objectives, prerequisites, steps, risks, and verification criteria.
- Produces a structured checklist for execution.
- Keeps the source text visible so the operator can review the result.
- Is designed to support retrieval from approved technical reference material.

## How OpenAI, Codex, and GPT-5.6 were used

- OpenAI models are used for structured reasoning over the supplied procedure.
- Codex was used to shape the product workflow, scaffold this repository, draft the prototype, and refine the submission materials.
- GPT-5.6 was used through the Codex workflow for planning, code generation, review, and the transformation prompt design.
- The project is intentionally human-in-the-loop: generated actions must be reviewed before execution.

## Architecture

1. Input: procedure, incident, or maintenance note.
2. Context: optional approved reference material.
3. Reasoning: an OpenAI model extracts and organizes the operational plan.
4. Output: JSON-compatible plan with checklist, risks, and validation steps.
5. Review: an operator confirms or edits the plan.

## Quick start

Requirements: Python 3.10+ and an OpenAI API key.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY="your-api-key"
python app.py
```

The prototype reads a procedure from `example_procedure.md` and prints a structured OpsPilot plan.

Set `OPENAI_MODEL` if your account uses a different available model. The default is `gpt-5.6` to match the Build Week workflow.

## Repository status

This is a Build Week prototype starter. The next iteration is a small browser UI with document upload, retrieval over approved references, editable checklists, and an audit trail.

## Safety and privacy

Do not place secrets in the repository. Do not send confidential operational documents to an external model without authorization. Review generated actions before using them in a real environment.
