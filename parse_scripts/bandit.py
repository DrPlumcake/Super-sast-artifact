import ast
import json
from datetime import datetime, timezone
from os import environ
from pathlib import Path

from parse_scripts.util import json_load

# Maps bandit severity to github annotation_level
# see: https://docs.github.com/en/rest/reference/checks#create-a-check-run
SEVERITY_MAP = {
    "low": "notice",
    "medium": "warning",
    "high": "failure",
    "undefined": "notice",
}


def gh_severity(severity):
    if ret := SEVERITY_MAP.get(severity.lower()):
        return ret
    raise NotImplementedError(f"Severity {severity} not implemented in {SEVERITY_MAP}")


def bandit_annotation(result):
    try:
        end_line = result["line_range"][-1]
    except (KeyError, IndexError):
        end_line = result["line_number"]

    d = dict(
        path=result["filename"],
        start_line=result["line_number"],
        end_line=end_line,
        annotation_level=gh_severity(result["issue_severity"]),
        title="Test: {test_name} id: {test_id}".format(**result),
        message="{issue_text} more info {more_info}".format(**result),
    )

    return d


def bandit_error(error):
    title = "Error processing file (not a python file?)"
    start_line, end_line = 1, 1
    message = error["reason"]
    try:
        ast.parse(Path(error["filename"]).read_text())
    except SyntaxError as e:
        title = "invalid syntax"
        end_line = start_line = e.lineno
        message = e.msg
    except Exception:  # nosec - I really want to ignore further exceptions here.
        # Use default error values
        pass

    return dict(
        path=error["filename"],
        start_line=start_line,
        end_line=end_line,
        annotation_level="failure",
        title=title,
        message=message,
    )


def bandit_annotations(results):
    return [bandit_annotation(result) for result in results["results"]]


def bandit_run_check(results, github_sha=None, dummy=False):
    annotations = bandit_annotations(results)
    errors = [bandit_error(e) for e in results["errors"]]
    conclusion = "success"
    title = "Bandit: no issues found"
    name = "Bandit comments"
    summary = (
        f"""Total statistics: {json.dumps(results['metrics']["_totals"], indent=2)}"""
    )

    if errors or annotations:
        conclusion = "failure"
        title = f"Bandit: {len(errors)} errors and {len(annotations)} annotations found"
    if dummy:
        conclusion = "neutral"
        name = "Bandit dummy run"
        title = "Bandit dummy run (always neutral)"

    return {
        "name": name,
        "head_sha": github_sha,
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "conclusion": conclusion,
        "output": {
            "title": title,
            "summary": summary,
            "annotations": annotations + errors,
        },
    }


# Only json data
def only_json(log):
    enum = 0
    with open(log, "r+") as log_fd:
        line = log_fd.readline()
        while not line.startswith("{"):
            enum = enum + 1
            line = log_fd.readline()
        log_fd.seek(0)
        lines = log_fd.readlines()

        # In case if json file without indentation, remove [enum:] from lines
        # lines_without_newlines = [line.strip() for line in lines[enum:]]
        # lines = ''.join(lines_without_newlines)

        log_fd.truncate(0)
        log_fd.seek(0)
        log_fd.writelines(lines[enum:-1])
        log_fd.write(lines[-1].strip())


def parse(log, sha=None):
    only_json(log)
    data = json_load(log)
    bandit_checks = bandit_run_check(data, sha, dummy=environ.get("DUMMY_ANNOTATION"))
    return json.dumps(bandit_checks)
