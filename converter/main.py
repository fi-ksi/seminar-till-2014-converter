import json
from pathlib import Path
from traceback import format_exc

from converter.html_writer import get_html_task, LOG
from converter.tex import get_tex_years


def main() -> None:
    dir_root = Path(__file__).parent.parent.resolve()
    years = list(get_tex_years(dir_root.joinpath('src').resolve()))
    dir_output = dir_root.joinpath('output').resolve()

    for year in years:
        for wave in year.waves:
            for task in wave.tasks:
                # noinspection PyBroadException
                ksi_task_dir = dir_output.joinpath(f"{year.first_year}").joinpath(f"{wave.index}").joinpath(
                    f"{task.index}")
                file_assigment = ksi_task_dir.joinpath('assigment.html')
                file_solution = ksi_task_dir.joinpath('solution.html')
                file_meta = ksi_task_dir.joinpath('info.json')

                print(f"{ksi_task_dir.relative_to(dir_root)}", end=' ... ', flush=True)
                if ksi_task_dir.exists():
                    print('skip')
                    continue

                try:
                    ksi_task = get_html_task(task)
                except KeyboardInterrupt:
                    print(LOG.text)
                    return
                except Exception:
                    print('ERROR')
                    file_traceback = dir_root.joinpath(f"error_convert_{year.index}_{wave.index}_{task.index}")
                    with file_traceback.open('w') as f:
                        f.write('\n'.join(format_exc()))
                    continue

                ksi_task_dir.mkdir(parents=True, exist_ok=True)
                with file_assigment.open('w') as f:
                    f.write(ksi_task.assigment)
                with file_solution.open('w') as f:
                    f.write(ksi_task.solution)
                with file_meta.open('w') as f:
                    json.dump({
                        'title': ksi_task.title,
                        'points': ksi_task.points
                    }, f, indent=True)

                print('OK')
                # return

    print(LOG.unknown_commands)


if __name__ == '__main__':
    main()
