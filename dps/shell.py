import subprocess
from typing import Dict, Generator, List

from dps.fsm import FSMContext
from dps.models import ShellExecResult


class LazyShellExecutor:
    def __init__(self) -> None:
        self._exec_chain: Dict[int, str] = {}
        self._fsm_context = FSMContext()

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

    def _sort_exec_chain(self, exec_chain: Dict[int, str]) -> Dict[int, str]:
        run_cmd = None

        for idx, cmd in exec_chain.items():
            if "manage.py runserver" in cmd:
                run_cmd = idx

        if run_cmd:
            item = exec_chain.pop(run_cmd)
            exec_chain = {i + 1: v for i, v in enumerate(exec_chain.values())}
            last_key = list(exec_chain.keys())[-1]
            exec_chain[last_key + 1] = item
        return exec_chain

    def get_exec_string(self) -> str:
        """
        Generate execution one line string
        :return: Execution string
        """
        return "; echo --del--;".join(
            [v for v in self._sort_exec_chain(exec_chain=self._exec_chain).values()]
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

    def exec(self) -> Generator[str, bytes, None]:
        """
        Execute shell commands
        :return: List of objects which have stdout, stderr, command attrs
        """

        exec_string = self.get_exec_string()
        process = subprocess.Popen(
            exec_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        while True:
            try:
                yield process.stdout.readline().decode("utf-8")
            except Exception as e:
                print(e)
                break

    def __repr__(self) -> str:
        return "<{}({})>".format(
            self.__class__.__name__, self.get_exec_string()
        ).replace("; echo --del--;", "; ")
