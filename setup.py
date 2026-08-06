# Build the CPython private remote-debugging module from version-matched sources.
# Project metadata and package discovery live in pyproject.toml.

from __future__ import annotations

import os
import sys
import sysconfig
from pathlib import Path

from setuptools import Extension, setup


ROOT = Path(__file__).parent.resolve()
NATIVE_DIR = ROOT / "_remote_debugging"

SOURCES_315 = [
    "module.c",
    "gc_stats.c",
    "object_reading.c",
    "code_objects.c",
    "frames.c",
    "frame_cache.c",
    "threads.c",
    "asyncio.c",
    "binary_io_writer.c",
    "binary_io_reader.c",
    "subprocess.c",
    "interpreters.c",
]

HEADERS_315 = [
    "_remote_debugging.h",
    "binary_io.h",
    "debug_offsets_validation.h",
    "gc_stats.h",
    "remote_debug.h",
    "clinic/module.c.h",
]

if sys.version_info[:2] == (3, 14):
    sources = ["remote_debugging_314.c"]
    headers = [
        "remote_debug_314.h",
        "clinic/_remote_debugging_module_314.c.h",
    ]
elif sys.version_info[:2] == (3, 15):
    sources = SOURCES_315
    headers = HEADERS_315
else:
    raise RuntimeError(
        "python-profiling supports CPython 3.14 and 3.15 only; "
        f"found {sys.version_info.major}.{sys.version_info.minor}"
    )

include_dirs = [
    str(NATIVE_DIR),
    str(Path(sysconfig.get_path("include")) / "internal"),
]
define_macros = [("Py_BUILD_CORE_MODULE", "1")]
libraries = []
library_dirs = []
extra_compile_args = []

if os.name == "nt":
    if sys.version_info[:2] >= (3, 15):
        libraries.append("ntdll")
    extra_compile_args.extend(["/std:c11", "/utf-8"])
else:
    extra_compile_args.append("-std=c11")

# Zstandard is used only by the 3.15 binary profile implementation.
if (
    sys.version_info[:2] >= (3, 15)
    and os.environ.get("PYTHON_PROFILING_WITH_ZSTD") == "1"
):
    define_macros.append(("HAVE_ZSTD", "1"))
    libraries.append("zstd")
    if value := os.environ.get("PYTHON_PROFILING_ZSTD_INCLUDE"):
        include_dirs.append(value)
    if value := os.environ.get("PYTHON_PROFILING_ZSTD_LIB"):
        library_dirs.append(value)

extension = Extension(
    "_remote_debugging",
    sources=[f"_remote_debugging/{source}" for source in sources],
    depends=[f"_remote_debugging/{header}" for header in headers],
    include_dirs=include_dirs,
    define_macros=define_macros,
    libraries=libraries,
    library_dirs=library_dirs,
    extra_compile_args=extra_compile_args,
    py_limited_api=False,
)

setup(ext_modules=[extension])
