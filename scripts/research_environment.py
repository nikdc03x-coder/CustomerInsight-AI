
"""Record the software environment used for CustomerInsight AI."""

from datetime import datetime, timezone
from pathlib import Path
import importlib.metadata
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/research_environment.md"

PACKAGES = [
    "numpy",
    "pandas",
    "scipy",
    "scikit-learn",
    "matplotlib",
    "plotly",
    "streamlit",
    "jupyterlab",
    "openpyxl",
    "nbformat",
    "nbclient",
    "ipykernel",
    "pytest",
]


def package_version(name):
    """Read the installed package version, when available."""
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "Not installed"


def main():
    """Create a Markdown record of the current Python environment."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# CustomerInsight AI — Research Environment",
        "",
        f"Generated (UTC): {timestamp}",
        "",
        "## System",
        "",
        f"- Python: {platform.python_version()}",
        f"- Platform: {platform.platform()}",
        f"- Executable: `{sys.executable}`",
        "",
        "## Python Libraries",
        "",
        "| Package | Installed version |",
        "|---|---|",
    ]

    for package in PACKAGES:
        lines.append(
            f"| {package} | {package_version(package)} |"
        )

    lines.extend([
        "",
        "## Reproducibility Notes",
        "",
        "This document records the environment used to execute",
        "the project's software and experiments.",
        "",
        "Package versions alone do not prove reproducibility.",
        "Original data, random seeds, preprocessing methods,",
        "experiment code and saved outputs are also required.",
        "",
    ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Environment report saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
