import json


def json_load(fpath):
    return json.loads(fpath.read_text())
