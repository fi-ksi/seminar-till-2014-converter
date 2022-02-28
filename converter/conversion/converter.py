import re
from re import Match
from typing import Iterator

import pypandoc
from pathlib import Path

from .types import Asset, MarkdownText, MarkdownTask

RE_TASK_HEAD = re.compile(r'\s*\\hlavicka{\d+}{\\zadani{\d+}{(.*?)}{([.\d]*?)}}\s*')
RE_ASSET = re.compile(r'\[.*?](\(.*?\))')


def convert_tex_file_to_md(source: Path) -> str:
    return pypandoc.convert(f"{source.absolute()}", "md")


def get_tex_assets(source: Path) -> Iterator[Asset]:
    return map(
        lambda match: Asset(
            link_name=match.group(1),
            file=source.parent.joinpath(match.group(1)).resolve()
        ),
        RE_ASSET.finditer(convert_tex_file_to_md(source))
    )


def parse_task_head(tex_source: Path) -> Match:
    with tex_source.open('r') as f:
        c = f.read()
    return next(RE_TASK_HEAD.finditer(c))


def parse_task_name(tex_source: Path) -> str:
    return parse_task_head(tex_source).group(1)


def parse_task_points(tex_source: Path) -> float:
    return float(parse_task_head(tex_source).group(2))


def get_markdown_text(file_latex: Path) -> MarkdownText:
    text = convert_tex_file_to_md(file_latex)
    assets = list(get_tex_assets(file_latex))

    return MarkdownText(
        content=text,
        assets=assets
    )


def get_markdown_task(file_latex: Path) -> MarkdownTask:
    base = get_markdown_text(file_latex)
    name = parse_task_name(file_latex)
    points = parse_task_points(file_latex)

    return MarkdownTask(
        points=points,
        name=name,
        content=base.content,
        assets=base.assets
    )
