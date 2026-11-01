#!/usr/bin/env bash
# Offline demonstration; no GPU, API key, or external requests.
set -euo pipefail
python -m unittest discover -s tests -q
python -m traceqa ask "ContextWindowExceededError max_output_tokens max_model_len" --mode hybrid
mkdir -p reports
python -m traceqa eval --variant b0 --out reports/b0.json
python -m traceqa eval --variant b1 --out reports/b1.json
python -m traceqa eval --variant b2 --out reports/b2.json
python -m traceqa compare reports/b0.json reports/b1.json
