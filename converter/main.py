from pathlib import Path

from converter.tex import get_tex_years


def main() -> None:
    print((list(get_tex_years(Path(__file__).parent.parent.joinpath('src').resolve(), 2008))))


if __name__ == '__main__':
    main()
