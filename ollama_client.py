"""Shared Ollama call plumbing, used by both dm.py (streaming, in-game
narration) and architect.py (one-shot, structured adventure generation).

No provider-abstraction layer here on purpose -- add one only when a second
provider actually needs supporting.
"""

import json
import os

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

# llama3.1:8b: reliably follows the tag/JSON instructions and runs
# acceptably (~30-60s/turn) on an 8-core CPU with no GPU. On a machine with
# a capable GPU, a larger model (e.g. nous-hermes2:10.7b) will be both
# faster and higher quality. Three ways to change it, in increasing
# precedence: edit _FALLBACK_MODEL below; set the DND_LITE_MODEL environment
# variable; or pass --model at the command line (see main.py), which flows
# through to DungeonMaster()/architect.build_adventure() as an explicit
# model= argument.
_FALLBACK_MODEL = "llama3.1:8b"


def _resolve_default_model() -> str:
    return os.environ.get("DND_LITE_MODEL", _FALLBACK_MODEL)


DEFAULT_MODEL = _resolve_default_model()


def warmup(model: str = DEFAULT_MODEL) -> None:
    """Best-effort call to get the model loaded into memory before the
    player's first real turn. Failures are swallowed -- the first real call
    will surface any actual problem."""
    try:
        requests.post(
            OLLAMA_URL,
            json={"model": model, "messages": [{"role": "user", "content": "hi"}], "stream": False},
            timeout=300,
        )
    except requests.RequestException:
        pass


def call_ollama(messages: list, model: str = DEFAULT_MODEL) -> str:
    """Non-streaming call. Returns the full response text.

    Raises RuntimeError on any connection failure or non-200 response so
    callers can present a friendly error instead of crashing.
    """
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": model, "messages": messages, "stream": False},
            timeout=300,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Could not reach Ollama at {OLLAMA_URL}: {e}") from e

    data = resp.json()
    return data["message"]["content"]


def stream_ollama(messages: list, model: str = DEFAULT_MODEL):
    """Streaming call. Yields text chunks as they arrive.

    Raises RuntimeError on any connection failure so callers can present a
    friendly error instead of crashing mid-story.
    """
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": model, "messages": messages, "stream": True},
            timeout=300,
            stream=True,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
            if chunk.get("done"):
                break
    except requests.RequestException as e:
        raise RuntimeError(f"Could not reach Ollama at {OLLAMA_URL}: {e}") from e
