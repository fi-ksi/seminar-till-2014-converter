import re
from typing import Iterator
from pathlib import Path

from .types import TexWave, TexTask, TexYear


def get_tex_tasks(dir_wave: Path) -> Iterator[TexTask]:
    dir_source = dir_wave.joinpath('sazba').resolve()

    if not dir_source.is_dir():
        return

    for file_assigment in filter(lambda x: x.name.endswith('.tex') and x.name.startswith('zadani_'), dir_source.iterdir()):
        file_solution = file_assigment.parent.joinpath(file_assigment.name.replace('zadani_', 'reseni_', 1)).resolve()
        index = int(next(re.finditer(r"(\d+).tex$", file_assigment.name)).group(1))
        yield TexTask(
            index=index,
            assigment=file_assigment,
            solution=file_solution
        )


def get_tex_waves(dir_year: Path) -> Iterator[TexWave]:
    for dir_wave in filter(lambda x: x.name.startswith('sada'), dir_year.iterdir()):
        index = int(next(re.finditer(r"sada(\d+)$", dir_wave.name)).group(1))
        tasks = list(get_tex_tasks(dir_wave))

        if not tasks:
            continue

        yield TexWave(index=index, tasks=tasks)


def get_tex_years(dir_root: Path, beginning_year: int = 2008) -> Iterator[TexYear]:
    for dir_year in filter(lambda x: x.is_dir(), dir_root.iterdir()):
        first_year = int(dir_year.name)
        second_year = first_year + 1

        year_name = f"{first_year}/{second_year}"
        year_index = first_year - beginning_year
        waves = list(get_tex_waves(dir_year))

        if not waves:
            continue

        yield TexYear(
            index=year_index,
            name=year_name,
            waves=waves
        )
