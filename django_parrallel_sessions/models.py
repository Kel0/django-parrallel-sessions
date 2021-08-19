from dataclasses import dataclass


@dataclass
class Git:
    branch: str


@dataclass
class DjangoInstanceSession:
    git: Git
    path: str
    status: str
