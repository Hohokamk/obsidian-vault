#!/usr/bin/env python3
"""Run the offline validation suite for the teaching starter code."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "validation_output"


def run(name: str, args: list[str], cwd: Path) -> None:
    print(f"\n== {name} ==")
    print(" ".join(args))
    completed = subprocess.run(args, cwd=cwd, check=False, text=True)
    if completed.returncode != 0:
        raise SystemExit(f"{name} failed with code {completed.returncode}")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    run("pytest", [sys.executable, "-m", "pytest", "code/tests", "-q"], ROOT)
    run("compileall", [sys.executable, "-m", "compileall", "-q", "code"], ROOT)
    run(
        "protocol dry-run",
        [sys.executable, "arrayctl.py", "--dry-run", "one", "--row", "3", "--col", "5"],
        ROOT / "code/host",
    )
    run(
        "mapping generation",
        [
            sys.executable,
            "code/automation/generate_mapping.py",
            "code/config/array_config.yaml",
            "--out",
            str(OUT / "mapping"),
        ],
        ROOT,
    )
    simulation_cwd = OUT / "simulation"
    simulation_cwd.mkdir()
    run(
        "array-factor demonstration",
        [sys.executable, str(ROOT / "code/simulation/demo.py")],
        simulation_cwd,
    )
    print(f"\nValidation outputs: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
