from pathlib import Path

import click

from dps.django_utils import DjangoManager
from dps.shell import LazyShellExecutor
from dps.venv_utils import VEnvManager


@click.command()
@click.option("--port", default=8000, help="django port")
@click.option("--branch", default="master", help="git branch")
@click.option("--venv", help="path to venv")
@click.option(
    "--venv_type", default="venv", help="venv context | Choices: \n1. venv \n2. pyenv"
)
@click.option("--django", default=Path().resolve(), help="path to django project")
@click.option("--dst", default="~/", help="django project copies destination path")
@click.option("--host", default="localhost", help="django host")
def run(port, branch, venv, venv_type, django, dst, host):
    venv = Path(venv).resolve()
    django = Path(django).resolve() if isinstance(django, str) else django
    dst = Path(dst).resolve()

    shell_exec = LazyShellExecutor()
    venv_manager = VEnvManager(path=venv, shell_executor=shell_exec, context=venv_type)
    venv_manager.activate()

    django_manager = DjangoManager(
        path=django,
        host=host,
        dst=dst,
        shell_executor=shell_exec,
    )
    django_manager.runserver(port=port, branch=branch)
    for line in shell_exec.exec():
        if line.strip() == "--del--":
            continue

        if len(line.strip()) == 0:
            continue

        print(line.strip())


if __name__ == "__main__":
    run()
