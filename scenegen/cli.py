import argparse, json, pathlib, logging, datetime
from .validator import validate, ValidationError
from .generator import generate_rpy


def _setup_logging() -> pathlib.Path:
    """Configure logging and return the log file path."""
    log_dir = pathlib.Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"scenegen_{datetime.datetime.now():%Y%m%d_%H%M%S}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return log_file

def main(argv=None):
    p = argparse.ArgumentParser(prog="scenegen", description="SceneGen: JSON -> Ren'Py scenes generator")
    p.add_argument("--in", dest="infile", required=True, help="Input scenes JSON")
    p.add_argument("--out-dir", dest="outdir", required=True, help="Output directory (Ren'Py /game)")
    p.add_argument("--fail-on-warning", action="store_true", help="Fail if any warnings are emitted")
    args = p.parse_args(argv)

    log_file = _setup_logging()
    logging.info("Log file: %s", log_file)
    logging.captureWarnings(True)
    class _WarnHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.had_warning = False

        def emit(self, record):
            if record.levelno >= logging.WARNING:
                self.had_warning = True

    warn_handler = _WarnHandler()
    root_logger = logging.getLogger()
    root_logger.addHandler(warn_handler)

    src = pathlib.Path(args.infile)
    outdir = pathlib.Path(args.outdir)
    logging.info("Input: %s", src)
    logging.info("Output dir: %s", outdir)
    if not src.exists():
        logging.error("Input not found: %s", src)
        return 2
    data = json.loads(src.read_text(encoding="utf-8"))
    logging.info("Validating JSON")
    try:
        validate(data)
    except ValidationError as e:
        logging.error("Validation error: %s", e)
        return 3

    logging.info("Generating Ren'Py files")
    files = generate_rpy(data)
    for rel, content in files.items():
        path = outdir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logging.info("Wrote %s", path)
    logging.info("Generated %d files into %s", len(files), outdir)
    root_logger.removeHandler(warn_handler)
    if args.fail_on_warning and warn_handler.had_warning:
        logging.error("Warnings were emitted, failing as requested")
        return 4
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
