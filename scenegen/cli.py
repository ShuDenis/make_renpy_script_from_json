import argparse, json, pathlib, sys
from .validator import validate, ValidationError
from .generator import generate_rpy

def main(argv=None):
    p = argparse.ArgumentParser(prog="scenegen", description="SceneGen: JSON -> Ren'Py scenes generator")
    p.add_argument("--in", dest="infile", required=True, help="Input scenes JSON")
    p.add_argument("--out-dir", dest="outdir", required=True, help="Output directory (Ren'Py /game)")
    p.add_argument("--fail-on-warning", action="store_true", help="(reserved)")
    args = p.parse_args(argv)

    src = pathlib.Path(args.infile)
    outdir = pathlib.Path(args.outdir)
    if not src.exists():
        print(f"Input not found: {src}", file=sys.stderr)
        return 2
    data = json.loads(src.read_text(encoding="utf-8"))
    try:
        validate(data)
    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 3

    files = generate_rpy(data)
    for rel, content in files.items():
        path = outdir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Generated {len(files)} files into {outdir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
