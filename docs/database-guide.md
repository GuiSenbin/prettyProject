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
- `20260705_0004_auth_table_split.py`：分离出用户授权凭证表 `user_social_auths` 以解耦多端登录映射，并使 `users.phone` 设为可空。
- `20260706_0005_user_profiles.py`：新增个人护肤档案表 `user_profiles`，与 `users.id` 一对一关联。

## 当前表与企业级账号体系

系统采用**「用户主体（User Core）与 授权凭证（User Auth）解耦分离」**的双表架构设计，为后续增加多登录渠道（如微信、支付宝、抖音、苹果登录）以及打通/合并账号提供高扩展性保障。

### 1. `users`（用户主表）
存放与任何登录方式都无关的公共用户核心属性：
* `id` (INTEGER, PK)：系统全局唯一用户标识。
* `phone` (VARCHAR, Unique, Nullable)：绑定手机号（实名合规基础，可空支持先体验再绑定）。
* `display_name` (VARCHAR)：展示昵称。
* `avatar_url` (VARCHAR, Nullable)：头像静态访问链接，支持本地 static 目录或 OSS 访问。
* `login_type` (VARCHAR)：最近一次的登录方式（如 username, phone 等）。

### 2. `user_social_auths`（用户授权凭证表）
集中管理用户所有的登录账号和渠道标识，实现无限横向扩充：
* `id` (INTEGER, PK)：自增主键。
* `user_id` (INTEGER, FK)：关联 `users.id`，代表凭证属于哪位用户。
* `identity_type` (VARCHAR)：认证渠道类型，包括 `'username'` (用户名密码)、`'phone'` (手机验证码/密码)、`'wechat'` (微信)、`'alipay'` (支付宝) 等。
* `identifier` (VARCHAR)：该登录渠道下的唯一标识（用户名、手机号、微信 `unionid`、支付宝 `user_id` 等）。
* `credential` (VARCHAR, Nullable)：密码密钥凭证（存放 PBKDF2 哈希加密值；三方登录可留空或存放 Token）。

### 3. 多渠道账号合并与打通规则
* 当用户使用微信或支付宝首次授权进入系统时，若对应 `unionid` 不存在，系统会自动在 `users` 创建主账号并往 `user_social_auths` 绑定一条微信号凭证，允许其“先免绑体验”。
* 用户后续进行手机号绑定认证时，系统会在 `user_social_auths` 检索该手机号：
  * **若手机号已被其他账号独立绑定**：直接将当前微信号的 `user_id` 更改映射为手机号的老账号 ID，以极低的 DDL 成本在 1 秒内无缝完成跨渠道账号数据打通与合并。

## 后续规则

产品库、AI 问答、个人档案详情都必须通过新 migration 单独建表。应用启动时禁止隐式 `DROP TABLE`。废弃表、字段清理必须通过 migration 明确执行。

产品库、AI 问答、个人档案详情都必须通过新 migration 单独建表。应用启动时禁止隐式 `DROP TABLE`。废弃表、字段清理必须通过 migration 明确执行。

### 4. `user_profiles`（个人护肤档案表）
存放护肤推荐所需的结构化档案，与账号体系解耦：
* `user_id`：关联 `users.id`，每个用户最多一份档案。
* `gender`、`age`：基础画像，用于条件展示和推荐分层。
* `skin_type`、`skin_tone`、`face_shape`、`skin_concerns`：肤况和脸型信息。
* `known_allergies`、`pregnancy_status`、`period_acne`、`last_period_start`、`cycle_length_days`：安全避雷和女性条件字段。
* `preference_notes`：偏好、禁忌和生活习惯等自由文本。
