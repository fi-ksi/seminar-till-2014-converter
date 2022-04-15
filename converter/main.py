from pathlib import Path

from converter.remote import Backend
from converter.tex import get_tex_years
from converter.markdown import write_tex_year


def main() -> None:
    dir_seminar = Path('/media/ramdisk/tmp-seminar')
    years = get_tex_years(Path(__file__).parent.parent.joinpath('src').resolve())
    for year in years:
        pass
        # write_tex_year(year, dir_seminar)

    backend = Backend('http://localhost:3030', dir_seminar, 739)
    for task in backend.list_local_tasks():
        backend.create_task(task)


if __name__ == '__main__':
    main()
