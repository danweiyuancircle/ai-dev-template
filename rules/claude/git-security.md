---
name: git-security
description: Git 提交安全规则
type: claude-rule
tags: [security, git]
version: 1.0.0
author: chances
---

# Git 提交安全规则

每次执行 `git add` 或 `git commit` 前必须遵循以下规则。违反时必须**立即停止并提示用户确认**。

## 一、禁止提交的文件

### 绝对禁止（无论任何理由）
以下文件**永远不得**被 `git add`：

| 文件类型 | 示例 |
|---|---|
| 环境变量文件 | `.env`、`.env.local`、`.env.production`、`*.env` |
| SSH 密钥 | `id_rsa`、`id_ed25519`、`*.pem`、`*.key` |
| 证书文件 | `*.p12`、`*.pfx`、`*.jks`、`*.keystore` |
| 数据库文件 | `*.sql`（含真实数据的）、`*.dump`、`*.sqlite` |
| 原始数据 | `*.xlsx`、`*.csv`（含用户/学生等敏感数据的） |
| 日志文件 | `*.log` |
| Docker 卷数据 | `pgdata/`、`cache/*.json` |

### 检测方法
在执行 `git add` 前，检查暂存区是否包含上述文件：
```bash
git diff --cached --name-only | grep -iE '\.(env|pem|key|p12|pfx|jks|dump|sqlite|log)$'
```

## 二、禁止提交的内容

### 必须扫描的敏感模式
对每个将要提交的文件内容，检查是否包含以下模式：

| 类型 | 匹配模式 | 示例 |
|---|---|---|
| API Key | `sk-[a-zA-Z0-9]{20,}` | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| AWS Key | `AKIA[0-9A-Z]{16}` | `AKIAIOSFODNN7EXAMPLE` |
| 密码赋值 | `password\s*[:=]\s*["'][^"']{4,}` | `password = "abc123"` |
| 数据库连接串 | `://\w+:[^@\s]+@` | `postgresql://user:pass@host` |
| 私钥内容 | `-----BEGIN (RSA |EC )?PRIVATE KEY-----` | PEM 私钥 |
| Token | `token\s*[:=]\s*["'][a-zA-Z0-9_\-]{20,}` | `token = "ghp_xxxx"` |
| Secret | `secret\s*[:=]\s*["'][^"']{8,}` | `secret = "my-secret"` |
| 服务器 IP+端口 | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+` | `8.218.87.23:66` |
| SSH 连接 | `ssh\s+.*@\d{1,3}\.\d{1,3}` | `ssh root@8.218.87.23` |

### 例外：允许的模式
以下情况**不算**违规：
- `.env.example` 中的占位符（如 `DEEPSEEK_API_KEY=your-key-here`）
- 代码中从环境变量读取的引用（如 `os.getenv("API_KEY")`）
- `localhost` 或 `127.0.0.1` 的连接串
- 文档中的示例/假数据（如 `sk-xxxxxxxxxxxx`）
- 配置文件中的空字符串默认值（如 `api_key: str = ""`）

## 三、提交前检查流程

每次 `git commit` 前必须执行：

```
1. 检查暂存文件列表 → 是否包含禁止文件类型？
2. 检查文件内容差异 → 是否包含敏感模式？
3. 检查 .gitignore → 是否已排除敏感目录？
4. 通过 → 执行提交
5. 未通过 → 停止，提示用户具体违规项
```

### 自动检查命令
```bash
# 检查暂存区的敏感文件
git diff --cached --name-only | grep -iE '\.(env|pem|key|log|dump|sqlite)$'

# 检查暂存区内容中的敏感信息
git diff --cached -U0 | grep -iE '(sk-[a-zA-Z0-9]{20}|AKIA[0-9A-Z]{16}|-----BEGIN.*PRIVATE KEY|password\s*[:=]\s*"[^"]{4,}"|://\w+:[^@\s]+@[^l])'
```

## 四、.gitignore 最低要求

每个项目的 `.gitignore` 必须至少包含：

```gitignore
# 环境变量
.env
*.env
.env.*

# 密钥
*.pem
*.key
*.p12

# 缓存与编译
__pycache__/
*.pyc
node_modules/
dist/

# 日志
*.log

# 数据库
*.sqlite
*.dump
```

如果项目的 `.gitignore` 缺少以上条目，提交前必须先补全。

## 五、已提交敏感数据的处理

如果发现敏感数据已存在于 git 历史中：

1. **立即通知用户**，说明哪些数据已泄露
2. **建议轮换凭证**（API Key、密码等）
3. **提供清理命令**（但不自动执行，等用户确认）：
```bash
# 从所有历史中删除文件
git filter-repo --path <file> --invert-paths --force

# 或使用 BFG
bfg --delete-files <filename>
```

## 六、违规处理流程

当检测到提交操作包含敏感数据时：

1. **立即停止** `git add` 或 `git commit`
2. **列出具体违规项**：
   - 文件名和行号
   - 匹配到的敏感模式类型
   - 敏感内容的部分摘要（如 `sk-5522****dc3`，脱敏显示）
3. **提供建议**：
   - 将文件加入 `.gitignore`
   - 将敏感值移到 `.env`
   - 使用环境变量替代硬编码
4. **等待用户明确确认**后才能继续
5. 如用户确认提交，添加注释：`# GIT-SECURITY: 用户已确认提交此内容`
