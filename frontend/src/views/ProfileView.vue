<template>
  <div class="profile-page">
    <h2 class="page-title">个人美妆档案</h2>
    <p class="page-desc">这是你的可编辑美妆画像，AI 会据此判断产品、妆容和护肤方案是否适合你</p>

    <div class="profile-card">
      <div class="form-section">
        <ProfileForm v-model="formData" />
        <div class="form-actions">
          <button class="btn btn-primary" @click="handleSave" :disabled="saving">
            {{ saving ? '保存中...' : userStore.profile ? '更新档案' : '创建档案' }}
          </button>
          <button class="btn btn-outline" @click="handleReset">重置</button>
        </div>
      </div>

      <div v-if="userStore.profile" class="preview-section">
        <div class="preview-card">
          <div class="preview-avatar">👤</div>
          <h3>{{ userStore.profile.name }}</h3>
          <div class="preview-tags">
            <span v-if="skinTag" class="tag">🧴 {{ skinTag }}</span>
            <span v-if="faceTag" class="tag">👤 {{ faceTag }}</span>
            <span v-if="toneTag" class="tag">🎨 {{ toneTag }}</span>
            <span v-if="displayAge" class="tag">🎂 {{ displayAge }}</span>
          </div>
          <p class="preview-status">✅ 档案已保存，AI 助手将根据你的资料提供个性化推荐</p>
          <router-link to="/chat" class="btn btn-primary">去咨询 AI 助手 →</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import ProfileForm from '@/components/ProfileForm.vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'

const userStore = useUserStore()
const appStore = useAppStore()
const saving = ref(false)

const ageLabels = {
  under18: '18岁以下', '18-22': '18-22岁', '23-28': '23-28岁',
  '29-35': '29-35岁', '36-45': '36-45岁', over45: '45岁以上',
}

const skinLabels = { dry: '干性', oily: '油性', combination: '混合性', normal: '中性', sensitive: '敏感性' }
const faceLabels = { round: '圆脸', square: '方脸', oval: '鹅蛋脸', heart: '心形脸', diamond: '菱形脸' }
const toneLabels = { fair: '白皙', light: '自然偏白', medium: '自然肤色', tan: '小麦色', dark: '深色' }

const skinTag = computed(() => userStore.profile?.skin_type ? skinLabels[userStore.profile.skin_type] : '')
const faceTag = computed(() => userStore.profile?.face_shape ? faceLabels[userStore.profile.face_shape] : '')
const toneTag = computed(() => userStore.profile?.skin_tone ? toneLabels[userStore.profile.skin_tone] : '')
const displayAge = computed(() => {
  const age = userStore.profile?.age
  if (!age) return ''
  if (ageLabels[age]) return ageLabels[age]
  return /^\d+$/.test(age) ? `${age}岁` : age
})

const formData = reactive({
  name: '', age: '', gender: '', skin_type: '',
  face_shape: '', skin_tone: '', concerns: [],
})

onMounted(async () => {
  await userStore.fetchLatest()
  if (userStore.profile) {
    Object.assign(formData, userStore.profile)
  }
})

async function handleSave() {
  saving.value = true
  const result = await userStore.save(formData)
  saving.value = false
  if (result.ok) {
    appStore.showToast('档案保存成功！🎉', 'success')
  } else {
    appStore.showToast('保存失败: ' + result.error, 'error')
  }
}

async function handleReset() {
  if (!userStore.profile) {
    appStore.showToast('没有需要重置的档案', 'info')
    return
  }
  const result = await userStore.reset()
  if (result.ok) {
    Object.assign(formData, { name: '', age: '', gender: '', skin_type: '', face_shape: '', skin_tone: '', concerns: [] })
    appStore.showToast('已重置档案', 'info')
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.profile-card {
  background: $white;
  border-radius: $radius;
  box-shadow: $shadow;
  padding: 36px;
  display: flex;
  gap: 36px;

  .form-section { flex: 1; }

  .form-actions {
    display: flex;
    gap: 12px;
    margin-top: 24px;
  }

  .preview-section { flex: 0 0 280px; }

  .preview-card {
    background: linear-gradient(135deg, $mint-bg-dark, $mint-bg);
    border: 1px solid $mint-pale;
    border-radius: $radius;
    padding: 28px 24px;
    text-align: center;

    .preview-avatar { font-size: 56px; margin-bottom: 8px; }

    h3 {
      font-size: 20px;
      font-weight: 700;
      color: $mint-dark;
      margin-bottom: 12px;
    }

    .preview-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      margin-bottom: 16px;
    }

    .preview-status {
      font-size: 13px;
      color: $text-light;
      margin-bottom: 16px;
    }
  }
}

@media (max-width: 768px) {
  .profile-card {
    flex-direction: column;
    padding: 24px;
    .preview-section { flex: 1; }
  }
}
</style>
