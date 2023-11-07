import os
import subprocess
import sys

import pytest


def assert_silent_subprocess(code):
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert proc.returncode == 0, proc
    assert proc.stdout == b''
    assert proc.stderr == b''


def test_hotfix_silent():
    code = """if 1:
        import pyarrow
        import pyarrow_hotfix
        """
    assert_silent_subprocess(code)


def test_hotfix_uninstall():
    code = """if 1:
        import pyarrow
        import pyarrow_hotfix

        pyarrow_hotfix.uninstall()
        """
    assert_silent_subprocess(code)


def test_hotfix_uninstall_reinstall():
    code = """if 1:
        import pyarrow
        import pyarrow_hotfix

        pyarrow_hotfix.uninstall()
        pyarrow_hotfix.install()
        """
    assert_silent_subprocess(code)
