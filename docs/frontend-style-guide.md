# 前端工程规范

## 目录

- 页面：`frontend/src/views/<Module>/index.vue`
- 模块组件：`frontend/src/views/<Module>/components/`
- 全局组件：`frontend/src/components/`
- 状态：`frontend/src/stores/`
- API：`frontend/src/api/`
- 工具：`frontend/src/utils/`

## 组件归属

模块专属组件不进入全局 `components/`。产品库、产品详情、个人档案、AI 问答和设置中心都应优先在自己的 `views/<Module>/` 目录内组织页面和模块组件。

涉及用户关键操作（如上传头像、修改用户名/手机号）统一收口至 `Settings` 模块，不允许在 `Profile` 档案表单中混合呈现账号级鉴权设置。

产品库列表和产品详情之间的状态恢复由 `frontend/src/stores/product.js` 维护。涉及产品搜索、懒加载、详情返回和滚动定位时，不要在页面卸载或返回时清空这些状态。

AI 问答消息流由 `frontend/src/stores/chat.js` 维护。历史回看必须展示后端保存的 `structured_payload`，不要为了重放历史再次请求模型生成旧答案。

## 样式

SCSS 变量由 `vite.config.js` 全局注入，Vue 文件不要重复写 `@use '@/assets/styles/variables' as *;`。响应式必须使用 `_variables.scss` 中的 `respond()` mixin。

所有按钮必须使用全局按钮体系：`.btn`、`.btn-primary`、`.btn-secondary`、`.btn-ghost`、`.btn-icon`。业务页面不允许单独定义深色主按钮、重复渐变或重复阴影。

SCSS 样式声明必须严格遵循 DOM 树层级进行嵌套编写，禁止采用平铺或无关联的方式声明样式类选择器，以提高代码易读性与维护性。禁止在局部 Vue 页面中覆写或重新定义全局的标签（如 `button`）与全局类名（如 `.btn`, `.btn-secondary` 等）。若需要控制按钮的长度，请控制其父级 flex 容器。

HTML 中禁止编写任何既无实质样式挂载、又无 JS/API 绑定引用的多余 Class 类名（例如可以直接使用嵌套 `.card p` 声明的属性，禁止在子节点上写额外的类名）。样式文件中禁止残留任何未在 Template 模板里真实用到的 CSS/SCSS 类。所有样式类之间的 `}` 结束与下一个类声明必须紧贴换行，**严禁保留任何空行**。

## 断点

- `phone-sm`：小屏手机，最大 380px。
- `phone`：移动手机，最大 767px。
- `tablet-portrait`：iPad 竖屏，768px 到 1023px。
- `tablet-landscape`：iPad 横屏，1024px 到 1279px。
- `desktop`：桌面，1280px 及以上。

## 图标

通用操作图标使用 `lucide-vue-next`。微信、支付宝等品牌图标用本地 SVG 组件封装。

## API 调用

`frontend/src/api/request.js` 只负责 axios 实例、baseURL、fallback 和错误处理。每个业务模块恢复后必须有自己的 API 文件，例如 `user.js`、`product.js`。

业务层不要直接拼后端 URL，也不要在 store 或组件里直接调用 `request.get('/xxx')`。store 应该调用模块 API，例如 `userApi.getUser(id)`。后端路径变化时，只允许优先改对应 API 文件。

## 环境配置

前端环境变量按 Vite mode 区分：

- `frontend/.env.development`：本地开发环境，默认通过 Vite 代理访问本地后端。
- `frontend/.env.staging`：测试/预发环境，用于上线前联调。
- `frontend/.env.production`：正式环境，只配置生产 API，不允许 fallback 到 localhost。
- `frontend/.env.example`：示例文件，用于说明必填变量。

业务代码只读取 `import.meta.env`，不要在组件、store 或模块 API 里写死正式/测试 API 域名。
