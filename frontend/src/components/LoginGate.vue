<template>
  <section class="login-gate">
    <img class="login-bg" src="/images/登录页-背景.png" alt="" />

    <div class="login-content">
      <header class="brand-area">
        <img class="brand-logo" src="/images/logo2.png" alt="智颜 AI" />
        <div class="brand-text">
          <h1>智颜 AI</h1>
          <p>精准护肤，定制专属美妆</p>
        </div>
      </header>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="glass-input">
          <label class="phone-row">
            <span>+86</span>
            <input v-model="phone" inputmode="tel" maxlength="20" placeholder="请输入手机号" />
          </label>
          <label class="code-row">
            <input v-model="code" inputmode="numeric" maxlength="6" placeholder="请输入验证码" />
            <button type="button" @click="handleCode">获取验证码</button>
          </label>
        </div>

        <button class="login-button" type="submit">一键登录</button>

        <div class="divider">
          <span></span>
          <strong>其他登录方式</strong>
          <span></span>
        </div>

        <div class="social-logins">
          <button type="button" @click="handleSocialLogin('微信')">
            <span class="social-icon wechat" aria-hidden="true">
              <svg viewBox="0 0 1024 1024" focusable="false">
                <path d="M183.379592 699.559184c-4.179592 0-8.359184-1.044898-11.493878-3.657143-6.269388-4.702041-9.404082-12.016327-7.836734-19.330612l13.061224-77.322449C136.881633 553.273469 114.938776 496.326531 114.938776 437.289796 114.938776 292.571429 246.073469 175.020408 408.032653 175.020408c76.8 0 149.420408 26.644898 204.8 74.710204 55.379592 48.587755 86.726531 113.893878 88.293878 183.379592 0 5.746939-2.089796 10.971429-6.269388 14.628572s-9.404082 5.746939-15.151021 5.746938c-5.22449-0.522449-9.404082-0.522449-13.583673-0.522449-112.326531 0-203.232653 79.934694-203.232653 178.677551 0 13.583673 1.567347 27.167347 5.22449 40.751021 1.567347 5.746939 0.522449 11.493878-2.612245 16.195918-3.134694 4.702041-8.359184 7.836735-14.106123 8.881633-14.106122 2.089796-28.734694 3.134694-43.363265 3.134694-52.767347 0-104.489796-12.538776-149.420408-36.571429l-65.828572 34.481633c-3.134694 0-6.269388 1.044898-9.404081 1.044898z" fill="#0B9682" />
                <path d="M303.542857 352.653061m-35.004081 0a35.004082 35.004082 0 1 0 70.008163 0 35.004082 35.004082 0 1 0-70.008163 0Z" fill="#DCFFFA" />
                <path d="M512 352.653061m-35.004082 0a35.004082 35.004082 0 1 0 70.008164 0 35.004082 35.004082 0 1 0-70.008164 0Z" fill="#DCFFFA" />
                <path d="M849.502041 849.502041c-3.134694 0-6.269388-0.522449-9.404082-2.089796l-52.244898-27.167347c-37.093878 19.330612-78.889796 29.779592-122.253061 29.779592-134.269388 0-242.938776-98.220408-242.938776-218.383674S531.853061 412.734694 665.6 412.734694 909.061224 510.955102 909.061224 631.118367c0 48.065306-17.763265 95.085714-50.677551 133.22449l10.44898 61.64898c1.044898 7.314286-1.567347 15.15102-7.836735 19.330612-3.134694 3.134694-7.314286 4.179592-11.493877 4.179592z" fill="#16C4AF" />
                <path d="M576.261224 575.738776m-29.779591 0a29.779592 29.779592 0 1 0 59.559183 0 29.779592 29.779592 0 1 0-59.559183 0Z" fill="#DCFFFA" />
                <path d="M755.461224 575.738776m-29.779591 0a29.779592 29.779592 0 1 0 59.559183 0 29.779592 29.779592 0 1 0-59.559183 0Z" fill="#DCFFFA" />
              </svg>
            </span>
            微信登录
          </button>
          <button type="button" @click="handleSocialLogin('支付宝')">
            <span class="social-icon alipay" aria-hidden="true">
              <svg viewBox="0 0 1024 1024" focusable="false">
                <path d="M614.675968 605.184a495.616 495.616 0 0 0 51.2-111.104 496.128 496.128 0 0 0 31.232-114.688H486.163968V307.2h256V256h-256V135.68H362.259968v114.688H120.083968v51.2L358.675968 300.032v77.824H167.699968v40.448H563.475968a358.4 358.4 0 0 1-18.432 73.728L512.275968 568.32c-10.752 25.088-184.832-64.512-283.136-64.512s-216.576 40.448-227.328 153.6a174.08 174.08 0 0 0 149.504 197.632 374.784 374.784 0 0 0 256-36.864 596.48 596.48 0 0 0 150.016-120.32l392.192 190.464s24.064-36.864 42.496-72.192A776.704 776.704 0 0 0 1024.275968 742.4l-409.6-136.704z m-402.432 186.88c-138.752 0-166.4-68.096-166.4-116.224s29.696-102.4 145.92-109.056 275.456 83.456 275.456 83.456-116.736 142.336-256 142.336z m0 0" fill="#0b9682" />
              </svg>
            </span>
            支付宝登录
          </button>
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

    <!-- 隐私政策与用户协议抽屉阅读器 -->
    <PrivacyConsentDialog v-model="activeDoc" />
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import PrivacyConsentDialog from './PrivacyConsentDialog.vue'

const emit = defineEmits(['logged-in'])
const appStore = useAppStore()
const userStore = useUserStore()

const phone = ref('')
const code = ref('')
const agreed = ref(false)
const activeDoc = ref('') // 控制文档抽屉状态

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
@use '@/assets/styles/variables' as *;

.login-gate {
  position: relative;
  height: 100dvh;
  overflow: hidden;
  background: #f4fbfb;
  color: $text-primary;
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
  height: 100%;
  box-sizing: border-box;
  padding: calc(max(6vh, 45px) + env(safe-area-inset-top)) 30px calc(24px + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: 10px;
  flex: 0 0 auto;

  .brand-logo {
    width: clamp(72px, 10vh, 92px);
    height: auto;
    filter: drop-shadow(0 16px 24px rgba(10, 166, 194, 0.18));
  }
  h1 {
    font-size: clamp(24px, 3.5vh, 32px);
    font-weight: 500;
    letter-spacing: 0.14em;
    color: rgba(31, 41, 43, 0.88);
  }
  p {
    margin-top: 4px;
    color: rgba(77, 85, 88, 0.74);
    font-size: clamp(12px, 1.5vh, 14px);
    letter-spacing: 0.28em;
  }
}

.login-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-self: center;
  margin-top: 2vh;
  transform: translateY(-8vh) scale(0.9);
  transform-origin: bottom center;
}

.glass-input {
  box-sizing: border-box;
  width: 106%;
  align-self: center;
  aspect-ratio: 2.65 / 1;
  padding: 26px 34px 22px;
  border: 0;
  border-radius: 24px;
  background: url('/images/登录页-input.png') center / 100% 100% no-repeat;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.phone-row,
.code-row {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  gap: 18px;
}

.phone-row {
  border-bottom: 1px solid rgba(140, 161, 164, 0.18);

  span {
    color: rgba(25, 39, 42, 0.82);
    font-size: 15px;
    font-weight: 600;
  }
}

.glass-input input {
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

.code-row button {
  flex: 0 0 auto;
  color: $mint-primary;
  font-size: 14px;
  font-weight: 700;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.login-button {
  width: 100%;
  height: clamp(48px, 7vh, 60px);
  margin-top: min(2vh, 14px);
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.36), transparent), linear-gradient(135deg, #9ccfe8, #319d98 52%, #b7f2ea);
  color: $white;
  font-size: clamp(16px, 2.2vh, 20px);
  font-weight: 600;
  letter-spacing: 0.18em;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.7),
    inset 0 -2px 0 rgba(38, 139, 133, 0.28),
    0 22px 42px rgba(54, 174, 165, 0.28);
  border: 0;
  cursor: pointer;
}

.divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 18px;
  margin: min(3vh, 24px) 0 min(1.5vh, 12px);

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
  margin-bottom: min(1.5vh, 10px);

  button {
    display: grid;
    justify-items: center;
    gap: 8px;
    color: rgba(51, 65, 69, 0.72);
    font-size: 13px;
    font-weight: 500;
    background: transparent;
    border: 0;
    cursor: pointer;
  }

  .social-icon {
    width: clamp(44px, 6vh, 54px);
    height: clamp(44px, 6vh, 54px);
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.52);
    box-shadow:
      inset 0 0 0 1px rgba(255, 255, 255, 0.72),
      0 12px 30px rgba(72, 135, 136, 0.1);

    svg {
      width: 68%;
      height: 68%;
      display: block;
    }
  }

  .alipay svg {
    width: 58%;
    height: 58%;
    transform: translateX(1px);
  }
}

.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: min(2.5vh, 18px);
  color: rgba(63, 78, 82, 0.66);
  font-size: 12px;
  cursor: pointer;

  input {
    display: none;
  }

  > span {
    width: 16px;
    height: 16px;
    border: 1.5px solid rgba(78, 105, 108, 0.34);
    border-radius: 3px;
    background: rgba(255, 255, 255, 0.42);
    flex: 0 0 auto;
  }

  em {
    font-style: normal;
  }

  a {
    color: $mint-primary;
    text-decoration: underline;
    font-weight: 700;
    cursor: pointer;
    margin: 0 2px;
    transition: $transition;

    &:hover {
      color: $mint-dark;
    }
  }

  &.checked > span {
    border-color: $mint-primary;
    background:
      linear-gradient(135deg, transparent 42%, $white 43% 55%, transparent 56%),
      $mint-primary;
  }
}

@media (min-width: 769px) {
  .login-gate {
    max-width: 430px;
    margin: 0 auto;
    box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
  }
}

@media (max-height: 700px) {
  .login-content {
    padding-top: calc(max(4vh, 30px) + env(safe-area-inset-top));
    padding-bottom: calc(14px + env(safe-area-inset-bottom));
  }
  .brand-area {
    gap: 12px;
    .brand-logo {
      width: 68px;
    }
  }
  .login-button {
    margin-top: 18px;
  }
  .divider {
    margin: 18px 0 10px;
  }
  .social-logins {
    gap: 16px;
    .social-icon {
      width: 42px;
      height: 42px;
    }
  }
  .agreement {
    margin-top: 12px;
  }
}
</style>
