from pathlib import Path

from converter.html import get_html_task, LOG
from converter.remote import Backend
from converter.tex import get_tex_years


def main() -> None:
    years = get_tex_years(Path(__file__).parent.parent.joinpath('src').resolve())
    for year in years:
        for wave in year.waves:
            for task in wave.tasks:
                try:
                    print(get_html_task(task))
                except KeyboardInterrupt:
                    print(LOG.text)
                    return
                print(LOG.unknown_commands)
                return


if __name__ == '__main__':
    main()
