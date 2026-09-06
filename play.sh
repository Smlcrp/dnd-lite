#!/usr/bin/env bash
# One-command setup + launch: creates the venv, installs deps, makes sure
# Ollama is running with the default model pulled, then starts the game.
# Every step checks current state first and skips work that's already done.
# Any arguments (e.g. --model llama3.1:8b) are passed through to main.py.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

OLLAMA_URL="http://localhost:11434"

ollama_is_up() {
    .venv/bin/python -c "
import urllib.request, sys
try:
    urllib.request.urlopen('$OLLAMA_URL', timeout=2)
except Exception:
    sys.exit(1)
"
}

if [ -d .venv ]; then
    echo "Virtual environment already exists, skipping creation."
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Checking dependencies (installs only what's missing/outdated)..."
.venv/bin/pip install --quiet --disable-pip-version-check -r requirements.txt

if ! command -v ollama >/dev/null 2>&1; then
    echo "Error: 'ollama' is not installed. Install it from https://ollama.com/download, then re-run this script." >&2
    exit 1
fi

if ollama_is_up; then
    echo "Ollama server already running, skipping startup."
else
    echo "Starting Ollama server..."
    ollama serve >/tmp/ollama-serve.log 2>&1 &
    for _ in $(seq 1 30); do
        ollama_is_up && break
        sleep 1
    done
    ollama_is_up || { echo "Error: Ollama server did not come up in time. Check /tmp/ollama-serve.log." >&2; exit 1; }
fi

MODEL="${DND_LITE_MODEL:-llama3.1:8b}"
if ollama list | awk '{print $1}' | grep -qx "$MODEL"; then
    echo "Model $MODEL already pulled, skipping download."
else
    echo "Pulling model $MODEL (first run only, this may take a while)..."
    ollama pull "$MODEL"
fi

exec .venv/bin/python main.py "$@"
