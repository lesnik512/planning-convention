import index


def test_empty_input_returns_empty() -> None:
    assert index.parse_frontmatter("") == {}


def test_no_leading_delimiter_returns_empty() -> None:
    assert index.parse_frontmatter("# heading\nsummary: x\n") == {}


def test_parses_single_line_scalars() -> None:
    text = "---\nsummary: did a thing\nstatus: accepted\n---\n# body\n"
    assert index.parse_frontmatter(text) == {"summary": "did a thing", "status": "accepted"}


def test_null_value_becomes_empty_string() -> None:
    assert index.parse_frontmatter("---\nsummary: null\n---\n") == {"summary": ""}


def test_quotes_are_stripped() -> None:
    text = "---\na: \"double\"\nb: 'single'\n---\n"
    assert index.parse_frontmatter(text) == {"a": "double", "b": "single"}


def test_line_without_separator_is_skipped() -> None:
    text = "---\nnocolon\nsummary: kept\n---\n"
    assert index.parse_frontmatter(text) == {"summary": "kept"}


def test_indented_continuation_lines_are_skipped() -> None:
    text = "---\nsummary: kept\n  indented: ignored\n\ttabbed: ignored\n---\n"
    assert index.parse_frontmatter(text) == {"summary": "kept"}


def test_second_delimiter_terminates_block() -> None:
    text = "---\nsummary: kept\n---\nafter: ignored\n"
    assert index.parse_frontmatter(text) == {"summary": "kept"}
