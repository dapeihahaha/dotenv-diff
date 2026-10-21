import json

import pytest

from dotenv_diff.cli import EXIT_ERROR, EXIT_OK, EXIT_PROBLEMS, main
from dotenv_diff.diff import compare
from dotenv_diff.parser import parse_text


@pytest.fixture
def files(tmp_path):
    def make(env, template):
        e = tmp_path / ".env"
        t = tmp_path / ".env.example"
        e.write_text(env)
        t.write_text(template)
        return str(e), str(t)

    return make


def test_compare_categories():
    env = parse_text("A=1\nB=\nEXTRA=x")
    template = parse_text("A=\nB=\nC=")
    result = compare(env, template)
    assert result.missing == ["C"]
    assert result.empty == ["B"]
    assert result.extra == ["EXTRA"]


def test_compare_ignore():
    result = compare(parse_text("X=1"), parse_text("A=\nX="), ignore=["A", "X"])
    assert result.to_dict() == {"missing": [], "extra": [], "empty": []}


def test_ok(files, capsys):
    env, tpl = files("A=1\nB=2", "A=\nB=")
    assert main([env, tpl, "--no-color"]) == EXIT_OK
    assert "matches" in capsys.readouterr().out


def test_missing_fails(files, capsys):
    env, tpl = files("A=1", "A=\nB=")
    assert main([env, tpl, "--no-color"]) == EXIT_PROBLEMS
    out = capsys.readouterr().out
    assert "Missing: 1" in out and "- B" in out


def test_extra_only_fails_in_strict(files):
    env, tpl = files("A=1\nX=1", "A=")
    assert main([env, tpl]) == EXIT_OK
    assert main([env, tpl, "--strict"]) == EXIT_PROBLEMS


def test_empty_and_allow_empty(files):
    env, tpl = files("A=", "A=")
    assert main([env, tpl]) == EXIT_PROBLEMS
    assert main([env, tpl, "--allow-empty"]) == EXIT_OK


def test_json_output(files, capsys):
    env, tpl = files("A=1\nA=2\nX=1", "A=\nB=")
    assert main([env, tpl, "--format", "json"]) == EXIT_PROBLEMS
    data = json.loads(capsys.readouterr().out)
    assert data == {
        "missing": ["B"],
        "extra": ["X"],
        "empty": [],
        "duplicates": ["A"],
        "ok": False,
    }


def test_file_not_found(tmp_path, capsys):
    assert main([str(tmp_path / "nope"), str(tmp_path / "nope2")]) == EXIT_ERROR
    assert "file not found" in capsys.readouterr().err


def test_parse_error(files, capsys):
    env, tpl = files("BROKEN", "A=")
    assert main([env, tpl]) == EXIT_ERROR
    assert "expected KEY=VALUE" in capsys.readouterr().err
