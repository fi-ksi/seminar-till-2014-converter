from typing import NamedTuple, List
from pathlib import Path


class Asset(NamedTuple):
    link_name: str
    file: Path


class MarkdownText(NamedTuple):
    content: str
    assets: List[Asset]


class MarkdownTask(NamedTuple):
    content: str
    assets: List[Asset]
    name: str
    points: float
