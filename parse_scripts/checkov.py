import json
from datetime import datetime, timezone
from os import environ

from parse_scripts.util import json_load

SEVERITY_MAP = {"FAILED": "failure", "PASSED": "notice"}


def gh_severity(severity):
    if ret := SEVERITY_MAP.get(severity):
        return ret
    raise NotImplementedError(f"Severity {severity} not implemented in {SEVERITY_MAP}")


def checkov_test(test):
    message = test["check_name"]
    if test["guideline"] is not None:
        info = test["guideline"]
        message = f"{message} - More info: {info}"
    return dict(
        path=test["repo_file_path"],
        start_line=test["file_line_range"][0],
        end_line=test["file_line_range"][1],
        annotation_level=gh_severity(test["check_result"]["result"]),
        title=test["check_id"],
        message=message,
    )


def checkov_entries(data):
    # We only take into consideration failed tests for annotations
    return [checkov_test(test) for test in data["results"]["failed_checks"]]


def checkov_results(log, github_sha=None, dummy=False):
    dockerfile_checks = checkov_entries(log[0])
    github_checks = checkov_entries(log[1])

    conclusion = "success"
    title = "Checkov: All tests passed"
    if dockerfile_checks or github_checks:
        conclusion = "failure"
        title = f"""Checkov: {log[0]["summary"]["failed"] + log[1]["summary"]["failed"]} failed checks"""

    check_type_0 = json.dumps(log[0]["check_type"])
    check_type_1 = json.dumps(log[1]["check_type"])
    summary_0 = json.dumps(log[0]["summary"], indent=2)
    summary_1 = json.dumps(log[1]["summary"], indent=2)
    url = log[0]["url"]

    summary = f"""Total statistics:\n Check_Type: {check_type_0}\n{summary_0}\n\n Check_Type: {check_type_1}\n{summary_1}\n\n{url}"""

    name = "Checkov Comments"
    if dummy:
        conclusion = "neutral"
        title = "Checkov dummy run (always neutral)"
        name = "Checkov dummy run"

    results = {
        "name": name,
        "head_sha": github_sha,
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "conclusion": conclusion,
        "output": {
            "title": title,
            "summary": summary,
            "annotations": dockerfile_checks + github_checks,
        },
    }
    return results


def parse(log_path, sha=None):
    data = json_load(log_path)
    dummy = False
    if environ.get("INPUT_IGNORE_FAILURE") == "true":
        dummy = True
    annotations = checkov_results(log=data, github_sha=sha, dummy=dummy)
    return json.dumps(annotations)
