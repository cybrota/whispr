import os

import yaml

from whispr.logging import logger


def write_to_yaml_file(config: dict, file_path: str):
    """Writes a given config object to a file in YAML format"""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.dump(config, file)
        logger.info(f"{file_path} has been created.")


def load_config(file_path: str) -> dict:
    """Loads a given config file"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise e
