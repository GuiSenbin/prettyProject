<template>
  <section class="login-page">
    <div class="login-shell">
      <img src="@/assets/images/登录页-背景.png" alt="" />
      <div class="login-content">
        <BrandIcon />
        <form class="login-form" @submit.prevent="handleLogin">
          <div class="glass-input">
            <label class="phone-row">
              <input v-model="username" maxlength="50" placeholder="请输入账号/手机号" />
            </label>
            <label class="code-row">
              <input v-model="password" :type="showPassword ? 'text' : 'password'" maxlength="50" placeholder="请输入密码" />
              <button class="toggle-password" type="button" @click="showPassword = !showPassword">
                <Eye v-if="showPassword" :size="18" />
                <EyeOff v-else :size="18" />
              </button>
            </label>
          </div>
          <button class="btn btn-primary" type="submit">一键登录</button>
          <div class="divider">
            <span></span>
            <strong>其他登录方式</strong>
            <span></span>
          </div>
          <div class="social-logins">
            <SocialLoginButton name="微信" type="wechat" @login="handleSocialLogin" />
            <SocialLoginButton name="支付宝" type="alipay" @login="handleSocialLogin" />
          </div>
        </form>
        <label class="agreement" :class="{ checked: agreed }">
          <input v-model="agreed" type="checkbox" />
          <span></span>
          <em>我已阅读并同意<a @click.stop="activeDoc = 'user'">《用户协议》</a>与<a @click.stop="activeDoc = 'privacy'">《隐私政策》</a></em>
        </label>
      </div>
    </div>
    <PrivacyConsentDialog v-model="activeDoc" />
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'
import BrandIcon from './components/BrandIcon.vue'
import PrivacyConsentDialog from './components/PrivacyConsentDialog.vue'
import SocialLoginButton from './components/SocialLoginButton.vue'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
const emit = defineEmits(['logged-in'])
const appStore = useAppStore()
const userStore = useUserStore()
const username = ref('')
const password = ref('')
const agreed = ref(false)
const activeDoc = ref('')
const showPassword = ref(false)
function assertAgreement() {
  if (agreed.value) return true
  appStore.showToast('请先阅读并同意用户协议与隐私政策', 'warning')
  return false
}
async function handleLogin() {
  if (!assertAgreement()) return
  if (!username.value.trim()) {
    appStore.showToast('请输入账号/手机号', 'warning')
    return
  }
  if (!password.value.trim()) {
    appStore.showToast('请输入密码', 'warning')
    return
  }
  try {
    const res = await userStore.login(username.value.trim(), password.value.trim())
    if (res.ok) {
      appStore.showToast('登录成功，欢迎使用智颜 AI', 'success')
      emit('logged-in')
    } else {
      appStore.showToast(res.error || '登录失败，请检查账号密码', 'error')
    }
  } catch (err) {
    appStore.showToast(err.response?.data?.detail || '登录连接失败，请检查网络或配置', 'error')
  }
}
function handleSocialLogin(name) {
  if (!assertAgreement()) return
  appStore.showToast(`该登录方式暂未开放，请使用账号密码登录`, 'info')
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100dvh;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #f4fbfb;
  .login-shell {
    position: relative;
    width: min(100vw, 430px);
    height: 100dvh;
    max-height: 932px;
    min-height: 667px;
    overflow: hidden;
    background: #f4fbfb;
    @include respond(tablet-portrait) {
      height: min(100dvh, 932px);
      border-radius: 22px;
      box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
    }
    @include respond(tablet-landscape) {
      height: min(100dvh, 820px);
      min-height: 667px;
      border-radius: 22px;
      box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
    }
    @include respond(desktop) {
      height: min(100dvh, 932px);
      border-radius: 22px;
      box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
    }
    img {
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
      gap: clamp(30px, 0dvh, 48px);
      padding: clamp(142px, 20dvh, 198px) 32px 28px;
      @include respond(phone-sm) {
        padding-right: 26px;
        padding-left: 26px;
      }
      .login-form {
        display: grid;
        gap: 9px;
        .glass-input {
          min-height: 124px;
          display: grid;
          grid-template-rows: 1fr 1fr;
          padding: 18px 28px;
          margin: 0 -12px;
          background: url('@/assets/images/登录页-input.png') center / 100% 100% no-repeat;
          @include respond(phone-sm) {
            padding-right: 24px;
            padding-left: 24px;
          }
          input {
            min-width: 0;
            flex: 1;
            border: 0;
            background: transparent;
            color: $text-primary;
            font-size: 15px;
            outline: none;
            &::placeholder {
              color: rgba(83, 101, 105, 0.48);
            }
          }
          .phone-row,
          .code-row {
            display: flex;
            align-items: center;
            gap: 18px;
            min-width: 0;
          }
          .phone-row {
            border-bottom: 1px solid rgba(140, 161, 164, 0.18);
          }
          .code-row {
            justify-content: space-between;
            .toggle-password {
              border: 0;
              background: transparent;
              color: rgba(83, 101, 105, 0.48);
              cursor: pointer;
              display: flex;
              align-items: center;
              justify-content: center;
              padding: 0 4px;
              &:active {
                opacity: 0.7;
              }
            }
          }
        }
        button[type="submit"] {
          width: 100%;
        }
        .divider {
          display: grid;
          grid-template-columns: 1fr auto 1fr;
          align-items: center;
          gap: 18px;
          margin-top: 10px;
          span {
            height: 1px;
            background: rgba(119, 141, 145, 0.22);
          }
          strong {
            color: rgba(75, 86, 89, 0.72);
            font-size: 14px;
            font-weight: 500;
          }
        }
        .social-logins {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 28px;
        }
      }
      .agreement {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        color: rgba(63, 78, 82, 0.66);
        font-size: 12px;
        cursor: pointer;
        input {
          display: none;
        }
        & > span {
          position: relative;
          width: 16px;
          height: 16px;
          flex: 0 0 auto;
          border: 1.5px solid rgba(78, 105, 108, 0.34);
          border-radius: 3px;
          background: rgba(255, 255, 255, 0.42);
          transition: $transition;
        }
        em {
          font-style: normal;
        }
        a {
          color: $mint-primary;
          text-decoration: underline;
          font-weight: 700;
        }
        &.checked {
          & > span {
            border-color: $mint-primary;
            background: $mint-primary;
            &::after {
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
          }
        }
      }
    }
  }
}
</style>
