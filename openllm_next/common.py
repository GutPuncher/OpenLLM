import shlex
import os
from typing_extensions import TypedDict
import pydantic
import json
import questionary
import subprocess
import pathlib


ERROR_STYLE = "red"
SUCCESS_STYLE = "green"


CLLAMA_HOME = pathlib.Path.home() / ".openllm_next"
REPO_DIR = CLLAMA_HOME / "repos"
TEMP_DIR = CLLAMA_HOME / "temp"
VENV_DIR = CLLAMA_HOME / "venv"

REPO_DIR.mkdir(exist_ok=True, parents=True)
TEMP_DIR.mkdir(exist_ok=True, parents=True)
VENV_DIR.mkdir(exist_ok=True, parents=True)

CONFIG_FILE = CLLAMA_HOME / "config.json"


class Config(pydantic.BaseModel):
    repos: dict[str, str] = {
        "default": "git+https://github.com/bojiang/bentovllm@main#subdirectory=bentoml"
    }
    default_repo: str = "default"


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return Config(**json.load(f))
    return Config()


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.dict(), f, indent=2)


class RepoInfo(TypedDict):
    name: str
    path: str
    url: str
    server: str
    owner: str
    repo: str
    branch: str


class ModelInfo(TypedDict):
    repo: RepoInfo
    path: str


class BentoInfo(TypedDict):
    model: ModelInfo
    bento_yaml: dict


def run_command(cmd, cwd=None, env=None, copy_env=True):
    questionary.print("\n")
    env = env or {}
    if cwd:
        questionary.print(f"$ cd {cwd}", style="bold")
    if env:
        for k, v in env.items():
            questionary.print(f"$ export {k}={shlex.quote(v)}", style="bold")
    if copy_env:
        env = {**os.environ, **env}
    questionary.print(f"$ {' '.join(cmd)}", style="bold")
    try:
        subprocess.run(cmd, cwd=cwd, env=env, check=True)
    except subprocess.CalledProcessError:
        questionary.print("Command failed", style=ERROR_STYLE)
        return
