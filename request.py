import requests

def gh(url, method="GET", data=None, headers=None, token=None):
    headers = dict(
        headers or {}, **{"Accept": "application/vnd.github.antiope-preview+json"}
    )
    if token:
        headers["Authorization"] = f"token {token}"
    return requests.request(method=method, url=url, headers=headers, data=data)

    