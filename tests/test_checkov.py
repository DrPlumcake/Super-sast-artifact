import json
from pathlib import Path

from parse_scripts import checkov

TEST_DIR = Path(__file__).parent
JSON_DIR = TEST_DIR / "json"


def test_checkov_parse():
    expected_comments = json.loads((TEST_DIR / "data/checkov_input.json").read_text())
    with open(JSON_DIR / "checkov.json", "r") as fd:
        data = json.load(fd)
    actual_comments = checkov.checkov_results(log=data, github_sha="stuff")
    actual_comments["completed_at"] = "00:00"
    assert expected_comments == actual_comments
