import os
import sys
from pathlib import Path
from typing import Union, Optional, List

from git import Repo
import django
from django.core.management import call_command


class GitManager:
    def __init__(self, source: str) -> None:
        self.source = source
        self.repo = None

    def set_source(self, source: Union[str, Path]) -> None:
        self.source = source
        self.repo = Repo(self.source)

    def call(self, operation, *args, **kwargs):
        method = getattr(self.repo, operation)
        return method(*args, **kwargs)


class DjangoManager:
    def __init__(self, settings: str) -> None:
        self.source = settings
        self.settings = None

    def find_settings_module(self, project_dir: Union[str, Path],
                             ignore: Optional[List[str]] = None) -> None:
        if ignore is None:
            ignore = []
        ignore += ["__pycache__", ".idea", "site-packages"]

        items = os.listdir(project_dir)
        for item in items:
            s = os.path.join(project_dir, item)

            if any(True for i in ignore if i in str(s)):
                continue
            if os.path.isdir(s):
                self.find_settings_module(project_dir=s, ignore=ignore)
            if str(item) == "settings.py":
                self.settings = s

    def set_settings_env(self, project_dir: Union[str, Path],
                         ignore: Optional[List[str]] = None) -> None:
        sys.path.append(self.source)
        self.find_settings_module(project_dir=project_dir, ignore=ignore)
        sys.path.append(self.settings)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", ".".join(self.settings.split('/')[-3:]))
        django.setup()

    def call(self, *args, **kwargs):
        return call_command(*args, **kwargs)

    def activate_virtual_environment(self, environment_root):
        """Configures the virtual environment starting at ``environment_root``."""
        activate_script = os.path.join(
            environment_root, 'Scripts', 'activate_this.py')


class CommandManager:
    def __init__(self, django_settings: str, git_repo: str) -> None:
        self.git_manager = GitManager(source=git_repo)
        self.django_manager = DjangoManager(settings=django_settings)

    def call_django_command(self, *args, **kwargs):
        return self.django_manager.call(*args, **kwargs)

    def call_git_command(self, operation, *args, **kwargs):
        return self.git_manager.call(operation, *args, **kwargs)
