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
- 上传前文件审查：确认不提交 `.DS_Store`、`__pycache__/`、`*.pyc`、`.env`、`.venv/`、`node_modules/`、`frontend/dist/` 等本地缓存、敏感配置、依赖目录和构建产物。
- 分支上传：上传前确认当前工作分支、目标分支和环境分支，避免把业务改动推到错误分支。

## 变更归档

- 2026-07-20：同步 README 与 docs 宪法到当前 2.0 口径；确认 V2 真实大模型接入已完成，并将 V3 规划扩展为 AI 答案精细化、长期摘要和压缩历史会话。
- 2026-07-16：新增 AI 问答多会话、历史回看、重命名、软删除、脱敏问答日志和登录态鉴权；同步恢复 Chat 前端问答页、侧边栏历史会话入口及相关文档规范。
- 2026-07-15：增强产品适配分析提示、产品详情功效展示与补档案回跳；优化后端不可达错误提示，补充欧莱雅防晒产品素材与导入逻辑。
- 2026-07-14：新增产品库主库、个人产品库、产品详情、成分分析、产品静态图、统一接口响应封装及相关迁移和测试；同步调整顶部导航与设置/档案返回逻辑。

## 文档归档

长期规范放在 `docs/` 根目录。阶段性审计、一次性排查和专项治理记录统一放入 `docs/audits/`，文件名使用 `YYYY-MM-topic.md`。

## 交付规则

不能只因为代码写完就交付。必须完成结构审核、样式审核、提示词审核、接口 smoke test 和构建验证。
