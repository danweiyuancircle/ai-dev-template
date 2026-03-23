from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ait.core.config import DEFAULT_REPO_PATH
from ait.core.registry import scan_resources

console = Console()


def list_resources(
    type: str | None = typer.Option(None, "--type", "-t", help="Filter by type (claude-rule, cursor-rule, skill, template, mcp)"),
    tag: str | None = typer.Option(None, "--tag", help="Filter by tag"),
    repo_path: Path = typer.Option(DEFAULT_REPO_PATH, "--repo-path", help="Path to repo"),
) -> None:
    """List all available resources."""
    if not repo_path.is_dir():
        console.print(f"[red]Repo not found at {repo_path}. Run 'ait install' first.[/red]")
        raise typer.Exit(1)

    resources = scan_resources(repo_path, type_filter=type, tag_filter=tag)
    if not resources:
        console.print("[yellow]No resources found.[/yellow]")
        return

    table = Table(title="Available Resources")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Version")
    table.add_column("Tags")
    table.add_column("Description")

    for r in resources:
        table.add_row(r.name, r.type, r.version, ", ".join(r.tags), r.description)

    console.print(table)
