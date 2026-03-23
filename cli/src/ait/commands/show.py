from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from ait.core.config import DEFAULT_REPO_PATH
from ait.core.registry import scan_resources, find_resource

console = Console()


def show_resource(
    name: str = typer.Argument(help="Resource name"),
    repo_path: Path = typer.Option(DEFAULT_REPO_PATH, "--repo-path", help="Path to repo"),
) -> None:
    """Show details of a specific resource."""
    if not repo_path.is_dir():
        console.print(f"[red]Repo not found at {repo_path}. Run 'ait install' first.[/red]")
        raise typer.Exit(1)

    resources = scan_resources(repo_path)
    resource = find_resource(resources, name)
    if not resource:
        console.print(f"[red]Resource '{name}' not found.[/red]")
        raise typer.Exit(1)

    info = (
        f"[cyan]Name:[/cyan] {resource.name}\n"
        f"[cyan]Type:[/cyan] {resource.type}\n"
        f"[cyan]Version:[/cyan] {resource.version}\n"
        f"[cyan]Author:[/cyan] {resource.author}\n"
        f"[cyan]Tags:[/cyan] {', '.join(resource.tags)}\n"
        f"[cyan]File:[/cyan] {resource.file_path}"
    )
    console.print(Panel(info, title=resource.description))

    if resource.content:
        console.print("\n[bold]Content preview:[/bold]")
        preview = "\n".join(resource.content.splitlines()[:30])
        console.print(Syntax(preview, "markdown", theme="monokai"))
