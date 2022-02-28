from pathlib import Path

from converter.tex import get_tex_years
from converter.markdown import write_tex_year


def main() -> None:
    years = get_tex_years(Path(__file__).parent.parent.joinpath('src').resolve())
    for year in years:
        write_tex_year(year, Path('/media/ramdisk/tmp-seminar'))


if __name__ == '__main__':
    main()
