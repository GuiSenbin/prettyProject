<!-- 登录页面：承载手机号登录、社交登录和协议入口。 -->
<template>
  <section class="login-page">
    <div class="login-shell">
      <img class="login-bg" src="@/assets/images/登录页-背景.png" alt="" />
      <div class="login-content">
        <BrandIcon />
        <form class="login-form" @submit.prevent="handleLogin">
          <div class="glass-input">
            <label class="phone-row">
              <span>+86</span>
              <input v-model="phone" inputmode="tel" maxlength="20" placeholder="请输入手机号" />
            </label>
            <label class="code-row">
              <input v-model="code" inputmode="numeric" maxlength="6" placeholder="请输入验证码" />
              <button class="btn btn-ghost code-button" type="button" @click="handleCode">获取验证码</button>
            </label>
          </div>
          <button class="btn btn-primary login-button" type="submit">一键登录</button>
          <div class="divider">
            <span></span>
            <strong>其他登录方式</strong>
            <span></span>
          </div>
          <div class="social-logins">
            <SocialLoginButton name="微信" type="wechat" @login="handleSocialLogin" />
            <SocialLoginButton name="支付宝" type="alipay" @login="handleSocialLogin" />
          </div>
          <label class="agreement" :class="{ checked: agreed }">
            <input v-model="agreed" type="checkbox" />
            <span></span>
            <em>
              我已阅读并同意
              <a @click.prevent.stop="activeDoc = 'agreement'">《用户协议》</a>
              与
              <a @click.prevent.stop="activeDoc = 'privacy'">《隐私政策》</a>
            </em>
          </label>
        </form>
      </div>
    </div>
    <PrivacyConsentDialog v-model="activeDoc" />
  </section>
</template>

<script setup>
import { ref } from 'vue'
import BrandIcon from './components/BrandIcon.vue'
import PrivacyConsentDialog from './components/PrivacyConsentDialog.vue'
import SocialLoginButton from './components/SocialLoginButton.vue'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'

const emit = defineEmits(['logged-in'])
const appStore = useAppStore()
const userStore = useUserStore()
const phone = ref('')
const code = ref('')
const agreed = ref(false)
const activeDoc = ref('')

function assertAgreement() {
  if (agreed.value) return true
  appStore.showToast('请先阅读并同意用户协议与隐私政策', 'warning')
  return false
}

function handleCode() {
  if (!phone.value.trim()) {
    appStore.showToast('请先输入手机号', 'warning')
    return
  }
  appStore.showToast('验证码已发送（演示）', 'success')
}

function handleLogin() {
  if (!assertAgreement()) return
  userStore.login(maskPhone(phone.value.trim()))
  appStore.showToast('登录成功，欢迎使用智颜 AI', 'success')
  emit('logged-in')
}

function handleSocialLogin(name) {
  if (!assertAgreement()) return
  userStore.login(name === '微信' ? '微信用户' : '支付宝用户')
  appStore.showToast(`${name}登录成功`, 'success')
  emit('logged-in')
}

function maskPhone(value) {
  if (!value) return '186****0905'
  const digits = value.replace(/\D/g, '')
  if (digits.length < 7) return value
  return `${digits.slice(0, 3)}****${digits.slice(-4)}`
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100dvh;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #f4fbfb;
}
.login-shell {
  position: relative;
  width: min(100vw, 430px);
  height: 100dvh;
  max-height: 932px;
  min-height: 667px;
  overflow: hidden;
  background: #f4fbfb;
}
.login-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
.login-content {
  position: relative;
  z-index: 1;
  min-height: 100%;
  display: grid;
  grid-template-rows: auto auto;
  align-content: start;
  gap: clamp(30px, 5dvh, 48px);
  padding: clamp(142px, 24dvh, 198px) 32px 28px;
}
.login-form {
  display: grid;
  gap: 14px;
}
.glass-input {
  min-height: 124px;
  display: grid;
  grid-template-rows: 1fr 1fr;
  padding: 18px 28px;
  margin: 0 -12px;
  background: url('@/assets/images/登录页-input.png') center / 100% 100% no-repeat;
}
.phone-row,
.code-row {
  display: flex;
  align-items: center;
  gap: 18px;
  min-width: 0;
}
.code-row {
  justify-content: space-between;
}
.phone-row {
  border-bottom: 1px solid rgba(140, 161, 164, 0.18);
}
.phone-row span {
  color: rgba(25, 39, 42, 0.44);
  font-size: 15px;
  font-weight: 600;
}
.glass-input input {
  min-width: 0;
  flex: 1;
  border: 0;
  background: transparent;
  color: $text-primary;
  font-size: 15px;
  outline: none;
}
.glass-input input::placeholder {
  color: rgba(83, 101, 105, 0.48);
}
.code-button {
  flex: 0 0 auto;
  width: auto;
  color: $mint-primary;
  font-size: 14px;
  font-weight: 700;
  min-height: auto;
  padding: 0;
}
.login-button {
  width: 100%;
}
.divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 18px;
  margin-top: 10px;
}
.divider span {
  height: 1px;
  background: rgba(119, 141, 145, 0.22);
}
.divider strong {
  color: rgba(75, 86, 89, 0.72);
  font-size: 14px;
  font-weight: 500;
}
.social-logins {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}
.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(63, 78, 82, 0.66);
  font-size: 12px;
  cursor: pointer;
}
.agreement input {
  display: none;
}
.agreement > span {
  position: relative;
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  border: 1.5px solid rgba(78, 105, 108, 0.34);
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.42);
  transition: $transition;
}
.agreement em {
  font-style: normal;
}
.agreement a {
  color: $mint-primary;
  text-decoration: underline;
  font-weight: 700;
}
.agreement.checked > span {
  border-color: $mint-primary;
  background: $mint-primary;
}
.agreement.checked > span::after {
  content: '';
  position: absolute;
  left: 4.5px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: 2px solid $white;
  border-left: 0;
  border-top: 0;
  transform: rotate(45deg);
}
@include respond(phone-sm) {
  .login-content {
    padding-right: 26px;
    padding-left: 26px;
  }
  .glass-input {
    padding-right: 24px;
    padding-left: 24px;
  }
}
@include respond(tablet-portrait) {
  .login-shell {
    height: min(100dvh, 932px);
    border-radius: 22px;
    box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
  }
}
@include respond(tablet-landscape) {
  .login-shell {
    height: min(100dvh, 820px);
    min-height: 667px;
    border-radius: 22px;
    box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
  }
}
@include respond(desktop) {
  .login-shell {
    height: min(100dvh, 932px);
    border-radius: 22px;
    box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
  }
}
</style>
