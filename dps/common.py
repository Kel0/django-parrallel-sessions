from typing import Protocol


class VEnvProtocol(Protocol):
    path = None

    def activate(self):
        """
        Activate virtual environment
        """


class VEnvTypeProtocol(Protocol):
    _manager = None

    def validate(self, *args, **kwargs):
        """
        Make sure that venv is exist
        """

    def get_activate_string(self):
        pass


class ShellExecutorProtocol:
    def add_to_exec_chain(self, activate_str):
        pass

    def exec(self):
        pass
