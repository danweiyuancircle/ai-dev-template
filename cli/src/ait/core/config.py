from pathlib import Path

# Central repo location
DEFAULT_REPO_URL = "https://github.com/danweiyuancircle/ai-dev-template.git"
DEFAULT_REPO_PATH = Path.home() / ".ai-dev-template"

# Resource source directories (relative to repo root)
RESOURCE_DIRS: dict[str, str] = {
    "claude-rule": "rules/claude",
    "cursor-rule": "rules/cursor",
    "skill": "skills",
    "template": "templates",
    "mcp": "mcp",
}

# Global install targets (absolute paths)
GLOBAL_TARGETS: dict[str, Path] = {
    "claude-rule": Path.home() / ".claude" / "rules",
    "skill": Path.home() / ".claude" / "skills",
}

# Project-level install targets (relative to project root)
PROJECT_TARGETS: dict[str, str] = {
    "claude-rule": ".claude/rules",
    "cursor-rule": ".cursor/rules",
    "skill": ".claude/skills",
    "template": ".",
    "mcp": ".claude",
}

# Install modes by type
INSTALL_MODES: dict[str, str] = {
    "claude-rule": "symlink",
    "cursor-rule": "symlink",
    "skill": "symlink",
    "template": "copy",
    "mcp": "merge",
}

VALID_TYPES = set(RESOURCE_DIRS.keys())

CONFIG_FILENAME = ".ai-rules.json"
PROFILES_DIR = "profiles"
