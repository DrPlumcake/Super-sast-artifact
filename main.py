from pathlib import Path
from argparse import ArgumentParser
from subprocess import (  # nosec - module is used cleaning environment variables and with shell=False
    Popen, PIPE
)
from os import environ, dup2, getuid, getgid, mkdir
import logging
from sys import stdout, stderr, path
from request import gh
from sys import exit


path.append(Path(__file__).parent)
from parse_scripts import bandit, safety

# Log to stdout
# for both stdout and stderr.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

def env_json(tool, environ=environ):
    value_tool = json_arg_dict.get(tool, "None")
    if value_tool == "None":
        return
    value = value_tool.get("args", "None")
    if value == "None":
        return
    var = f"{tool.upper()}_ARGS"
    if environ.get(var, value) != value:
        env = environ.get(var, value)
        environ[var] = env + value
    else:
        environ[var] = value
        
if __name__ == "__main__":
    from entrypoint import _show_environ, run_sast, TOOLS_MAP, _copy_java_validators
    
    LOG_DIR = Path("./log_dir")

    if LOG_DIR.exists():
        print(f"La directory {LOG_DIR} esiste già")
    else:
        try:
            mkdir(LOG_DIR)
            print(f"La directory {LOG_DIR} è stata creata con successo")
        except OSError as e:
            print(f"Errore durante la creazione della directory {LOG_DIR}: {e}")
            exit(1)

    parser = ArgumentParser()
    parser.add_argument(
        "--config-dir",
        help="Directory containing config files",
        default="/app/config",
    )
    parser.add_argument(
        "--environs",
        help="Environment variables to pass to the tools",
        default="",
        action="store_true",
    )
    parser.add_argument(
        "--dump-config",
        help="Environment variables to pass to the tools",
        default="",
        action="store_true",
    )
    args = parser.parse_args()
    json_arg_dict = {
        "trivy_config": {
            "args": " -f json",
            "log": "trivy_config.log"
        },
        "trivy_filesystem": {
            "args": " -f json",
            "log": "trivy.log"
            },
        "bandit": {
            "args": " -f json",
            "parse": bandit,
            "log": "bandit.log"
            },
        "safety": {
            "args": " --output json",
            "parse": safety,
            },
        "kubescape": {
            "args": " --format json",
            "parse": "kubescape.py"
            },
        "checkov": {
            "args":  " -o json",
            "parse": "checkov.parse"
            },
        "semgrep": {
            "args": " --json",
            "parse": "semgrep.parse"
            },
        "spotbugs":{},
        "owasp_dependency_check": {},
        "spotless_check": {},
        "spotless_apply": {}
        }
    '''
    REQUIRED_ENV = {"GITHUB_API_URL", "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_TOKEN"}
    if not REQUIRED_ENV < set(environ):
        log.warning(
            "Missing one or more of the following environment variables",
            REQUIRED_ENV - set(environ),
        )
        raise SystemExit(1)
    '''
    try:
        if args.environs or args.dump_config:
            _show_environ(Path(args.config_dir), dump_config=args.dump_config)
        tee = Popen(
            ["/usr/bin/tee", "super-sast.log"], shell=False, stdin=PIPE, stdout=PIPE
        )
        # Cause tee's stdin to get a copy of our stdin/stdout (as well as that
        # of any child processes we spawn)
        sast_to_log = Popen(
            ["python", "sast_to_log.py"], shell=False, stdin=tee.stdout, stdout=stdout
        )
        dup2(tee.stdin.fileno(), stdout.fileno())
        dup2(tee.stdin.fileno(), stderr.fileno())
        # tee's stdout is used as input for sast_to_log code
        # os.dup2(sast_to_log.stdin.fileno(), tee.stdout.fileno())
        sast_status = {}
        _copy_java_validators()
        run_all = environ.get("RUN_ALL_TOOLS", "true").lower() == "true"
        for tool, command in TOOLS_MAP.items():
            env_json(tool)
            status = run_sast(
                tool,
                command,
                environ.copy(),
                config_dir=Path(args.config_dir),
                log_file=stdout,
                run_all=run_all,
            )
            sast_status[tool] = status
        log.info("All tools finished")
        log.info(sast_status)
        local = False
        if environ.get("LOCAL") == "true":
            local = True
        if not local:
            u_patch = "{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/commits/{GITHUB_SHA}/check-runs".format(
            **environ
            )
            u_post = "{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/check-runs".format(**environ)
        
        for tool in json_arg_dict.keys():
            log_file = f"{tool}.log"
            LOG_FILE = Path(LOG_DIR) / log_file
            if Path(LOG_FILE).exists():
                # File is empty
                if tool != "bandit" and tool != "safety":
                    log.info(f"Sorry, annotations for {tool} are not available")
                    continue
                if Path(LOG_FILE).stat().st_size == 0:
                    log.info(f"{log_file} is empty. Skipping parsing")
                    continue
                elif Path(LOG_FILE).stat().st_size > 0:
                    # tool_checks must be a Json object ready for request
                    module = json_arg_dict.get(tool)["parse"]
                    tool_checks = module.parse(LOG_FILE, environ.get("GITHUB_SHA"))
                    if local:
                        log.info("Request skipped for local testing")
                        continue
                    else:
                        res = gh(
                        u_post,
                        method="POST",
                        data=tool_checks,
                        token=environ["GITHUB_TOKEN"],
                        )
                        log.info("Request Status:", res.status_code, res.json(), res.url)
                    
            else:
                log.error(f"{LOG_FILE} does not exists")
        log.info("Annotations succesfully sendend to PR: Process Completed\n") 
        exit(0)
    except Exception as e:
        log.error(
            "An exception occurred while running SAST, context information below\n"
            f" - UID: {getuid()}\n - GID: {getgid()}\n"
            f" - Error: {type(e).__name__} -> {e}"
        )
        raise e
