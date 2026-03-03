# Nuxt.js 全栈管理后台 — 技术选型方案

## 项目定位

管理后台 / Dashboard 系统，需要用户认证，架构追求简洁实用。

---

## 技术栈总览

| 层级 | 技术选择 | 说明 |
|------|---------|------|
| 框架 | **Nuxt 4** | Vue 3 全栈框架，当前稳定版（2025.7 发布），内置 SSR/SSG + Nitro 服务端 |
| UI 组件库 | **Nuxt UI v4** | 官方组件库，合并了 Nuxt UI Pro，125+ 组件全部免费 |
| CSS | **Tailwind CSS v4** | Nuxt UI 自带，无需额外配置 |
| 图标 | **Lucide Icons** | Nuxt UI 默认图标集 |
| 数据库 | **SQLite / MySQL** | 开发用 SQLite 零配置，生产可切换 MySQL，通过环境变量切换 |
| ORM | **Drizzle ORM** | 轻量、类型安全、SQL-like API |
| 认证 | **nuxt-auth-utils** | Nuxt 官方认证模块，基于 Session |
| 数据校验 | **Zod** | 前后端统一的 Schema 校验 |
| 状态管理 | **Nuxt useState** | 内置 composable，简单场景足够 |
| 包管理器 | **pnpm** | 快速、节省磁盘空间 |

---

## 方案对比（为什么这么选）

### ORM 选择：Drizzle vs Prisma vs 裸 SQL

| 维度 | Drizzle ORM | Prisma | 裸 SQL (better-sqlite3) |
|------|------------|--------|------------------------|
| 包体积 | ~50KB | ~8MB | ~0 |
| 类型安全 | 完整 | 完整 | 无 |
| SQLite + MySQL | 均原生支持 | 均支持 | 需分别处理 |
| 学习曲线 | 低（接近 SQL） | 中 | 无（就是 SQL） |
| 迁移工具 | drizzle-kit | prisma migrate | 手动 |
| 运行时依赖 | 无额外运行时 | 需要 Prisma Client | 无 |

**推荐 Drizzle ORM** — 轻量、类型安全、API 接近原生 SQL，和 Nuxt 的轻量哲学一致。

### 认证选择：nuxt-auth-utils vs @sidebase/nuxt-auth

| 维度 | nuxt-auth-utils | @sidebase/nuxt-auth |
|------|----------------|---------------------|
| 维护方 | Nuxt 官方 | 社区 |
| 复杂度 | 低 | 高（基于 NextAuth） |
| Session 管理 | 内置 | 内置 |
| OAuth 支持 | 支持主流 Provider | 支持更多 Provider |
| 适用场景 | 中小型项目 | 复杂认证需求 |

**推荐 nuxt-auth-utils** — 官方维护，简单直接，管理后台够用。

---

## 项目结构

```
project/
├── app/
│   ├── components/        # 公共组件
│   ├── composables/       # 组合式函数
│   ├── layouts/
│   │   └── dashboard.vue  # Dashboard 布局（侧边栏 + 顶栏）
│   ├── pages/
│   │   ├── index.vue      # 首页/仪表盘
│   │   ├── login.vue      # 登录页
│   │   └── [模块名]/      # 各业务模块页面
│   ├── middleware/
│   │   └── auth.ts        # 路由守卫：未登录跳转登录页
│   └── app.vue
├── server/
│   ├── api/               # API 路由 (自动映射 /api/*)
│   │   ├── auth/
│   │   │   ├── login.post.ts
│   │   │   ├── logout.post.ts
│   │   │   └── session.get.ts
│   │   └── [模块名]/      # 各业务模块 API
│   ├── database/
│   │   ├── index.ts       # Drizzle 实例初始化（根据环境变量切换驱动）
│   │   └── schema/
│   │       ├── sqlite.ts   # SQLite Schema 定义
│   │       └── mysql.ts    # MySQL Schema 定义
│   ├── middleware/
│   │   └── auth.ts        # 服务端认证中间件
│   └── utils/             # 服务端工具函数
├── drizzle/               # 数据库迁移文件（自动生成）
├── drizzle.config.ts      # Drizzle Kit 配置
├── nuxt.config.ts
├── package.json
└── .env
```

---

## 核心模块说明

### 1. Nuxt UI Dashboard 布局

Nuxt UI v4 合并了原 Nuxt UI Pro，内置 125+ 组件，Dashboard 相关组件开箱即用：

- `UDashboardGroup` — 布局容器
- `UDashboardSidebar` — 侧边栏（支持折叠、响应式）
- `UDashboardPanel` — 内容面板
- `UDashboardNavbar` — 顶部导航栏
- `UDashboardToolbar` — 工具栏（筛选、搜索等）
- `UNavigationMenu` — 导航菜单
- `UTable` — 数据表格
- `UForm` — 表单组件

这些组件覆盖了管理后台 90% 的 UI 需求，无需额外引入组件库。Nuxt UI v4 还包含原 Pro 版的页面模板（Landing、Dashboard、SaaS 等），全部免费。

### 2. 数据库层 (Drizzle + SQLite / MySQL)

通过环境变量 `DB_DIALECT` 切换数据库，Schema 分文件定义，初始化层统一导出 `db` 和 `tables`。

**SQLite Schema:**

```typescript
// server/database/schema/sqlite.ts
import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core'
import { sql } from 'drizzle-orm'

export const users = sqliteTable('users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  username: text('username').unique().notNull(),
  passwordHash: text('password_hash').notNull(),
  role: text('role', { enum: ['admin', 'user'] }).default('user'),
  createdAt: text('created_at').default(sql`(CURRENT_TIMESTAMP)`).notNull(),
})
```

**MySQL Schema:**

```typescript
// server/database/schema/mysql.ts
import { mysqlTable, int, varchar, timestamp } from 'drizzle-orm/mysql-core'

export const users = mysqlTable('users', {
  id: int('id').primaryKey().autoincrement(),
  username: varchar('username', { length: 255 }).unique().notNull(),
  passwordHash: varchar('password_hash', { length: 255 }).notNull(),
  role: varchar('role', { length: 20 }).default('user'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})
```

**统一初始化（根据环境变量切换）:**

```typescript
// server/database/index.ts
const dialect = process.env.DB_DIALECT || 'sqlite'

let db: any

if (dialect === 'mysql') {
  const { drizzle } = await import('drizzle-orm/mysql2')
  const schema = await import('./schema/mysql')
  db = drizzle({ connection: { uri: process.env.DATABASE_URL! }, schema })
} else {
  const { drizzle } = await import('drizzle-orm/better-sqlite3')
  const schema = await import('./schema/sqlite')
  db = drizzle({ connection: { source: process.env.DATABASE_URL || './data/app.db' }, schema })
}

export { db }
```

**Drizzle Kit 配置（也根据环境变量切换）:**

```typescript
// drizzle.config.ts
import 'dotenv/config'
import { defineConfig } from 'drizzle-kit'

const dialect = (process.env.DB_DIALECT || 'sqlite') as 'sqlite' | 'mysql'

export default defineConfig({
  out: './drizzle',
  schema: `./server/database/schema/${dialect}.ts`,
  dialect,
  dbCredentials: {
    url: process.env.DATABASE_URL || './data/app.db',
  },
})
```

**环境变量示例:**

```bash
# .env — 开发环境 (SQLite，零配置)
DB_DIALECT=sqlite
DATABASE_URL=./data/app.db

# .env.production — 生产环境 (MySQL)
DB_DIALECT=mysql
DATABASE_URL=mysql://user:password@localhost:3306/my_admin
```

### 3. 认证流程

```
登录页 → POST /api/auth/login → 校验密码 → 设置 Session Cookie
                                                    ↓
页面请求 → auth middleware 检查 Session → 通过 → 渲染页面
                                        → 未通过 → 跳转登录页
```

基于 `nuxt-auth-utils` 的 Session 机制，服务端用 `useSession()` 管理用户会话。

### 4. API 设计规范

使用 Nitro 的文件路由，方法名即请求方法：

```
server/api/users/index.get.ts    → GET    /api/users      (列表)
server/api/users/index.post.ts   → POST   /api/users      (新增)
server/api/users/[id].get.ts     → GET    /api/users/:id   (详情)
server/api/users/[id].put.ts     → PUT    /api/users/:id   (更新)
server/api/users/[id].delete.ts  → DELETE /api/users/:id   (删除)
```

每个 API 使用 Zod 校验入参：

```typescript
// server/api/users/index.post.ts
import { z } from 'zod'

const schema = z.object({
  username: z.string().min(3),
  password: z.string().min(6),
  role: z.enum(['admin', 'user']).default('user'),
})

export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, schema.parse)
  // ... 插入数据库
})
```

---

## 依赖清单

```json
{
  "dependencies": {
    "nuxt": "^4.x",
    "@nuxt/ui": "^4.x",
    "drizzle-orm": "^0.3x",
    "better-sqlite3": "^11.x",
    "mysql2": "^3.x",
    "nuxt-auth-utils": "^0.x",
    "zod": "^3.x"
  },
  "devDependencies": {
    "drizzle-kit": "^0.3x",
    "@types/better-sqlite3": "^7.x",
    "typescript": "^5.x"
  }
}
```

核心依赖仅 **7 个**，开发依赖 **3 个**。

---

## nuxt.config.ts 配置

```typescript
export default defineNuxtConfig({
  modules: [
    '@nuxt/ui',
    'nuxt-auth-utils',
  ],

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    session: {
      password: process.env.NUXT_SESSION_PASSWORD || '',
    },
  },

  devtools: { enabled: true },
})
```

---

## 开发工作流

```bash
# 初始化项目（默认创建 Nuxt 4）
pnpm dlx nuxi@latest init my-admin
cd my-admin
pnpm add @nuxt/ui drizzle-orm better-sqlite3 mysql2 nuxt-auth-utils zod
pnpm add -D drizzle-kit @types/better-sqlite3

# 开发
pnpm dev

# 数据库迁移
pnpm drizzle-kit generate   # 生成迁移文件
pnpm drizzle-kit migrate    # 执行迁移
pnpm drizzle-kit studio     # 可视化数据库管理

# 构建部署
pnpm build
node .output/server/index.mjs
```

---

## 部署方案

管理后台推荐 **Node.js 直接部署**：

```bash
# 构建
pnpm build

# 用 PM2 部署
pm2 start .output/server/index.mjs --name my-admin

# 或用 Docker
# SQLite 模式：挂载 data/ 目录确保数据库文件持久化
# MySQL 模式：配置 DATABASE_URL 环境变量指向 MySQL 服务
```

> **部署建议**:
> - **单机/小规模**: 用 SQLite，零运维，数据文件挂载即可
> - **多实例/高并发**: 切换 MySQL，支持连接池和多进程并发写入
> - SQLite 不适合 Serverless 平台（如 Vercel），如有需要可用 Turso（云端 SQLite）

---

## 架构图

```
┌─────────────────────────────────────────────────┐
│                   浏览器                         │
│  ┌───────────────────────────────────────────┐  │
│  │  Nuxt UI Dashboard Layout                 │  │
│  │  ┌──────────┐ ┌────────────────────────┐  │  │
│  │  │ Sidebar  │ │ Content Panel          │  │  │
│  │  │ 导航菜单  │ │ UTable / UForm / ...   │  │  │
│  │  │          │ │                        │  │  │
│  │  └──────────┘ └────────────────────────┘  │  │
│  └───────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────┘
                       │ useFetch / $fetch
                       ▼
┌─────────────────────────────────────────────────┐
│              Nitro Server (API)                  │
│  ┌─────────────┐  ┌─────────────────────────┐   │
│  │ Auth 中间件  │  │ server/api/**/*.ts      │   │
│  │ Session 管理 │  │ Zod 校验 → Drizzle 操作  │   │
│  └─────────────┘  └────────────┬────────────┘   │
└────────────────────────────────┼─────────────────┘
                                 │ Drizzle ORM
                                 ▼
                    ┌─────────────────────┐
                    │  SQLite / MySQL     │
                    │  (环境变量切换)       │
                    └─────────────────────┘
```

---

## 总结

这套技术栈的核心优势：

1. **极简** — 核心依赖仅 7 个，无冗余
2. **全 TypeScript** — 从数据库 Schema 到前端组件，端到端类型安全
3. **灵活部署** — 开发用 SQLite 零配置，生产可切 MySQL，环境变量一键切换
4. **开箱即用** — Nuxt UI 内置 Dashboard 组件，不需要从零搭建布局
5. **双数据库支持** — SQLite 和 MySQL 各自独立 Schema，Drizzle Kit 迁移工具统一管理
