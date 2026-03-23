---
name: ui-ux-pro-max
description: AI 设计智能 Skill，内置 100 条行业推理规则
type: skill
tags: [ui, ux, design, frontend]
version: 1.0.0
author: chances
---

# UI UX Pro Max

AI 设计智能 Skill，内置 100 条行业推理规则，为前端项目生成专业级 UI/UX 方案。

- **仓库**: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

## 核心功能

### 设计系统生成器 (Design System Generator)

分析项目需求后自动生成完整的设计系统，包含：

- 配色方案（96 套行业配色板，含 HEX 色值）
- 字体搭配（57 组 Google Fonts 配对方案）
- UI 风格推荐（67 种，如 glassmorphism、minimalism、brutalism、bento grid 等）
- 图表类型建议（25 种）
- UX 准则（99 条）
- 反模式过滤 + 交付前无障碍/响应式检查清单

### 行业推理引擎

100 条规则覆盖：科技/SaaS、金融、医疗、电商、服务、创意、新兴科技。
根据项目所属行业自动匹配合适的设计规范。

## 支持的技术栈

| 平台 | 技术栈 |
|------|--------|
| Web | HTML + Tailwind, React, Next.js, shadcn/ui, Vue, Nuxt.js, Nuxt UI, Svelte, Astro |
| 移动端 | SwiftUI, Jetpack Compose, React Native, Flutter |

## 安装方式

**Claude Code (Marketplace):**

```bash
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

**CLI:**

```bash
npm install -g uipro-cli
uipro init --ai claude
```

兼容 15+ AI 编码工具：Cursor、Windsurf、GitHub Copilot、Continue、Gemini CLI 等。

## 使用方式

- **自动激活**: 在 Claude Code 中直接描述 UI/UX 需求即可触发
- **斜杠命令**: `/ui-ux-pro-max [需求描述]`（Kiro、GitHub Copilot、Roo Code）

## 典型输出

生成内容包含：风格推荐、配色方案（HEX）、字体搭配、关键效果说明、反模式警告、无障碍/响应式检查清单。
