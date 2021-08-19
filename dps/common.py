from typing import Protocol


class VEnvProtocol(Protocol):
    path = None

    def activate(self):
        """
        Activate virtual environment
        """


class VEnvTypeProtocol(Protocol):
    _manager = None

    def validate(self, activate_path):
        """
        Make sure that venv is exist
        """

    def get_activate_string(self):
        pass


class ShellExecutorProtocol:
    def exec(self):
        pass
