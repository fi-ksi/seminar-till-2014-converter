import re
from re import Match
from typing import Iterable, Optional
from mimetypes import guess_type

from pathlib import Path

RE_TASK_HEAD = re.compile(r'\s*\\hlavicka{.*?}{\\zadani{.*?}{(.*?)}{([.\d]*?)}}\s*')
RE_TEX_ASSET = re.compile(r'\\includegraphics.*?{(.*?)}')


def find_asset(directory: Path, asset_name: str) -> Optional[Path]:
    if directory.joinpath('__toplevel__').exists():
        return None

    for child in directory.iterdir():
        if child.name == asset_name:
            return child
        if child.name.startswith(f"{asset_name}.") and guess_type(child)[0].startswith('image/'):
            return child

    return find_asset(directory.parent.resolve(), asset_name)


def get_tex_assets(file_tex: Path) -> Iterable[Path]:
    with file_tex.open('r') as f:
        content = f.read()

    return map(
        lambda x: find_asset(file_tex.parent.resolve(), x.group(1)),
        RE_TEX_ASSET.finditer(content)
    )


def parse_task_head(tex_source: Path) -> Match:
    with tex_source.open('r') as f:
        c = f.read()
    try:
        return next(RE_TASK_HEAD.finditer(c))
    except StopIteration:
        raise ValueError(f"No head inside {tex_source}")


def parse_task_name(tex_source: Path) -> str:
    return parse_task_head(tex_source).group(1)


def parse_task_points(tex_source: Path) -> float:
    return float(parse_task_head(tex_source).group(2))
