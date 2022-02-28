from typing import NamedTuple, List
from pathlib import Path


class TexTask(NamedTuple):
    index: int
    assigment: Path
    solution: Path


class TexWave(NamedTuple):
    index: int
    tasks: List[TexTask]


class TexYear(NamedTuple):
    index: int
    name: str
    first_year: int
    second_year: int
    waves: List[TexWave]
