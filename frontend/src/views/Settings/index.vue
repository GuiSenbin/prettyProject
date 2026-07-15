<!-- 设置中心 -->
<template>
  <div class="settings-page">
    <header class="settings-nav">
      <button type="button" aria-label="返回" @click="handleBack">
        <ChevronLeft :size="28" stroke-width="2.6" />
      </button>
      <h1>设置中心</h1>
    </header>

    <main class="settings-content">
      <!-- 个人资料 -->
      <section class="settings-section">
        <h3>个人资料</h3>
        <div class="settings-card">
          <div class="settings-item avatar-item" @click="triggerUpload">
            <span>头像</span>
            <div class="avatar-wrap">
              <template v-if="loadingAvatar">
                <span class="loading-text">上传中...</span>
              </template>
              <template v-else>
                <img v-if="userStore.session?.avatar_url" :src="userStore.session.avatar_url" alt="avatar" class="avatar-img" />
                <div v-else class="avatar-fallback">{{ initials }}</div>
              </template>
              <input type="file" ref="fileInput" hidden accept="image/*" @change="handleFileChange" />
            </div>
          </div>
          
          <div class="settings-item" @click="openModal('username')">
            <span>用户名</span>
            <div class="item-value">
              <span>{{ userStore.displayName }}</span>
              <ChevronRight :size="16" class="arrow" />
            </div>
          </div>
        </div>
      </section>

      <!-- 账号安全 -->
      <section class="settings-section">
        <h3>账号安全</h3>
        <div class="settings-card">
          <div class="settings-item" @click="openModal('phone')">
            <span>手机号绑定</span>
            <div class="item-value">
              <span :class="{'unbound': !userStore.displayPhone}">{{ userStore.displayPhone || '未绑定' }}</span>
              <ChevronRight :size="16" class="arrow" />
            </div>
          </div>
        </div>
      </section>

      <!-- 第三方绑定预留 -->
      <section class="settings-section">
        <h3>第三方账号 (敬请期待)</h3>
        <div class="settings-card disabled-card">
          <div class="settings-item">
            <div class="social-label">
              <MessageSquare :size="18" />
              <span>微信绑定</span>
            </div>
            <span class="unbound">未绑定</span>
          </div>
          <div class="settings-item">
            <div class="social-label">
              <Wallet :size="18" />
              <span>支付宝绑定</span>
            </div>
            <span class="unbound">未绑定</span>
          </div>
        </div>
      </section>
    </main>

    <!-- 通用输入弹窗 -->
    <InputModal
      v-model="showModal"
      v-model:inputValue="inputValue"
      :title="modalType === 'username' ? '修改用户名' : '绑定手机号'"
      :content="modalType === 'username' ? '请设置一个新的唯一用户名' : '请输入您的11位手机号'"
      :placeholder="modalType === 'username' ? '请输入用户名' : '请输入手机号'"
      :maxlength="modalType === 'username' ? 20 : 11"
      :errorMessage="errorMessage"
      :saving="saving"
      @confirm="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronLeft, ChevronRight, MessageSquare, Wallet } from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { userApi } from '@/api/user'
import InputModal from '@/components/input-modal.vue'

const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const fileInput = ref(null)
const loadingAvatar = ref(false)

const showModal = ref(false)
const modalType = ref('') // 'username' | 'phone'
const inputValue = ref('')
const saving = ref(false)
const errorMessage = ref('')

const initials = computed(() => userStore.displayName.slice(0, 1))

function handleBack() {
  router.replace('/chat')
}

function triggerUpload() {
  if (loadingAvatar.value) return
  fileInput.value.click()
}

async function handleFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  
  if (file.size > 10 * 1024 * 1024) {
    appStore.showToast('图片大小不能超过 10MB', 'warning')
    return
  }

  loadingAvatar.value = true
  try {
    const res = await userApi.uploadAvatar(userStore.userId, file)
    userStore.session.avatar_url = res.data.avatar_url
    userStore.saveSession()
  } catch (err) {
    console.error(err)
    appStore.showToast('头像上传失败', 'error')
  } finally {
    loadingAvatar.value = false
    e.target.value = ''
  }
}

function openModal(type) {
  modalType.value = type
  errorMessage.value = ''
  if (type === 'username') {
    inputValue.value = userStore.displayName
  } else {
    inputValue.value = userStore.displayPhone
  }
  showModal.value = true
}

async function handleSave() {
  const val = inputValue.value.trim()
  if (!val) {
    errorMessage.value = '内容不能为空'
    return
  }
  if (modalType.value === 'phone' && !/^1\d{10}$/.test(val)) {
    errorMessage.value = '请输入正确的11位手机号'
    return
  }
  if (val === userStore.displayName || val === userStore.displayPhone) {
    showModal.value = false
    return
  }

  saving.value = true
  errorMessage.value = ''
  try {
    const payload = modalType.value === 'username' ? { display_name: val } : { phone: val }
    const res = await userApi.updateUser(userStore.userId, payload)
    
    // 更新本地 state
    if (modalType.value === 'username') {
      userStore.session.name = res.display_name
    } else {
      userStore.session.phone = res.phone
    }
    userStore.saveSession()
    showModal.value = false
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || '保存失败，可能是该账号已被占用'
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.settings-page {
  min-height: 100dvh;
  background:
    linear-gradient(180deg, rgba(218, 247, 248, 0.95) 0%, rgba(245, 253, 253, 0.94) 42%, #ffffff 100%),
    #f4fbfc;
  .settings-nav {
    position: sticky;
    top: 0;
    z-index: 100;
    display: grid;
    grid-template-columns: 36px 1fr 36px;
    align-items: center;
    min-height: 40px;
    padding: calc(6px + env(safe-area-inset-top)) 20px 6px;
    background: rgba(221, 247, 248, 0.65);
    backdrop-filter: blur(12px);
    button {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: flex-start;
      margin-left: -8px;
      border: 0;
      border-radius: 0;
      background: transparent;
      color: #111827;
      cursor: pointer;
      padding: 0;
      svg {
        display: block;
      }
    }
    h1 {
      color: #111827;
      font-size: 17px;
      font-weight: 500;
      line-height: 1.2;
      text-align: center;
      letter-spacing: 0.08em;
      margin: 0;
    }
  }
  .settings-content {
    padding: 22px 20px 20px;
    .settings-section {
      margin-bottom: 24px;
      h3 {
        font-size: 13px;
        color: #8c9baa;
        margin: 0 0 10px 12px;
        font-weight: 500;
      }
      .settings-card {
        background: #ffffff;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(13, 124, 135, 0.03);
        &.disabled-card {
          opacity: 0.6;
          pointer-events: none;
        }
        .settings-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          font-size: 15px;
          color: #2c3e50;
          cursor: pointer;
          border-bottom: 1px solid #f0f2f5;
          &:last-child {
            border-bottom: none;
          }
          &:active {
            background: #f8fafc;
          }
          &.avatar-item {
            padding: 12px 20px;
            .avatar-wrap {
              width: 48px;
              height: 48px;
              border-radius: 50%;
              overflow: hidden;
              background: #e2e8f0;
              display: flex;
              align-items: center;
              justify-content: center;
              .avatar-img {
                width: 100%;
                height: 100%;
                object-fit: cover;
              }
              .avatar-fallback {
                font-size: 20px;
                font-weight: 600;
                color: #64748b;
              }
              .loading-text {
                font-size: 10px;
                color: #64748b;
              }
            }
          }
          .item-value {
            display: flex;
            align-items: center;
            color: #64748b;
            font-size: 14px;
            .arrow {
              margin-left: 6px;
              color: #cbd5e1;
            }
            .unbound {
              color: #94a3b8;
            }
          }
          .social-label {
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .unbound {
            color: #94a3b8;
          }
        }
      }
    }
  }
}

@include respond(phone-sm) {
  .settings-page .settings-nav {
    h1 {
      font-size: 21px;
    }
    button {
      width: 36px;
      height: 36px;
    }
  }
}
</style>
