import pytest
import subprocess
import sys
import os

def run_coplc(args):
    """Giả lập gọi script coplc.py bằng subprocess."""
    cli_path = os.path.join(os.path.dirname(__file__), "..", "coplc.py")
    cmd = [sys.executable, cli_path] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def test_cli_help():
    res = run_coplc(["-h"])
    assert res.returncode == 0
    assert "COPL Compiler CLI" in res.stdout

def test_cli_check_success():
    res = run_coplc(["check", "examples/01_minimal.copl"])
    assert res.returncode == 0
    assert "Frontend passed." in res.stdout
    assert "Check completed successfully for examples/01_minimal.copl." in res.stdout

def test_cli_check_file_not_found():
    res = run_coplc(["check", "examples/missing_file.copl"])
    assert res.returncode == 1
    assert "File 'examples/missing_file.copl' not found." in res.stdout

def test_cli_build_success(tmp_path):
    out_dir = str(tmp_path / "build_test")
    res = run_coplc(["build", "examples/02_can_driver.copl", "--out-dir", out_dir])
    
    assert res.returncode == 0
    assert "Frontend passed." in res.stdout
    assert "Generating C code..." in res.stdout
    
    # Kiểm tra xem file có sinh ra trong out_dir không
    assert os.path.exists(os.path.join(out_dir, "02_can_driver.h"))
    assert os.path.exists(os.path.join(out_dir, "02_can_driver.c"))

def test_cli_build_missing_file():
    res = run_coplc(["build", "doesntexist.copl"])
    assert res.returncode == 1
    assert "File 'doesntexist.copl' not found." in res.stdout
