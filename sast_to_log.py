# From input write to tool.log

from sys import stdin, stdout
from pathlib import Path
from main import logging
import os, stat
from subprocess import run
PATH_LOG_DIR = Path(__file__).parent / "log_dir"

def write_to_log(tool, path):
    # Remove file if exists
    if path.exists():
        os.remove(path)

    # Open the tool.log file and write in it
    file_handler = logging.FileHandler(path, mode='w')
    log.addHandler(file_handler)
    os.chmod(path=path, mode=0o666)
    line_counter = 0
    error_found = 0
    end_loop = 1
    while(end_loop):
        line = stdin.readline().rstrip()
        if line[25:].strip().startswith(f"Running {tool}") or line[25:].strip().startswith(f"Preparing {tool}") or line.strip().endswith("WARNING Directory /code/.m2 already exists. Skipping copy.") or line[25:].strip().startswith("Running trivy"):
            continue
        if line.strip().endswith("Skipping maven command because pom.xml is missing") or line[:-2].strip().endswith(f"{tool} failed with status"):
            # exit status_code = 0 -> end of tool file
            if line.startswith("}"):
                log.info("}")
            exit_from_log(file_handler)
            log.info(line[1:])
            return
        if line.strip().endswith(f"Skipping {tool}") and line[20:28].strip() != "WARNING":
            exit_from_log(file_handler)
            log.info(line)
            return
        if line[25:35].strip() == "Preparing" and line[36:].strip() != tool and not line.strip().endswith(tool):
            exit_from_log(file_handler)
            return # (line[36:].strip())
        if line[21:27].strip() == "ERROR":
            if line[27:].strip().startswith("An exception occurred while running SAST"):
                # Two other lines to read and then closes the file
                line_counter = 2
                error_found = 1
        if line[25:44].strip == "All tools finished":
            end_loop = 0
            exit_from_log(file_handler)
            return
        log.info(line)
        if error_found:
            if not line_counter:
                exit_from_log(file_handler)
                return
            else:
                line_counter = line_counter - 1
    exit_from_log(file_handler)
    

def exit_from_log(handler):
    # The file is closed so we remove the handler from the list      
    log.removeHandler(handler)

if __name__ == "__main__":
    # from main import TOOLS_MAP // doesn't work for some reason
    tool_list=[
        "trivy_config",
        "trivy_filesystem",
        "bandit",
        "safety",
        "kubescape",
        "checkov",
        "semgrep",
        "spotbugs",
        "owasp_dependency_check",
        "spotless_check",
        "spotless_apply",
    ]
    # Log to stdout.
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(stream=stdout),
        ],
    )
    log = logging.getLogger(__name__)
    for tool in tool_list:
        log_path = PATH_LOG_DIR / f"{tool}.log"
        next_tool = write_to_log(tool=tool, path=log_path)
    
    line = stdin.readline().strip()
    while line[20:24] == "INFO":
        log.info(line)
        line = stdin.readline().strip()  