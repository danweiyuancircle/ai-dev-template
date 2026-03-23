# cli/src/ait/commands/add.py
import json
from pathlib import Path

import typer
from rich.console import Console

from ait.core.config import CONFIG_FILENAME, DEFAULT_REPO_PATH, INSTALL_MODES, PROJECT_TARGETS
from ait.core.linker import copy_file, create_symlink, merge_mcp
from ait.core.registry import find_resource, scan_resources

console = Console()


def add(
    name: str = typer.Argument(help="Resource name to add"),
    repo_path: Path = typer.Option(DEFAULT_REPO_PATH, "--repo-path", help="Path to repo"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
) -> None:
    """Add a single resource to the current project."""
    if not repo_path.is_dir():
        console.print(f"[red]Repo not found at {repo_path}. Run 'ait install' first.[/red]")
        raise typer.Exit(1)

    resources = scan_resources(repo_path)
    resource = find_resource(resources, name)

    if not resource:
        similar = [r.name for r in resources if name.lower() in r.name.lower()]
        console.print(f"[red]Resource '{name}' not found.[/red]")
        if similar:
            console.print(f"Did you mean: {', '.join(similar)}?")
        raise typer.Exit(1)

    project_dir = Path.cwd()
    mode = INSTALL_MODES[resource.type]
    target_dir = PROJECT_TARGETS[resource.type]

    entry: dict | None = None

    if mode == "symlink":
        target = project_dir / target_dir / resource.file_path.name
        create_symlink(resource.file_path, target)
        console.print(f"[green]✓[/green] {resource.name} → {target}")
        entry = {
            "name": resource.name,
            "type": resource.type,
            "version": resource.version,
            "target": str(Path(target_dir) / resource.file_path.name),
            "mode": "symlink",
        }

    elif mode == "copy":
        target = project_dir / "CLAUDE.md"
        was_copied = copy_file(resource.file_path, target, force=force)
        if not was_copied:
            console.print(f"[yellow]{target} already exists. Use --force to overwrite.[/yellow]")
            raise typer.Exit(1)
        console.print(f"[green]✓[/green] {resource.name} → {target}")
        entry = {
            "name": resource.name,
            "type": resource.type,
            "version": resource.version,
            "target": "CLAUDE.md",
            "mode": "copy",
        }

    elif mode == "merge":
        mcp_data = json.loads(resource.file_path.read_text(encoding="utf-8"))
        mcp_data.pop("_meta", None)
        target = project_dir / target_dir / "mcp.json"
        added_keys = merge_mcp(mcp_data, target)
        all_source_keys = list(mcp_data.get("mcpServers", {}).keys())
        console.print(f"[green]✓[/green] {resource.name} — merged {added_keys}")
        entry = {
            "name": resource.name,
            "type": resource.type,
            "version": resource.version,
            "target": str(Path(target_dir) / "mcp.json"),
            "mode": "merge",
            "merged_keys": all_source_keys,
        }

    if entry:
        config_path = project_dir / CONFIG_FILENAME
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
        else:
            config = {"profile": None, "resources": [], "repo": str(repo_path)}

        config["resources"] = [r for r in config["resources"] if r["name"] != resource.name]
        config["resources"].append(entry)

        from ait.core.project import ensure_gitignore, save_project_config
        save_project_config(project_dir, config)
        ensure_gitignore(project_dir)
