# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库性质

这是 **AIT（AI Dev Config Manager）** 项目，包含 `ait` CLI 工具和 AI 开发配置资源（Rules、Skills、MCP、模板、Profile）。同时保留技术栈选型模板、经验文档和通用脚本。主要语言为中文。

同时适配 **Cursor** 和 **Claude Code** 两套 AI 编码工具。

## 目录约定

- `frontend/` — 按终端类型划分（tv、mobile、admin、desktop、mini-program、landing）
- `backend/` — 按语言划分（python、node）
- `scripts/` — 通用工具脚本
- `docs/` — 学习笔记与方法论
- `skills/` — AI Skill 配置与说明文档
- `mcp/` — MCP 配置片段（带 `_meta` 元数据）
- `devops/`、`prompts/` — 占位目录，待填充
- `rules/` — Claude Code 和 Cursor 规则文件（带 frontmatter 元数据）
- `templates/` — CLAUDE.md 项目模板
- `profiles/` — Profile 组合配置
- `cli/` — ait CLI 工具源码（Python + typer）

子目录内的 `CLAUDE.md` 和 `cursor.mdc` 是面向具体项目的开发规则，不要修改其内容风格。

## 现有关键文档

- `frontend/tv/webview/vue/` — Android TV WebView + Vue 3 开发规则（Chromium 53 兼容约束）
- `frontend/admin/nuxt-tech-selection.md` — Nuxt 4 全栈管理后台技术选型
- `scripts/vue-build-deploy.py` — Vue 项目一键部署脚本（依赖 paramiko）
- `skills/ui-ux-pro-max.md` — UI/UX Pro Max Skill 功能说明
- `docs/ai-engineering-compound-growth.md` — AI 工程化实践笔记

## 编写规范

- 新增文档放到对应分类目录下，空目录用 `.gitkeep` 占位
- 同一项目模板需同时提供 `CLAUDE.md`（Claude Code）和 `cursor.mdc`（Cursor）两个版本
- `README.md` 的"目录结构"和"已有文档"两节需要与实际文件保持同步
- Commit message 使用中文描述，前缀遵循 conventional commits（feat/fix/docs/refactor）

## 脚本运行

```bash
# Vue 部署脚本（需先安装 paramiko）
pip install paramiko
python scripts/vue-build-deploy.py --help

# ait CLI（全局安装）
cd cli && uv tool install .
ait --help
```
