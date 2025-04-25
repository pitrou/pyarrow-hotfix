import contextlib
import os

import pytest

import pyarrow as pa
import pyarrow.parquet as pq

import pyarrow_hotfix


pa_version = tuple(map(int, pa.__version__.split('.')))

here = os.path.dirname(__file__)

ipc_file = os.path.join(here, 'data.arrow')
pq_file = os.path.join(here, 'data.pq')

has_parquet_extension_support = pa_version >= (0, 15)

deserialization_disabled = pa_version >= (14, 0, 1)

require_parquet_extension_support = pytest.mark.skipif(
    not has_parquet_extension_support,
    reason="PyArrow version does support extension types with Parquet")


@contextlib.contextmanager
def uninstalled_hotfix():
    pyarrow_hotfix.uninstall()
    try:
        yield
    finally:
        pyarrow_hotfix.install()


def assert_hotfix_functional(capsys, func, *args, **kwargs):
    if pa_version < (0, 15) or pa_version >= (21, 0):
        table = func(*args, **kwargs)
        expected_schema = pa.schema([pa.field('ext', pa.null())])
        assert table.schema.equals(expected_schema, check_metadata=False)
    else:
        expected = "Disallowed deserialization of 'arrow.py_extension_type'"
        with pytest.raises(RuntimeError, match=expected):
            func(*args, **kwargs)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def assert_hotfix_disabled(capsys, func, *args, **kwargs):
    if not deserialization_disabled:
        with uninstalled_hotfix():
            with pytest.raises(Exception):
                func(*args, **kwargs)
        captured = capsys.readouterr()
        assert captured.out.strip() == "hello world!"
        assert captured.err == ""
    else:
        with uninstalled_hotfix():
            func(*args, **kwargs)
        captured = capsys.readouterr()
        assert captured.out.strip() == ""
        assert captured.err == ""


def read_ipc(ipc_file):
    return pa.ipc.open_file(ipc_file).read_all()


def read_parquet(pq_file):
    return pq.read_table(pq_file)


def test_ipc(capsys):
    assert_hotfix_functional(capsys, read_ipc, ipc_file)


@require_parquet_extension_support
def test_parquet(capsys):
    assert_hotfix_functional(capsys, read_parquet, pq_file)


def test_ipc_uninstalled(capsys):
    assert_hotfix_disabled(capsys, read_ipc, ipc_file)


@require_parquet_extension_support
def test_parquet_uninstalled(capsys):
    assert_hotfix_disabled(capsys, read_parquet, pq_file)


def test_uninstall_reinstall(capsys):
    with uninstalled_hotfix():
        pass
    assert_hotfix_functional(capsys, read_ipc, ipc_file)
    if has_parquet_extension_support:
        assert_hotfix_functional(capsys, read_parquet, pq_file)


def test_uninstalled_twice(capsys):
    with uninstalled_hotfix():
        assert_hotfix_disabled(capsys, read_ipc, ipc_file)


def test_reinstalled_twice(capsys):
    with uninstalled_hotfix():
        pass
    pyarrow_hotfix.install()
    assert_hotfix_functional(capsys, read_ipc, ipc_file)
    if has_parquet_extension_support:
        assert_hotfix_functional(capsys, read_parquet, pq_file)
