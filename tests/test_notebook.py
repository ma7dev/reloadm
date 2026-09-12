from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient


def test_example_notebook_executes() -> None:
    repository = Path(__file__).parents[1]
    notebook_path = repository / "examples" / "reloadm_demo.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4)

    NotebookClient(
        notebook,
        timeout=60,
        kernel_name="python3",
        resources={"metadata": {"path": str(repository)}},
    ).execute()
