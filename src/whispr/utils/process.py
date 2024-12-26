import os
import subprocess
import shlex

from whispr.logging import logger


def execute_command(
    command: tuple, no_env: bool, secrets: dict
) -> subprocess.CompletedProcess[bytes]:
    """Executes a Unix/Windows command.
    Arg: `no_env` decides whether secrets are passed vai environment or K:V pairs in command arguments.
    """
    if not secrets:
        secrets = {}

    try:
        usr_command = shlex.split(command[0])

        if no_env:
            # Pass as --env K=V format (secure)
            usr_command.extend([f"{k}={v}" for k, v in secrets.items()])
        else:
            # Pass via environment (slightly insecure)
            os.environ.update(secrets)

        sp = subprocess.run(usr_command, env=os.environ, shell=False, check=True)
        return sp
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Encountered a problem while running command: '{command[0]}'. Aborting."
        )
        raise e
