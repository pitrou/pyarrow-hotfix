# SPDX-FileCopyrightText: 2023-present Antoine Pitrou <antoine@python.org>
#
# SPDX-License-Identifier: Apache-2.0

def install():
    import atexit
    import pyarrow as pa

    if not hasattr(pa, "ExtensionType"):
        # Unsupported PyArrow version?
        return

    if getattr(pa, "_hotfix_installed", False):
        return

    class ForbiddenExtensionType(pa.ExtensionType):
        def __arrow_ext_serialize__(self):
            return b""

        @classmethod
        def __arrow_ext_deserialize__(cls, storage_type, serialized):
            import io
            import pickletools
            out = io.StringIO()
            pickletools.dis(serialized, out)
            raise RuntimeError(
                "forbidden deserialization of 'arrow.py_extension_type': "
                "storage_type = %s, serialized = %r, "
                "pickle disassembly:\n%s"
                % (storage_type, serialized, out.getvalue()))

    if hasattr(pa, "unregister_extension_type"):
        # 0.15.0 <= PyArrow
        pa.unregister_extension_type("arrow.py_extension_type")
        pa.register_extension_type(ForbiddenExtensionType(pa.null(),
                                                          "arrow.py_extension_type"))
    elif hasattr(pa.lib, "_unregister_py_extension_type"):
        # 0.14.1 <= PyArrow < 0.15.0
        pa.lib._unregister_py_extension_type()
        atexit.unregister(pa.lib._unregister_py_extension_type)
    else:
        # PyArrow 0.14.0
        del pa.lib._extension_types_initializer

    pa._hotfix_installed = True


def uninstall():
    import atexit
    import pyarrow as pa

    if not hasattr(pa, "ExtensionType"):
        # Unsupported PyArrow version?
        return

    if not getattr(pa, "_hotfix_installed", False):
        return

    if hasattr(pa, "unregister_extension_type"):
        # 0.15.0 <= PyArrow
        pa.unregister_extension_type("arrow.py_extension_type")
        pa.lib._register_py_extension_type()
    elif hasattr(pa.lib, "_register_py_extension_type"):
        # 0.14.1 <= PyArrow < 0.15.0
        pa.lib._register_py_extension_type()
        atexit.register(pa.lib._unregister_py_extension_type)
    elif hasattr(pa.lib, "_ExtensionTypesInitializer"):
        # PyArrow 0.14.0
        pa.lib._extension_types_initializer = pa.lib._ExtensionTypesInitializer()

    pa._hotfix_installed = False


install()
