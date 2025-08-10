import json
import subprocess
import sys


def test_cli_processes_single_file(tmp_path, dialog_project):
    src = tmp_path / "dialogs.json"
    src.write_text(json.dumps(dialog_project), encoding="utf8")
    out_dir = tmp_path / "out"
    result = subprocess.run(
        [sys.executable, "-m", "dialoggen.cli", "--in", str(src), "--out-dir", str(out_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (out_dir / "dialogs_day1_intro.rpy").exists()


def test_cli_processes_directory(tmp_path, dialog_project):
    src_dir = tmp_path / "input"
    src_dir.mkdir()
    (src_dir / "tree.json").write_text(json.dumps(dialog_project), encoding="utf8")
    out_dir = tmp_path / "out"
    result = subprocess.run(
        [sys.executable, "-m", "dialoggen.cli", "--in", str(src_dir), "--out-dir", str(out_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (out_dir / "dialogs_day1_intro.rpy").exists()
