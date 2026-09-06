"""Shared Ollama call plumbing, used by both dm.py (streaming, in-game
narration) and architect.py (one-shot, structured adventure generation).

No provider-abstraction layer here on purpose -- add one only when a second
provider actually needs supporting.
"""

import json

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "nous-hermes2:10.7b"


def warmup(model: str = DEFAULT_MODEL) -> None:
    """Best-effort call to get the model loaded into memory before the
    player's first real turn. Failures are swallowed -- the first real call
    will surface any actual problem."""
    try:
        requests.post(
            OLLAMA_URL,
            json={"model": model, "messages": [{"role": "user", "content": "hi"}], "stream": False},
            timeout=120,
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
            timeout=120,
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
            timeout=120,
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
