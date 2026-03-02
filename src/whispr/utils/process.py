import os
import subprocess  # nosec B404
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
        if len(command) == 1:
            usr_command = shlex.split(command[0])
        else:
            usr_command = list(command)

        command_env = os.environ.copy()

        if no_env:
            # Pass as --env K=V format (secure)
            usr_command.extend([f"{k}={v}" for k, v in secrets.items()])
        else:
            # Pass via subprocess environment only
            command_env.update(secrets)

        sp = subprocess.run(  # nosec B603
            usr_command, env=command_env, shell=False, check=True
        )
        return sp
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Encountered a problem while running command: '{' '.join(command)}'. Aborting."
        )
        raise e
