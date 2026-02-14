# PolyMC Python API

A lightweight Python interface for running [PolyMC](https://github.com/eskoruppa/PolyMC) simulations programmatically. Designed for adaptive workflows where simulation parameters are chosen iteratively based on prior results.

PolyMC is a Monte Carlo simulation package for semiflexible polymers, supporting sequence-dependent simulations of DNA at the rigid base pair level.

## Requirements

- Python 3.10+
- A compiled PolyMC executable
- No external Python dependencies (standard library only)

## Installation

Copy `polymc.py` into your project or add it to your Python path:

```bash
cp polymc.py /path/to/your/project/
```

## Quick Start

```python
from polymc import PolyMC

# Initialize with path to executable
sim = PolyMC("./PolyMC")
print(sim)  # PolyMC(exec_file='./PolyMC', version='0.73')

# Run a simulation
result = sim.run(
    input_file="input.in",
    output_dir="output/run_001",
    params={"num_bp": 101, "force": 2.0, "T": 300, "sequence": "seq.seq"},
)

if result["success"]:
    print(f"Done in {result['elapsed_time']:.1f}s")
```

## API Reference

### `PolyMC(exec_file)`

Constructor. Validates the executable by running it without arguments and checking for the `PolyMC version` string in the output.

| Parameter   | Type  | Description                                      |
|-------------|-------|--------------------------------------------------|
| `exec_file` | `str` | Path to the PolyMC executable (absolute or relative). |

**Attributes:**

| Attribute   | Type  | Description                          |
|-------------|-------|--------------------------------------|
| `exec_file` | `str` | Path to the executable.              |
| `version`   | `str` | Parsed PolyMC version (e.g. `"0.73"`). |

**Raises** `PolyMCExecutableError` if the file is missing, not executable, or not a valid PolyMC binary.

---

### `run(input_file, output_dir, params=None, timeout=None, capture_output=False, dry_run=False, raise_on_failure=False)`

Executes a PolyMC simulation as a blocking subprocess.

**Parameters:**

| Parameter          | Type             | Default | Description                                                                                          |
|--------------------|------------------|---------|------------------------------------------------------------------------------------------------------|
| `input_file`       | `str`            | —       | Path to the `.in` input file.                                                                        |
| `output_dir`       | `str`            | —       | Base output path passed to `-dir`. PolyMC creates the directory and uses this as the basename for all output files. |
| `params`           | `dict` or `None` | `None`  | Simulation parameters forwarded as command-line flags (see [Parameter Dictionary](#parameter-dictionary)). |
| `timeout`          | `float` or `None`| `None`  | Maximum wall-clock time in seconds. Process is killed if exceeded.                                   |
| `capture_output`   | `bool`           | `False` | Include stdout/stderr in the result dictionary.                                                      |
| `dry_run`          | `bool`           | `False` | Build and return the command without executing.                                                      |
| `raise_on_failure` | `bool`           | `False` | Raise `PolyMCError` on failure instead of returning `success=False`.                                 |

**Returns** a dictionary:

| Key             | Type            | Description                                            |
|-----------------|-----------------|--------------------------------------------------------|
| `"success"`     | `bool`          | `True` if the expected output file was created.        |
| `"elapsed_time"`| `float`         | Wall-clock time in seconds (`0.0` for dry runs).       |
| `"output_base"` | `str`           | The `output_dir` value passed to `-dir`.               |
| `"command"`     | `str`           | The full command string.                               |
| `"stdout"`      | `str` or `None` | Process stdout (only if `capture_output=True`).        |
| `"stderr"`      | `str` or `None` | Process stderr (only if `capture_output=True`).        |

**Success criterion:** The file `output_dir + ".in"` exists after the process completes. This is the copy of the input file that PolyMC writes to the output directory.

---

### Parameter Dictionary

The `params` dictionary is converted to command-line flags:

```python
# Key-value pairs become: -key value
params = {"num_bp": 101, "T": 300, "force": 2.5}
# → -num_bp 101 -T 300 -force 2.5

# None values become boolean flags: -key (no value)
params = {"EV": None}
# → -EV

# IDB and sequence files are passed like any other parameter
params = {"IDB": "TWLC.idb", "sequence": "myseq.seq", "num_bp": 101}
```

Command-line flags always take precedence over values in the input file, matching PolyMC's native behavior.

---

### Exceptions

| Exception                | Description                                             |
|--------------------------|---------------------------------------------------------|
| `PolyMCError`            | Base exception for all API errors.                      |
| `PolyMCExecutableError`  | Raised when the executable is invalid (subclass of `PolyMCError`). |

## Usage Examples

### Basic Simulation

```python
from polymc import PolyMC

sim = PolyMC("/path/to/PolyMC")

result = sim.run(
    input_file="config/base.in",
    output_dir="output/test_001",
    params={
        "num_bp": 101,
        "T": 300,
        "force": 2.0,
        "steps": 1000000,
        "IDB": "TWLC.idb",
        "sequence": "seq",
    },
)
print(result["command"])
```

### Dry Run

Inspect the command without running the simulation:

```python
result = sim.run(
    input_file="config/base.in",
    output_dir="output/test",
    params={"num_bp": 200, "force": 5.0},
    dry_run=True,
)
print(result["command"])
# /path/to/PolyMC -in config/base.in -dir output/test -num_bp 200 -force 5.0
```

### With Timeout and Output Capture

```python
result = sim.run(
    input_file="config/base.in",
    output_dir="output/long_run",
    params={"steps": 500000000},
    timeout=3600,           # kill after 1 hour
    capture_output=True,    # capture terminal output
)

if not result["success"]:
    print(f"Failed after {result['elapsed_time']:.0f}s")
    print(result["stderr"])
```

### Adaptive Workflow

The primary use case — iteratively choosing parameters based on results:

```python
from polymc import PolyMC

sim = PolyMC("./PolyMC")

force = 0.0
for i in range(20):
    result = sim.run(
        input_file="config/base.in",
        output_dir=f"output/adaptive/run_{i:03d}",
        params={"num_bp": 101, "force": force},
    )
    if not result["success"]:
        print(f"Run {i} failed")
        break

    # Analyze output and decide next parameters
    force = analyze_and_update(result["output_base"])
```

### Parameter Sweep

```python
import itertools

forces = [0.0, 1.0, 2.0, 5.0]
temperatures = [280, 300, 320]

for force, temp in itertools.product(forces, temperatures):
    tag = f"f{force}_T{temp}"
    result = sim.run(
        input_file="config/base.in",
        output_dir=f"output/sweep/{tag}",
        params={"force": force, "T": temp},
    )
    print(f"{tag}: {'OK' if result['success'] else 'FAIL'} ({result['elapsed_time']:.1f}s)")
```

## How It Works

The API is a thin wrapper around `subprocess.run`. It does not modify input files. The workflow is:

1. **Constructor** validates the executable by running it without arguments and parsing the version string from the output.
2. **`run()`** constructs a command of the form:
   ```
   {exec_file} -in {input_file} -dir {output_dir} [-key value ...] [-flag ...]
   ```
3. The command is executed as a blocking subprocess.
4. After completion, the API checks for the existence of `{output_dir}.in` (the input file copy that PolyMC writes to the output directory) to determine success.

## License

MIT
