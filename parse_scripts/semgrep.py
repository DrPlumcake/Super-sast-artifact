import json
from datetime import datetime, timezone
from pathlib import Path

JSON_DIR = Path(__file__).parent.parent / "tests/json"

severity_converter = {
    "info": "notice",
    "warn": "warning",
}


def semgrep_to_gh_severity(severity):
    if severity.startswith("err"):
        return "failure"
    return severity_converter.get(severity)


def semgrep_message(error):
    return error["message"].split("\n")[1]


def semgrep_span(entry, span):
    start_line = end_line = 1
    start_column = end_column = None
    if isinstance(span["start"]["line"], int) and isinstance(span["end"]["line"], int):
        start_line = span["start"]["line"]
        end_line = span["end"]["line"]
        if start_line == end_line:
            start_column = span["start"]["col"]
            end_column = span["end"]["col"]

    d = dict(
        path=span["file"],
        start_line=start_line,
        end_line=end_line,
        start_column=start_column,
        end_column=end_column,
        annotation_level=semgrep_to_gh_severity(entry["level"]),
        title=entry["type"],
        message=semgrep_message(entry),
    )
    return d


def summary(data):
    d = {
        "Total_errors": len(data["errors"]),
        "Semgrep_Version": data["version"],
        "paths_scanned": len(data["paths"]["scanned"]),
    }

    return f"""Semgrep statistics: {json.dumps(d, indent=2)}"""


def semgrep_entries(entry):
    return [semgrep_span(entry, span=span) for span in entry["spans"]]


def semgrep_errors(data):
    errors_list = []
    for error in data["errors"]:
        errors_list.extend(semgrep_entries(error))
    return errors_list


def parse_data(log, github_sha=None):
    conclusion = "success"
    title = "Semgrep: "
    semgrep_annotations = semgrep_errors(data=log)

    if semgrep_annotations:
        conclusion = "failure"
        title.join(f"{len(semgrep_annotations)} errors found")
    else:
        title.join("no errors found")

    text = None
    if "_comment" in log["paths"]:
        text = log["paths"]["_comment"]
    results = {
        "name": "Semgrep Comments",
        "head_sha": github_sha,
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "conclusion": conclusion,
        "output": {
            "title": title,
            "summary": summary(log),
            "text": text,
            "annotations": semgrep_annotations,
        },
    }

    return results


def only_json(log):
    enum = 0
    with open(log, "r+") as log_fd:
        line = log_fd.readline()
        while not line.startswith("{"):
            enum = enum + 1
            line = log_fd.readline()
        log_fd.truncate(0)
        log_fd.seek(0)
        tmp = json.loads(line)
        # Re-writing the file to make it more understandable
        json.dump(tmp, log_fd, indent=2)


def parse(log_path, sha=None):
    only_json(log_path)
    with open(log_path, "r") as log:
        data = json.load(log)
    semgrep_data = parse_data(data, sha)
    return json.dumps(semgrep_data)
