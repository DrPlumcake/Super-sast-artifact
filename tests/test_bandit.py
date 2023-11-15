from pathlib import Path

from parse_scripts import bandit
from parse_scripts.util import json_load

TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / "data"


def test_errors():
    results = json_load(DATA_DIR / "bandit_error.json")
    errors = [bandit.bandit_error(error) for error in results["errors"]]
    assert errors[0]["path"] == "LICENSE"
    assert errors[1] == {
        "path": "tests/data/python-01/py2.py",
        "start_line": 2,
        "end_line": 2,
        "annotation_level": "failure",
        "title": "invalid syntax",
        "message": "Missing parentheses in call to 'print'. Did you mean print(...)?",
    }


def test_annotations():
    data = json_load(DATA_DIR / "bandit.json")
    annotations = bandit.bandit_annotations(data)
    assert annotations[0]["path"] == "canary.py"
    assert annotations[0]["start_line"] == 3


def test_run_check():
    data = json_load(DATA_DIR / "bandit.json")
    run_check_body = bandit.bandit_run_check(data)
    assert run_check_body["conclusion"] == "failure"
