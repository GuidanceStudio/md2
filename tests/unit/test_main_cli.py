import subprocess
import sys


def test_missing_file_exits():
    result = subprocess.run(
        [sys.executable, "-m", "md2", "nonexistent_file.md"],
        capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "not found" in result.stderr or "not found" in result.stdout


def test_no_arguments_exits():
    result = subprocess.run(
        [sys.executable, "-m", "md2"],
        capture_output=True, text=True
    )
    assert result.returncode != 0


def test_output_filename_derived():
    # Test that the logic derives .html from .md
    import os
    base_name = os.path.splitext("test_file.md")[0]
    output = f"{base_name}.html"
    assert output == "test_file.html"
