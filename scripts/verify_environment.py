"""Verify the active Python runtime and ORS runtime dependencies."""
from __future__ import annotations

import argparse
import importlib.metadata
import sys

REQUIRED_DISTRIBUTIONS = (
    "fastapi",
    "uvicorn",
    "pydantic",
    "numpy",
    "scipy",
    "pandas",
    "openpyxl",
    "XlsxWriter",
    "python-multipart",
    "reportlab",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--python-series",
        default="3.15",
        help="Required Python major.minor series (default: 3.15).",
    )
    args = parser.parse_args()
    expected = tuple(int(part) for part in args.python_series.split("."))
    actual = sys.version_info[: len(expected)]

    print(f"Python runtime: {sys.version.split()[0]}")
    if actual != expected:
        print(f"ERROR: expected Python {args.python_series}.x, got {sys.version.split()[0]}")
        return 1

    failures: list[str] = []
    for distribution in REQUIRED_DISTRIBUTIONS:
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            failures.append(f"{distribution}: not installed")
            continue
        print(f"OK  {distribution} {version}")

    # Import native/scientific packages too; metadata alone cannot detect a broken wheel.
    import_checks = (
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("xlsxwriter", "xlsxwriter"),
        ("python-multipart", "multipart"),
        ("reportlab", "reportlab"),
    )
    for distribution, module in import_checks:
        try:
            __import__(module)
        except Exception as exc:  # Report import/ABI problems clearly to the user.
            failures.append(f"{distribution}: import failed ({type(exc).__name__}: {exc})")

    if failures:
        print("\nEnvironment verification FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nEnvironment verification PASSED. ORS dependencies can be imported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
