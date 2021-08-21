import os
import platform

from .common import VEnvProtocol


class VirtualEnvironment:
    os_platform = platform.system()
    activate_string_format = ". {venv_path}/{activate_path}"
    venv_activate_path_unix = "bin/activate"
    venv_activate_path_windows = "Scripts/activate"

    def __init__(self, manager: VEnvProtocol) -> None:
        self._manager = manager

    def validate(self) -> bool:
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
        path = str(self._manager.path)
        venv_path = path[:-1] if path[-1] == "/" else path
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

    def validate(self) -> bool:
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
