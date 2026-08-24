# DSPy Self-Improving Prompt Optimizer

A declarative prompt compiler and optimizer implementing the DSPy paradigm: replacing fragile manual prompt strings with programmatic signatures, metric evaluators, and automated MIPROv2 teleprompter search over few-shot examples and instruction candidates.

## Key Capabilities

- **Declarative Signatures**: Separates pipeline architecture (`inputs`, `outputs`, `instructions`) from runtime prompts.
- **MIPROv2 Teleprompter**: Automates instruction proposal search and bootstraps few-shot demonstrations against target metrics.
- **Metric Evaluation Harness**: Computes Token F1, format compliance, and semantic verification scores.
- **Dynamic Compilation**: Re-compiles and optimizes pipeline parameters without code refactoring.

## Quick Start

### Local Setup

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Run optimizer server
uvicorn src.main:app --reload --port 8000

# 3. Execute tests
pytest tests/ -v
```

### Endpoints

- `POST /predict`: Execute declarative forward pass.
- `POST /compile`: Run teleprompter optimizer against a training dataset.
- `POST /evaluate`: Score compiled pipeline against a test dataset.
