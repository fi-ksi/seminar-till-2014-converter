from typing import TypedDict, List
from pathlib import Path


class TexTask(TypedDict):
    index: int
    assigment: Path
    solution: Path


class TexWave(TypedDict):
    index: int
    tasks: List[TexTask]


class TexYear(TypedDict):
    index: int
    name: str
    waves: List[TexWave]
