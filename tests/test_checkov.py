from pathlib import Path

from parse_scripts import checkov
from parse_scripts.util import json_load

TEST_DIR = Path(__file__).parent
JSON_DIR = TEST_DIR / "json"
DATA_DIR = TEST_DIR / "data"


def test_parse():
    expected_comments = json_load(DATA_DIR / "checkov_input.json")
    data = json_load(JSON_DIR / "checkov.json")
    actual_comments = checkov.checkov_results(log=data, github_sha="stuff")
    actual_comments["completed_at"] = "00:00"
    assert expected_comments == actual_comments
