import shutil
import subprocess
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
        .replace(r'\mensinadpis', r'\textbf')\
        .replace(r'\bullet ', r'\\ -')\
        .replace(r'\begin{code}', r'___begin__code') \
        .replace(r'\end{code}', r'___end__code')
    with file_tex_tmp.open('w') as f:
        f.write('\\usepackage{graphicx}\n')
        f.write('\\usepackage{pdfpages}\n')
        f.write('\\usepackage[utf8]{inputenc}\n')
        f.write('\\usepackage{enumitem}  \n')
        f.write(tex_content)

    # copy all assets locally
    for asset in get_tex_assets(file_tex):
        if asset is None:
            continue
        shutil.copy(asset, dir_convert.joinpath(asset.name))

    # convert latex to html
    stdout = check_output([
        'latex2html',
        '-dir', f"{dir_convert.absolute()}",
        '-split', '0',
        '-info', '0',
        '-no_navigation',
        '-use_dvipng',
        '-discard',
        f"{file_tex_tmp.absolute()}"
    ], text=True, stderr=PIPE, timeout=15)
    LOG.add_run(stdout)

    # parse crated HTML
    file_index = dir_convert.joinpath('index.html')
    with file_index.open('r', errors='replace') as f:
        index_html = f.read()

    # replace wrong tags and image sizes
    index_html = index_html\
        .replace('height: 195.54ex', 'height: 1em') \
        .replace(r'___begin__code', r'<pre><code>') \
        .replace(r'___emd__code', r'</code></pre>')

    soup = BeautifulSoup(index_html, 'html.parser')

    # inline latex math instead of including it as an image
    for math in soup.find_all(class_='MATH'):
        math_text = ""
        to_delete: List[Path] = []
        for img in math.find_all('img'):
            math_text += img['alt'] + " "
            to_delete.append(dir_convert.joinpath(img['src']))
        for file in to_delete:
            file.unlink(missing_ok=True)
        math.string = math_text

    # crop remaining svgs
    display = Display()
    display.start()
    for child in dir_convert.iterdir():
        if not child.name.lower().endswith('.svg'):
            continue
        try:
            call([
                'inkscape',
                '--verb=FitCanvasToDrawing',
                '--verb=FileSave',
                '--verb=FileQuit',
                f"{child.absolute()}"
            ], timeout=15)
        except subprocess.TimeoutExpired:
            child.unlink()
    display.stop()

    # inline all remaining images
    for img in soup.find_all('img'):
        file_img = dir_convert.joinpath(img['src'])
        if not file_img.exists():
            continue
        with file_img.open('rb') as f:
            img_b64 = b64encode(f.read()).decode('ascii')
        img['src'] = f"data:{guess_type(file_img)[0]};base64,{img_b64}"

    # delete temporary directory
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
