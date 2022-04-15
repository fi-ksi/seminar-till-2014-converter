from pathlib import Path
from typing import Iterator, Optional

from .types import BETask, BEWave, BETaskMeta
from .login import get_session


class Backend:
    def __init__(self, url: str, dir_seminar: Path, author_id: int) -> None:
        assert dir_seminar.is_dir()
        self.__session = get_session(url)
        self.__dir_root = dir_seminar
        self.__url = url
        self.__year_offset: Optional[int] = None
        self.__author_id = author_id

    @property
    def year_offset(self) -> int:
        if self.__year_offset is not None:
            return self.__year_offset
        for year in self.get_remote_years():
            year_id = year['id']
            year_first = int(year['year'].split('/', 1)[0].strip())
            return year_first - year_id
        raise ValueError()

    def get_remote_years(self) -> list:
        return self.__session.get(f'{self.__url}/years').json()['years']

    def get_year_index(self, first_year: int) -> int:
        return first_year - self.year_offset

    def list_local_tasks(self) -> Iterator[BETask]:
        for dir_year in self.__dir_root.iterdir():
            if not dir_year.is_dir() or not dir_year.name.isdigit():
                continue
            for dir_wave in dir_year.iterdir():
                if not dir_wave.is_dir() or not dir_wave.name.startswith('vlna'):
                    continue
                for dir_task in dir_wave.iterdir():
                    if not dir_task.is_dir() or not dir_task.name.startswith('uloha_'):
                        continue
                    git_path = f"{dir_task.relative_to(self.__dir_root)}"
                    for uploaded_tasks in self.list_remote_tasks(int(dir_year.name)):
                        if uploaded_tasks.git_path == git_path:
                            is_uploaded = True
                            break
                    else:
                        is_uploaded = False

                    yield BETask(git_path=git_path, deployed_=is_uploaded, wave=None)

    def list_remote_tasks(self, first_year: int) -> Iterator[BETask]:
        return map(
            lambda x: BETask(deployed_=True, git_path=x['git_path'], wave=x['wave']),
            self.__session.get(
                f'{self.__url}/admin/atasks/',
                headers={'year': str(self.get_year_index(first_year))}
            ).json()['atasks']
        )

    def list_remote_waves(self, first_year: int) -> Iterator[BEWave]:
        for wave in self.__session.get(
                f'{self.__url}/waves/',
                headers={'year': str(self.get_year_index(first_year))}
        ).json()['waves']:
            yield BEWave(
                index=wave['id'],
                directory_=self.__dir_root.joinpath(f'vlna{wave["index"]}').resolve()
            )

    def get_task_meta(self, task: BETask) -> BETaskMeta:
        dir_task = self.__dir_root.joinpath(task.git_path)
        assert dir_task.is_dir()

        file_assigment = dir_task.joinpath('assigment.md')
        with file_assigment.open('r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('# '):
                    task_name = line[2:].strip()
                    break
            else:
                raise ValueError

        first_year, wave_name, _ = task.git_path.split('/', 2)
        return BETaskMeta(
            name=task_name,
            first_year=int(first_year),
            directory=dir_task,
            wave_directory=dir_task.parent.resolve()
        )

    def create_year(self, first_year: int) -> int:
        for year in self.get_remote_years():
            if year['year'].startswith(f"{first_year}"):
                return year['id']

        year_index = self.get_year_index(first_year)

        r = self.__session.post(
            f'{self.__url}/years/',
            json={
                'year': {
                    'year': f'{first_year} / {first_year + 1}',
                    'index': year_index,
                    'point_pad': 0,
                    'sealed': False
                }
            }
        )

        assert r.ok, r.text

        return year_index

    def create_wave(self, dir_wave: Path) -> int:
        first_year = int(dir_wave.parent.resolve().name)

        for wave in self.list_remote_waves(first_year):
            print(dir_wave, wave.directory_)
            if wave.directory_ == dir_wave:
                return wave.index

        self.create_year(first_year)

        wave_index = int(dir_wave.name.replace('vlna', ''))

        r = self.__session.post(
            f'{self.__url}/waves/',
            json={
                'wave': {
                    'year': self.get_year_index(first_year),
                    'index': wave_index,
                    'caption': f'{wave_index}. vlna',
                    'time_published': '2040-01-01',
                    'garant': self.__author_id
                }
            }
        )

        assert r.ok, r.text

        return r.json()['wave']['id']

    def create_task(self, task: BETask) -> None:
        meta = self.get_task_meta(task)
        wave_index = self.create_wave(meta.wave_directory)

        for task2 in self.list_remote_tasks(meta.first_year):
            if task.git_path == task2.git_path:
                return

        r = self.__session.post(
            f'{self.__url}/admin/atasks/',
            headers={'year': str(self.get_year_index(meta.first_year))},
            json={
                'atask': {
                    'wave': wave_index,
                    'title': meta.name,
                    'author': self.__author_id,
                    'git_branch': 'master',
                    'git_commit': '',
                    'git_path': f"{meta.directory.relative_to(self.__dir_root)}"
                }
            }
        )

        assert r.ok, f"{r.status_code=} {r.text=}"
