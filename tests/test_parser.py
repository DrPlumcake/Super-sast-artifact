from pathlib import Path

import pytest
PARSE_DIR = Path(__file__).parent.parent / "parse_scripts"
JSON_DIR = Path(__file__).parent. / "json"
from PARSE_DIR.bandit import parse as bandit_parse
from PARSE_DIR.safety import parse as safety_parse
from PARSE_DIR.checkov import parse as checkov_parse
from PARSE_DIR.semgrep import parse as semgrep_parse

json_list = {
    'bandit': "bandit_parse",
    'safety': "safety_parse",
    'checkov': "checkov_parse",
    'semgrep': "semgrep_parse",
}

#possibilità di import dentro ciclo for
'''
for tool in json_list:
    parse_name = f"{tool}_parse"
    from PARSE_DIR.tool import parse as parse_name
''' 



# Parser Main Test
@pytest.mark.parametrize("tool, parse", json_list)
def test_parse(tool):
    results = json.loads(Path(f"{tool}.json").read_text())
    annotations =  parse(results)
    if tool == "bandit":
        assert annotations[0]["path"] == "canary.py"
        assert annotations[0]["start_line"] == 3
    elif tool == "safety":
        assert annotations[0]["package_name"] == "py"
        assert annotations[0]["vulnerable_spec"] == "<=1.11.0"
    elif tool == "checkov":
        assert annotations[0]["check_result"]["result"] == "FAILED"
        assert annotations[0]["code_block"][0] == 3
    elif tool == "semgrep":
        assert annotations[0][]
    
    