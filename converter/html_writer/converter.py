import shutil
import re
from typing import List, Set, Iterable
from base64 import b64encode
from mimetypes import guess_type

from converter.tex import TexTask
from tempfile import mkdtemp
from pathlib import Path
from subprocess import check_output, PIPE, call
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup

RE_TEX_ASSET = re.compile(r'\\includegraphics.*?{(.*?)}')


class HtmlConversionLog:
    def __init__(self):
        self.__runs: List[List[str]] = []

    def add_run(self, stdout: str) -> None:
        self.__runs.append(stdout.split('\n'))

    @property
    def runs(self) -> List[List[str]]:
        return self.__runs

    @property
    def lines(self) -> List[str]:
        r: List[str] = []
        for x in self.runs:
            r.extend(x)
        return r

    @property
    def text(self) -> str:
        return '\n'.join(self.lines)

    @property
    def unknown_commands(self) -> Set[str]:
        r: Set[str] = set()
        line_start = 'Unknown commands: '
        for line in self.lines:
            if not line.startswith(line_start):
                continue
            r.update(line[len(line_start):].split(' '))
        return r


LOG = HtmlConversionLog()


def get_tex_assets(file_tex: Path) -> Iterable[Path]:
    with file_tex.open('r') as f:
        content = f.read()

    return map(
        lambda x: file_tex.parent.joinpath(x.group(1)).resolve(),
        RE_TEX_ASSET.finditer(content)
    )


def tex_to_html(file_tex: Path) -> str:
    dir_convert = Path(mkdtemp(prefix='ksi_task_', dir='/media/ramdisk'))
    file_tex_tmp = dir_convert.joinpath('input.tex')

    with file_tex.open('r') as f:
        tex_content = f.read()
    tex_content = tex_content\
        .replace(r'\hlavicka', r'%\hlavicka')\
        .replace(r'\mensinadpis', r'\textbf')
    with file_tex_tmp.open('w') as f:
        f.write(r'\usepackage{graphicx}')
        f.write('\n')
        f.write(tex_content)

    for asset in get_tex_assets(file_tex):
        shutil.copy(asset, dir_convert.joinpath(asset.name))

    stdout = check_output([
        'latex2html',
        '-dir', f"{dir_convert.absolute()}",
        '-split', '0',
        '-info', '0',
        '-no_navigation',
        '-use_dvipng',
        '-discard',
        f"{file_tex_tmp.absolute()}"
    ], text=True, stderr=PIPE)
    LOG.add_run(stdout)

    display = Display()
    display.start()
    for child in dir_convert.iterdir():
        if not child.name.lower().endswith('.svg'):
            continue
        call([
            'inkscape',
            '--verb=FitCanvasToDrawing',
            '--verb=FileSave',
            '--verb=FileQuit',
            f"{child.absolute()}"
        ])
    display.stop()

    file_index = dir_convert.joinpath('index.html')
    with file_index.open('r') as f:
        index_html = f.read()
    index_html = index_html.replace('height: 195.54ex', 'height: 1em')

    soup = BeautifulSoup(index_html, 'html.parser')
    for img in soup.find_all('img'):
        file_img = dir_convert.joinpath(img['src'])
        with file_img.open('rb') as f:
            img_b64 = b64encode(f.read()).decode('ascii')
        img['src'] = f"data:{guess_type(file_img)[0]};base64,{img_b64}"

    index_html = soup.prettify()
    with file_index.open('w') as f:
        f.write(index_html)

    return f"{dir_convert.absolute()}"


def get_html_task(task: TexTask) -> str:
    return tex_to_html(task.assigment)
