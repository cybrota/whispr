import os
import stat

TOKEN_DIR = "~/.whispr"
CACHE_FILE = "~/.whispr/cache.encrypted"
TOKEN_EXPIRATION_SECONDS = 10800  # 3 hours
TOKEN_ALGORITHM = "HS256"
ENCRYPTION_NONCE_SIZE = 24
LOG_LEVEL = "INFO"
LOG_FILE = "~/.whispr/whispr.log"
DEFAULT_NAMESPACE = "default"


def get_token_dir():
    """
    Returns the expanded and absolute path for TOKEN_DIR.
    Uses os.path.expanduser to expand '~' and os.path.abspath for the absolute path.
    """
    expanded_path = os.path.expanduser(TOKEN_DIR)
    absolute_path = os.path.abspath(expanded_path)
    return absolute_path


def ensure_directories_exist():
    """
    Checks if the TOKEN_DIR exists, and if not, creates it with proper permissions.
    For directories, the current user needs read, write, and execute permissions,
    so we use mode 0o700 (rwx------).
    """
    token_dir = get_token_dir()
    if not os.path.exists(token_dir):
        try:
            # Create the directory with mode 0o700 to give the current user read, write, and execute permissions.
            os.makedirs(token_dir, mode=0o700, exist_ok=True)
            print(f"Directory created: {token_dir}")

            # Ensure permissions are correctly set
            os.chmod(token_dir, 0o700)
        except OSError as e:
            print(f"Failed to create directory {token_dir}: {e}")
    else:
        # If the directory exists, enforce that it has the correct permissions.
        try:
            current_mode = stat.S_IMODE(os.lstat(token_dir).st_mode)
            if current_mode != 0o700:
                os.chmod(token_dir, 0o700)
                print(f"Permissions updated for directory: {token_dir}")
            else:
                print(f"Directory already exists with correct permissions: {token_dir}")
        except OSError as e:
            print(f"Failed to update permissions for {token_dir}: {e}")
