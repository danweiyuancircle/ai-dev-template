# cli/src/ait/commands/remove.py
import json
from pathlib import Path

import typer
from rich.console import Console

from ait.core.config import CONFIG_FILENAME
from ait.core.linker import remove_mcp_keys, remove_symlink

console = Console()


def remove(
    name: str = typer.Argument(help="Resource name to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation for copy-mode resources"),
) -> None:
    """Remove a resource from the current project."""
    project_dir = Path.cwd()
    config_path = project_dir / CONFIG_FILENAME

    if not config_path.exists():
        console.print(f"[red]{CONFIG_FILENAME} not found.[/red]")
        raise typer.Exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    resource_entry = next((r for r in config["resources"] if r["name"] == name), None)

    if not resource_entry:
        console.print(f"[red]Resource '{name}' not in current project.[/red]")
        raise typer.Exit(1)

    target = project_dir / resource_entry["target"]
    mode = resource_entry["mode"]

    if mode == "symlink":
        if remove_symlink(target):
            console.print(f"[green]✓[/green] Removed symlink: {target}")
        else:
            console.print(f"[yellow]Symlink not found: {target}[/yellow]")

    elif mode == "copy":
        if target.exists():
            if not force:
                confirm = typer.confirm(f"{target} may have been modified. Delete it?")
                if not confirm:
                    console.print("Skipped.")
                    return
            target.unlink()
            console.print(f"[green]✓[/green] Removed: {target}")

    elif mode == "merge":
        merged_keys = resource_entry.get("merged_keys", [])
        if merged_keys:
            remove_mcp_keys(target, merged_keys)
            console.print(f"[green]✓[/green] Removed MCP keys: {merged_keys}")
        else:
            console.print("[yellow]No merged keys to remove.[/yellow]")

    config["resources"] = [r for r in config["resources"] if r["name"] != name]

    from ait.core.project import save_project_config
    save_project_config(project_dir, config)
    console.print(f"[green]Removed '{name}' from {CONFIG_FILENAME}[/green]")
