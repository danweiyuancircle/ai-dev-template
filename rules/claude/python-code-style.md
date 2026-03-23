---
name: python-code-style
description: Python + FastAPI 代码规范
type: claude-rule
tags: [python, fastapi, code-style]
version: 1.0.0
author: chances
---

# Python + FastAPI 代码规范

所有 Python / FastAPI 项目必须遵循以下规范。AI 生成或修改代码时，必须严格按照这些规则执行。

## 一、项目结构

### 强制规则
- 使用 `pyproject.toml` 作为项目元数据和依赖管理的唯一入口（不再使用 `setup.py` / `setup.cfg`）
- 推荐使用 `uv` 管理依赖，次选 `pip` + `requirements.txt`
- 必须有 `.gitignore`（至少包含 `__pycache__/`、`*.pyc`、`.env`、`dist/`、`*.egg-info/`）
- 必须有 `.python-version` 文件声明 Python 版本

### 标准目录结构
```
project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI 应用入口
│       ├── config.py            # Settings 配置
│       ├── dependencies.py      # 全局依赖（数据库会话、认证等）
│       ├── exceptions.py        # 自定义异常 + 异常处理器
│       ├── models/              # SQLAlchemy / ORM 模型
│       │   ├── __init__.py
│       │   └── user.py
│       ├── schemas/             # Pydantic 请求/响应 schema
│       │   ├── __init__.py
│       │   └── user.py
│       ├── routers/             # 路由模块（按业务域拆分）
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/            # 业务逻辑层
│       │   ├── __init__.py
│       │   └── user.py
│       └── utils/               # 工具函数
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── alembic/                     # 数据库迁移
│   ├── env.py
│   └── versions/
├── alembic.ini
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .python-version
├── .env.example
└── .gitignore
```

- 小型脚本/单文件项目可以不使用 `src/` 布局
- 测试文件统一放在 `tests/` 目录，文件名以 `test_` 开头

### 分层原则

| 层 | 职责 | 禁止 |
|---|---|---|
| `routers/` | 接收请求、参数校验、调用 service、返回响应 | 不写业务逻辑、不直接操作数据库 |
| `services/` | 业务逻辑、事务编排 | 不感知 HTTP 概念（Request/Response/状态码） |
| `models/` | ORM 模型定义 | 不包含业务逻辑 |
| `schemas/` | Pydantic 请求/响应模型 | 不依赖 ORM 模型 |
| `dependencies.py` | FastAPI 依赖注入（DB session、当前用户等） | 不写业务逻辑 |

## 二、Python 版本与兼容性

### 强制规则
- 新项目最低支持 Python 3.10+
- 使用现代语法特性：

| 旧写法 | 新写法（强制） |
|---|---|
| `typing.List[int]` | `list[int]` |
| `typing.Dict[str, int]` | `dict[str, int]` |
| `typing.Optional[str]` | `str \| None` |
| `typing.Union[str, int]` | `str \| int` |
| `typing.Tuple[int, ...]` | `tuple[int, ...]` |
| `from __future__ import annotations` | 不需要（3.10+ 原生支持） |

## 三、代码风格

### 格式化与 Lint
- 使用 `ruff` 作为唯一的 linter + formatter（替代 flake8 / black / isort）
- `pyproject.toml` 中的最小 ruff 配置：

```toml
[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "RUF",  # ruff-specific
]

[tool.ruff.lint.isort]
known-first-party = ["app"]
```

### 命名规范

| 类型 | 风格 | 示例 |
|---|---|---|
| 模块/包 | `snake_case` | `user_service.py` |
| 函数/方法 | `snake_case` | `get_user_by_id()` |
| 变量 | `snake_case` | `user_count` |
| 类 | `PascalCase` | `UserService` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| 私有属性/方法 | `_leading_underscore` | `_parse_token()` |
| 类型变量 | `PascalCase` | `T = TypeVar("T")` |
| 协议/抽象基类 | `PascalCase` + 语义后缀 | `Serializable`、`BaseRepository` |
| 路由函数 | `snake_case` 动词开头 | `create_user()`、`list_orders()` |
| Pydantic Schema | `PascalCase` + 用途后缀 | `UserCreate`、`UserResponse`、`UserUpdate` |

### 禁止的写法

```python
# ❌ 单字母变量（循环索引除外）
d = get_data()

# ✅ 有意义的名称
user_data = get_data()

# ❌ 匈牙利命名法
str_name = "Alice"
lst_users = []

# ✅ 直接命名
name = "Alice"
users = []

# ❌ 布尔变量不带 is/has/can/should 前缀
active = True

# ✅ 布尔变量语义明确
is_active = True
has_permission = False
```

## 四、类型标注

### 强制规则
- 所有公开函数/方法**必须**有参数和返回值类型标注
- 私有函数**推荐**有类型标注
- 类属性**必须**有类型标注

```python
# ❌ 缺少类型标注
def get_user(user_id):
    ...

# ✅ 完整标注
def get_user(user_id: int) -> User | None:
    ...

# ✅ 复杂类型使用 TypeAlias
type UserMap = dict[str, list[User]]

# ✅ 数据类必须标注
@dataclass
class UserProfile:
    name: str
    age: int
    email: str | None = None
```

### 禁止 `Any`
- 不得使用 `Any` 作为"懒标注"，除非与外部动态库交互且无法确定类型
- 使用 `Any` 时必须附注释说明原因

## 五、FastAPI 路由与接口设计

### 路由组织

```python
# routers/user.py
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    body: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.create(body)
```

### 强制规则
- 每个路由模块使用独立 `APIRouter`，在 `main.py` 中统一注册
- **禁止**所有路由写在 `main.py` 中（超过 2 个路由必须拆分）
- 路由函数只做：参数接收 → 调用 service → 返回结果，**不写业务逻辑**
- 必须显式声明 `status_code` 和 `response_model`
- 路由路径使用复数名词 + RESTful 风格

### RESTful 路由规范

| 操作 | 方法 | 路径 | 状态码 |
|---|---|---|---|
| 列表查询 | `GET` | `/users` | 200 |
| 详情查询 | `GET` | `/users/{user_id}` | 200 |
| 创建 | `POST` | `/users` | 201 |
| 全量更新 | `PUT` | `/users/{user_id}` | 200 |
| 部分更新 | `PATCH` | `/users/{user_id}` | 200 |
| 删除 | `DELETE` | `/users/{user_id}` | 204 |

### 分页查询

```python
# schemas/common.py
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int

# routers/user.py
@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserResponse]:
    return await service.list(pagination)
```

## 六、Pydantic Schema 规范

### 强制规则
- 请求和响应使用不同的 Schema，**禁止**复用同一个 Model

```python
# schemas/user.py

class UserBase(BaseModel):
    """共享字段基类"""
    name: str = Field(max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """创建请求"""
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    """更新请求 - 所有字段可选"""
    name: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None

class UserResponse(UserBase):
    """响应"""
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

- **禁止**在响应 Schema 中暴露密码、内部 ID、敏感字段
- 使用 `Field()` 添加校验约束（`min_length`、`ge`、`le`、`pattern` 等）
- 更新 Schema 的字段必须全部可选（`None` 默认值）

## 七、依赖注入

### 强制规则
- 数据库会话、当前用户、配置等通过 `Depends()` 注入
- **禁止**在路由函数中直接创建数据库会话或实例化 service

```python
# dependencies.py
from collections.abc import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await authenticate(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="认证失败")
    return user

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)
```

```python
# ❌ 路由中直接创建会话
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    async with async_session_factory() as db:
        user = await db.get(User, user_id)
        return user

# ✅ 依赖注入
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.get_by_id(user_id)
```

## 八、异常处理

### 统一异常体系

```python
# exceptions.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

# 业务异常基类
class AppError(Exception):
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR") -> None:
        self.message = message
        self.code = code

class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: int | str) -> None:
        super().__init__(
            message=f"{resource} 不存在",
            code="NOT_FOUND",
        )
        self.resource = resource
        self.resource_id = resource_id

class BusinessError(AppError):
    """业务规则校验失败"""
    pass

class PermissionDeniedError(AppError):
    """权限不足"""
    pass

# 注册异常处理器
def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(request: Request, exc: PermissionDeniedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"code": exc.code, "message": exc.message},
        )
```

### 强制规则
- **禁止**在 service 层抛出 `HTTPException`（service 不感知 HTTP）
- service 层抛出业务异常，由异常处理器统一转换为 HTTP 响应
- **禁止**裸 `except:` 或 `except Exception: pass`
- 错误响应格式统一为 `{"code": "ERROR_CODE", "message": "描述"}`
- **禁止**在错误消息中回显用户输入

```python
# ❌ service 中抛 HTTPException
class UserService:
    async def get_by_id(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404)  # 耦合 HTTP
        return user

# ✅ service 中抛业务异常
class UserService:
    async def get_by_id(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundError("用户", user_id)
        return user
```

## 九、数据库与 ORM

### 强制规则
- 使用 **SQLAlchemy 2.0** 风格（声明式映射 + async）
- 数据库迁移使用 **Alembic**，**禁止**手动执行 DDL
- **禁止**在路由层直接写 SQL 查询

```python
# models/base.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

# models/user.py
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(default=True)
```

### 异步数据库会话

```python
# config.py / database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
```

### 查询规范

```python
# ❌ 旧式查询
session.query(User).filter(User.id == user_id).first()

# ✅ SQLAlchemy 2.0 风格
result = await session.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

## 十、异步编程

### 强制规则
- FastAPI 路由函数统一使用 `async def`
- 异步函数内**禁止**调用同步阻塞操作（IO、网络、sleep）
- 使用 `asyncio.to_thread()` 包装不可避免的同步调用

```python
# ❌ 异步函数中调用同步阻塞
async def get_data():
    result = requests.get(url)          # 阻塞事件循环
    data = open("file.txt").read()      # 阻塞事件循环

# ✅ 使用异步库
async def get_data():
    async with httpx.AsyncClient() as client:
        result = await client.get(url)
    data = await asyncio.to_thread(Path("file.txt").read_text)
```

- HTTP 客户端使用 `httpx`，**禁止** `requests`
- 数据库使用异步驱动（`asyncpg`、`aiomysql`）

## 十一、中间件与生命周期

### 强制规则

```python
# main.py
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # 启动时执行
    logger.info("应用启动")
    yield
    # 关闭时执行
    await engine.dispose()
    logger.info("应用关闭")

app = FastAPI(
    title="My API",
    version="1.0.0",
    lifespan=lifespan,
)
```

- 使用 `lifespan` 管理应用生命周期，**禁止** `@app.on_event("startup")`（已废弃）
- CORS 中间件必须明确指定允许的域名，**禁止**生产环境使用 `allow_origins=["*"]`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # 从环境变量读取
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

## 十二、配置管理

### 强制规则
- 使用 Pydantic Settings 管理配置

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 应用
    app_name: str = "My API"
    debug: bool = False

    # 数据库
    database_url: str
    db_pool_size: int = 5

    # Redis
    redis_url: str = "redis://localhost:6379"

    # 认证
    secret_key: str
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()
```

- **禁止**在代码中硬编码配置值（数据库地址、密钥、端口等）
- **禁止**在模块顶层执行副作用（网络请求、数据库连接、文件读取）

## 十三、日志

### 强制规则
- 使用标准库 `logging` 或 `structlog`，**禁止** `print()` 出现在非调试代码中
- 使用 `%s` 占位符或 structlog 的结构化日志，**禁止** f-string 拼接日志

```python
# ❌ print 调试
print(f"User {user_id} not found")

# ❌ f-string 日志（参数不会延迟求值，且无法被日志聚合工具解析）
logger.info(f"User {user_id} created")

# ✅ 占位符日志
logger.info("User %s created", user_id)

# ✅ structlog
logger.info("user_created", user_id=user_id)
```

### 日志级别使用规范

| 级别 | 使用场景 |
|---|---|
| `DEBUG` | 开发调试信息，生产环境不输出 |
| `INFO` | 关键业务流程节点（用户注册、订单创建等） |
| `WARNING` | 异常但可恢复的情况（重试、降级） |
| `ERROR` | 错误但服务仍可用（单次请求失败） |
| `CRITICAL` | 服务不可用（数据库连接断开、必要服务宕机） |

## 十四、测试

### 强制规则
- 使用 `pytest` + `pytest-asyncio` + `httpx`
- 使用 `TestClient` 或 `AsyncClient` 测试 API

```python
# conftest.py
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

# test_user.py
@pytest.mark.anyio
async def test_create_user_returns_201(client: AsyncClient):
    response = await client.post("/users/", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securepass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert "password" not in data  # 响应不包含密码

@pytest.mark.anyio
async def test_get_nonexistent_user_returns_404(client: AsyncClient):
    response = await client.get("/users/99999")
    assert response.status_code == 404
```

- 测试函数名描述行为而非实现
- 测试数据使用 `pytest.fixture`，不要硬编码
- 测试结构遵循 Arrange-Act-Assert

## 十五、函数与类设计

### 强制规则

```python
# ❌ 超过 3 个位置参数
def create_user(name, age, email, role, department):
    ...

# ✅ 使用关键字参数或 Pydantic model
def create_user(request: CreateUserRequest) -> User:
    ...
```

- 函数体不超过 50 行（超过则拆分）
- 单个文件不超过 500 行（超过则拆分模块）
- 嵌套不超过 3 层（使用 early return 降低嵌套）

```python
# ❌ 深层嵌套
def process(data):
    if data:
        if data.is_valid:
            if data.has_items:
                for item in data.items:
                    ...

# ✅ 提前返回
def process(data):
    if not data:
        return
    if not data.is_valid:
        return
    if not data.has_items:
        return
    for item in data.items:
        ...
```

## 十六、数据校验与序列化

### 强制规则
- API 输入/输出使用 **Pydantic v2** 进行校验
- 内部数据结构优先使用 `dataclass`，需要校验时用 Pydantic
- **禁止**在业务逻辑中手动校验字典字段

```python
# ❌ 手动校验字典
def create_user(data: dict):
    if "name" not in data:
        raise ValueError("name required")

# ✅ Pydantic 自动校验
class CreateUserRequest(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: EmailStr
```

## 十七、常见反模式（禁止）

| 反模式 | 正确做法 |
|---|---|
| 可变默认参数 `def f(items=[])` | `def f(items: list \| None = None)` |
| `import *` | 显式导入 |
| 循环导入 | 重构模块或延迟导入 |
| 全局可变状态 | 依赖注入 |
| `os.path` 字符串拼接 | `pathlib.Path` |
| `datetime.now()` 无时区 | `datetime.now(tz=UTC)` |
| 手动拼接 SQL | ORM 或参数化查询 |
| `== True` / `== None` | `is True` / `is None` |
| `len(x) == 0` | `not x` |
| `type(x) == SomeType` | `isinstance(x, SomeType)` |
| `dict.keys()` 遍历 | 直接 `for k in dict` |
| 嵌套字典传递数据 | `dataclass` / `TypedDict` / Pydantic model |
| `@app.on_event("startup")` | `lifespan` context manager |
| service 层抛 `HTTPException` | 抛业务异常，异常处理器转换 |
| 路由里写数据库查询 | 调用 service 层 |
| `allow_origins=["*"]`（生产） | 明确列出允许的域名 |

## 十八、注释与文档

### 强制规则
- 注释用于解释 **为什么（why）**，而非 **做了什么（what）**
- 公开 API / 库函数必须有 docstring（Google 风格）
- 内部函数不需要 docstring，代码本身应自解释

```python
# ❌ 无用注释
# 获取用户
user = get_user(user_id)

# ✅ 解释原因
# 此处使用缓存查询，因为用户表 QPS 超过 5000
user = cache.get_user(user_id)
```

### API 文档
- 路由函数的 docstring 会自动生成 OpenAPI 描述，保持简洁
- 使用 `summary` 参数替代 docstring 标题

```python
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="创建用户",
)
async def create_user(body: UserCreate) -> UserResponse:
    """根据提交的信息创建新用户，邮箱不可重复。"""
    ...
```

## 十九、安全编码

### 强制规则
- SQL 查询必须使用参数化绑定，**禁止**字符串拼接
- 用户输入必须校验后使用，**禁止**直接信任
- 文件路径操作必须防止路径遍历攻击
- 序列化/反序列化**禁止** `pickle.loads()` 处理不可信数据
- 密码存储必须使用 `bcrypt` / `argon2`，**禁止**明文或 MD5/SHA
- JWT 密钥从环境变量读取，**禁止**硬编码

```python
# ❌ SQL 注入
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ 参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ 路径遍历
file_path = f"/uploads/{user_input_filename}"

# ✅ 路径安全校验
safe_path = Path("/uploads") / Path(user_input_filename).name

# ❌ 硬编码密钥
SECRET_KEY = "my-super-secret-key"

# ✅ 环境变量
SECRET_KEY = settings.secret_key
```
