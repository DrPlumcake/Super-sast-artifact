from pathlib import Path

import pytest

from parse_scripts import checkov
from parse_scripts.util import json_load

TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / "data"


@pytest.mark.parametrize(
    "infile,expected",
    [
        (f, f.with_suffix(".annotations.json"))
        for f in DATA_DIR.glob("checkov-[0-9][0-9].json")
    ],
)
def test_parse(infile, expected):
    expected_comments = json_load(expected)
    data = json_load(infile)
    actual_comments = checkov.checkov_results(log=data, github_sha="stuff")
    actual_comments["completed_at"] = "00:00"
    assert expected_comments == actual_comments
