# Logical Puzzle Solver

A LangChain-powered logical puzzle solver with hidden Chain-of-Thought reasoning, self-verification, and diagnostic feedback loops.

---

## Architecture

```
                                    ┌─────────────────────────────────────┐
                                    │           USER INPUT                │
                                    │         (Puzzle Text)               │
                                    └─────────────┬───────────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              PUZZLE PIPELINE (app.py)                                   │
│                                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  CLASSIFIER  │───▶│   STRATEGY   │───▶│    SOLVER    │───▶│   VERIFIER   │          │
│  │              │    │   SELECTOR   │    │ (Hidden CoT) │    │ (Diagnostic) │          │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────┬──────┘          │
│         │                   │                   │                    │                 │
│         │                   │                   │                    │                 │
│         │◀──────────────────┴───────────────────┴────────────────────┤                 │
│         │                    FEEDBACK LOOP                           │                 │
│         │           (Routes to correct component)                    │                 │
│         │                                                            │                 │
│         └────────────────────────────────────────────────────────────┘                 │
│                                                  │                                     │
│                                                  ▼                                     │
│                                         ┌──────────────┐                               │
│                                         │   EXPLAINER  │                               │
│                                         │ (Structured) │                               │
│                                         └──────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────────────────┐
                                    │           JSON OUTPUT               │
                                    │    (Answer + Explanation)           │
                                    └─────────────────────────────────────┘
```

---

## Pipeline Steps

| Step | Component | Purpose |
|------|-----------|---------|
| 1 | **Classifier** | Identifies puzzle type (ordering/constraint/deduction) and difficulty (easy/medium/hard) |
| 2 | **Strategy Selector** | Chooses solving approach: constraint_elimination, case_analysis, backtracking, or direct_inference |
| 3 | **Solver** | Solves puzzle using hidden Chain-of-Thought (internal reasoning not exposed) |
| 4 | **Verifier** | Validates solution AND diagnoses issues (classifier/strategy/solver) |
| 5 | **Explainer** | Generates structured explanation with assumptions, deductions, and verification status |

---

## Feedback Loop

If verification fails, the verifier identifies **where** the issue originated:

```
issue_source: "classifier" → Re-classify with feedback
issue_source: "strategy"  → Re-select strategy with feedback
issue_source: "solver"    → Re-solve with feedback
```

The pipeline retries up to 3 times, routing feedback only to the problematic component.

---

## Project Structure

```
logical-puzzle-solver/
├── app.py                 # Main pipeline orchestrator
├── config.py              # Configuration (LLM settings)
├── requirements.txt       # Dependencies
├── .env                   # API keys (create from .env.example)
│
├── core/                  # Pipeline components
│   ├── chains.py          # LangChain chain builder
│   ├── classifier.py      # Puzzle classifier
│   ├── strategy.py        # Strategy selector
│   ├── solver.py          # Puzzle solver
│   ├── verifier.py        # Solution verifier
│   └── explainer.py       # Explanation builder
│
├── models/
│   └── llm_client.py      # LLM factory (OpenAI/Azure)
│
└── prompts/               # Prompt templates
    ├── classifier.txt
    ├── strategy_selector.txt
    ├── solver.txt
    ├── verifier.txt
    └── explainer.txt
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env with your OpenAI or Azure OpenAI credentials

# 3. Run
python app.py
```

---

## Configuration

Edit `.env` file:

**For OpenAI:**
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
```

**For Azure OpenAI:**
```
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=your-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

## Output Format

```json
{
  "puzzle_type": "constraint",
  "difficulty": "hard",
  "strategy": "constraint_elimination",
  "answer": "The German owns the Fish.",
  "explanation": {
    "assumptions": [
      "Five people live in five different colored houses...",
      "Each person has a different nationality..."
    ],
    "deductions": [
      "The Norwegian lives in the first house...",
      "The German is determined to own the Fish."
    ],
    "verification": "All clues are satisfied."
  }
}
```

---

## Key Features

- **Hidden CoT**: Internal reasoning never exposed to user
- **Self-Verification**: Automatic solution validation
- **Diagnostic Feedback**: Identifies and fixes issues at the right component
- **Structured Output**: Clean JSON with assumptions, deductions, verification
- **Retry Logic**: Up to 3 attempts with targeted feedback
