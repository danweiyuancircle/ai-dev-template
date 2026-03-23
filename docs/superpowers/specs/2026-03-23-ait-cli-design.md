# AIT CLI 设计文档

> AI 开发配置管理工具 — 跨机器、跨项目复用 Rules、Skills、MCP、模板

## 1. 目标

提供一个 CLI 工具 `ait`，将 `ai-dev-template` 仓库作为中心存储，通过 symlink 机制实现：

- 全局安装：clone 仓库后一键 symlink 所有 rules/skills 到 `~/.claude/` 等目标路径
- 项目配置：通过 profile 或手动选择，为项目配置所需的 AI 开发资源
- 换机复用：新电脑 clone + `ait install` 即可恢复全部配置

## 2. 管理范围

| 类型 | 仓库源路径 | 全局安装目标 | 项目安装目标 | 安装方式 |
|---|---|---|---|---|
| Claude Code rules | `rules/claude/` | `~/.claude/rules/` | `.claude/rules/` | symlink |
| Cursor rules | `rules/cursor/` | — | `.cursor/rules/` | symlink |
| Skills | `skills/` | `~/.claude/skills/` | `.claude/skills/` | symlink |
| CLAUDE.md 模板 | `templates/` | — | `./CLAUDE.md` | copy |
| MCP 配置 | `mcp/` | `~/.claude/mcp.json` | `.claude/mcp.json` | merge |

## 3. 技术栈

| 组件 | 选型 |
|---|---|
| 语言 | Python 3.10+ |
| CLI 框架 | typer |
| 依赖管理 | uv |
| Frontmatter 解析 | python-frontmatter |
| YAML 解析 | PyYAML |
| 安装方式 | `uv tool install` / `pipx` |

## 4. 仓库目录结构

```
ai-dev-template/
├── rules/
│   ├── claude/                    # Claude Code rules (.md)
│   │   ├── vue-use-eui.md
│   │   ├── server-security.md
│   │   ├── git-security.md
│   │   └── python-code-style.md
│   └── cursor/                    # Cursor rules (.mdc)
│       └── tv-webview-vue.mdc
├── skills/                        # Claude Code skills (.md)
│   └── ui-ux-pro-max.md
├── templates/                     # CLAUDE.md 项目模板
│   ├── tv-webview-vue.md
│   └── nuxt-admin.md
├── mcp/                           # MCP 配置片段 (.json)
│   └── context7.json
├── profiles/                      # Profile 定义
│   ├── vue-admin.yaml
│   └── fastapi.yaml
├── cli/                           # CLI 工具源码
│   ├── pyproject.toml
│   └── src/
│       └── ait/
│           ├── __init__.py
│           ├── main.py            # typer app 入口
│           ├── commands/
│           │   ├── install.py
│           │   ├── use.py
│           │   ├── list_cmd.py
│           │   ├── update.py
│           │   ├── add.py
│           │   ├── remove.py
│           │   ├── sync.py
│           │   ├── status.py
│           │   ├── profiles.py
│           │   └── show.py
│           └── core/
│               ├── config.py      # 路径常量、配置
│               ├── linker.py      # symlink 创建/清理
│               └── registry.py    # 扫描仓库、解析 frontmatter
└── .ai-rules.json                 # (项目级) 由 CLI 生成
```

## 5. 资源文件 Frontmatter 规范

### Markdown 资源（rules、skills、templates）

```markdown
---
name: vue-use-eui
description: Vue 项目统一使用 @danweiyuan/eui 组件库
type: claude-rule
tags: [vue, ui, eui]
version: 1.0.0
author: chances
---

（正文内容）
```

**type 可选值**：`claude-rule` | `cursor-rule` | `skill` | `template` | `mcp`

### MCP 配置（JSON）

```json
{
  "_meta": {
    "name": "context7",
    "description": "Context7 文档查询服务",
    "type": "mcp",
    "tags": ["docs", "context"],
    "version": "1.0.0",
    "author": "chances"
  },
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@anthropic/context7-mcp"]
    }
  }
}
```

安装时去掉 `_meta` 字段，将 `mcpServers` 内容合并到目标 `mcp.json`。

## 6. Profile 定义

```yaml
# profiles/vue-admin.yaml
name: vue-admin
description: Vue 3 管理后台项目配置
author: chances
version: 1.0.0

rules:
  claude:
    - vue-use-eui
    - server-security
    - git-security
  cursor:
    - tv-webview-vue

skills:
  - ui-ux-pro-max

templates:
  - nuxt-admin

mcp:
  - context7
```

通过资源的 `name` 字段关联。

## 7. CLI 命令

### 全局操作

```bash
ait install                    # clone 仓库到 ~/.ai-dev-template/
                               # symlink 全局 rules 和 skills

ait update                     # git pull 更新仓库
                               # 显示更新了哪些文件

ait list                       # 列出所有资源
ait list --type claude-rule    # 按类型筛选
ait list --tag vue             # 按标签筛选

ait status                     # 全局安装状态：已安装、断链检测

ait profiles                   # 列出所有可用 profile

ait show <name>                # 查看资源详情（frontmatter + 内容预览）
```

### 项目级操作

```bash
ait use <profile>              # 按 profile 配置当前项目

ait add <name>                 # 添加单个资源到当前项目

ait remove <name>              # 移除资源（删除 symlink）

ait sync                       # 根据 .ai-rules.json 重建所有链接
```

## 8. `.ai-rules.json` 结构

```json
{
  "profile": "vue-admin",
  "resources": [
    {
      "name": "vue-use-eui",
      "type": "claude-rule",
      "version": "1.0.0",
      "target": ".claude/rules/vue-use-eui.md",
      "mode": "symlink"
    },
    {
      "name": "nuxt-admin",
      "type": "template",
      "version": "1.0.0",
      "target": "CLAUDE.md",
      "mode": "copy"
    },
    {
      "name": "context7",
      "type": "mcp",
      "version": "1.0.0",
      "target": ".claude/mcp.json",
      "mode": "merge"
    }
  ],
  "repo": "~/.ai-dev-template",
  "updated_at": "2026-03-23T10:00:00"
}
```

- `profile` 为 `null` 表示纯手动 add
- `mode`：`symlink` | `copy` | `merge`

## 9. 核心流程

### `ait install`

1. 检查 `~/.ai-dev-template/` 是否存在
   - 不存在 → `git clone` 仓库到该目录
   - 已存在 → `git pull` 更新
2. 扫描仓库所有资源，解析 frontmatter，构建索引
3. 将 `rules/claude/` 下所有文件 symlink 到 `~/.claude/rules/`
4. 将 `skills/` 下文件 symlink 到 `~/.claude/skills/`
5. 输出安装摘要

### `ait use <profile>`

1. 读取 `profiles/<profile>.yaml`
2. 校验所有引用的资源名是否存在
3. 对每种类型执行安装：
   - `claude-rule` → symlink 到 `.claude/rules/`
   - `cursor-rule` → symlink 到 `.cursor/rules/`
   - `skill` → symlink 到 `.claude/skills/`（项目级）
   - `template` → copy 到项目根目录 `CLAUDE.md`（已存在则提示确认）
   - `mcp` → 去掉 `_meta`，合并到 `.claude/mcp.json`（已有 key 不覆盖）
4. 生成 `.ai-rules.json`
5. 将 `.ai-rules.json` 加入 `.gitignore`
6. 输出安装结果

### `ait sync`

1. 读取当前目录 `.ai-rules.json`
2. 检查 repo 路径是否存在（不存在则提示先 `ait install`）
3. 逐个资源重建：
   - `symlink` → 重新创建链接
   - `copy` → 跳过（已存在则不覆盖）
   - `merge` → 检查 `mcp.json` 缺失的 key，补充
4. 输出同步结果

## 10. 安装方式

```bash
# 开发模式
cd ai-dev-template/cli
uv sync
uv run ait --help

# 全局安装
cd ai-dev-template/cli
uv tool install .

# 或通过 pipx
pipx install ./cli
```

## 11. 设计约束

- macOS 优先，symlink 无限制
- 个人使用场景，不考虑多用户协作
- 仓库删除则所有 symlink 失效，`ait status` 可检测断链
- template 用 copy 因为 CLAUDE.md 通常需按项目修改
- mcp 用 merge 避免覆盖已有配置
