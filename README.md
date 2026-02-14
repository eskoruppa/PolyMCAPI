# PolyMC Python API

A lightweight Python interface for running Monte Carlo simulations with [PolyMC](https://github.com/eskoruppa/PolyMC).

PolyMC is a Monte Carlo simulation package for semiflexible polymers, supporting sequence-dependent simulations of DNA at the rigid base pair level.

## Requirements

- Python 3.10+
- A compiled PolyMC executable
- No external Python dependencies (standard library only)

## Installation

### From Source

Clone this repository and install with pip:

```bash
git clone https://github.com/eskoruppa/PolyMCAPI
cd PolyMCAPI
pip install -e .
```

The `-e` flag installs in editable mode, which is useful for development.

For a regular installation:

```bash
pip install .
```

### From GitHub (Direct)

Install directly from GitHub without cloning:

```bash
pip install git+https://github.com/eskoruppa/PolyMCAPI.git
```

### Usage After Installation

Once installed, you can import the package from anywhere:

```python
from polymcapi import PolyMC
```

## Quick Start

```python
from polymcapi import PolyMC

# Initialize with path to executable
sim = PolyMC("./example/PolyMC")
print(sim)  # PolyMC(exec_file='./example/PolyMC', version='0.73')

# Run a simulation
result = sim.run(
    input_file="example/input",
    output_dir="example/output/run_001",
    params={
        "num_bp": 101,
        "idb": "example/TWLC.idb",
        "seq": "example/seq",
        "steps": 400000,
        "equi": 0,
        "XYZn": 1000
    },
)

if result["success"]:
    print(f"Done in {result['elapsed_time']:.1f}s")
```

See [example.py](example.py) for a complete working example.

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
params = {
    "idb": "TWLC.idb",
    "seq": "myseq.seq",
    "num_bp": 101,
    "steps": 400000,
    "equi": 0,
    "XYZn": 1000
}
# → -idb TWLC.idb -seq myseq.seq -num_bp 101 -steps 400000 -equi 0 -XYZn 1000
```

## Project Structure

```
PolyMCAPI/
├── polymcapi/
│   ├── __init__.py      # Package initialization
│   └── polymc.py        # Main PolyMC class implementation
├── example/
│   ├── PolyMC           # PolyMC executable
│   ├── input            # Input configuration file
│   ├── seq              # DNA sequence file
│   └── TWLC.idb         # IDB parameter file
├── example.py           # Complete working example
├── pyproject.toml       # Package metadata and build configuration
├── setup.py             # Setup script (for backwards compatibility)
├── MANIFEST.in          # Files to include in source distribution
├── README.md            # This file
└── LICENSE              # License information
```

## Exception Handling

The API defines two exception types:

- **`PolyMCError`**: Base exception for all PolyMC API errors.
- **`PolyMCExecutableError`**: Raised when the executable is not found, not executable, or not a valid PolyMC binary.

Use `raise_on_failure=True` to have the `run()` method raise exceptions on simulation failures:

```python
try:
    result = sim.run(
        input_file="input",
        output_dir="output/run_001",
        params={"num_bp": 101},
        raise_on_failure=True
    )
except PolyMCError as e:
    print(f"Simulation failed: {e}")
```

**Note:** Command-line flags always take precedence over values in the input file, matching PolyMC's native behavior.

## Development

### Setting Up a Development Environment

Clone the repository and install in editable mode:

```bash
git clone https://github.com/eskoruppa/PolyMCAPI
cd PolyMCAPI
pip install -e .
```

This allows you to make changes to the code and test them immediately without reinstalling.

### Building a Distribution

To build source and wheel distributions:

```bash
pip install build
python -m build
```

This creates distribution files in the `dist/` directory.

### Running the Example

The included example demonstrates the API:

```bash
python example.py
```

Note: You need a compiled PolyMC executable in the `example/` directory for this to work.

## License

This project is licensed under the GNU General Public License v2.0. See [LICENSE](LICENSE) for details.
