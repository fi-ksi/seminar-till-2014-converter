import re
from pathlib import Path
from shutil import copy, rmtree
from typing import Union, Optional
from subprocess import check_call, PIPE

from ..conversion import MarkdownText, MarkdownTask, get_markdown_text, get_markdown_task
from ..tex import TexTask, TexWave, TexYear

from unidecode import unidecode


def write_markdown_text(source: Union[MarkdownText, MarkdownTask], target: Path, dir_assets: Path, content_prefix: str = '') -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    dir_assets.mkdir(parents=True, exist_ok=True)

    text_content = source.content

    for asset in source.assets:
        file_source = asset.file

        if not file_source.exists():
            if not file_source.name.endswith('.png'):
                file_source = file_source.parent.joinpath(file_source.name + '.png').resolve()

        file_target = dir_assets.joinpath(file_source.name)

        if not file_source.is_file():
            print(f"WARN: missing asset '{file_source}' with link '{asset.link_name}'")
            continue

        copy(file_source, file_target)

        text_content = text_content.replace(
            f"({asset.link_name})",
            f"({file_target.relative_to(target.parent.resolve())})"
        )

    with target.open('w') as f:
        if content_prefix:
            f.write(content_prefix)
        f.write(text_content)


def write_tex_task(task: TexTask, dir_wave: Path) -> None:
    assigment = get_markdown_task(task.assigment)
    solution = get_markdown_text(task.solution)

    task_lowercase_name = ''.join(filter(
        lambda x: x == ' ' or x.isalnum(),
        unidecode(assigment.name).lower())
    )
    task_lowercase_name = re.sub(r'\s+', '_', task_lowercase_name)

    dir_task = dir_wave.joinpath(f"uloha_{task.index:02d}_{task_lowercase_name}")
    if dir_task.exists():
        print(f'INFO: {dir_task.name} already exists')
        return
    dir_task.mkdir(parents=True, exist_ok=False)

    file_assigment = dir_task.joinpath('assigment.md')
    dir_data = dir_task.joinpath('data')
    file_solution = dir_task.joinpath('solution.md')
    dir_solution_data = dir_task.joinpath('task_solution')

    try:
        write_markdown_text(assigment, file_assigment, dir_data, content_prefix=f'# {assigment.name}\n\n')
        write_markdown_text(solution, file_solution, dir_solution_data)
        check_call(['git', 'add', "."], stdin=PIPE, cwd=dir_task, stdout=PIPE)
        check_call(['git', 'commit', '-m', f'chore: init {task_lowercase_name}'], stdin=PIPE, cwd=dir_task, stdout=PIPE)
    except:
        rmtree(dir_task)
        raise


def write_tex_wave(wave: TexWave, dir_year: Path, year: Optional[TexYear] = None) -> None:
    dir_wave = dir_year.joinpath(f"vlna{wave.index}")
    for task in wave.tasks:
        try:
            write_tex_task(task, dir_wave)
        except RuntimeError:
            print(f'ERR: cannot convert {task.index} in wave {wave.index} in year '
                  f'{year.first_year if year is not None else None}')


def write_tex_year(year: TexYear, dir_root: Path) -> None:
    dir_year = dir_root.joinpath(f"{year.first_year}")
    for wave in year.waves:
        write_tex_wave(wave, dir_year, year)
