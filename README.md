# make_renpy_script_from_json

A small utility to convert JSON-described dialogues into a Ren'Py script.

## Project structure

```
README.md
LICENSE
pyproject.toml
scripts/
    run.py
src/
    make_renpy_script/
        __init__.py
        converter.py
tests/
    test_converter.py
```

## Usage

Install the package in editable mode and run the converter:

```bash
pip install -e .
python scripts/run.py path/to/dialogue.json -o output.rpy
```

Run the test suite with:

```bash
pytest
```
