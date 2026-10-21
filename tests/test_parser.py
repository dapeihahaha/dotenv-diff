import pytest

from dotenv_diff.parser import ParseError, duplicate_keys, parse_text


def values(text):
    return {k: e.value for k, e in parse_text(text).items()}


def test_basic_and_comments():
    text = "# comment\n\nA=1\nB = two \n"
    assert values(text) == {"A": "1", "B": "two"}


def test_export_prefix():
    assert values("export TOKEN=abc") == {"TOKEN": "abc"}


def test_quoted_values():
    text = "A='hello # not a comment'\nB=\"line\\nbreak\"\nC=\"\""
    assert values(text) == {"A": "hello # not a comment", "B": "line\nbreak", "C": ""}


def test_inline_comment_on_unquoted_value():
    assert values("A=value # trailing") == {"A": "value"}
    assert values("A=val#ue") == {"A": "val#ue"}


def test_empty_value():
    assert values("A=") == {"A": ""}


def test_value_containing_equals():
    assert values("URL=postgres://u:p@h/db?a=b") == {"URL": "postgres://u:p@h/db?a=b"}


def test_line_numbers():
    entries = parse_text("\n# c\nA=1\n")
    assert entries["A"].line == 3


def test_missing_equals_raises():
    with pytest.raises(ParseError) as exc:
        parse_text("A=1\nBROKEN", path=".env")
    assert ".env:2" in str(exc.value)


def test_invalid_key_raises():
    with pytest.raises(ParseError):
        parse_text("1ABC=x")


def test_unterminated_quote_raises():
    with pytest.raises(ParseError):
        parse_text('A="oops')


def test_duplicate_keys():
    assert duplicate_keys("A=1\nB=2\nA=3\nexport B=4\nC=5") == ["A", "B"]
