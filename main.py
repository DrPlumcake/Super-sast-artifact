from collections import namedtuple
from pathlib import Path
from argparse import ArgumentParser
from subprocess import (  # nosec - module is used cleaning environment variables and with shell=False
    Popen, PIPE
)
from os import environ, dup2, getuid, getgid
import logging
from sys import stdout, stderr
from request import gh
from parse_scripts import bandit

PATH = Path(__file__).parent

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

def env_json(tool):
    value = json_arg_dict.get(tool, "None")
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
        "trivy_config": " -f json",
        "trivy_filesystem": " -f json",
        "bandit": "-f json",
        "safety": " --output json",
        "kubescape": " --format json",
        "checkov": " -o json",
        "semgrep": " --json",
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

        log.info(f"The log of bandit is in {PATH}log_dir/bandit.log")
        bandit_checks = bandit.bandit_parse("log_dir/bandit.log")
        
        u_patch = "{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/commits/{GITHUB_SHA}/check-runs".format(
            **environ
        )
        u_post = "{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/check-runs".format(**environ)
        res = gh(
            u_post,
            method="POST",
            data=bandit_checks,
            token=environ["GITHUB_TOKEN"],
        )
        log.info("Workflow status:", res.status_code, res.json(), res.url)
    except Exception as e:
        log.error(
            "An exception occurred while running SAST, context information below\n"
            f" - UID: {getuid()}\n - GID: {getgid()}\n"
            f" - Error: {type(e).__name__} -> {e}"
        )
        raise e

        '''
        for tool in json_arg_dict.keys():
            run(["python", parse_scripts/f"{tool}.py", log_dir/f"{tool}.log"])   
        
        '''
