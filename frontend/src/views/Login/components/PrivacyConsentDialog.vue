<template>
  <transition name="slide-up">
    <!-- 当 modelValue 不为空时，渲染底层遮罩和滑出的文档抽屉 -->
    <div v-if="modelValue" class="drawer-overlay" @click.self="close">
      <div class="document-drawer">
        <header class="drawer-header">
          <h3>{{ modelValue === 'agreement' ? '《用户协议》' : '《隐私政策》' }}</h3>
          <button class="close-btn" @click="close">✕</button>
        </header>
        
        <div class="drawer-content">
          <!-- 用户协议正文 -->
          <div v-if="modelValue === 'agreement'" class="doc-text">
            <h4>1. 服务说明</h4>
            <p>「智颜 AI」是一款依托人工智能技术，为用户提供科学测肤、化妆品成分安全扫描、个人护肤档案建立、及智能妆容搭配建议的个人美妆助手。本平台提供的所有AI推荐、成分防雷分析均基于现有公开科研数据及算法模型推理生成。</p>
            
            <h4>2. 用户行为规范</h4>
            <p>您在使用本平台时，应遵守法律法规。严禁上传包含暴力、色情、侵犯他人隐私或肖像权的照片或文字。严禁以非正常手段（如网络爬虫、暴力接口请求）抓取本平台的数据、UI 界面或算法推理结果。若用户违反上述规定，平台有权暂停、封禁其账号。</p>
            
            <h4>3. 知识产权声明</h4>
            <p>3.1 平台所有的 UI 视觉设计、薄荷绿主题资产、商标、Logo、算法模型、前端及后端源码的版权均归本平台官方所有。</p>
            <p>3.2 用户上传的原始皮肤测试照片版权归用户本人所有。本平台在分析完成后，仅为提供测肤报告而限时处理，不保留且不将照片用于任何商业运作。</p>
            
            <h4>4. AI 生成免责声明</h4>
            <p class="warning-text">⚠️ 核心提醒：本平台 AI 顾问小蜜给出的所有肤质诊断、护肤防雷建议、以及成分匹配结论，仅作为日常美容、保养与社交搭配之参考，不具备任何临床治疗建议或专业医疗诊断效力。如您的皮肤出现严重病理性过敏、皮炎等症状，必须前往正规医院皮肤科就诊，平台不对 AI 生成结果的绝对准确性、绝对安全承诺或特定审美期望负责。</p>
            
            <h4>5. 服务中断与免责</h4>
            <p>因三方云服务器故障、网络延迟、不可抗力等原因导致系统临时宕机或服务中断，平台将努力尽快修复，但不承担由此带来的任何直接或间接损失赔偿责任。</p>
          </div>

          <!-- 隐私政策正文 -->
          <div v-if="modelValue === 'privacy'" class="doc-text">
            <h4>1. 我们如何收集和使用您的信息</h4>
            <p>我们遵循“最小必要原则”收集数据，用于维护核心测肤业务的安全运行：</p>
            <ul>
              <li><b>设备与日志信息</b>：仅为了进行 Crash 闪退分析、风控安全校验及不同机型的屏幕自适应，收集您的设备型号、操作系统版本。</li>
              <li><b>相机与相册权限</b>：仅在您拍照测肤或上传头像时使用。我们在此<b>庄严承诺：您上传的所有照片和面部特征数据，均在云端即时 AI 推理完成后的 24 小时内完全在服务器端物理抹除，不保留任何备份，绝不用于模型二次迭代或广告推送。</b></li>
            </ul>

            <h4>2. 数据存储与安全</h4>
            <p>我们收集的所有个人信息均依法存储于中国境内的安全云服务器中，并采取 HTTPS 双向加密传输等强力保卫技术，防止数据泄露、滥用或非授权篡改。</p>

            <h4>3. 第三方 SDK 目录披露</h4>
            <p>为了保障一键快捷登录和系统运行稳定性，我们接入了以下第三方 SDK，它们的数据收集及政策链接如下：</p>
            <table class="sdk-table">
              <thead>
                <tr>
                  <th>SDK名称</th>
                  <th>收集目的</th>
                  <th>收集字段</th>
                  <th>合规链接</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>微信登录 SDK</td>
                  <td>微信一键登录</td>
                  <td>微信昵称、头像、OpenID</td>
                  <td><a href="https://weixin.qq.com/cgi-bin/readtemplate?t=weixin_agreement&s=privacy" target="_blank">微信隐私政策</a></td>
                </tr>
                <tr>
                  <td>支付宝 SDK</td>
                  <td>支付宝快捷登录</td>
                  <td>支付宝唯一账号标识、昵称</td>
                  <td><a href="https://render.alipay.com/p/yuyan/180020000001192914/preview.html" target="_blank">支付宝隐私政策</a></td>
                </tr>
              </tbody>
            </table>

            <h4>4. 您的个人权利</h4>
            <p>您有权查询、修正、更正您的个人美妆档案及添加的产品库。如需彻底删除数据，您只需在个人档案页点击“退出登录（重置档案）”按钮，系统将立即永久注销您的本站身份，并从本地 `localStorage` 以及后台服务器中彻底擦除您所有的测肤与避雷历史记录，不作留存。</p>
          </div>
        </div>

        <footer class="drawer-footer">
          <button class="btn btn-agree btn-block" @click="close">我已阅读并返回</button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', '')
}
</script>

<style lang="scss" scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(18, 38, 39, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
/* 抽屉阅读面板 */
.document-drawer {
  position: relative;
  width: 100%;
  max-width: 430px;
  height: 85vh;
  background: $white;
  border-radius: 28px 28px 0 0;
  box-shadow: 0 -15px 50px rgba(11, 47, 50, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}
.drawer-header {
  height: 60px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(140, 161, 164, 0.12);
  flex: 0 0 auto;
  h3 {
    font-size: 17px;
    font-weight: 700;
    color: rgba(30, 48, 51, 0.9);
  }
  .close-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(140, 161, 164, 0.1);
    border: 0;
    font-size: 14px;
    color: rgba(92, 108, 110, 0.8);
    cursor: pointer;
    transition: $transition;
    &:hover {
      background: rgba(140, 161, 164, 0.2);
    }
  }
}
.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  box-sizing: border-box;
  -webkit-overflow-scrolling: touch;
}
.doc-text {
  color: rgba(62, 79, 82, 0.88);
  line-height: 1.7;
  font-size: 13px;
  text-align: left;
  h4 {
    font-size: 14px;
    color: rgba(22, 38, 41, 0.92);
    margin: 20px 0 8px;
    font-weight: 700;
  }
  p {
    margin: 0 0 10px;
  }
  .warning-text {
    background: rgba(230, 162, 60, 0.06);
    border-left: 3px solid #e6a23c;
    padding: 10px 14px;
    border-radius: 4px;
    color: #b88230;
    font-size: 12.5px;
  }
  ul {
    padding-left: 18px;
    margin-bottom: 12px;
  }
  .sdk-table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 12px;
    th, td {
      border: 1px solid rgba(140, 161, 164, 0.18);
      padding: 8px;
      text-align: left;
    }
    th {
      background: rgba(45, 143, 111, 0.05);
      color: $mint-dark;
      font-weight: 600;
    }
    a {
      color: $mint-primary;
      text-decoration: underline;
    }
  }
}
.drawer-footer {
  padding: 16px 24px calc(16px + env(safe-area-inset-bottom));
  border-top: 1px solid rgba(140, 161, 164, 0.12);
  flex: 0 0 auto;
  .btn-block {
    width: 100%;
    height: 48px;
    border-radius: 24px;
    font-weight: 700;
    background: $gradient-primary;
    color: $white;
    border: 0;
    cursor: pointer;
    box-shadow: 0 8px 20px rgba(26, 122, 92, 0.2);
  }
}
/* 抽屉动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}
@media (max-width: 480px) {
  .document-drawer {
    max-width: 100vw;
  }
}
</style>
