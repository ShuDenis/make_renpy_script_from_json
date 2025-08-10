# make_renpy_script_from_json

Utilities to generate Ren'Py scripts from JSON descriptions.

The project contains two generators:

* **dialogue** – converts a simple dialogue JSON into a single `.rpy` file.
* **scenes** – validates scene descriptions and produces Ren'Py screens/labels.

Both generators can be used programmatically or via the command line.

## Command line usage

From the repository root or after installing the package, run:

```bash
python -m make_renpy_script dialogue path/to/dialogue.json -o output
python -m make_renpy_script scenes path/to/scenes.json -o output
```

If the input path points to a directory (or is omitted), all `*.json` files
within it are processed. The output directory defaults to `output/` and the
input path defaults to `input/`.

## Development

Run the test suite with:

```bash
pytest
```
