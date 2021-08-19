import os
import dbm
import subprocess
import random
from pathlib import Path
from typing import List, Optional, Tuple, Union

from hashlib import md5

from django_parrallel_sessions.utils import copytree, DisplayablePath, build_settings_path
from django_parrallel_sessions.commands import CommandManager


class DjangoSessionProtocol:
    """
    Protocol class for django session entities
    """
    def __init__(self, source: Union[str, Path]) -> None:
        self.source = source

    @property
    def status(self):
        return False

    def is_exist(self) -> bool:
        """
        Check if session exist
        :return: Status of existence
        """
        is_exists = Path(self.source).exists()
        return is_exists

    def copy(
        self,
        destination: Union[str, Path],
        symlinks: bool,
        ignore: Optional[List[str]]
    ) -> Union[str, Path]:
        """
        Copy source directory to destination
        :param destination: Destination path
        :param symlinks: Enable symlinks?
        :param ignore: Ignore files
        """
        copytree(
            src=self.source,
            dst=destination,
            symlinks=symlinks,
            ignore=ignore
        )
        return destination


class DjangoSessionViewer:
    def __init__(self, source: Union[str, Path]) -> None:
        self._protocol = DjangoSessionProtocol(source=source)

    def as_tree(self, ignore: Optional[List[str]] = None, capture_output: bool = False) -> Optional[str]:
        """
        Represent directory structure as tree
        :param ignore: Directories or file for ignore
        :param capture_output: Will return tree structure
        :return: Tree structure
        """
        if ignore is None:
            ignore = []

        output = None
        if capture_output:
            output = ""

        if self._protocol.is_exist():
            for item in DisplayablePath.make_tree(
                root=self._protocol.source,
                ignore=ignore
            ):
                if item:
                    print(item.displayable())
                    if not capture_output:
                        continue

                    output += "{}\n".format(str(item.displayable()))
        return output

    def get(self) -> Tuple[Optional[DjangoSessionProtocol], bool]:
        """
        Get directory
        :return: None, False if directory doesn't exist and returns
            DjangoSessionProtocol, True if directory exists
        """
        status = self._protocol.is_exist()
        if status:
            return self._protocol, status
        return None, status


class DjangoSessionCreator:
    def __init__(self, source: Union[str, Path]) -> None:
        self._protocol = DjangoSessionProtocol(source=source)

    def make_file_hash(self):
        return md5("{}{}".format(
            self._protocol.source,
            str(random.randint(1, 100000))
        ).encode()).hexdigest()

    def create(
        self,
        destination: Union[str, Path],
        symlinks: bool,
        ignore: Optional[List[str]]
    ) -> Union[str, Path]:
        """
        Copy source directory to destination
        :param destination: Destination path
        :param symlinks: Enable symlinks?
        :param ignore: Ignore files
        """
        return self._protocol.copy(
            destination=destination,
            symlinks=symlinks,
            ignore=ignore
        )


class DjangoSessionManager:
    def __init__(self, source: Union[str, Path],
                 destination_folder: Optional[Union[str, Path]] = None,
                 ignore: Optional[List[str]] = None) -> None:
        self.source = source
        self.destination_folder = destination_folder
        if self.destination_folder is None:
            self.destination_folder = Path().resolve().parent

        self.ignore = ignore
        if self.ignore is None:
            self.ignore = []

        self.viewer = DjangoSessionViewer(source=source)
        self.creator = DjangoSessionCreator(source=source)
        self.manager = CommandManager(
            git_repo=self._get_dest_folder(as_path=True),
            django_settings=build_settings_path(self._get_dest_folder()),
        )

    def _get_dest_folder(self, as_path: bool = False) -> Union[str, Path]:
        dest_folder = (
            str(self.destination_folder)[:-1]
            if str(self.destination_folder)[-1] == "\\"
            else str(self.destination_folder)
        )
        if as_path:
            return Path(dest_folder)
        return dest_folder

    def startup(self, port: int, branch: str):
        with dbm.open('cache', 'c') as db:
            print("Creating directory on machine... | == | 4%")
            path = self.creator.create(
                destination="{}/{}".format(
                    self._get_dest_folder(),
                    self.creator.make_file_hash()
                ),
                ignore=self.ignore,
                symlinks=False
            )
            print(path, "PATH")
            self.manager.git_manager.set_source(source=path)
            self.manager.django_manager.set_settings_env(
                project_dir=path,
                ignore=["sirius-backend-auth"]
            )

            print("Checkout to the branch... | ======= | 60%")
            pipe_git = self.manager.call_git_command("checkout", branch)
            print(pipe_git)
            # pipe_git = subprocess.run(
            #     ("cd", path, "&", "git", "checkout", branch),
            #     capture_output=True, text=True,
            #     shell=True,
            # )
            # print(pipe_git.stdout)
            # # if len(pipe_git.stderr.decode("utf-8")) > 0:
            # #     raise RuntimeError(pipe_git.stderr.decode("utf-8"))
            #
            # print("Starting the django session... | ========= | 80%")
            # pipe_run = subprocess.run(
            #     ("./manage.py", "runserver", str(port)),
            #     capture_output=True, text=True,
            #     shell=True
            # )
            # print(pipe_run.stdout)
            # pid = subprocess.run(
            #     ('lsof', '-i', ':{}'.format(str(port)), "/dev/null"),
            #     capture_output=True,
            # )
            # print(pid.stdout.decode("utf-8"))


(
    DjangoSessionManager("/Users/hamlet/Desktop/gits/sirius-backend", destination_folder="/Users/hamlet/Desktop")
    .startup(8009, 'feature/2201')
)
