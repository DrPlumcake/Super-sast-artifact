import logging
from pathlib import Path

from main import env_json, parse_tools
from parse_scripts import bandit, checkov, safety, semgrep

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    handlers=[],
)
log = logging.getLogger(__name__)

TEST_DIR = Path(__file__).parent
LOG_DIR = TEST_DIR / "log_dir_test"

json_arg_dict = {
    "trivy_config": {"args": " -f json", "log": "trivy_config.log"},
    "trivy_filesystem": {"args": " -f json", "log": "trivy.log"},
    "bandit": {"args": " -f json", "parse": bandit, "log": "bandit.log"},
    "safety": {
        "args": " --output json",
        "parse": safety,
    },
    "kubescape": {"args": " --format json", "parse": "kubescape.py"},
    "checkov": {"args": " -o json", "parse": checkov, "log": "checkov.log"},
    "semgrep": {"args": " --json", "parse": semgrep, "log": "semgrep.log"},
    "spotbugs": {},
    "owasp_dependency_check": {},
    "spotless_check": {},
    "spotless_apply": {},
}


def test_main_print():
    # Fixture: after a super-sast-run

    expected_text = [
        "Sorry, annotations for trivy_config are not available\n",
        "Sorry, annotations for trivy_filesystem are not available\n",
        "bandit.log does not exists\n",
        "safety.log is empty. Skipping parsing\n",
        "Sorry, annotations for kubescape are not available\n",
        "checkov Request skipped for local testing\n",
        "semgrep.log is empty. Skipping parsing\n",
        "Sorry, annotations for spotbugs are not available\n",
        "Sorry, annotations for owasp_dependency_check are not available\n",
        "Sorry, annotations for spotless_check are not available\n",
        "Sorry, annotations for spotless_apply are not available\n",
    ]

    log.setLevel(logging.INFO)
    file_handler = logging.FileHandler(TEST_DIR / "super-sast-test.log", mode="w")
    log.addHandler(file_handler)
    parse_tools(dict=json_arg_dict, log=log, log_path=LOG_DIR, test=True, local=True)
    with open(TEST_DIR / "super-sast-test.log", "r") as sast_fd:
        text = sast_fd.readlines()
    assert text == expected_text


def test_env_json():
    env = {
        # Normal case
        "BANDIT_ARGS": "",
        # Wrong tool name
        "TOOL_ARGS": "",
        # Not args var
        "SAFETY_CONFIG": "",
        # Other args instead of empty
        "SEMGREP_ARGS": "--verbose",
        # var already set to json
        "CHECKOV_ARGS": " -o json",
    }
    env_json(dict=json_arg_dict, tool="bandit", environ=env)
    env_json(dict=json_arg_dict, tool="semgrep", environ=env)
    env_json(dict=json_arg_dict, tool="safety", environ=env)
    env_json(dict=json_arg_dict, tool="checkov", environ=env)
    env_json(dict=json_arg_dict, tool="tool", environ=env)
    assert env == {
        "BANDIT_ARGS": " -f json",
        "TOOL_ARGS": "",
        "SAFETY_ARGS": " --output json",
        "SAFETY_CONFIG": "",
        "SEMGREP_ARGS": "--verbose --json",
        "CHECKOV_ARGS": " -o json",
    }
