
import contextlib
import os
import pytest

import pyarrow as pa
import pyarrow.parquet as pq

import pyarrow_hotfix


here = os.path.dirname(__file__)

ipc_file = os.path.join(here, 'data.arrow')
pq_file = os.path.join(here, 'data.pq')


@contextlib.contextmanager
def uninstalled_hotfix():
    pyarrow_hotfix.uninstall()
    try:
        yield
    finally:
        pyarrow_hotfix.install()


def test_ipc(capsys):
    expected = "forbidden deserialization of 'arrow.py_extension_type'"
    with pytest.raises(RuntimeError, match=expected):
        pa.ipc.open_stream(ipc_file).read_batch()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_parquet(capsys):
    expected = "forbidden deserialization of 'arrow.py_extension_type'"
    with pytest.raises(RuntimeError, match=expected):
        pq.read_table(pq_file)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_ipc_uninstalled(capsys):
    with uninstalled_hotfix():
        with pytest.raises(Exception):
            pa.ipc.open_stream(ipc_file).read_batch()
    captured = capsys.readouterr()
    assert captured.out.strip() == "arbitrary execution!"
    assert captured.err == ""


def test_parquet_uninstalled(capsys):
    with uninstalled_hotfix():
        with pytest.raises(Exception):
            pq.read_table(pq_file)
    captured = capsys.readouterr()
    assert captured.out.strip() == "arbitrary execution!"
    assert captured.err == ""


def test_uninstall_reinstall(capsys):
    with uninstalled_hotfix():
        pass
    expected = "forbidden deserialization of 'arrow.py_extension_type'"
    with pytest.raises(RuntimeError, match=expected):
        pa.ipc.open_stream(ipc_file).read_batch()
    with pytest.raises(RuntimeError, match=expected):
        pq.read_table(pq_file)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
