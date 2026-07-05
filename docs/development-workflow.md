# 开发流程规范

## 新增需求

1. 判断需求所属模块。
2. 前端改动放入对应 `views/<Module>/`。
3. 后端改动放入对应 `modules/<module>/`。
4. 涉及数据库结构时新增 Alembic migration。
5. 更新相关规范文档或模块边界说明。

## 环境命令

- 本地开发：`npm run dev`
- 测试环境构建：`npm run build:staging`
- 正式环境构建：`npm run build:production`

前端接口地址由 `frontend/.env.development`、`frontend/.env.staging`、`frontend/.env.production` 控制。不要在业务代码里写死测试或正式 API 地址。

## 提交前检查

- 前端构建：`npm run build`
- 后端编译：`./.venv/bin/python -m compileall backend/app`
- 数据库迁移：`./.venv/bin/alembic -c backend/alembic.ini upgrade head`
- 旧模块残留搜索：确认没有无关旧路由、旧页面和旧表操作。

## 文档归档

长期规范放在 `docs/` 根目录。阶段性审计、一次性排查和专项治理记录统一放入 `docs/audits/`，文件名使用 `YYYY-MM-topic.md`。

## 交付规则

不能只因为代码写完就交付。必须完成结构审核、样式审核、提示词审核、接口 smoke test 和构建验证。
