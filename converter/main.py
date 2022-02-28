from pathlib import Path

from converter.conversion import get_markdown_task
from converter.tex import get_tex_years


def main() -> None:
    task = next(get_tex_years(Path(__file__).parent.parent.joinpath('src').resolve())).waves[0].tasks[0]
    print(task)
    print(get_markdown_task(task.assigment))


if __name__ == '__main__':
    main()
