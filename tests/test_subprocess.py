import subprocess
import sys


def assert_silent_subprocess(code):
    proc = subprocess.run([sys.executable, "-c", code],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    assert proc.returncode == 0, proc
    assert proc.stdout == b''
    assert proc.stderr == b''


def test_silent():
    code = """if 1:
        import pyarrow, pyarrow_hotfix
        """
    assert_silent_subprocess(code)


def test_uninstall():
    code = """if 1:
        import pyarrow, pyarrow_hotfix

        pyarrow_hotfix.uninstall()
        """
    assert_silent_subprocess(code)


def test_uninstall_reinstall():
    code = """if 1:
        import pyarrow, pyarrow_hotfix

        pyarrow_hotfix.uninstall()
        pyarrow_hotfix.install()
        """
    assert_silent_subprocess(code)


def test_install_twice():
    code = """if 1:
        import pyarrow, pyarrow_hotfix

        pyarrow_hotfix.install()
        """
    assert_silent_subprocess(code)


def test_uninstall_twice():
    code = """if 1:
        import pyarrow, pyarrow_hotfix

        pyarrow_hotfix.uninstall()
        pyarrow_hotfix.uninstall()
        """
    assert_silent_subprocess(code)

def test_import_twice():
    code = """if 1:
        import sys
        import pyarrow
        import pyarrow_hotfix
        del sys.modules['pyarrow_hotfix']
        del pyarrow_hotfix
        import pyarrow_hotfix
        """
    assert_silent_subprocess(code)

def test_no_pyarrow():
    code = """if 1:
        import sys
        sys.modules['pyarrow'] = None  # causes ModuleNotFoundError
        import pyarrow_hotfix
        pyarrow_hotfix.uninstall()
        """
    assert_silent_subprocess(code)
