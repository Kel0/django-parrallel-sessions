from dataclasses import asdict, dataclass
from enum import Enum

from dps.venv_types import PyEnv, VirtualEnvironment

__blank__: str = ""


class VenvTypes(Enum):
    venv = VirtualEnvironment
    pyenv = PyEnv


@dataclass
class BaseModel:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ShellExecResult(BaseModel):
    command: str = __blank__
    stdout: str = __blank__
    stderr: str = __blank__
