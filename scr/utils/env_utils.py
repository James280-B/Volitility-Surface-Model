import os

from dotenv import load_dotenv


def load_environment_variables() -> None:
    file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))  # TODO: CHANGE THIS FOR THE LOVE OF GOD
    env_path = os.path.join(parent_dir, ".env")
    load_dotenv(env_path, override=True)


def read_environment_variables(env_name: str) -> str:
    load_environment_variables()
    value = os.getenv(env_name)
    return value
