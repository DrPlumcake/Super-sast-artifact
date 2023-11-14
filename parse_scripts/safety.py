import json
from datetime import datetime, timezone


def safety_to_gh_severity(safety_severity):
    if safety_severity == "cvssv2" or safety_severity == "cvssv3":
        return "warning"
    else:
        return "notice"


def vulnerability(data, entry_name, entry_num):
    vuln = data["vulnerabilities"][entry_num]
    severity = vuln["severity"]
    # Message contains also other links
    advisory = vuln["advisory"].split("\r\n")[0]
    url = vuln["more_info_url"]
    message = f"{advisory} - Other links:{url}"
    d = dict(
        path=data["affected_packages"][entry_name]["found"],
        # no code
        start_line=1,
        end_line=1,
        # not sure about this
        annotation_level=safety_to_gh_severity(severity),
        title=vuln["CVE"],
        message=message,
    )
    return d


def vulnerabilities_to_annotations(data):
    vulns = []
    counter = 0
    for vuln in data["vulnerabilities"]:
        element = vulnerability(
            data=data, entry_name=vuln["package_name"], entry_num=counter
        )
        vulns.append(element)
        counter = counter + 1
    return vulns


def statistics(data):
    stats = {
        "SCANNED": data["scanned"],
        "SAFETY_VERSION": data["safety_version"],
        "TIMESTAP": data["timestamp"],
        "PACKAGES_FOUND": data["packages_found"],
        "VULNERABILITIES_FOUND": data["vulnerabilities_found"],
        "VULNERABILITIES_IGNORED": data["vulnerabilities_ignored"],
        "REMEDIATIONS_RECOMMENDED": data["remediations_recommended"],
        "OS_TYPE": data["telemetry"]["os_type"],
        "PYTHON_VERSION": data["telemetry"]["python_version"],
        "SAFETY_COMMAND": data["telemetry"]["safety_command"],
        "SAFETY_VERSION": data["telemetry"]["safety_version"],
    }
    return stats


def results(data, github_sha=None):
    safety_vulns = vulnerabilities_to_annotations(data)
    conclusion = "success"
    title = "Safety: No vulnerabilities found"
    if safety_vulns:
        conclusion = "failure"
        title = f"Safety: {len(safety_vulns)} vulnerabilities found"
    summary = f"""Statistics: {json.dumps(statistics(data["report_meta"]), indent=2)}"""
    results = {
        "name": "Safety Comments",
        "head_sha": github_sha,
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "conclusion": conclusion,
        "output": {"title": title, "summary": summary, "annotations": safety_vulns},
    }
    return results


def parse(log_path, sha=None):
    with open(log_path, "r") as safety_fd:
        data = json.load(safety_fd)
    safety_checks = results(data, sha)
    return json.dumps(safety_checks)
