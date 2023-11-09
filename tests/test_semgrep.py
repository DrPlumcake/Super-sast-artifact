import json
from pathlib import Path

import parse_scripts.semgrep

DATA_DIR = Path(__file__).parent / "json"


def test_semgrep():
    out_file = DATA_DIR / "semgrep.json"
    output = out_file.read_text()
    data = json.loads(output)
    parse_scripts.semgrep.parse_data(data, "stuff")
    raise NotImplementedError
