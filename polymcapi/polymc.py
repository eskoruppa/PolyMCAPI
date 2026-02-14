"""
PolyMC Python API
=================
A lightweight Python interface for running PolyMC simulations.

PolyMC is a Monte Carlo simulation package for semiflexible polymers,
supporting sequence-dependent simulations of DNA at the rigid base pair level.

This module provides the `PolyMC` class, which wraps the PolyMC executable
and allows simulations to be configured and launched from Python, with 
support for adaptive parameter selection workflows.

Example
-------
    from polymc import PolyMC

    sim = PolyMC("./PolyMC")
    result = sim.run(
        input_file="input.in",
        output_dir="output/run01",
        params={"num_bp": 101, "force": 2.0, "T": 300},
    )
    if result["success"]:
        print(f"Simulation completed in {result['elapsed_time']:.1f}s")
"""

from __future__ import annotations

import os
import re
import subprocess
import time
from typing import Optional


class PolyMCError(Exception):
    """Base exception for PolyMC API errors."""
    pass


class PolyMCExecutableError(PolyMCError):
    """Raised when the PolyMC executable is invalid or not found."""
    pass


class PolyMC:
    """Python interface for running PolyMC simulations.

    Parameters
    ----------
    exec_file : str
        Path to the PolyMC executable (absolute or relative).

    Attributes
    ----------
    exec_file : str
        Path to the PolyMC executable.
    version : str
        Version string of the PolyMC executable, parsed during construction.

    Raises
    ------
    PolyMCExecutableError
        If the executable is not found, not executable, or does not
        appear to be a valid PolyMC binary.
    """

    def __init__(self, exec_file: str):
        self.exec_file = exec_file
        self.version = self._validate_executable()

    def _validate_executable(self) -> str:
        """Validate the PolyMC executable and return its version string.

        Runs the executable with no arguments and checks for the expected
        version output. This confirms that the file exists, is executable,
        and is indeed a PolyMC binary.

        Returns
        -------
        str
            The PolyMC version string (e.g. "0.73").

        Raises
        ------
        PolyMCExecutableError
            If validation fails for any reason.
        """
        if not os.path.isfile(self.exec_file):
            raise PolyMCExecutableError(
                f"Executable not found: {self.exec_file}"
            )
        if not os.access(self.exec_file, os.X_OK):
            raise PolyMCExecutableError(
                f"File is not executable: {self.exec_file}"
            )

        try:
            result = subprocess.run(
                [self.exec_file],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            raise PolyMCExecutableError(
                f"Executable timed out during validation: {self.exec_file}"
            )
        except OSError as e:
            raise PolyMCExecutableError(
                f"Failed to run executable: {self.exec_file}\n{e}"
            )

        # Check both stdout and stderr for the version string
        combined_output = result.stdout + result.stderr
        match = re.search(r"PolyMC version:\s*(\S+)", combined_output)
        if not match:
            raise PolyMCExecutableError(
                f"Executable does not appear to be PolyMC "
                f"(no version string found): {self.exec_file}\n"
                f"Output was:\n{combined_output}"
            )
        return match.group(1)

    def _build_command(
        self,
        input_file: str,
        output_dir: str,
        params: Optional[dict] = None,
    ) -> list[str]:
        """Build the command as a list of arguments.

        Parameters
        ----------
        input_file : str
            Path to the input file.
        output_dir : str
            Base output path passed to -dir.
        params : dict, optional
            Additional simulation parameters.

        Returns
        -------
        list of str
            The command as a list suitable for subprocess.
        """
        cmd = [self.exec_file, "-in", input_file, "-dir", output_dir]
        if params:
            for key, value in params.items():
                cmd.append(f"-{key}")
                if value is not None:
                    cmd.append(str(value))
        return cmd

    @staticmethod
    def _command_string(cmd: list[str]) -> str:
        """Convert a command list to a human-readable string.

        Parameters
        ----------
        cmd : list of str
            Command as a list of arguments.

        Returns
        -------
        str
            The command as a single string.
        """
        parts = []
        for part in cmd:
            if " " in part:
                parts.append(f'"{part}"')
            else:
                parts.append(part)
        return " ".join(parts)

    def run(
        self,
        input_file: str,
        output_dir: str,
        params: Optional[dict] = None,
        timeout: Optional[float] = None,
        capture_output: bool = False,
        dry_run: bool = False,
        raise_on_failure: bool = False,
    ) -> dict:
        """Run a PolyMC simulation.

        Constructs the command line from the provided input file, output
        directory, and parameter dictionary, then executes the simulation
        as a blocking subprocess.

        Parameters
        ----------
        input_file : str
            Path to the PolyMC input file (.in).
        output_dir : str
            Base output path passed to PolyMC via -dir. PolyMC creates
            the directory if needed and uses this as the basename for
            all output files.
        params : dict, optional
            Simulation parameters as ``{key: value}`` pairs, forwarded
            as command-line flags ``-key value``. A ``None`` value produces
            a boolean flag (``-key`` with no value).
        timeout : float, optional
            Maximum wall-clock time in seconds. If exceeded, the process
            is killed and the run is marked as unsuccessful. Default is
            ``None`` (no limit).
        capture_output : bool, optional
            If ``True``, stdout and stderr are included in the result
            dictionary. Default is ``False``.
        dry_run : bool, optional
            If ``True``, build and return the command without executing
            the simulation. Default is ``False``.
        raise_on_failure : bool, optional
            If ``True``, raise a ``PolyMCError`` when the simulation
            fails (non-zero exit code, timeout, or missing output).
            Default is ``False``.

        Returns
        -------
        dict
            A dictionary with the following keys:

            - **success** (*bool*): ``True`` if the expected output file
              (``output_dir + '.in'``) was created.
            - **elapsed_time** (*float*): Wall-clock time in seconds
              (``0.0`` if ``dry_run``).
            - **output_base** (*str*): The ``output_dir`` value, i.e. the
              base path for all output files.
            - **command** (*str*): The full command string.
            - **stdout** (*str or None*): Process stdout, only if
              ``capture_output=True``.
            - **stderr** (*str or None*): Process stderr, only if
              ``capture_output=True``.

        Raises
        ------
        PolyMCError
            If ``raise_on_failure=True`` and the simulation fails.
        """
        cmd = self._build_command(input_file, output_dir, params)
        command_str = self._command_string(cmd)

        result = {
            "success": False,
            "elapsed_time": 0.0,
            "output_base": output_dir,
            "command": command_str,
            "stdout": None,
            "stderr": None,
        }

        if dry_run:
            return result

        # Run the simulation
        stdout_text = ""
        stderr_text = ""
        timed_out = False

        t_start = time.time()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout_text = proc.stdout
            stderr_text = proc.stderr
        except subprocess.TimeoutExpired as e:
            timed_out = True
            stdout_text = e.stdout or ""
            stderr_text = e.stderr or ""
        finally:
            elapsed = time.time() - t_start

        result["elapsed_time"] = elapsed

        if capture_output:
            result["stdout"] = stdout_text
            result["stderr"] = stderr_text

        expected_output = output_dir + ".in"
        result["success"] = os.path.isfile(expected_output)

        if not result["success"] and raise_on_failure:
            if timed_out:
                msg = (
                    f"Simulation timed out after {timeout:.0f}s.\n"
                    f"Command: {command_str}"
                )
            else:
                msg = (
                    f"Simulation failed (output not created).\n"
                    f"Command: {command_str}"
                )
                if stderr_text:
                    msg += f"\nstderr: {stderr_text}"
            raise PolyMCError(msg)

        return result

    def __repr__(self) -> str:
        return f"PolyMC(exec_file={self.exec_file!r}, version={self.version!r})"