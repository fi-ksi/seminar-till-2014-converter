import shutil
from typing import List, Set
from base64 import b64encode
from mimetypes import guess_type

from converter.html_writer.types import KSITask
from converter.tex import TexTask
from tempfile import mkdtemp
from pathlib import Path
from subprocess import check_output, PIPE, call
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup

from converter.tex_parser.parser import get_tex_assets, parse_task_name, parse_task_points


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


def tex_to_html(file_tex: Path) -> str:
    dir_convert = Path(mkdtemp(prefix='ksi_task_', dir='/media/ramdisk'))
    file_tex_tmp = dir_convert.joinpath('input.tex')

    with file_tex.open('r') as f:
        tex_content = f.read()
    tex_content = tex_content\
        .replace(r'\hlavicka', r'%\hlavicka')\
        .replace(r'\mensinadpis', r'\\ -')\
        .replace(r'\bullet ', '')
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
    ], text=True, stderr=PIPE, timeout=60)
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
        ], timeout=60)
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

    shutil.rmtree(dir_convert)

    return soup.find('body').decode_contents()


def get_html_task(task: TexTask) -> KSITask:
    return KSITask(
        index=task.index,
        title=parse_task_name(task.assigment),
        points=parse_task_points(task.assigment),
        assigment=tex_to_html(task.assigment),
        solution=tex_to_html(task.solution) if task.solution.exists() else '<p>Tato úloha nemá řešení</p>'
    )
