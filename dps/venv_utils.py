import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

from dps.common import ShellExecutorProtocol, VEnvTypeProtocol
from dps.models import ShellExecResult, VenvTypes


class LazyShellExecutor:
    def __init__(self) -> None:
        self._exec_chain: Dict[int, str] = {}

    def add_to_exec_chain(self, command: str) -> None:
        """
        Add command to execution chain
        :param command: Bash shell command
        """
        keys_list = list(self._exec_chain.keys())
        if not len(keys_list):
            last_key = -1
        else:
            last_key = list(self._exec_chain.keys())[-1]
        self._exec_chain.update({last_key + 1: command})

    def remove_from_exec_chain(self, command: str) -> str:
        """
        Remove command from execution chain
        :param command: Bash shell command
        :return: Removed command
        """
        for key, value in self._exec_chain.items():
            if command.lower() == value.lower():
                del self._exec_chain[key]
                return value

    def get_exec_string(self) -> str:
        """
        Generate execution one line string
        :return: Execution string
        """
        return "; echo --del--;".join(
            [v for v in self._exec_chain.values()]
        )  # --del-- is delimiter in stdout

    def get_std_results(self, stdout, stderr) -> List[ShellExecResult]:
        """
        Get stdout, stderr results
        :param stdout: Pipe.stdout
        :param stderr: Pipe.stderr
        :return: List of objects which have stdout, stderr, command attrs
        """
        results = []
        for idx, item in enumerate(
            # replace \n to " " and split by --del-- delimiter
            stdout.decode("utf-8")
            .replace("\n", " ")
            .split("--del--")
        ):
            results.append(
                ShellExecResult(command=self._exec_chain[idx], stdout=item.strip())
            )

        for idx, item in enumerate(
            stderr.decode("utf-8").replace("\n", " ").split("--del--")
        ):
            results[idx].stderr = item.strip()

        return results

    def exec(self) -> List[ShellExecResult]:
        """
        Execute shell commands
        :return: List of objects which have stdout, stderr, command attrs
        """
        exec_string = self.get_exec_string()
        pipe = subprocess.run(exec_string, capture_output=True, shell=True)
        return self.get_std_results(pipe.stdout, pipe.stderr)

    def __repr__(self) -> str:
        return "<{}({})>".format(
            self.__class__.__name__, self.get_exec_string()
        ).replace("; echo --del--;", "; ")


class VEnvManager:
    """
    Virtual environment manager
    """

    def __init__(
        self,
        path: Union[Path, str],
        shell_executor: Optional[ShellExecutorProtocol] = None,
        context: Optional[str] = None,
    ) -> None:
        self.path = path
        self.shell_executor = shell_executor
        if self.shell_executor is None:
            self.shell_executor = LazyShellExecutor()
        self.context: VEnvTypeProtocol = getattr(VenvTypes, context.lower()).value(
            manager=self
        )

    def activate(self) -> None:
        """
        Add activation commands to exec chain
        """
        activate_str = self.context.get_activate_string()
        if not self.context.validate(activate_str):
            raise FileNotFoundError("{} not exists".format(self.path))

        self.shell_executor.add_to_exec_chain(activate_str)
