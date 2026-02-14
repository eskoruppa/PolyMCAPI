# PolyMC Python API

A lightweight Python interface for running Monte Carlo simulations with [PolyMC](https://github.com/eskoruppa/PolyMC).

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
