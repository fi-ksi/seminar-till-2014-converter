# Seminar converter

Converts KSI tasks from before year 2014 into SQL statement
that can be inserted into a backend database.

## Requirements

### Tasks

Because the content of the tasks is inside hidden repository,
it is necessary to first initialize submodules

```bash
git submodule init
```

which will clone all tasks inside the `seminar-till-2014` directory.

### Python

All Python requirements are listed inside `requirements.txt` file and
can be installed by running

```bash
pip install -r requirements.txt
```

### Commands

The converter requires following commands to be available:

- `latex2html` to convert LaTeX to HTML
- `inkscape` to resize SVG images

## Usage

To generate HTML task files from `seminar-till-2014` directory to `output` directory,
execute

```bash
python main.py
```

To process the generated `output` directory into a single SQL statement,
first adjust global constants inside `generate_sql.py` and
then execute

```bash
python generate_sql.py
```

This will print the SQL import statement to the standard output.

## Code structure

The code is split into two folders:

- `tex` contains functions that take care of locating all TeX tasks together with their solutions (`locator.py`) and for parsing task metadata (`parser.py`) - name, points and assets
- `html_writer` converts TeX tasks into HTML strings that can be inserted into KSI database (`converter.py`)

Both sub-directories have a `types.py` file which contains custom-defined types.
