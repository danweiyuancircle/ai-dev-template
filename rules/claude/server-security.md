---
name: server-security
description: 服务器安全部署规则
type: claude-rule
tags: [security, server, docker, nginx]
version: 1.0.0
author: chances
---

# 服务器安全部署规则

所有项目部署到云服务器时必须遵循以下规则。如果任何操作违反这些规则，必须**立即提示用户并获得明确确认**后才能继续。

## 一、端口与网络隔离

### 强制规则
- 数据库（PostgreSQL/MySQL/Redis 等）**禁止暴露到宿主机端口**，仅通过 Docker 内部网络访问
- 后端应用端口绑定 `127.0.0.1`，不允许 `0.0.0.0`
- 仅 Nginx/反向代理的 80/443 端口绑定 `0.0.0.0`

### docker-compose 示例
```yaml
# ✅ 正确
backend:
  ports:
    - "127.0.0.1:{port}:{port}"

db:
  # 不写 ports，仅内部网络

# ❌ 违规 — 需要提示用户
db:
  ports:
    - "{db_port}:{db_port}"
backend:
  ports:
    - "{port}:{port}"
```

## 二、凭证与密钥管理

### 强制规则
- **禁止在代码中硬编码**数据库密码、API Key、Secret 等凭证
- 所有凭证通过 `.env` 文件或环境变量注入
- `.env` 文件必须在 `.gitignore` 中排除
- 数据库密码最少 24 位，包含大小写字母和数字
- 提供 `.env.example` 模板文件（仅含占位符，不含真实值）

### 违规检测
如果在代码中发现以下内容，必须提示用户：
- 硬编码的数据库连接字符串含真实密码
- API Key 出现在非 `.env` 文件中
- SSH 密码、私钥路径出现在代码或文档中

## 三、Nginx 安全配置（最小访问控制）

### 核心原则
**只开放业务必需的路径和方法，其余一律拒绝。**

### 强制规则

每个项目的 Nginx 配置必须包含以下安全基线（具体路径、端口、超时时间根据项目在项目级 CLAUDE.md 中配置）：

**1. 频率限制（http 块）**
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=page_limit:10m rate=30r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
```

**2. 安全响应头（server 块）**
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

**3. 全局限制（server 块）**
```nginx
client_max_body_size 1m;        # 无文件上传业务时默认 1m
client_body_timeout 10s;
client_header_timeout 10s;
limit_conn conn_limit 20;
```

**4. 敏感文件屏蔽（最高优先级）**
```nginx
location ~ /\. {
    deny all;
    return 404;
}

location ~* \.(env|git|xlsx|sql|log|bak|dump|tar|gz|zip|csv)$ {
    deny all;
    return 404;
}
```

**5. API 路径最小化**
```nginx
location /api {
    limit_except GET POST {
        deny all;
    }
    limit_req zone=api_limit burst=20 nodelay;
    # proxy_pass 等具体配置由项目决定
}
```

**6. 攻击路径屏蔽**
```nginx
location ~ ^/(admin|phpmyadmin|wp-admin|cgi-bin|actuator|console|debug) {
    deny all;
    return 404;
}
```

### 违规检测
如果 Nginx 配置中出现以下情况，必须提示用户：
- 缺少 `limit_req` 频率限制
- `client_max_body_size` 大于 10m（除非有文件上传业务）
- API 路径允许 PUT/DELETE 但业务不需要
- 缺少 `location ~ /\.` 敏感文件屏蔽
- 使用 `proxy_pass` 但未设置 `proxy_connect_timeout`

### 部署后必须验证
```bash
# 1. 敏感文件返回 404
curl -s -o /dev/null -w "%{http_code}" http://{server}/.git/config
curl -s -o /dev/null -w "%{http_code}" http://{server}/.env

# 2. 安全头存在
curl -sI http://{server}/ | grep -i "x-frame-options"
curl -sI http://{server}/ | grep -i "x-content-type-options"

# 3. 非法方法被拒绝
curl -s -o /dev/null -w "%{http_code}" -X DELETE http://{server}/api/health

# 4. 攻击路径被屏蔽
curl -s -o /dev/null -w "%{http_code}" http://{server}/phpmyadmin

# 5. 正常服务可用
curl -s http://{server}/api/health
```

## 四、Docker 容器安全

### 强制规则
- Dockerfile 必须使用非 root 用户运行应用
- 必须创建 `.dockerignore` 排除 `.env`、`.git`、`cache/`、`__pycache__`
- Python 项目设置 `ENV PYTHONUNBUFFERED=1`
- Node.js 项目设置 `ENV NODE_ENV=production`

## 五、CORS 配置

### 强制规则
- **禁止生产环境使用 `*` 通配符**
- 必须明确列出允许的域名/IP
- 通过环境变量配置，便于不同环境切换

```
# ✅ 正确 — 明确列出
ALLOWED_ORIGINS=http://localhost,http://{server_ip}

# ❌ 违规
ALLOWED_ORIGINS=*
```

## 六、API 安全

### 强制规则
- 敏感数据查询接口必须有限流（推荐 5-10 次/分钟/IP）
- 错误消息不得回显用户输入内容（防止信息泄露）
- 不得提供批量查询/列表接口暴露全量数据
- 如项目含认证机制，未配置时必须在日志中输出 WARNING

```
# ✅ 正确 — 通用错误消息
return {"message": "记录不存在"}

# ❌ 违规 — 回显用户输入
return {"message": f"未找到: {user_input}"}
```

## 七、数据安全

### 强制规则
- 手机号在返回前必须脱敏（如 `138****5678`）
- 身份证号在返回前必须脱敏（如 `420***********1234`）
- 查询日志中的 PII（姓名、手机号等）建议加密存储
- 数据源文件（Excel/CSV 等）不可通过 Web 直接访问
- 数据库数据仅通过应用层访问，不暴露数据库管理端口

## 八、Git 仓库安全

### 强制规则
`.gitignore` 必须包含：
```
.env
*.env
__pycache__/
*.pyc
node_modules/
dist/
*.log
```

### 违规检测
如果发现以下文件被 `git add`，必须立即阻止并提示用户：
- `.env` 文件
- 含真实密码/密钥的配置文件
- SSH 私钥文件
- 数据库备份文件（`.sql`、`.dump`）
- 含敏感数据的原始数据文件（`.xlsx`、`.csv`）

## 九、SSH 安全

### 强制规则
- **禁止密码登录**，仅允许密钥认证
- **禁止 root 密码登录**（`PermitRootLogin prohibit-password` 或 `without-password`）
- **禁止使用默认 22 端口**，改为非标端口（如 66）
- SSH 私钥文件（`id_rsa`、`id_ed25519` 等）**禁止出现在代码仓库、文档、聊天记录中**
- 服务器 IP、SSH 端口、用户名**禁止写入代码仓库**（包括 README、部署文档）

### 违规检测
如果在任何文件中发现以下内容，必须立即提示用户：
- SSH 连接命令含完整 IP + 端口 + 用户名
- 服务器凭证信息（IP、端口、密码、密钥路径）
- `sshd_config` 中 `PasswordAuthentication yes`

### 安全基线配置（`/etc/ssh/sshd_config`）
```
Port 66                              # 非标端口
PermitRootLogin prohibit-password    # 禁止 root 密码登录
PasswordAuthentication no            # 禁止所有密码登录
PubkeyAuthentication yes             # 启用密钥认证
MaxAuthTries 3                       # 最大尝试次数
LoginGraceTime 30                    # 登录超时 30 秒
```

### 配合 fail2ban
建议服务器配置 fail2ban 防暴力破解：
```
# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 66
maxretry = 5
bantime = 3600
```

### 部署操作规范
- 通过 SSH 连接服务器时，连接信息从本地 `~/.ssh/config` 读取，不在命令行暴露
- 推荐在 `~/.ssh/config` 中配置 Host 别名：
```
Host myserver
    HostName <ip>
    Port <port>
    User root
    IdentityFile ~/.ssh/id_rsa
```
- 部署脚本中使用 `ssh myserver` 而非完整连接命令

## 十、数据持久化与防删除

### 核心原则
**所有业务数据必须通过 Docker Named Volume 持久化。任何可能导致数据丢失的操作，必须提前说明原因并获得用户确认。**

### 强制规则 — Docker Volume

- 数据库容器**必须挂载 Named Volume**到数据目录
- **禁止使用匿名卷或仅容器内存储**
- 重启策略必须设为 `unless-stopped` 或 `always`

```yaml
# ✅ 正确 — Named Volume 持久化
db:
  volumes:
    - dbdata:/var/lib/postgresql/data  # PostgreSQL
    # 或 - dbdata:/var/lib/mysql       # MySQL
  restart: unless-stopped

volumes:
  dbdata:

# ❌ 违规 — 数据在容器内，删除即丢失
db:
  # 没有 volumes 配置
```

### 危险操作清单

以下命令**执行前必须停止、说明原因、说明影响、等待用户确认**：

| 命令 | 风险等级 | 后果 |
|---|---|---|
| `docker compose down -v` | **致命** | 删除所有 Volume，数据永久丢失 |
| `docker volume rm <name>` | **致命** | 删除指定 Volume，数据永久丢失 |
| `docker volume prune` | **致命** | 删除所有未使用的 Volume |
| `docker system prune -a --volumes` | **致命** | 清除所有镜像、容器、Volume |
| `rm -rf /var/lib/docker/volumes/` | **致命** | 删除所有 Docker 数据 |
| `DROP TABLE` / `DROP DATABASE` | **致命** | 删除数据库表或整个数据库 |
| `DELETE FROM <table>` 无 WHERE | **高危** | 清空整张表数据 |
| `TRUNCATE TABLE` | **高危** | 清空表数据且无法回滚 |
| `rm -rf` 含数据目录 | **高危** | 删除文件系统数据 |
| `git clean -fdx` | **高危** | 删除所有未跟踪文件（含数据文件） |

### 违规处理
当 AI 需要执行以上任何操作时，必须：

1. **立即停止**，不执行该命令
2. **说明原因**：为什么需要执行这个操作
3. **说明影响**：会删除哪些数据、多少条记录
4. **提供替代方案**（如有）：是否有不删除数据的方式达到目的
5. **等待用户明确回复"确认"**后才能执行

示例对话：
```
AI: 我需要执行 `docker compose down -v` 来重建数据库。
    原因：数据库 schema 发生了不兼容的变更。
    影响：将删除数据库 Volume，所有业务数据将永久丢失。
    替代方案：可以用 ALTER TABLE 迁移 schema，不需要删库。
    是否确认执行？
```

### 备份建议
生产环境建议配置定期备份：
```bash
# PostgreSQL 备份
docker exec <db_container> pg_dump -U <user> <database> > backup_$(date +%Y%m%d).sql

# MySQL 备份
docker exec <db_container> mysqldump -u <user> -p<password> <database> > backup_$(date +%Y%m%d).sql

# Volume 备份
docker run --rm -v <volume_name>:/data -v $(pwd):/backup alpine tar czf /backup/volume_$(date +%Y%m%d).tar.gz /data
```

## 十一、部署后检查清单

每次部署完成后，必须执行以下验证：

```bash
# 1. 数据库端口不可外部访问
timeout 3 nc -z {server_ip} {db_port} && echo "FAIL" || echo "PASS"

# 2. 后端端口不可外部直连
timeout 3 nc -z {server_ip} {backend_port} && echo "FAIL" || echo "PASS"

# 3. 敏感文件不可下载
curl -s -o /dev/null -w "%{http_code}" http://{server}/.git/config  # 必须 404
curl -s -o /dev/null -w "%{http_code}" http://{server}/.env          # 必须 404

# 4. 正常服务可用
curl -s http://{server}/api/health  # 必须返回 200

# 5. 安全头存在
curl -sI http://{server}/ | grep -i "x-frame-options"  # 必须有输出

# 6. 非法方法被拒绝
curl -s -o /dev/null -w "%{http_code}" -X DELETE http://{server}/api/health  # 必须 403/405

# 7. Volume 存在且数据完整
docker volume ls | grep {volume_name}  # 必须存在
```

## 十二、违规处理流程

当 AI 检测到操作违反以上任何规则时：

1. **立即停止**当前操作
2. **明确告知**用户违反了哪条规则
3. **说明风险**（可能导致的安全后果）
4. **等待用户确认**后才能继续执行
5. 如果用户坚持违规操作，在代码中添加 `# SECURITY WARNING: 用户已确认此操作` 注释
