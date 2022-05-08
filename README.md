# Seminar converter

Converts KSI tasks from before year 2014 into SQL statement
that can be inserted into a backend database.

## Requirements

All requirements are listed inside `converter/requirements.txt` file and
can be installed by running

```bash
pip install -r converter/requirements.txt
```

## Usage

To generate HTML task files from `src` directory to `output` directory,
execute

```bash
python converter/main.py
```

To process the generated `output` directory into a single SQL statement,
first adjust global constants inside `converter/generate_sql.py` and
then execute

```bash
python converter/generate_sql.py
```

This will print the SQL import statement to the standard output.
