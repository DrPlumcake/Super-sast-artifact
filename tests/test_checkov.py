import json
from pathlib import Path

from parse_scripts import checkov

TEST_DIR = Path(__file__).parent
JSON_DIR = TEST_DIR / "json"


def test_checkov_parse():
    expected_comments = {
        "name": "Checkov Comments",
        "head_sha": "stuff",
        "completed_at": "00:00",
        "conclusion": "failure",
        "output": {
            "title": "Checkov: 2 failed checks",
            "summary": """Total statistics:\n Check_Type: "dockerfile"\n{\n  "passed": 9,\n  "failed": 1,\n  "skipped": 0,\n  "parsing_errors": 0,\n  "resource_count": 1,\n  "checkov_version": "2.2.327"\n}\n\n Check_Type: "github_actions"\n{\n  "passed": 37,\n  "failed": 1,\n  "skipped": 0,\n  "parsing_errors": 0,\n  "resource_count": 0,\n  "checkov_version": "2.2.327"\n}\n\nAdd an api key '--bc-api-key <api-key>' to see more detailed insights via https://bridgecrew.cloud""",
            "annotations": [
                {
                    "path": "/Dockerfile",
                    "start_line": 3,
                    "end_line": 3,
                    "start_column": 1,
                    "end_column": 1,
                    "annotation_level": "failure",
                    "title": "CKV_DOCKER_7",
                    "message": "Ensure the base image uses a non latest version tag - More info: https://docs.paloaltonetworks.com/content/techdocs/en_US/prisma/prisma-cloud/prisma-cloud-code-security-policy-reference/docker-policies/docker-policy-index/ensure-the-base-image-uses-a-non-latest-version-tag.html",
                },
                {
                    "path": "/.github/workflows/bandit.yml",
                    "start_line": 0,
                    "end_line": 1,
                    "start_column": 1,
                    "end_column": 1,
                    "annotation_level": "failure",
                    "title": "CKV2_GHA_1",
                    "message": "Ensure top-level permissions are not set to write-all",
                },
            ],
        },
    }
    with open(JSON_DIR / "checkov.json", "r") as fd:
        data = json.load(fd)
    actual_comments = checkov.checkov_results(log=data, github_sha="stuff")
    actual_comments["completed_at"] = "00:00"
    assert expected_comments == actual_comments
