import os
import atexit
from hashlib import md5
from pathlib import Path
from random import randint
from typing import List, Optional, Union

from git import Repo

from dps.shell import LazyShellExecutor
from dps.utils import copytree, remove_tree


class GitManager:
    def __init__(self, path: Union[Path, str]) -> None:
        self.repo = Repo(path).git
        self.path = path

    def checkout(self, branch: str):
        return self.repo.checkout(branch)


class DjangoManager:
    def __init__(
        self,
        path: Union[Path, str],
        dst: Union[Path, str],
        host: Optional[str] = "localhost",
        ignore: Optional[List[str]] = None,
        shell_executor: Optional[LazyShellExecutor] = None,
    ) -> None:
        self.path = path
        self.dst = dst
        self.host = host
        if shell_executor is None:
            raise ValueError("shell_executor can not be NoneType")
        self.shell_executor = shell_executor
        self.repo = Repo
        self.ignore = ignore if ignore is not None else []

    def __make_hash(self) -> str:
        return md5(str(randint(1, 10000)).encode()).hexdigest()

    def get_git_repo(self, destination: Union[Path, str]) -> Repo.git:
        return self.repo(destination).git

    def runserver(self, port: int, branch: str) -> None:
        destination = os.path.join(self.dst, self.__make_hash())
        print("Copying directory into {}".format(self.dst))
        copytree(src=self.path, dst=destination, ignore=self.ignore)
        atexit.register(remove_tree, path=destination)
        git_repo = self.get_git_repo(destination=destination)
        print(git_repo.checkout(branch))
        command = "python {manage_py_path} runserver {host}:{port}".format(
            manage_py_path=os.path.join(destination, "manage.py"),
            host=self.host,
            port=port,
        )
        self.shell_executor.add_to_exec_chain(command)
