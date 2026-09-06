from unittest.mock import MagicMock, patch

import pytest
import requests

import ollama_client


def test_call_ollama_returns_content():
    fake_resp = MagicMock()
    fake_resp.raise_for_status.return_value = None
    fake_resp.json.return_value = {"message": {"content": "You enter the tavern."}}

    with patch("ollama_client.requests.post", return_value=fake_resp) as mock_post:
        result = ollama_client.call_ollama([{"role": "user", "content": "hi"}])

    assert result == "You enter the tavern."
    assert mock_post.call_args.kwargs["json"]["stream"] is False


def test_call_ollama_raises_runtime_error_on_connection_failure():
    with patch("ollama_client.requests.post", side_effect=requests.ConnectionError("refused")):
        with pytest.raises(RuntimeError):
            ollama_client.call_ollama([{"role": "user", "content": "hi"}])


def test_stream_ollama_yields_chunks_and_stops_on_done():
    fake_resp = MagicMock()
    fake_resp.raise_for_status.return_value = None
    fake_resp.iter_lines.return_value = [
        b'{"message": {"content": "Hel"}, "done": false}',
        b'{"message": {"content": "lo."}, "done": true}',
        b'{"message": {"content": "unreachable"}, "done": false}',
    ]

    with patch("ollama_client.requests.post", return_value=fake_resp):
        chunks = list(ollama_client.stream_ollama([{"role": "user", "content": "hi"}]))

    assert chunks == ["Hel", "lo."]


def test_stream_ollama_skips_empty_lines():
    fake_resp = MagicMock()
    fake_resp.raise_for_status.return_value = None
    fake_resp.iter_lines.return_value = [
        b"",
        b'{"message": {"content": "ok"}, "done": true}',
    ]

    with patch("ollama_client.requests.post", return_value=fake_resp):
        chunks = list(ollama_client.stream_ollama([{"role": "user", "content": "hi"}]))

    assert chunks == ["ok"]


def test_stream_ollama_raises_runtime_error_on_connection_failure():
    with patch("ollama_client.requests.post", side_effect=requests.ConnectionError("refused")):
        with pytest.raises(RuntimeError):
            list(ollama_client.stream_ollama([{"role": "user", "content": "hi"}]))


def test_warmup_swallows_exceptions():
    with patch("ollama_client.requests.post", side_effect=requests.ConnectionError("refused")):
        ollama_client.warmup()  # should not raise


def test_call_ollama_uses_generous_timeout_for_cpu_cold_starts():
    fake_resp = MagicMock()
    fake_resp.raise_for_status.return_value = None
    fake_resp.json.return_value = {"message": {"content": "ok"}}

    with patch("ollama_client.requests.post", return_value=fake_resp) as mock_post:
        ollama_client.call_ollama([{"role": "user", "content": "hi"}])

    # A cold model load on CPU can take well over a minute -- keep enough
    # margin that a slow first turn doesn't spuriously raise RuntimeError.
    assert mock_post.call_args.kwargs["timeout"] >= 300
