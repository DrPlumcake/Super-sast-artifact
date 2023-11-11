import logging
from argparse import ArgumentParser
from os import dup2, environ, getgid, getuid, mkdir
from pathlib import Path
from subprocess import (  # nosec - module is used cleaning environment variables and with shell=False
    PIPE,
    Popen,
)
from sys import exit, stderr, stdout

from parse_scripts import bandit, checkov, safety, semgrep
from request import gh

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


def parse_tools(dict, log, log_path, test=False, local=False):
    for tool, tool_setup in dict.items():
        log_file_name = f"{tool}.log"
        log_file_path = Path(log_path) / log_file_name
        if tool not in ["bandit", "safety", "semgrep", "checkov"]:
            log.info(f"Sorry, annotations for {tool} are not available")
            continue
        if not Path(log_file_path).exists():
            # File is empty
            log.error(f"{log_file_name} does not exists")
            continue
        if Path(log_file_path).stat().st_size == 0:
            log.info(f"{log_file_name} is empty. Skipping parsing")
            continue
        # tool_checks must be a Json object ready for request
        parse_function = tool_setup["parse"].parse
        tool_checks = parse_function(log_file_path, environ.get("GITHUB_SHA"))
        if local:
            log.info(f"{tool} Request skipped for local testing")
            if not test:
                log.setLevel(logging.DEBUG)
                log.debug(f"Result: {tool_checks}")
                log.setLevel(logging.INFO)
            continue

        if not test:
            res = gh(
                u_post,
                method="POST",
                data=tool_checks,
                token=environ["GITHUB_TOKEN"],
            )
            log.info("Request Status: %s %s %s", res.status_code, res.content, res.url)


if __name__ == "__main__":
    from entrypoint import TOOLS_MAP, _copy_java_validators, _show_environ, run_sast

    LOG_DIR = Path("./log_dir")

    if LOG_DIR.exists():
        log.info(f"La directory {LOG_DIR} esiste già")
    else:
        try:
            mkdir(LOG_DIR)
            log.info(f"La directory {LOG_DIR} è stata creata con successo")
        except OSError as e:
            log.info(f"Errore durante la creazione della directory {LOG_DIR}: {e}")
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
    """
    REQUIRED_ENV = {"GITHUB_API_URL", "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_TOKEN"}
    if not REQUIRED_ENV < set(environ):
        log.warning(
            "Missing one or more of the following environment variables",
            REQUIRED_ENV - set(environ),
        )
        raise SystemExit(1)
    """
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
            u_post = "{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/check-runs".format(
                **environ
            )

        parse_tools(
            dict=json_arg_dict, log=log, log_path=LOG_DIR, test=False, local=local
        )

        log.info("Annotations succesfully sendend to PR: Process Completed\n")
        exit(0)
    except Exception as e:
        log.error(
            "An exception occurred while running SAST, context information below\n"
            f" - UID: {getuid()}\n - GID: {getgid()}\n"
            f" - Error: {type(e).__name__} -> {e}"
        )
        raise e
