# cli/src/ait/commands/install.py
import subprocess
from pathlib import Path

import typer
from rich.console import Console

from ait.core.config import DEFAULT_REPO_PATH, DEFAULT_REPO_URL, GLOBAL_TARGETS, RESOURCE_DIRS
from ait.core.linker import create_symlink

console = Console()


def install(
    repo_path: Path = typer.Option(DEFAULT_REPO_PATH, "--repo-path", help="Use an existing local repo instead of cloning"),
) -> None:
    """Clone the repo (or update if exists) and install global rules/skills."""
    # Step 1: Clone or update
    if repo_path == DEFAULT_REPO_PATH:
        if not repo_path.is_dir():
            console.print(f"Cloning repo to {repo_path}...")
            subprocess.run(["git", "clone", DEFAULT_REPO_URL, str(repo_path)], check=True)
            console.print("[green]Cloned successfully.[/green]")
        else:
            console.print(f"Repo exists at {repo_path}, pulling updates...")
            subprocess.run(["git", "-C", str(repo_path), "pull", "--ff-only"], check=True)
            console.print("[green]Updated.[/green]")

    if not repo_path.is_dir():
        console.print(f"[red]Repo path {repo_path} does not exist.[/red]")
        raise typer.Exit(1)

    # Step 2: Symlink global resources
    installed = 0
    for resource_type, target_dir in GLOBAL_TARGETS.items():
        source_dir = repo_path / RESOURCE_DIRS[resource_type]
        if not source_dir.is_dir():
            continue
        target_dir.mkdir(parents=True, exist_ok=True)

        for source_file in sorted(source_dir.iterdir()):
            if source_file.name.startswith(".") or not source_file.is_file():
                continue
            target = target_dir / source_file.name
            create_symlink(source_file, target)
            installed += 1
            console.print(f"  [green]✓[/green] {source_file.name} → {target}")

    console.print(f"\n[green]Installed {installed} global resources.[/green]")
