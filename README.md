# python-profiling

`python-profiling` backports the [`profiling`](https://docs.python.org/3.15/library/profiling.html)
package introduced in Python 3.15 to CPython 3.14. It provides both a deterministic tracing profiler and a
low-overhead statistical sampling profiler named **Tachyon**.

> **Status: Alpha.** This project depends on CPython private C APIs and the native `_remote_debugging`
> extension. It does not support PyPy or the Python limited ABI. The profiler and target process must use
> the same CPython major and minor version.

## Features

- `profiling.tracing`: deterministic profiling that records every call and return and produces `pstats`-compatible output.
- `profiling.sampling`: external statistical sampling of a target process's Python call stacks.
- Run a script or module, attach to a PID, or capture a one-shot stack dump.
- Export pstats, collapsed stacks, interactive flame graphs, differential flame graphs, Firefox Profiler data,
  source heatmaps, JSONL, and raw binary profiles.
- Wall-clock, CPU, GIL, and exception modes, plus all-thread sampling, async awareness, GC/native synthetic frames,
  opcode collection, subprocess profiling, and a live TUI.

## Requirements

- **CPython 3.14 or 3.15** (the current release range is `>=3.14,<3.16`).
- Windows, Linux, or macOS.
- Building from source requires a C compiler and CPython development headers:
  - Windows: Visual Studio 2022 Build Tools with **Desktop development with C++**.
  - Debian/Ubuntu: `build-essential python3.14-dev`.
  - macOS: Xcode Command Line Tools.
- Attaching to another process may require additional privileges. See [Permissions and platform notes](#permissions-and-platform-notes).

## Installation

```bash
pip install python-profiling
```

For an editable development installation:

```bash
python -m pip install -e .
```

Raw binary profiles are uncompressed by default. If the zstd development library is installed, enable it at build time:

```bash
# Linux/macOS
PYTHON_PROFILING_WITH_ZSTD=1 python -m pip install .

# PowerShell
$env:PYTHON_PROFILING_WITH_ZSTD = "1"
python -m pip install .
```

Custom zstd include and library directories can be supplied with `PYTHON_PROFILING_ZSTD_INCLUDE` and
`PYTHON_PROFILING_ZSTD_LIB`, respectively.

## Quick start

### Statistical sampling

```bash
# Profile a script; pstats output is printed to the terminal by default
python -m profiling.sampling run examples/workload.py

# Profile a module
python -m profiling.sampling run -m http.server 8000

# Generate a self-contained interactive HTML flame graph
python -m profiling.sampling run --flamegraph -o profile.html examples/workload.py

# Attach to a running CPython process
python -m profiling.sampling attach -d 10 -a --flamegraph -o profile.html 12345

# Display a running process's current stacks
python -m profiling.sampling dump -a 12345
```

Run `python -m profiling.sampling --help` or
`python -m profiling.sampling <run|attach|dump|replay> --help` for the complete command-line reference.

### Deterministic tracing

```bash
python -m profiling.tracing examples/workload.py
python -m profiling.tracing -o trace.pstats examples/workload.py
python -m profiling.tracing -m examples.workload
```

The tracing profiler can also be used programmatically:

```python
from profiling import tracing

tracing.run("sum(i * i for i in range(100_000))")
```

## Output formats and raw data

| Option | Output | Purpose |
| --- | --- | --- |
| `--pstats` | Terminal table, or binary pstats with `-o` | General analysis and use with `pstats` |
| `--collapsed` | `.txt` | Brendan Gregg-style collapsed stacks |
| `--flamegraph` | Self-contained `.html` | Interactive call-stack flame graph |
| `--diff-flamegraph BASELINE` | `.html` | Comparison against a baseline binary profile |
| `--gecko` | `.json` | Import into [Firefox Profiler](https://profiler.firefox.com/) |
| `--heatmap` | HTML directory | Source-line and opcode heatmap |
| `--jsonl` | `.jsonl` | Aggregated raw data for programs, scripts, and agents |
| `--binary` | `.bin` | High-throughput raw samples that can be replayed later |

The binary format stores sample timestamps, string and frame tables, and encoded stack changes. It is intended for
capture-first, analyze-later workflows:

```bash
python -m profiling.sampling run --binary -o raw-profile.bin examples/workload.py
python -m profiling.sampling replay --flamegraph -o profile.html raw-profile.bin
python -m profiling.sampling replay --jsonl -o profile.jsonl raw-profile.bin
```

JSONL records appear in the fixed order `meta`, `string_table`, `frame_table`, `agg`, and `end`.
Every line includes a schema version (`v`) and a per-run `run_id`. Consumers should ignore unknown record types and
fields for forward compatibility. See the module documentation in `profiling/sampling/jsonl_collector.py` for the
complete schema.

## Permissions and platform notes

- Linux access is controlled by `ptrace_scope` and `CAP_SYS_PTRACE`; containers commonly require `--cap-add=SYS_PTRACE`.
- macOS may require `sudo`, and System Integrity Protection may prevent access to system Python processes.
- On Windows, attaching to a process owned by another user may require an Administrator terminal.
- The profiler and target must use the same CPython major and minor version. Pre-release builds may require an exact version match.
- `--live` requires `curses`, which is usually unavailable in the official Windows Python distribution.
- Profilers are intended to locate performance bottlenecks; use `timeit` instead for microbenchmarks.

## Building distributions

```bash
python -m pip install build
python -m build
```

`setup.py` describes only the platform-specific `_remote_debugging` C extension. Project metadata, Python package
discovery, and resource declarations are maintained in `pyproject.toml`. Because the extension depends on CPython
private APIs, wheels must be built separately for every supported Python minor version and platform.

## License and origin

The code is backported from CPython and distributed under the Python Software Foundation License Version 2 and the
third-party licenses listed in the repository's [`LICENSE`](LICENSE) file. Bundled frontend assets such as D3 and
d3-flame-graph retain their respective licenses.

This project is not an official Python Software Foundation distribution.
