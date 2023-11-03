import json
from pathlib import Path

JSON_DIR = Path(__file__).parent.parent / "tests/json"

def semgrep_results(log):
    for result in log["results"]:
        return semgrep_result(result)
    
def semgrep_result(result):

    # if start_line == end_line:
        # coloumns?? 
    
    d = dict(
        path = result["path"],
        end_line = result["end"]["line"],
        start_line = result["start"]["line"],
        message = result["extra"]["message"],
        annotation_level = result["extra"]["severity"],
        title = result["extra"]["metadata"]["vulnerability_class"],
    )
    
    return d

#output is text, for now is readed from a different file than super-sast.log
def parse(output):
    log = json.load(output)
    semgrep_data = semgrep_results(log)
    return json.dump(log, indent = 4)

parse(JSON_DIR / "semgrep.json")