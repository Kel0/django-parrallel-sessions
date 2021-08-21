import os
import shutil
from pathlib import Path
from typing import List, Optional, Union


class DisplayablePath:
    display_filename_prefix_middle = "├──"
    display_filename_prefix_last = "└──"
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None, ignore=None):
        if ignore is None:
            ignore = []

        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(
            [path for path in root.iterdir() if criteria(root, ignore)],  # noqa
            key=lambda s: str(s).lower(),
        )

        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(
                    path,
                    parent=displayable_root,
                    is_last=is_last,
                    criteria=criteria,
                    ignore=ignore,
                )
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, root, ignore):
        for file in ignore:
            if file in str(root):
                return False
        return True

    @property
    def display_name(self):
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.display_name

        _filename_prefix = (
            self.display_filename_prefix_last
            if self.is_last
            else self.display_filename_prefix_middle
        )

        parts = ["{!s} {!s}".format(_filename_prefix, self.display_name)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                self.display_parent_prefix_middle
                if parent.is_last
                else self.display_parent_prefix_last
            )
            parent = parent.parent

        return "".join(reversed(parts))


def build_settings_path(default_path: Union[str, Path]) -> str:
    default_path = default_path if default_path[0] == "s" else default_path
    return default_path


def loader(length, index, text) -> None:
    max_sharps = 10
    percent = index * 100 // length
    sharps = index * max_sharps // length

    if sharps == max_sharps - 1:
        loader(length, index + 1, text)

    print(
        text
        + " | "
        + "".join(["==" for _ in range(sharps)])
        + " | "
        + str(percent)
        + "%"
    )


def copytree(
    src: str,
    dst: str,
    symlinks: bool = False,
    ignore: Optional[List[str]] = None,
) -> None:
    """
    Copy entire tree

    :param src: Source file path
    :param dst: Destination of source file
    :param symlinks: Any symlinks
    :param ignore: Ignore files
    """
    if not os.path.exists(dst):
        os.makedirs(dst)

    items = os.listdir(src)
    for idx, item in enumerate(items):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)

        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
            continue

        if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
            shutil.copy2(s, d)


def remove_tree(path):
    return shutil.rmtree(path, ignore_errors=True)
