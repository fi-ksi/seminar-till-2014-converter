from pathlib import Path
from typing import NamedTuple, Optional


class BETask(NamedTuple):
    deployed_: bool
    wave: Optional[int]
    git_path: str


class BETaskMeta(NamedTuple):
    name: str
    first_year: int
    directory: Path
    wave_directory: Path


class BEWave(NamedTuple):
    directory_: Path
    index: int

