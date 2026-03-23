# cli/src/ait/commands/update.py
import subprocess
from pathlib import Path

import typer
from rich.console import Console

from ait.core.config import DEFAULT_REPO_PATH

console = Console()


def update(
    repo_path: Path = typer.Option(DEFAULT_REPO_PATH, "--repo-path", help="Path to repo"),
) -> None:
    """Update the repo (git pull) and show what changed."""
    if not repo_path.is_dir():
        console.print(f"[red]Repo not found at {repo_path}. Run 'ait install' first.[/red]")
        raise typer.Exit(1)

    # Get current HEAD before pull
    old_head = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    # Pull
    subprocess.run(["git", "-C", str(repo_path), "pull", "--ff-only"], check=True)

    # Get new HEAD
    new_head = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    if old_head == new_head:
        console.print("[green]Already up to date.[/green]")
        return

    # Show changed files
    diff = subprocess.run(
        ["git", "-C", str(repo_path), "diff", "--name-status", old_head, new_head],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    console.print("[green]Updated. Changed files:[/green]")
    for line in diff.splitlines():
        console.print(f"  {line}")
