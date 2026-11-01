# PowerShell offline demo; run in repository root after pip install -e .
$ErrorActionPreference='Stop'
python -m unittest discover -s tests -q
if (!(Test-Path reports)) { New-Item -ItemType Directory reports | Out-Null }
python -m traceqa ask 'ContextWindowExceededError max_output_tokens max_model_len' --mode hybrid
python -m traceqa eval --variant b0 --out reports/b0.json
python -m traceqa eval --variant b1 --out reports/b1.json
python -m traceqa eval --variant b2 --out reports/b2.json
python -m traceqa compare reports/b0.json reports/b1.json
