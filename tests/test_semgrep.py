from pathlib import Path

import parse_scripts.semgrep
from parse_scripts.util import json_load

DATA_DIR = Path(__file__).parent / "json"

expected_results = {
    "name": "Semgrep Comments",
    "head_sha": "stuff",
    "completed_at": "2023-11-09T15:29:33.821590Z",
    "conclusion": "failure",
    "output": {
        "title": "Semgrep: ",
        "summary": 'Semgrep statistics: {\n  "Total_errors": 1,\n  "Semgrep_Version": "1.34.0",\n  "paths_scanned": 36\n}',
        "text": "<add --verbose for a list of skipped paths>",
        "annotations": [
            {
                "path": ".github/workflows/test.yml",
                "start_line": 31,
                "end_line": 31,
                "start_column": 114,
                "end_column": 117,
                "annotation_level": "warning",
                "title": "Syntax error",
                "message": " When parsing a snippet as Bash for metavariable-pattern in rule 'yaml.github-actions.security.curl-eval.curl-eval'",
            }
        ],
    },
}


def test_parse_data():
    data = json_load(DATA_DIR / "semgrep.json")
    actual_results = parse_scripts.semgrep.parse_data(data, "stuff")
    actual_results["completed_at"] = "2023-11-09T15:29:33.821590Z"
    assert expected_results == actual_results
