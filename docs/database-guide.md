# 数据库治理规范

## 本地数据库

本地 SQLite 文件位于 `backend/data/miyang.db`。数据库文件、WAL 和 SHM 文件不进入版本控制。

## 迁移

数据库结构变化必须新增 Alembic migration。执行迁移使用：

```bash
./.venv/bin/alembic -c backend/alembic.ini upgrade head
```

当前迁移链：

- `20260705_0001_initial_schema.py`：创建最小 `users` 表和索引。
- `20260705_0002_chat_user_fk.py`：兼容旧迁移链的 no-op，不创建聊天表。
- `20260705_0003_clean_users_baseline.py`：把旧用户档案表迁成最小用户身份表。

## 当前表

- `users`：基础用户身份，仅包含手机号/展示名/登录类型和时间戳。

## 后续规则

产品库、AI 问答、个人档案详情都必须通过新 migration 单独建表。应用启动时禁止隐式 `DROP TABLE`。废弃表、字段清理必须通过 migration 明确执行。
