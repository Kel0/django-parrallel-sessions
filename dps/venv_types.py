import os
import platform
from pathlib import Path
from typing import Union

from .common import VEnvProtocol


class VirtualEnvironment:
    os_platform = platform.system()
    activate_string_format = ". {venv_path}/{activate_path}"
    venv_activate_path_unix = "bin/activate"
    venv_activate_path_windows = "Scripts/activate"

    def __init__(self, manager: VEnvProtocol) -> None:
        self._manager = manager

    def validate(self, activate_path: Union[Path, str]) -> bool:
        """
        Check venv for existence
        :param activate_path: Path to virtualenv activate script
        :return: Boolean status
        """
        return os.path.exists(activate_path)

    def get_activate_string(self) -> str:
        """
        Get venv activation command for different platforms
        :return: Venv activation command
        """
        venv_path = (
            self._manager.path[:-1]
            if self._manager.path[-1] == "/"
            else self._manager.path
        )
        if self.os_platform.lower() in ["darwin", "linux", "arch"]:
            return self.activate_string_format.format(
                venv_path=venv_path, activate_path=self.venv_activate_path_unix
            )
        return self.activate_string_format.format(
            venv_path=venv_path, activate_path=self.venv_activate_path_windows
        )


class PyEnv:
    os_platform = platform.system()
    activate_string_format = "pyenv local {venv_name}"

    def __init__(self, manager: VEnvProtocol) -> None:
        self._manager = manager

    def validate(self, _) -> bool:
        """
        Check venv for existence
        :return: Boolean status
        """
        return os.path.exists(self._manager.path)

    def get_activate_string(self) -> str:
        """
        Get venv activation command for different platforms
        :return: Venv activation command
        """
        if self.os_platform.lower() not in ["darwin", "linux", "arch"]:
            raise RuntimeError("pyenv is not compatible with windows")

        path = str(self._manager.path)
        venv_name = path.split("/")[-1] if path[-1] != "/" else path[:-1].split("/")[-1]

        return self.activate_string_format.format(venv_name=venv_name)
