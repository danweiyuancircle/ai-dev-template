---
name: vue-use-eui
description: Vue 项目统一使用 @danweiyuan/eui 组件库
type: claude-rule
tags: [vue, ui, eui]
version: 1.0.0
author: chances
---

# Vue 项目统一使用 @danweiyuan/eui 组件库

所有 Vue 3 项目必须使用 `@danweiyuan/eui` 组件库进行 UI 开发，禁止使用裸 HTML 元素和手写样式。

## 安装

```bash
npm install @danweiyuan/eui
```

`.npmrc` 配置：
```
@danweiyuan:registry=https://registry.npmjs.org/
```

## 强制规则

### 禁止裸 HTML 元素

| 禁止 | 使用 |
|------|------|
| `<button>` | `<EButton>` |
| `<input>` | `<EInput>` / `<EInputNumber>` |
| `<select>` + `<option>` | `<ESelect :options="...">` |
| `<textarea>` | `<ETextarea>` |
| `<input type="checkbox">` | `<ECheckbox>` |
| `<input type="radio">` | `<ERadio>` |
| 手写 `position:fixed` 弹窗 | `<EModal>` / `<EDrawer>` / `<EFormDialog>` |
| 手写删除确认 | `<EConfirmDialog>` |
| 手写 toast/通知 | `useToast()` / `useNotification()` |
| 手写表格 | `<EDataTable>` |
| 手写分页 | `<EPagination>` |
| 手写面包屑 | `<EBreadcrumb>` |
| 手写标签页 | `<ETabs>` |
| 手写折叠面板 | `<ECollapse>` |
| 手写导航菜单 | `<EMenu>` |
| 手写管理后台布局 | `<EAdminLayout>` |

### 禁止硬编码颜色

使用 CSS 变量 token，不要直接写 Tailwind 颜色类：

| 禁止 | 使用 |
|------|------|
| `bg-indigo-500` | `bg-[var(--ui-color-primary)]` |
| `text-slate-900` | `text-[var(--ui-text-base)]` |
| `border-gray-200` | `border-[var(--ui-border)]` |
| `bg-white` | `bg-[var(--ui-bg-base)]` |

### 主题与暗黑模式

```vue
import { useTheme } from '@danweiyuan/eui'
const { isDark, toggleDark, setPrimaryColor } = useTheme()
```

### 图标

使用 lucide-vue-next（@danweiyuan/eui 已内置）：

```vue
import { User, Settings } from 'lucide-vue-next'
```

### 导入方式

```css
/* CSS 入口 */
@import "tailwindcss";
@import "@danweiyuan/eui/theme";
@source "node_modules/@danweiyuan/eui/dist/**/*.js";
```

```vue
<!-- 按需导入组件 -->
<script setup>
import { EButton, EInput, EModal, EDataTable } from '@danweiyuan/eui'
</script>
```

## 组件库文档

完整组件清单、Props、用法示例见 `@danweiyuan/eui` 包内的 README.md。
如在本地开发，文档站运行：`cd frontend && npm run dev:docs`（端口 3002）。
