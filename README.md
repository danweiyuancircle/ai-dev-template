# AIT — AI Dev Config Manager

跨机器、跨项目复用 AI 开发配置（Rules、Skills、MCP、模板），基于 Git + symlink 机制。

## ait CLI

`ait` 是本仓库的核心工具，基于 **symlink 机制**管理所有 AI 开发配置：

- 全局安装 rules/skills 到 `~/.claude/`，修改仓库后所有项目自动同步
- 通过 profile 组合配置，一键为项目安装 rules + skills + 模板 + MCP
- 换电脑只需 `ait install` + `ait sync` 即可恢复全部配置

### 安装

```bash
# 需要 Python 3.10+ 和 uv
cd cli && uv tool install .
```

### 快速上手

```bash
# 1. 首次安装：克隆仓库 + 全局 symlink
ait install

# 2. 为项目应用 profile
cd your-project
ait use vue-admin

# 3. 换电脑后恢复
ait install
cd your-project
ait sync
```

### 命令速查

| 命令 | 说明 |
|------|------|
| `ait install` | 克隆仓库到 `~/.ai-dev-template/`，全局 rules/skills 软链接到 `~/.claude/` |
| `ait update` | `git pull` 更新仓库，显示变更文件 |
| `ait use <profile>` | 按 profile 为当前项目安装全部资源（切换 profile 自动清理旧资源） |
| `ait sync` | 根据 `.ai-rules.json` 重建所有资源链接 |
| `ait add <name>` | 向当前项目单独添加一个资源 |
| `ait remove <name>` | 从当前项目移除一个资源 |
| `ait status` | 显示全局 + 项目级安装状态，检测断链 |
| `ait list` | 列出所有资源（支持 `--type` / `--tag` 过滤） |
| `ait show <name>` | 查看资源详情和内容预览 |
| `ait profiles` | 列出所有可用 profile |

### 资源类型与安装方式

| 类型 | 仓库路径 | 安装方式 | 说明 |
|------|----------|----------|------|
| Claude Rules | `rules/claude/` | symlink | 全局 → `~/.claude/rules/`，项目 → `.claude/rules/` |
| Cursor Rules | `rules/cursor/` | symlink | 项目 → `.cursor/rules/` |
| Skills | `skills/` | symlink | 全局 → `~/.claude/skills/`，项目 → `.claude/skills/` |
| 模板 | `templates/` | copy | 复制到项目 `CLAUDE.md`（去除 frontmatter） |
| MCP | `mcp/` | merge | 合并到项目 `.claude/mcp.json`（不覆盖已有配置） |

### Profile 示例

```yaml
# profiles/vue-admin.yaml
name: vue-admin
description: Vue 3 管理后台项目配置

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

## 目录结构

```
ait/
├── rules/                             # AI 编码规则
│   ├── claude/                        # Claude Code rules (.md)
│   └── cursor/                        # Cursor rules (.mdc)
├── skills/                            # Claude Code skills
├── templates/                         # CLAUDE.md 项目模板
├── mcp/                               # MCP 配置片段
├── profiles/                          # Profile 组合配置
├── cli/                               # ait CLI 工具源码 (Python + typer)
├── frontend/                          # 前端项目模板
│   ├── tv/webview/vue/                # Android TV WebView + Vue (Chromium 53)
│   ├── admin/                         # 后台管理系统
│   ├── mobile/                        # 移动端
│   ├── desktop/                       # 桌面端
│   ├── landing/                       # 落地页
│   └── mini-program/                  # 小程序
├── backend/                           # 后端项目模板
│   ├── python/                        # FastAPI / Django / Flask
│   └── node/                          # Express / NestJS / Nitro
├── scripts/                           # 通用脚本工具
├── docs/                              # 学习笔记与方法论
├── devops/                            # 部署运维
└── prompts/                           # Prompt 模板
```

## 已有资源

### Rules

| 名称 | 类型 | 说明 |
|------|------|------|
| `vue-use-eui` | claude-rule | Vue 项目统一使用 @danweiyuan/eui 组件库 |
| `server-security` | claude-rule | 服务器安全部署规则 |
| `git-security` | claude-rule | Git 提交安全规则 |
| `python-code-style` | claude-rule | Python + FastAPI 代码规范 |
| `tv-webview-vue` | cursor-rule | Android TV WebView 开发规则（Chromium 53 兼容） |

### Skills / Templates / MCP

| 名称 | 类型 | 说明 |
|------|------|------|
| `ui-ux-pro-max` | skill | AI 设计智能 Skill，100+ 行业推理规则 |
| `tv-webview-vue` | template | Android TV WebView 项目 CLAUDE.md 模板 |
| `nuxt-admin` | template | Nuxt.js 全栈管理后台技术选型模板 |
| `context7` | mcp | Context7 文档查询服务 |

### 经验文档

| 文件 | 说明 |
|------|------|
| [`docs/ai-engineering-compound-growth.md`](docs/ai-engineering-compound-growth.md) | AI 工程化实践：上下文工程、Subagent 架构、经验沉淀 |

### 脚本

| 文件 | 说明 |
|------|------|
| [`scripts/vue-build-deploy.py`](scripts/vue-build-deploy.py) | Vue 项目一键打包部署（SSH 上传 + 备份 + 解压） |

## 添加新资源

所有资源文件需要 YAML frontmatter：

```markdown
---
name: my-rule
description: 规则描述
type: claude-rule    # claude-rule | cursor-rule | skill | template | mcp
tags: [tag1, tag2]
version: 1.0.0
author: your-name
---

正文内容...
```

MCP 配置使用 JSON `_meta` 字段：

```json
{
  "_meta": {
    "name": "my-mcp",
    "description": "MCP 描述",
    "type": "mcp",
    "tags": ["tag1"],
    "version": "1.0.0",
    "author": "your-name"
  },
  "mcpServers": { ... }
}
```

## 兼容性

适配 **Cursor** 和 **Claude Code** 两套 AI 编码工具。
