# cli/src/ait/commands/status.py
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ait.core.config import CONFIG_FILENAME, DEFAULT_REPO_PATH, GLOBAL_TARGETS

console = Console()


def status(
    repo_path: Path = typer.Option(DEFAULT_REPO_PATH, "--repo-path", help="Path to repo"),
) -> None:
    """Show installation status (global + project)."""
    console.print("[bold]Global Status[/bold]\n")

    if repo_path.is_dir():
        console.print(f"  Repo: [green]{repo_path}[/green]")
    else:
        console.print(f"  Repo: [red]Not found at {repo_path}[/red]")

    for resource_type, target_dir in GLOBAL_TARGETS.items():
        if not target_dir.is_dir():
            continue
        console.print(f"\n  [cyan]{resource_type}[/cyan] ({target_dir}):")
        for item in sorted(target_dir.iterdir()):
            if item.name.startswith("."):
                continue
            if item.is_symlink():
                resolved = item.resolve()
                if resolved.exists():
                    console.print(f"    [green]✓[/green] {item.name} → {resolved}")
                else:
                    console.print(f"    [red]✗[/red] {item.name} → {resolved} [BROKEN]")
            else:
                console.print(f"    [yellow]○[/yellow] {item.name} (regular file, not managed)")

    project_dir = Path.cwd()
    config_path = project_dir / CONFIG_FILENAME

    if config_path.exists():
        console.print(f"\n[bold]Project Status[/bold] ({project_dir})\n")
        config = json.loads(config_path.read_text(encoding="utf-8"))

        profile = config.get("profile")
        if profile:
            console.print(f"  Profile: [cyan]{profile}[/cyan]")

        table = Table()
        table.add_column("Resource", style="cyan")
        table.add_column("Type")
        table.add_column("Mode")
        table.add_column("Status")

        for res in config.get("resources", []):
            target = project_dir / res["target"]
            if res["mode"] == "symlink":
                if target.is_symlink() and target.resolve().exists():
                    st = "[green]OK[/green]"
                elif target.is_symlink():
                    st = "[red]BROKEN[/red]"
                else:
                    st = "[red]MISSING[/red]"
            elif res["mode"] == "copy":
                st = "[green]OK[/green]" if target.exists() else "[red]MISSING[/red]"
            else:
                st = "[green]OK[/green]" if target.exists() else "[yellow]NOT MERGED[/yellow]"

            table.add_row(res["name"], res["type"], res["mode"], st)

        console.print(table)
    else:
        console.print(f"\n[dim]No {CONFIG_FILENAME} in current directory.[/dim]")
