from pathlib import Path
from typing import Optional, Union

from dps.common import VEnvTypeProtocol
from dps.models import VenvTypes
from dps.shell import LazyShellExecutor


class VEnvManager:
    """
    Virtual environment manager
    """

    def __init__(
        self,
        path: Union[Path, str],
        shell_executor: Optional[LazyShellExecutor] = None,
        context: Optional[str] = None,
    ) -> None:
        self.path = path
        if shell_executor is None:
            raise ValueError("shell_executor can not be NoneType")
        self.shell_executor = shell_executor
        self.context: VEnvTypeProtocol = getattr(VenvTypes, context.lower()).value(
            manager=self
        )

    def activate(self) -> None:
        """
        Add activation commands to exec chain
        """
        activate_str = self.context.get_activate_string()
        if not self.context.validate():
            raise FileNotFoundError("{} not exists".format(self.path))

        self.shell_executor.add_to_exec_chain(activate_str)
