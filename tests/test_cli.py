import cli
import profile


def test_tag_filter_hides_tag_within_single_token():
    f = cli._TagFilter()
    assert f.feed("Before [SCENE: Docks] after") == "Before  after"


def test_tag_filter_hides_tag_split_across_multiple_tokens():
    f = cli._TagFilter()
    out = []
    for chunk in ["Before ", "[SCE", "NE: Doc", "ks] after"]:
        out.append(f.feed(chunk))
    assert "".join(out) == "Before  after"


def test_tag_filter_handles_multiple_tags():
    f = cli._TagFilter()
    out = f.feed("[BEAT]\nYou press onward.\n[CHECK: Perception]\nSomething glints.")
    assert out == "\nYou press onward.\n\nSomething glints."


def test_tag_filter_no_tags_passthrough():
    f = cli._TagFilter()
    assert f.feed("Nothing special happens.") == "Nothing special happens."


def test_main_handles_ollama_failure_gracefully(monkeypatch, capsys):
    """A cold-start timeout or dropped Ollama server during adventure setup
    should print a friendly message, not crash with a raw traceback -- and
    must never fall through into the main game loop."""
    monkeypatch.setattr(cli, "_pick_profile", lambda: profile.create_profile("Sam"))
    monkeypatch.setattr(cli, "_startup_menu", lambda prof: "new")

    def boom(prof, dungeon_master):
        raise RuntimeError("Could not reach Ollama at http://localhost:11434/api/chat: timed out")

    monkeypatch.setattr(cli, "_start_new_adventure", boom)
    monkeypatch.setattr(
        cli,
        "_main_loop",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("main loop must not run after a setup failure")),
    )

    cli.main()  # must not raise

    out = capsys.readouterr().out
    assert "DM error" in out
    assert "ollama serve" in out


def test_main_passes_explicit_model_override_to_dungeon_master(monkeypatch):
    monkeypatch.setattr(cli, "_pick_profile", lambda: profile.create_profile("Sam"))
    monkeypatch.setattr(cli, "_startup_menu", lambda prof: "quit")

    captured = {}

    class FakeDungeonMaster:
        def __init__(self, model):
            captured["model"] = model

    monkeypatch.setattr(cli.dm, "DungeonMaster", FakeDungeonMaster)

    cli.main(model="qwen2.5:7b")

    assert captured["model"] == "qwen2.5:7b"


def test_main_uses_dungeon_master_default_when_no_model_given(monkeypatch):
    """With no --model override, DungeonMaster() must be constructed with no
    argument at all -- not model=None -- so it falls back to its own default
    (ollama_client.DEFAULT_MODEL) rather than a broken None model string."""
    monkeypatch.setattr(cli, "_pick_profile", lambda: profile.create_profile("Sam"))
    monkeypatch.setattr(cli, "_startup_menu", lambda prof: "quit")

    captured = {"args": "not called"}

    class FakeDungeonMaster:
        def __init__(self, *args):
            captured["args"] = args

    monkeypatch.setattr(cli.dm, "DungeonMaster", FakeDungeonMaster)

    cli.main()

    assert captured["args"] == ()
