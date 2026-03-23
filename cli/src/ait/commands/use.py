from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml
from rich.console import Console

from ait.core.config import (
    CONFIG_FILENAME,
    DEFAULT_REPO_PATH,
    INSTALL_MODES,
    PROFILES_DIR,
    PROJECT_TARGETS,
)
from ait.core.linker import copy_file, create_symlink, merge_mcp, remove_mcp_keys, remove_symlink
from ait.core.project import ensure_gitignore, load_project_config, save_project_config
from ait.core.registry import find_resource, scan_resources

console = Console()


def _cleanup_old_resources(project_dir: Path, old_config: dict, new_names: set[str]) -> None:
    """Remove resources from old config that are not in the new profile."""
    for res in old_config.get("resources", []):
        if res["name"] in new_names:
            continue
        target = project_dir / res["target"]
        mode = res["mode"]
        if mode == "symlink":
            remove_symlink(target)
            console.print(f"  [dim]Cleaned up: {target}[/dim]")
        elif mode == "copy":
            if target.exists():
                target.unlink()
                console.print(f"  [dim]Cleaned up: {target}[/dim]")
        elif mode == "merge":
            merged_keys = res.get("merged_keys", [])
            if merged_keys:
                remove_mcp_keys(target, merged_keys)
                console.print(f"  [dim]Cleaned up MCP keys: {merged_keys}[/dim]")


def _install_resource(
    resource_name: str,
    resource_type: str,
    repo_path: Path,
    project_dir: Path,
    resources: list,
    *,
    force: bool = False,
) -> dict | None:
    """Install a single resource. Returns resource entry for .ai-rules.json or None."""
    resource = find_resource(resources, resource_name)
    if not resource:
        console.print(f"  [red]✗ Resource '{resource_name}' not found[/red]")
        return None

    # Validate resource type matches what the profile expects
    if resource.type != resource_type:
        console.print(
            f"  [red]✗ '{resource_name}' is type '{resource.type}' but profile expects '{resource_type}'[/red]"
        )
        return None

    mode = INSTALL_MODES[resource_type]
    target_dir = PROJECT_TARGETS[resource_type]

    if mode == "symlink":
        target = project_dir / target_dir / resource.file_path.name
        create_symlink(resource.file_path, target)
        console.print(f"  [green]✓[/green] {resource.name} → {target}")
        return {
            "name": resource.name,
            "type": resource_type,
            "version": resource.version,
            "target": str(Path(target_dir) / resource.file_path.name),
            "mode": "symlink",
        }

    elif mode == "copy":
        target = project_dir / "CLAUDE.md"
        was_copied = copy_file(resource.file_path, target, force=force, strip_frontmatter=True)
        if was_copied:
            console.print(f"  [green]✓[/green] {resource.name} → {target}")
        else:
            console.print(f"  [yellow]⊘[/yellow] {target} already exists (use --force to overwrite)")
            return None
        return {
            "name": resource.name,
            "type": resource_type,
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
        if added_keys:
            console.print(f"  [green]✓[/green] {resource.name} → merged {added_keys} into {target}")
        else:
            console.print(f"  [yellow]⊘[/yellow] {resource.name} — all keys already exist")
        return {
            "name": resource.name,
            "type": resource_type,
            "version": resource.version,
            "target": str(Path(target_dir) / "mcp.json"),
            "mode": "merge",
            "merged_keys": all_source_keys,
        }

    return None


def use(
    profile_name: str = typer.Argument(help="Profile name (matches profiles/<name>.yaml)"),
    repo_path: Path = typer.Option(DEFAULT_REPO_PATH, "--repo-path", help="Path to repo"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files without asking"),
) -> None:
    """Configure current project using a profile."""
    if not repo_path.is_dir():
        console.print(f"[red]Repo not found at {repo_path}. Run 'ait install' first.[/red]")
        raise typer.Exit(1)

    profile_path = repo_path / PROFILES_DIR / f"{profile_name}.yaml"
    if not profile_path.exists():
        console.print(f"[red]Profile '{profile_name}' not found at {profile_path}[/red]")
        raise typer.Exit(1)

    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    project_dir = Path.cwd()

    # Validate: max 1 template
    templates = profile.get("templates", [])
    if len(templates) > 1:
        console.print("[red]Profile has multiple templates — only 1 allowed.[/red]")
        raise typer.Exit(1)

    # Collect all resource names the new profile wants
    new_names: set[str] = set()
    rules = profile.get("rules", {})
    for rule_list in rules.values():
        new_names.update(rule_list)
    for key in ("skills", "templates", "mcp"):
        new_names.update(profile.get(key, []))

    # Cleanup old profile resources
    old_config = load_project_config(project_dir)
    if old_config:
        _cleanup_old_resources(project_dir, old_config, new_names)

    # Scan all resources from repo
    all_resources = scan_resources(repo_path)

    console.print(f"\n[bold]Applying profile: {profile_name}[/bold]\n")

    installed: list[dict] = []

    # Install claude rules
    for name in rules.get("claude", []):
        entry = _install_resource(name, "claude-rule", repo_path, project_dir, all_resources, force=force)
        if entry:
            installed.append(entry)

    # Install cursor rules
    for name in rules.get("cursor", []):
        entry = _install_resource(name, "cursor-rule", repo_path, project_dir, all_resources, force=force)
        if entry:
            installed.append(entry)

    # Install skills
    for name in profile.get("skills", []):
        entry = _install_resource(name, "skill", repo_path, project_dir, all_resources, force=force)
        if entry:
            installed.append(entry)

    # Install templates
    for name in templates:
        entry = _install_resource(name, "template", repo_path, project_dir, all_resources, force=force)
        if entry:
            installed.append(entry)

    # Install MCP
    for name in profile.get("mcp", []):
        entry = _install_resource(name, "mcp", repo_path, project_dir, all_resources, force=force)
        if entry:
            installed.append(entry)

    # Save config
    config = {
        "profile": profile_name,
        "resources": installed,
        "repo": str(repo_path),
    }
    save_project_config(project_dir, config)
    ensure_gitignore(project_dir)

    console.print(f"\n[green]Done. {len(installed)} resources installed. Config saved to {CONFIG_FILENAME}[/green]")
