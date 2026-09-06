import cli


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
