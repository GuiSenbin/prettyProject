# 数据库治理规范

## 本地数据库

本地 SQLite 文件位于 `backend/data/miyang.db`。数据库文件、WAL 和 SHM 文件不进入版本控制。

## 迁移

数据库结构变化必须新增 Alembic migration。执行迁移使用：

```bash
./.venv/bin/alembic -c backend/alembic.ini upgrade head
```

`backend/alembic/versions/*.py` 是数据库结构的迁移历史，属于项目代码，需要进入版本控制。即使某个迁移来自早期迭代，只要它仍在 `down_revision` 链上，就不能单独删除，否则新环境无法从空库升级到当前表结构。

不要提交的是本地数据库文件、WAL/SHM 文件、`__pycache__/`、`*.pyc` 等运行缓存。

当前迁移链：

- `20260705_0001_initial_schema.py`：创建最小 `users` 表和索引。
- `20260705_0002_chat_user_fk.py`：兼容旧迁移链的 no-op，不创建聊天表。
- `20260705_0003_clean_users_baseline.py`：把旧用户档案表迁成最小用户身份表。
- `20260705_0004_auth_table_split.py`：分离出用户授权凭证表 `user_social_auths` 以解耦多端登录映射，并使 `users.phone` 设为可空。
- `20260706_0005_user_profiles.py`：新增个人护肤档案表 `user_profiles`，与 `users.id` 一对一关联。
- `20260712_0006_products.py`：新增产品主表、成分表、产品-成分关联表和个人产品库表。
- `20260712_0007_product_source_url.py`：为产品表增加来源链接字段。
- `e947615dbf1b_add_safety_level_and_purposes.py`：为成分补充安全等级和使用目的。
- `20260713_0009_drop_product_import_candidates.py`：清理早期产品导入候选表。
- `20260713_0010_product_compliance_fields.py`：为产品表增加备案号和品牌起源国家字段。
- `20260715_0011_chat_sessions.py`：新增 AI 问答会话表、消息表和脱敏问答日志表。
- `96b5381de25e_add_avatar_url.py`：为用户表增加头像地址字段。

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

### 4. `user_profiles`（个人护肤档案表）
存放护肤推荐所需的结构化档案，与账号体系解耦：
* `user_id`：关联 `users.id`，每个用户最多一份档案。
* `gender`、`age`：基础画像，用于条件展示和推荐分层。
* `skin_type`、`skin_tone`、`face_shape`、`skin_concerns`：肤况和脸型信息。
* `known_allergies`、`pregnancy_status`、`period_acne`、`last_period_start`、`cycle_length_days`：安全避雷和女性条件字段。
* `preference_notes`：偏好、禁忌和生活习惯等自由文本。

### 5. `chat_sessions`（AI 问答会话表）
存放用户 AI 问答会话摘要：
* `user_id`：关联 `users.id`，历史会话必须按登录用户隔离。
* `title`、`title_edited`：会话标题和用户是否手动重命名。
* `deleted_at`：软删除时间，前端历史不展示已删除会话。

### 6. `chat_messages`（AI 问答消息表）
存放完整对话消息：
* `session_id`：关联 `chat_sessions.id`。
* `role`、`content_text`：消息角色与文本内容。
* `structured_payload`：AI 回答结构化卡片数据，用于历史回看时原样展示。
* `intent`、`subject_type`：意图和主体归属，供后续提示词与知识库优化。

### 7. `chat_question_logs`（脱敏问答日志表）
存放后续高频知识库建设所需的脱敏问答线索：
* `normalized_question`：脱敏后的用户问题。
* `intent`、`subject_type`、`context_used`：问题分类与上下文使用情况。
* `source`：回答来源，例如 `model`、`local_rule` 或模型不可用时的兜底来源。

### 8. 产品与成分相关表
产品库由产品事实、成分事实和用户个人产品库组成：
* `products`：产品主表，包含品牌、名称、分类、图片、来源链接、备案号、品牌起源国家等产品级事实。
* `ingredients`：成分主表，包含中文名、INCI 名、安全等级、使用目的和标签等成分级事实。
* `product_ingredients`：产品与成分的顺序关联表，用于还原完整成分表。
* `user_products`：用户个人产品库，关联当前用户和产品主库；历史数据必须按登录用户隔离。

### 9. V3 长期摘要规划
当前 AI 模型上下文只取当前会话最近 8 条消息，完整消息仍保存于 `chat_messages`。如果 V3 新增长期摘要/压缩历史会话能力，需要新增独立表或字段保存结构化摘要，例如：
* 摘要覆盖的会话 ID 和消息范围。
* 近期肤况、过敏/禁忌、正在使用的产品、用户目标和待确认问题。
* 摘要更新时间、生成来源和失效策略。

长期摘要不能替代个人档案。稳定且需要长期使用的信息，应由用户确认后写入 `user_profiles` 或专门的长期记忆结构。
