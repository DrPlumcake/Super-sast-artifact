from pathlib import Path

import pytest

import parse_scripts.semgrep
from parse_scripts.util import json_load

DATA_DIR = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "infile,expected",
    [
        (f, f.with_suffix(".annotations.json"))
        for f in DATA_DIR.glob("semgrep-[0-9][0-9].json")
    ],
)
def test_parse_data(infile, expected):
    data = json_load(infile)
    expected_results = json_load(expected)
    actual_results = parse_scripts.semgrep.parse_data(data, "stuff")
    actual_results["completed_at"] = "2023-11-09T15:29:33.821590Z"
    assert expected_results == actual_results
