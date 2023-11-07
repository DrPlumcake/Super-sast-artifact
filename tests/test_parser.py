from pathlib import Path
import pytest

PARSE_DIR = Path(__file__).parent.parent / "parse_scripts"
JSON_DIR = Path(__file__).parent / "json"

from main import env_json
#possibilità di import dentro ciclo for
'''
for tool in json_list:
    parse_name = f"{tool}_parse"
    from PARSE_DIR.tool import parse as parse_name
''' 
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
        "CHECKOV_ARGS": "-o json"
    }
    env_json("bandit", env)
    env_json("semgrep", env)
    env_json("safety", env)
    env_json("checkov", env)
    env_json("tool", env)
    assert env == {
        "BANDIT_ARGS": " -f json",
        "TOOL_ARGS": "",
        "SAFETY_CONFIG": "",
        "SEMGREP_ARGS": "--verbose --json",
        "CHECKOV_ARGS": "-o json"
    }
    