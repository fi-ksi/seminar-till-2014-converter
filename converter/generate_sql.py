import json
from pathlib import Path
from typing import Iterator, List

from converter.tex import TexYear, TexWave, get_tex_years

TASK_ID = 148
WAVE_ID = 13
THREAD_ID = 492
PREREQUISITE_ID = 140
WAVE_GARANT = 3
ICON_BASE = "/taskContent/10/icon/"


def mysql_escape(value: str) -> str:
    value = value.replace("'", r"")
    return f"'{value}'"


def generate_sql_insert(dir_seminar: Path, years: Iterator[TexYear]) -> str:
    year_queries: List[str] = ["BEGIN TRANSACTION;"]

    for year in years:
        dir_year = dir_seminar.joinpath(f"{year.first_year}")
        if not dir_year.exists():
            continue
        year_queries.append(generate_sql_year(dir_year, year))

    return '\n\n\n\n'.join(year_queries + ["COMMIT;"])


def generate_sql_year(dir_year, year: TexYear) -> str:
    year_queries: List[str] = []
    year_name = f"{year.first_year} / {year.second_year}"

    year_queries.append(
        f'INSERT INTO years VALUES({year.index}, {mysql_escape(year_name)}, FALSE, 0);'
    )

    for wave in sorted(year.waves, key=lambda x: x.index):
        dir_wave = dir_year.joinpath(f"{wave.index}")
        if not dir_wave.exists():
            continue
        year_queries.append(generate_sql_wave(dir_wave, wave, year))

    return '\n\n'.join(year_queries)


def generate_sql_wave(dir_wave, wave: TexWave, year: TexYear) -> str:
    global WAVE_ID
    wave_queries: List[str] = []
    wave_name = f"{wave.index}. vlna"
    wave_published = f"{year.first_year}-01-01 00:00:00"
    wave_id = WAVE_ID

    wave_queries.append(
        f'INSERT INTO waves VALUES({WAVE_ID}, {year.index}, {WAVE_ID}, {mysql_escape(wave_name)}, {WAVE_GARANT}, {mysql_escape(wave_published)});'
    )
    WAVE_ID += 1

    first_task_in_wave = True
    for task in sorted(wave.tasks, key=lambda x: x.index):
        dir_task = dir_wave.joinpath(f"{task.index}")
        if not dir_task.exists():
            continue
        wave_queries.append(generate_sql_task(dir_task, wave_id, year, first_task_in_wave))
        first_task_in_wave = False

    return '\n'.join(wave_queries)


def generate_sql_task(dir_task, wave_id: int, year: TexYear, first_task_in_wave: bool) -> str:
    global TASK_ID, THREAD_ID, PREREQUISITE_ID

    time_published = f"{year.first_year}-01-01 00:00:00"

    file_assigment = dir_task.joinpath('assigment.html')
    file_solution = dir_task.joinpath('solution.html')
    file_meta = dir_task.joinpath('info.json')
    with file_meta.open('r') as f:
        info = json.load(f)
    with file_assigment.open('r') as f:
        assigment = f.read().replace('\n', '')
    with file_solution.open('r') as f:
        solution = f.read().replace('\n', '')

    task_name = info['title']
    task_prerequisite = "NULL" if first_task_in_wave else PREREQUISITE_ID

    task_queries: List[str] = [
        f'INSERT INTO threads VALUES({THREAD_ID}, {mysql_escape(task_name)}, TRUE, {year.index});',
        f'INSERT INTO tasks VALUES({TASK_ID}, {mysql_escape(task_name)}, {WAVE_GARANT}, NULL, {wave_id}, {task_prerequisite}, "Korespondenční úloha", {mysql_escape(assigment)}, {mysql_escape(solution)}, {THREAD_ID}, {mysql_escape(ICON_BASE)}, {mysql_escape(time_published)}, {mysql_escape(time_published)}, TRUE, {mysql_escape("none")}, {mysql_escape("none")}, {mysql_escape("none")}, {mysql_escape(time_published)}, {mysql_escape("done")}, NULL);'
    ]

    if not first_task_in_wave:
        task_queries.extend([
            f'INSERT INTO prerequisities VALUES({PREREQUISITE_ID}, "ATOMIC", NULL, {TASK_ID - 1});',
        ])
        PREREQUISITE_ID += 1

    THREAD_ID += 1
    TASK_ID += 1

    return '\n'.join(task_queries)


if __name__ == '__main__':
    def main() -> int:
        dir_root = Path(__file__).parent.parent.resolve()
        years = get_tex_years(dir_root.joinpath('src').resolve())
        dir_output = dir_root.joinpath('output').resolve()

        print(generate_sql_insert(dir_output, years))
        return 0

    main()
