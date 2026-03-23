import json
from pathlib import Path

import typer
from rich.console import Console

from ait.core.config import CONFIG_FILENAME
from ait.core.linker import copy_file, create_symlink, merge_mcp
from ait.core.registry import find_resource, scan_resources

console = Console()


def sync(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
) -> None:
    """Rebuild all resources from .ai-rules.json (use after cloning on a new machine)."""
    project_dir = Path.cwd()
    config_path = project_dir / CONFIG_FILENAME

    if not config_path.exists():
        console.print(f"[red]{CONFIG_FILENAME} not found in current directory.[/red]")
        raise typer.Exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    repo_path = Path(config["repo"]).expanduser()

    if not repo_path.is_dir():
        console.print(f"[red]Repo not found at {repo_path}. Run 'ait install' first.[/red]")
        raise typer.Exit(1)

    all_resources = scan_resources(repo_path)
    synced = 0
    skipped = 0

    console.print("[bold]Syncing resources...[/bold]\n")

    for res_entry in config.get("resources", []):
        name = res_entry["name"]
        mode = res_entry["mode"]
        target = project_dir / res_entry["target"]

        resource = find_resource(all_resources, name)
        if not resource:
            console.print(f"  [red]✗ {name} — not found in repo[/red]")
            continue

        if mode == "symlink":
            if target.is_symlink() and target.resolve() == resource.file_path.resolve():
                skipped += 1
                continue
            create_symlink(resource.file_path, target)
            console.print(f"  [green]✓[/green] {name} → {target}")
            synced += 1

        elif mode == "copy":
            if target.exists() and not force:
                skipped += 1
                continue
            copy_file(resource.file_path, target, force=force)
            console.print(f"  [green]✓[/green] {name} → {target}")
            synced += 1

        elif mode == "merge":
            mcp_data = json.loads(resource.file_path.read_text(encoding="utf-8"))
            mcp_data.pop("_meta", None)
            added = merge_mcp(mcp_data, target)
            if added:
                console.print(f"  [green]✓[/green] {name} — merged {added}")
                synced += 1
            else:
                skipped += 1

    console.print(f"\n[green]Synced: {synced}, Skipped (already up-to-date): {skipped}[/green]")
