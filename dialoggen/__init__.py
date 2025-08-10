from pkgutil import extend_path
import pathlib
import sys

_src = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

__path__ = extend_path(__path__, __name__)
