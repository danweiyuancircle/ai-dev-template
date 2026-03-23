from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table

from ait.core.config import DEFAULT_REPO_PATH, PROFILES_DIR

console = Console()


def list_profiles(
    repo_path: Path = typer.Option(DEFAULT_REPO_PATH, "--repo-path", help="Path to repo"),
) -> None:
    """List all available profiles."""
    profiles_dir = repo_path / PROFILES_DIR
    if not profiles_dir.is_dir():
        console.print("[yellow]No profiles directory found.[/yellow]")
        return

    table = Table(title="Available Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Resources", style="green")

    for file in sorted(profiles_dir.glob("*.yaml")):
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
        name = file.stem
        desc = data.get("description", "")

        count = 0
        for key in ("rules", "skills", "templates", "mcp"):
            val = data.get(key)
            if isinstance(val, dict):
                count += sum(len(v) for v in val.values() if isinstance(v, list))
            elif isinstance(val, list):
                count += len(val)

        table.add_row(name, desc, str(count))

    console.print(table)
