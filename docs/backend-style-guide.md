# 后端工程规范

## 模块结构

每个后端模块统一包含：

- `router.py`：HTTP 路由，只处理请求、响应和依赖注入。
- `schemas.py`：Pydantic 入参和出参。
- `models.py`：SQLAlchemy 模型。
- `service.py`：业务逻辑和跨仓储编排。
- `repository.py`：数据库读写。

## 分层规则

API 层不直接写业务判断和复杂数据库查询。业务判断进入 service，数据库读写进入 repository。跨模块调用优先通过 service 或 repository 的明确接口完成。

## 错误处理

路由和 service 可以抛出 `HTTPException`。错误文案必须面向用户可理解，不暴露数据库和内部实现细节。

## 文件注释

每个 Python 文件开头必须有模块 docstring，说明该文件职责。
