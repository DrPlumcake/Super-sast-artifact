import requests

def gh(url, method="GET", data=None, headers=None, token=None):
    headers = dict(
        headers or {}, **{"Accept": "application/vnd.github.antiope-preview+json"}
    )
    if token:
        headers["Authorization"] = f"token {token}"
    return requests.request(method=method, url=url, headers=headers, data=data)


def to_gh_severity(bandit_severity):
    # Maps bandit severity to github annotation_level
    # see: https://docs.github.com/en/rest/reference/checks#create-a-check-run
    bandit_severity = bandit_severity.lower()
    bandit_severity_map = {
        "low": "notice",
        "medium": "warning",
        "high": "failure",
        "undefined": "notice",
    }
    return bandit_severity_map[bandit_severity]
    