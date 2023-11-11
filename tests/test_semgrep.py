import json
from pathlib import Path

import parse_scripts.semgrep

DATA_DIR = Path(__file__).parent / "json"

expected_results = {
    "name": "Semgrep Comments",
    "head_sha": "stuff",
    "completed_at": "2023-11-09T15:29:33.821590Z",
    "conclusion": "failure",
    "output": {
        "title": "Semgrep: ",
        "summary": 'Semgrep statistics: {"Total errors": 1, "Semgrep Version": "1.34.0", "paths scanned": 36}',
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
            },
            {
                "path": ".github/workflows/test.yml",
                "start_line": 31,
                "end_line": 31,
                "start_column": 157,
                "end_column": 160,
                "annotation_level": "warning",
                "title": "Syntax error",
                "message": " When parsing a snippet as Bash for metavariable-pattern in rule 'yaml.github-actions.security.curl-eval.curl-eval'",
            },
            {
                "path": ".github/workflows/test.yml",
                "start_line": 31,
                "end_line": 31,
                "start_column": 196,
                "end_column": 199,
                "annotation_level": "warning",
                "title": "Syntax error",
                "message": " When parsing a snippet as Bash for metavariable-pattern in rule 'yaml.github-actions.security.curl-eval.curl-eval'",
            },
            {
                "path": ".github/workflows/test.yml",
                "start_line": 31,
                "end_line": 31,
                "start_column": 234,
                "end_column": 237,
                "annotation_level": "warning",
                "title": "Syntax error",
                "message": " When parsing a snippet as Bash for metavariable-pattern in rule 'yaml.github-actions.security.curl-eval.curl-eval'",
            },
        ],
    },
}


def test_semgrep():
    out_file = DATA_DIR / "semgrep.json"
    output = out_file.read_text()
    data = json.loads(output)
    actual_results = parse_scripts.semgrep.parse_data(data, "stuff")
    assert (
        actual_results["output"]["annotations"][0]["start_line"]
        == expected_results["output"]["annotations"][0]["start_line"]
    )
    assert (
        actual_results["output"]["annotations"][0]["end_line"]
        == expected_results["output"]["annotations"][0]["end_line"]
    )
