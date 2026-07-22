<!-- 个人档案 -->
<template>
  <section class="profile-page">
    <header class="profile-nav">
      <button type="button" aria-label="返回" @click="handleBack">
        <ChevronLeft :size="28" stroke-width="2.6" />
      </button>
      <h1>个人档案</h1>
    </header>
    <div class="profile-stage" :style="heroStyle">
      <div class="profile-hero">
        <article>
          <span>个性化档案</span>
          <p>定制属于你的专属方案</p>
        </article>
      </div>
    </div>
    <form class="profile-form" @submit.prevent="handleSubmit">
      <section>
        <header>
          <UserRound :size="18" />
          <h3>基础信息</h3>
        </header>
        <div class="gender-options">
          <button
            v-for="item in genderOptions"
            :key="item.value"
            class="select-pill"
            :class="{ active: form.gender === item.value }"
            type="button"
            @click="form.gender = item.value"
          >
            <span>{{ item.icon }}</span>
            {{ item.label }}
          </button>
        </div>
        <label class="range-field">
          <span>年龄</span>
          <strong>{{ form.age ? form.age + ' 岁' : '未设置' }}</strong>
          <input v-model.number="form.age" type="range" min="12" max="60" :style="ageRangeStyle" />
          <small>
            <em
              v-for="mark in ageMarks"
              :key="mark.value"
              :class="{ active: form.age === mark.value }"
              :style="{ left: `${((mark.value - AGE_MIN) / (AGE_MAX - AGE_MIN)) * 100}%` }"
            >
              {{ mark.label }}
            </em>
          </small>
        </label>
      </section>
      <section>
        <header>
          <Sparkles :size="18" />
          <h3>肤况信息</h3>
        </header>
        <div>
          <div class="section-title-row">
            <p>肤质</p>
            <button class="hint-button" type="button" aria-label="查看肤质介绍">
              <HelpCircle :size="17" />
              <span>{{ selectedSkinTypeDescription }}</span>
            </button>
          </div>
          <div class="skin-scroll">
            <button
              v-for="item in skinTypeOptions"
              :key="item.label"
              class="select-chip"
              :class="{ active: form.skin_type === item.label }"
              type="button"
              @click="form.skin_type = item.label"
            >
              {{ item.label }}
              <Check v-if="form.skin_type === item.label" :size="15" />
            </button>
          </div>
        </div>
        <div>
          <div class="section-title-row">
            <p>肤色</p>
            <strong v-if="form.skin_tone" class="tone-value">{{ form.skin_tone }}</strong>
          </div>
          <div class="tone-wrap">
            <ul class="tone-row">
              <li v-for="item in skinToneOptions" :key="item.value">
                <button
                  :aria-label="item.label"
                  class="tone-dot"
                  :class="{ active: form.skin_tone === item.label }"
                  :style="{ backgroundColor: item.color }"
                  type="button"
                  @click="selectSkinTone(item)"
                ></button>
              </li>
            </ul>
          </div>
        </div>
        <div>
          <p>脸型</p>
          <div v-if="form.gender" class="face-scroll">
            <button
              v-for="(item, index) in faceShapeOptions"
              :key="item"
              class="face-option"
              :class="{ active: form.face_shape === item }"
              type="button"
              @click="form.face_shape = item"
            >
              <span :style="faceStyle(index)"></span>
              <em>{{ item }}</em>
            </button>
          </div>
          <div v-else class="face-placeholder">选择性别后展示对应脸型</div>
        </div>
        <div>
          <p>皮肤问题(可多选)</p>
          <div class="concern-grid">
            <button
              v-for="item in concernOptions"
              :key="item"
              class="concern-chip"
              :class="{ active: form.skin_concerns.includes(item) }"
              type="button"
              @click="toggleConcern(item)"
            >
              {{ item }}
              <Check v-if="form.skin_concerns.includes(item)" :size="15" />
            </button>
          </div>
        </div>
      </section>
      <section v-if="form.gender === 'female'">
        <header>
          <CalendarDays :size="18" />
          <h3>生理期</h3>
        </header>

        <div class="field-grid">
          <label>
            <span>最近一次开始日期</span>
            <input :value="formatShowDate(form.last_period_start)" type="text" readonly placeholder="请选择日期" @click="openDatePicker" />
          </label>
          <label>
            <span>平均周期</span>
            <div class="input-with-unit">
              <input v-model.number="form.cycle_length_days" type="number" min="20" max="45" />
              <span class="unit">天</span>
            </div>
          </label>
        </div>
      </section>
      <section v-if="showPregnancy">
        <header>
          <ShieldCheck :size="18" />
          <h3>孕哺状态</h3>
        </header>
        <div class="pregnancy-scroll">
          <button
            v-for="item in pregnancyOptions"
            :key="item"
            class="select-chip"
            :class="{ active: form.pregnancy_status === item }"
            type="button"
            @click="form.pregnancy_status = item"
          >
            {{ item }}
          </button>
        </div>
      </section>
      <section>
        <header>
          <ShieldAlert :size="18" />
          <h3>安全避雷</h3>
          <span class="sub-title">已知过敏源/成分不耐受</span>
        </header>
        <label>
          <textarea v-model.trim="form.known_allergies" maxlength="200" placeholder="如酒精不耐受、对水杨酸敏感等"></textarea>
        </label>
      </section>
      <section>
        <header>
          <NotebookPen :size="18" />
          <h3>偏好与注意事项</h3>
          <span class="sub-title">偏好与注意事项</span>
        </header>
        <label>
          <textarea v-model.trim="form.preference_notes" maxlength="260" placeholder="如讨厌香精味、最近熬夜、饮食辛辣等"></textarea>
        </label>
      </section>
      <button class="btn btn-primary" type="submit" :disabled="saving">
        {{ saving ? '保存中' : '保存档案' }}
      </button>
    </form>
    <!-- 自定义薄荷绿日期选择弹窗 -->
    <div v-if="showDatePicker" class="custom-datepicker-mask" @click="closeDatePicker">
      <div class="custom-datepicker-card" @click.stop>
        <header class="datepicker-header">
          <button type="button" @click="changeMonth(-1)">‹</button>
          <h4>{{ currentYear }}年 {{ currentMonth + 1 }}月</h4>
          <button type="button" @click="changeMonth(1)">›</button>
        </header>
        <div class="datepicker-weekdays">
          <span v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day">{{ day }}</span>
        </div>
        <div class="datepicker-days">
          <button
            v-for="(day, idx) in calendarDays"
            :key="idx"
            type="button"
            class="day-btn"
            :class="{
              active: isSameDay(day.date, tempSelectedDate),
              'other-month': !day.isCurrentMonth
            }"
            @click="selectDate(day.date)"
          >
            {{ day.dayNum }}
          </button>
        </div>
        <footer class="datepicker-footer">
          <button type="button" class="btn-cancel" @click="closeDatePicker">取消</button>
          <button type="button" class="btn-confirm" @click="confirmDate">确定</button>
        </footer>
      </div>
    </div>
    <ConfirmModal 
      v-model="showIncompleteModal" 
      title="确定要离开吗" 
      :content="'您还未填写必填项(性别/年龄)\n现在离开将不会保存任何数据'" 
      confirmText="去完善" 
      cancelText="放弃并离开"
      :showCancel="true"
      @cancel="handleModalCancel"
    />
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import ConfirmModal from '@/components/confirm-modal.vue'
import { CalendarDays, Check, ChevronLeft, HelpCircle, NotebookPen, ShieldAlert, ShieldCheck, Sparkles, UserRound } from 'lucide-vue-next'
import { profileApi } from '@/api/profile'
import defaultAvatar from '@/assets/images/头像-默认.png'
import femaleHero from '@/assets/images/个人档案-女.JPG'
import maleHero from '@/assets/images/个人档案-男.JPG'
import femaleFaces from '@/assets/images/脸型-女.png'
import maleFaces from '@/assets/images/脸型-男.png'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'

const appStore = useAppStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const saving = ref(false)
const originalFormData = ref('')

function takeSnapshot() {
  originalFormData.value = JSON.stringify(form)
}

function getTodayString() {
  const today = new Date()
  const yyyy = today.getFullYear()
  const mm = String(today.getMonth() + 1).padStart(2, '0')
  const dd = String(today.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

const genderOptions = [
  { label: '女', value: 'female', icon: '♀' },
  { label: '男', value: 'male', icon: '♂' },
]
const skinTypeOptions = [
  { label: '油皮', desc: '皮脂分泌旺盛，容易出油和堵塞毛孔，护理重点是温和控油、疏通毛孔，同时避免过度清洁。' },
  { label: '干皮', desc: '皮脂分泌较少，容易紧绷、起皮，护理重点是温和清洁和持续保湿，避免频繁去角质。' },
  { label: '中性', desc: '水油相对平衡，不易敏感或泛油，护理重点是稳定屏障、规律防晒和维持基础保湿。' },
  { label: '混油皮', desc: 'T 区更容易出油、两颊较稳定或偏干，护理重点是分区管理，出油区控油，两颊补水。' },
  { label: '混干皮', desc: '两颊偏干，T 区轻微出油或相对正常，护理重点是加强干燥区域保湿，并保持清爽不厚重。' },
  { label: '敏感肌', desc: '屏障较脆弱，易泛红刺痛，护理重点是减少刺激、精简成分，优先选择舒缓修护型产品。' },
]
const ageMarks = [
  { label: '12', value: 12 },
  { label: '20', value: 20 },
  { label: '28', value: 28 },
  { label: '36', value: 36 },
  { label: '44', value: 44 },
  { label: '52', value: 52 },
  { label: '60+', value: 60 },
]
const skinToneOptions = [
  { label: '白皙', value: 'fairWhite', color: '#f7e9e0' },
  { label: '自然偏白', value: 'fair', color: '#efdacd' },
  { label: '自然', value: 'natural', color: '#f0c9ad' },
  { label: '健康色', value: 'healthy', color: '#d89d72' },
  { label: '小麦色', value: 'wheat', color: '#bf835d' },
  { label: '深肤色', value: 'deep', color: '#93624d' },
]
const faceShapeOptions = ['瓜子脸', '鹅蛋脸', '方形脸', '圆脸', '长脸', '心形脸']
const concernOptions = ['痘痘', '闭口', '黑头', '泛红', '敏感', '干燥', '暗沉', '毛孔粗大', '细纹', '色斑']
const pregnancyOptions = ['不方便透露', '未怀孕', '备孕中', '怀孕中', '哺乳期']
const form = reactive({
  gender: '',
  age: null,
  skin_type: '',
  skin_tone: '',
  face_shape: '',
  skin_concerns: [],
  known_allergies: '',
  period_acne: false,
  last_period_start: '',
  cycle_length_days: 28,
  pregnancy_status: '不方便透露',
  preference_notes: '',
})
const heroImage = computed(() => {
  if (form.gender === 'male') return maleHero
  if (form.gender === 'female') return femaleHero
  return defaultAvatar
})
const heroStyle = computed(() => {
  const isDefault = !form.gender
  return {
    backgroundImage: isDefault
      ? `linear-gradient(90deg, rgba(220, 247, 248, 0.96), rgba(230, 250, 251, 0.76)), url(${heroImage.value})`
      : `linear-gradient(90deg, rgba(220, 247, 248, 0.96) 0%, rgba(231, 251, 251, 0.84) 46%, rgba(231, 251, 251, 0.28) 78%), url(${heroImage.value})`,
    backgroundSize: isDefault ? 'auto 100%, 165px auto' : 'auto 100%, auto 90%',
    backgroundPosition: isDefault ? 'center, right -22px center' : 'center center, right 0px top 1px',
  }
})
const faceSprite = computed(() => (form.gender === 'male' ? maleFaces : femaleFaces))
const showPregnancy = computed(() => form.gender === 'female' && form.age >= 18 && form.age <= 50)
const AGE_MIN = 12
const AGE_MAX = 60
const ageRangeStyle = computed(() => {
  const progress = ((form.age - AGE_MIN) / (AGE_MAX - AGE_MIN)) * 100
  return {
    background: `linear-gradient(90deg, #0d9b9d 0%, #28bbb0 ${progress}%, rgba(196, 211, 217, 0.52) ${progress}%, rgba(196, 211, 217, 0.52) 100%)`,
  }
})
const selectedSkinTypeDescription = computed(() => {
  const selected = skinTypeOptions.find((item) => item.label === form.skin_type)
  return selected?.desc || '选择肤质后，这里会展示对应护理重点，帮助你理解为什么推荐不同方案。'
})

watch(() => form.gender, (gender, oldGender) => {
  if (oldGender && gender !== oldGender) {
    Object.assign(form, {
      age: null,
      skin_type: '',
      skin_tone: '',
      face_shape: '',
      skin_concerns: [],
      known_allergies: '',
      period_acne: false,
      last_period_start: '',
      cycle_length_days: 28,
      pregnancy_status: '不方便透露',
      preference_notes: '',
    })
  } else if (gender !== 'female') {
    form.period_acne = false
    form.last_period_start = ''
    form.cycle_length_days = 28
    form.pregnancy_status = ''
  }
})
watch(showPregnancy, (visible) => {
  if (!visible) {
    form.pregnancy_status = ''
  } else if (!form.pregnancy_status) {
    form.pregnancy_status = '不方便透露'
  }
})

function faceStyle(index) {
  const femalePositions = [
    '-35.8px -13.4px',
    '-149.8px -13.4px',
    '-262.8px -13.4px',
    '-35.8px -111.1px',
    '-149.8px -110.1px',
    '-262.8px -110.1px'
  ]
  const malePositions = [
    '-35.8px -10.4px',
    '-149.8px -11.4px',
    '-263.8px -11.4px',
    '-35.8px -109.1px',
    '-149.8px -109.1px',
    '-262.8px -109.1px'
  ]
  const positions = form.gender === 'male' ? malePositions : femalePositions
  return {
    backgroundImage: `url(${faceSprite.value})`,
    backgroundSize: '372.1px 203.3px',
    backgroundPosition: positions[index] || '0px 0px',
  }
}
function toggleConcern(item) {
  const index = form.skin_concerns.indexOf(item)
  if (index >= 0) {
    form.skin_concerns.splice(index, 1)
    return
  }
  form.skin_concerns.push(item)
}
function selectSkinTone(item) {
  form.skin_tone = item.label
}
function handleBack() {
  // 意图：支持从产品详情引导补档案后回到原页面，同时继续交给 onBeforeRouteLeave 处理未完成提示与自动保存。
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  router.replace(redirect || '/chat')
}
function assignProfile(profile) {
  Object.assign(form, {
    gender: profile?.gender || '',
    age: profile?.age || null,
    skin_type: profile?.skin_type || '',
    skin_tone: profile?.skin_tone || '',
    face_shape: profile?.face_shape || '',
    skin_concerns: profile?.skin_concerns || [],
    known_allergies: profile?.known_allergies || '',
    period_acne: !!profile?.period_acne,
    last_period_start: profile?.last_period_start || '',
    cycle_length_days: profile?.cycle_length_days || 28,
    pregnancy_status: profile?.pregnancy_status || '不方便透露',
    preference_notes: profile?.preference_notes || '',
  })
  takeSnapshot()
}
function buildPayload() {
  return {
    gender: form.gender || null,
    age: form.age,
    skin_type: form.skin_type || null,
    skin_tone: form.skin_tone || null,
    face_shape: form.face_shape || null,
    skin_concerns: form.skin_concerns,
    known_allergies: form.known_allergies || null,
    period_acne: form.gender === 'female' ? form.period_acne : null,
    last_period_start: form.gender === 'female' && form.last_period_start ? form.last_period_start : null,
    cycle_length_days: form.gender === 'female' ? form.cycle_length_days : null,
    pregnancy_status: showPregnancy.value && form.pregnancy_status ? form.pregnancy_status : null,
    preference_notes: form.preference_notes || null,
  }
}
async function loadProfile() {
  if (!userStore.userId) return
  try {
    const profile = await profileApi.getProfile()
    if (profile) {
      assignProfile(profile)
    } else {
      takeSnapshot()
    }
  } catch (err) {
    appStore.showToast(err.message || '个人档案读取失败', 'error')
    takeSnapshot()
  }
}
const showIncompleteModal = ref(false)
const targetRoute = ref(null)
const isForceLeaving = ref(false)

function handleModalCancel() {
  isForceLeaving.value = true
  if (targetRoute.value) {
    router.push(targetRoute.value)
  } else {
    router.replace('/chat')
  }
}

async function handleSubmit() {
  const isNotCompleted = !form.gender || form.age === null || form.age === undefined || form.age === ''
  if (isNotCompleted) {
    appStore.showToast('请选择或填写您的性别与年龄', 'warning')
    return
  }
  if (!userStore.userId) {
    appStore.showToast('请先登录后再保存档案', 'warning')
    return
  }
  saving.value = true
  try {
    const profile = await profileApi.saveProfile(buildPayload())
    assignProfile(profile)
    takeSnapshot()
    
    // 意图：采用渐进式信息收集策略。只要核心依赖（必填项）满足即可入库持久化，边缘信息通过弱提示引导逐步完善，降低表单提交门槛。
    const allFilled = form.skin_type && form.skin_tone && form.face_shape
    if (allFilled) {
      appStore.showToast('个人档案保存成功', 'success')
    } else {
      appStore.showToast('已保存，部分信息可随时完善', 'success')
    }
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
    if (redirect) {
      router.replace(redirect)
    }
  } catch (err) {
    appStore.showToast(err.message || '保存失败，请稍后再试', 'error')
  } finally {
    saving.value = false
  }
}
onMounted(loadProfile)
const showDatePicker = ref(false)
const pickerDate = ref(new Date())
const tempSelectedDate = ref('')
const currentYear = computed(() => pickerDate.value.getFullYear())
const currentMonth = computed(() => pickerDate.value.getMonth())
function formatShowDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.replace(/-/g, ' / ')
}
function changeMonth(step) {
  const newDate = new Date(pickerDate.value)
  newDate.setMonth(newDate.getMonth() + step)
  pickerDate.value = newDate
}
function openDatePicker() {
  tempSelectedDate.value = form.last_period_start || getTodayString()
  pickerDate.value = new Date(tempSelectedDate.value)
  showDatePicker.value = true
}
function closeDatePicker() {
  showDatePicker.value = false
}
function selectDate(dateObj) {
  const yyyy = dateObj.getFullYear()
  const mm = String(dateObj.getMonth() + 1).padStart(2, '0')
  const dd = String(dateObj.getDate()).padStart(2, '0')
  tempSelectedDate.value = `${yyyy}-${mm}-${dd}`
}
function isSameDay(date1, date2Str) {
  if (!date2Str) return false
  const d2 = new Date(date2Str)
  return date1.getFullYear() === d2.getFullYear() &&
         date1.getMonth() === d2.getMonth() &&
         date1.getDate() === d2.getDate()
}
function confirmDate() {
  form.last_period_start = tempSelectedDate.value
  showDatePicker.value = false
}
const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDayIdx = new Date(year, month, 1).getDay()
  const currentMonthDays = new Date(year, month + 1, 0).getDate()
  const days = []
  const prevMonthDays = new Date(year, month, 0).getDate()
  for (let i = firstDayIdx - 1; i >= 0; i--) {
    days.push({
      date: new Date(year, month - 1, prevMonthDays - i),
      dayNum: prevMonthDays - i,
      isCurrentMonth: false
    })
  }
  for (let i = 1; i <= currentMonthDays; i++) {
    days.push({
      date: new Date(year, month, i),
      dayNum: i,
      isCurrentMonth: true
    })
  }
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    days.push({
      date: new Date(year, month + 1, i),
      dayNum: i,
      isCurrentMonth: false
    })
  }
  return days
})
const isNavigatingAway = ref(false)

onBeforeRouteLeave(async (to, from, next) => {
  if (isNavigatingAway.value || isForceLeaving.value) {
    next()
    return
  }
  const hasChanges = JSON.stringify(form) !== originalFormData.value
  const isNotCompleted = !form.gender || form.age === null || form.age === undefined || form.age === ''

  if (isNotCompleted) {
    targetRoute.value = to.fullPath
    showIncompleteModal.value = true
    next(false)
  } else if (hasChanges) {
    // 意图：挂起 Vue Router 的原生退出行为，等待异步状态持久化流转完毕后再安全放行。
    next(false)
    saving.value = true
    try {
      if (userStore.userId) {
        await profileApi.saveProfile(buildPayload())
        takeSnapshot()
        appStore.showToast('档案已自动保存', 'success')
      }
      isNavigatingAway.value = true
      router.push(to.fullPath)
    } catch (err) {
      appStore.showToast(err.message || '自动保存失败', 'error')
      saving.value = false
      next(false)
    }
  } else {
    next()
  }
})
// 移除 beforeunload 的原生弹框逻辑
</script>

<style lang="scss" scoped>
.profile-page {
  box-sizing: border-box;
  width: 100%;
  max-width: 430px;
  margin: 0 auto;
  padding-bottom: 8px;
  min-height: 100dvh;
  background:
    linear-gradient(180deg, rgba(218, 247, 248, 0.95) 0%, rgba(245, 253, 253, 0.94) 42%, #ffffff 100%),
    #f6fbfc;
  color: $text-primary;
  *,
  *::before,
  *::after {
    box-sizing: border-box;
  }
  .profile-nav {
    position: sticky;
    top: 0;
    z-index: 100;
    display: grid;
    grid-template-columns: 36px 1fr 36px;
    align-items: center;
    min-height: 40px;
    padding: calc(6px + env(safe-area-inset-top)) 20px 6px;
    background: linear-gradient(30deg, rgb(209, 243, 246) 35%, rgb(232, 244, 246) 56%);
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
  .profile-stage {
    position: relative;
    margin-top: 0;
    padding: 16px 20px 10px;
    background-color: #ddf7f8;
    background-repeat: no-repeat;
    box-shadow: 0 16px 38px rgba(10, 166, 194, 0.08);
    overflow: hidden;
    isolation: isolate;
    &::before {
      content: '';
      position: absolute;
      inset: 0;
      z-index: -1;
      background:
        linear-gradient(125deg, rgba(255, 255, 255, 0), rgba(114, 215, 220, 0.18), rgba(255, 255, 255, 0) 58%),
        radial-gradient(circle at 14% 18%, rgba(255, 255, 255, 0.88) 0 2px, transparent 3px),
        radial-gradient(circle at 25% 36%, rgba(255, 255, 255, 0.72) 0 1px, transparent 2px);
    }
  }
  .profile-hero {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    article {
      width: 204px;
      max-width: 62%;
      min-width: 0;
      span {
        width: max-content;
        display: inline-flex;
        align-items: center;
        min-height: 24px;
        padding: 4px 11px;
        border: 1px solid rgba(13, 124, 135, 0.22);
        border-radius: 12px;
        background: rgba(210, 244, 245, 0.64);
        color: $mint-primary;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
      }
      p {
        margin-top: 7px;
        color: rgba(67, 82, 102, 0.72);
        font-size: 12px;
        line-height: 1.56;
        letter-spacing: 0.12em;
      }
    }
  }
  .profile-form {
    display: grid;
    gap: 14px;
    margin-top: -36px;
    padding: 0 14px 28px;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    overflow-x: hidden;
    section {
      display: grid;
      gap: 8px;
      width: 100%;
      max-width: 100%;
      min-width: 0;
      padding: 16px;
      overflow: visible;
      border: 1px solid rgba(207, 238, 241, 0.82);
      border-radius: 22px;
      background: rgba(255, 255, 255, 0.76);
      box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
      backdrop-filter: blur(16px);
      & > div {
        width: 100%;
        max-width: 100%;
        min-width: 0;
      }
      header {
        display: flex;
        align-items: center;
        gap: 8px;
        color: $mint-primary;
        h3 {
          color: rgba(31, 41, 43, 0.88);
          font-size: 16px;
          font-weight: 800;
        }
        .sub-title {
          color: rgba(67, 82, 102, 0.46);
          font-size: 12px;
          font-weight: 500;
        }
      }
      p,
      label > span,
      .range-field > span {
        color: rgba(67, 82, 102, 0.72);
        font-size: 13px;
        font-weight: 800;
      }
      label {
        display: grid;
        gap: 9px;
        min-width: 0;
        input:not([type='checkbox']):not([type='range']),
        textarea {
          width: 100%;
          border: 1px solid rgba(207, 238, 241, 0.95);
          border-radius: 16px;
          background: rgba(255, 255, 255, 0.66);
          color: $text-primary;
          font-family: inherit;
          font-size: 14px;
          outline: none;
          transition: $transition;
          &:focus {
            border-color: rgba(13, 124, 135, 0.52);
            box-shadow: 0 0 0 4px rgba(114, 215, 220, 0.16);
          }
        }
        input:not([type='checkbox']):not([type='range']) {
          height: 38px;
          padding: 0 14px;
        }
        .input-with-unit {
          position: relative;
          display: flex;
          align-items: center;
          width: 100%;
          input {
            padding-right: 32px;
            &::-webkit-outer-spin-button,
            &::-webkit-inner-spin-button {
              -webkit-appearance: none;
              margin: 0;
            }
            &[type='number'] {
              -moz-appearance: textfield;
            }
          }
          .unit {
            position: absolute;
            right: 14px;
            color: rgba(67, 82, 102, 0.78);
            font-size: 13px;
            font-weight: 800;
            pointer-events: none;
          }
        }
        input[type='date'] {
          position: relative;
          accent-color: $mint-primary;
          &::-webkit-calendar-picker-indicator {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            opacity: 0;
            cursor: pointer;
            z-index: 2;
          }
        }
        textarea {
          min-height: 86px;
          resize: vertical;
          padding: 12px 14px;
          line-height: 1.7;
        }
      }
    }
    & > button {
      position: relative;
      z-index: 20;
      width: 100%;
      height: 50px;
      border-radius: 16px;
      letter-spacing: 0.1em;
      &:disabled {
        opacity: 0.7;
        cursor: not-allowed;
        transform: none;
      }
    }
  }
  .gender-options,
  .chip-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 9px;
    width: 100%;
    min-width: 0;
  }
  .chip-grid {
    .select-chip {
      min-height: 42px;
      padding-right: 10px;
      padding-left: 10px;
    }
  }
  .concern-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    padding-top: 4px;
    .concern-chip {
      min-width: 74px;
      min-height: 28px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      padding: 0 9px;
      border: 1.5px solid rgba(207, 238, 241, 0.92);
      border-radius: 13px;
      background: rgba(255, 255, 255, 0.62);
      color: rgba(67, 82, 102, 0.78);
      font-family: inherit;
      font-size: 13px;
      font-weight: 800;
      white-space: nowrap;
      cursor: pointer;
      transition: $transition;
      &.active {
        border-color: $mint-primary;
        background: rgba(230, 251, 250, 0.9);
        color: $mint-primary;
      }
    }
  }
  .skin-scroll,
  .pregnancy-scroll {
    display: flex;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    gap: 8px;
    padding: 10px 0 6px;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-x;
    scrollbar-width: thin;
    .select-chip {
      width: auto;
      flex: 0 0 auto;
      min-height: 30px;
      padding-right: 9px;
      padding-left: 9px;
      overflow: visible;
      text-overflow: clip;
    }
  }
  .select-pill,
  .select-chip {
    min-width: 0;
    width: 100%;
    min-height: 40px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border: 1.5px solid rgba(207, 238, 241, 0.92);
    border-radius: 13px;
    background: rgba(255, 255, 255, 0.58);
    color: rgba(67, 82, 102, 0.78);
    font-family: inherit;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
    transition: $transition;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    &.active {
      border-color: $mint-primary;
      background: rgba(230, 251, 250, 0.88);
      color: $mint-primary;
      box-shadow: inset 0 0 0 1px rgba(13, 124, 135, 0.08);
    }
  }
  .select-pill {
    span {
      font-size: 18px;
      line-height: 1;
    }
  }
  .range-field {
    grid-template-columns: 1fr auto;
    align-items: center;
    row-gap: 10px;
    strong {
      color: $mint-primary;
      font-size: 15px;
    }
    input[type='range'] {
      grid-column: 1 / -1;
      width: 100%;
      height: 3px;
      padding: 0;
      accent-color: $mint-primary;
      border: 0;
      border-radius: 3px;
      box-shadow: none;
      appearance: none;
      cursor: pointer;
      &::-webkit-slider-runnable-track {
        height: 3px;
        border-radius: 3px;
        background: transparent;
      }
      &::-webkit-slider-thumb {
        appearance: none;
        width: 18px;
        height: 18px;
        margin-top: -7.5px;
        border: 3px solid $white;
        border-radius: 50%;
        background: $mint-primary;
        box-shadow: 0 4px 12px rgba(13, 124, 135, 0.22);
        transform: translateX(-4px);
      }
      &::-moz-range-track {
        height: 3px;
        border-radius: 3px;
        background: transparent;
      }
      &::-moz-range-thumb {
        width: 14px;
        height: 14px;
        border: 3px solid $white;
        border-radius: 50%;
        background: $mint-primary;
        box-shadow: 0 4px 12px rgba(13, 124, 135, 0.22);
        transform: translateX(-4px);
      }
    }
    small {
      grid-column: 1 / -1;
      position: relative;
      display: block;
      height: 16px;
      margin-top: 4px;
      color: rgba(122, 138, 157, 0.56);
      font-size: 10px;
      font-weight: 800;
      em {
        position: absolute;
        top: 0;
        transform: translateX(-50%);
        font-style: normal;
        transition: $transition;
        white-space: nowrap;
        &:first-child {
          transform: translateX(0);
        }
        &:last-child {
          transform: translateX(-100%);
        }
        &.active {
          color: $mint-primary;
          transform: translate(-50%, -1px);
          &:first-child {
            transform: translate(0, -1px);
          }
          &:last-child {
            transform: translate(-100%, -1px);
          }
        }
      }
    }
  }
  .section-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    min-width: 0;
    p {
      flex: 0 0 auto;
    }
  }
  .tone-value {
    flex: 1 1 auto;
    min-width: 0;
    max-width: 52%;
    color: $mint-primary;
    font-size: 13px;
    font-weight: 800;
    text-align: right;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .hint-button {
    position: relative;
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border: 0;
    background: transparent;
    color: rgba(122, 138, 157, 0.88);
    cursor: help;
    span {
      position: absolute;
      right: 0;
      top: 34px;
      z-index: 30;
      width: min(252px, calc(100vw - 58px));
      padding: 10px 12px;
      border: 1px solid rgba(207, 238, 241, 0.95);
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.96);
      box-shadow: 0 14px 32px rgba(17, 24, 39, 0.12);
      color: rgba(67, 82, 102, 0.84);
      font-size: 12px;
      font-weight: 700;
      line-height: 1.55;
      text-align: left;
      opacity: 0;
      pointer-events: none;
      transform: translateY(-4px);
      transition: opacity 0.16s ease, transform 0.16s ease;
    }
    &:hover,
    &:focus {
      span {
        opacity: 1;
        transform: translateY(0);
      }
    }
  }
  .tone-wrap {
    position: relative;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    padding: 10px 0 0;
    .tone-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      margin: 0;
      padding: 0;
      list-style: none;
      li {
        flex: 1 1 0;
        display: flex;
        justify-content: center;
        min-width: 0;
      }
      .tone-dot {
        width: clamp(30px, 8.8vw, 42px);
        height: clamp(30px, 8.8vw, 42px);
        flex: 0 0 auto;
        display: grid;
        place-items: center;
        border: 2px solid rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        color: $mint-primary;
        cursor: pointer;
        box-shadow:
          0 10px 20px rgba(17, 24, 39, 0.07),
          inset 0 0 0 1px rgba(255, 255, 255, 0.55);
        transition: $transition;
        &.active {
          border: 2px solid $mint-primary;
          transform: translateY(-1px) scale(1.04);
        }
      }
    }
  }
  .face-scroll {
    display: flex;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    gap: 13px;
    padding: 10px 0 5px;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-x;
    scrollbar-width: thin;
    .face-option {
      position: relative;
      width: 76px;
      flex: 0 0 76px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 4px 0;
      border: 0;
      background: transparent;
      cursor: pointer;
      transition: $transition;
      span {
        width: 76px;
        height: 76px;
        border-radius: 50%;
        border: 1.5px solid rgba(207, 238, 241, 0.88);
        background-repeat: no-repeat;
        background-color: rgba(255, 255, 255, 0.72);
        transition: $transition;
      }
      em {
        color: rgba(30, 41, 45, 0.84);
        font-style: normal;
        font-size: 13px;
        text-align: center;
        white-space: nowrap;
        transition: $transition;
      }
      &.active {
        span {
          border-color: $mint-primary;
          box-shadow: 0 8px 20px rgba(13, 124, 135, 0.16);
        }
        em {
          color: $mint-primary;
        }
      }
    }
  }
  .face-placeholder {
    display: grid;
    place-items: center;
    min-height: 86px;
    margin-top: 10px;
    border: 1px dashed rgba(13, 124, 135, 0.25);
    border-radius: 18px;
    color: rgba(67, 82, 102, 0.54);
    font-size: 13px;
    font-weight: 700;
  }
  .field-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(92px, 0.72fr);
    gap: 10px;
    min-width: 0;
  }
}
@include respond(tablet-portrait) {
  .profile-page {
    border-right: 1px solid rgba(207, 238, 241, 0.72);
    border-left: 1px solid rgba(207, 238, 241, 0.72);
    box-shadow: 0 24px 80px rgba(17, 24, 39, 0.1);
  }
}
@include respond(tablet-landscape) {
  .profile-page {
    border-right: 1px solid rgba(207, 238, 241, 0.72);
    border-left: 1px solid rgba(207, 238, 241, 0.72);
    box-shadow: 0 24px 80px rgba(17, 24, 39, 0.1);
  }
}
@include respond(desktop) {
  .profile-page {
    border-right: 1px solid rgba(207, 238, 241, 0.72);
    border-left: 1px solid rgba(207, 238, 241, 0.72);
    box-shadow: 0 24px 80px rgba(17, 24, 39, 0.1);
  }
}
@include respond(phone-sm) {
  .profile-page {
    .profile-stage {
      min-height: 186px;
      padding-right: 18px;
      padding-left: 18px;
    }
    .profile-nav {
      grid-template-columns: 36px 1fr 36px;
      button {
        width: 36px;
        height: 36px;
      }
      h1 {
        font-size: 21px;
      }
    }
    .profile-hero {
      min-height: 102px;
      article {
        width: 178px;
        max-width: 62%;
        h2 {
          font-size: 20px;
        }
        p {
          font-size: 12px;
          letter-spacing: 0.08em;
        }
      }
    }
    .profile-form {
      padding-right: 12px;
      padding-left: 12px;
      section {
        padding: 14px;
      }
    }
    .gender-options,
    .chip-grid {
      gap: 8px;
    }
    .select-pill,
    .select-chip {
      min-height: 39px;
      padding-right: 8px;
      padding-left: 8px;
      font-size: 13px;
    }
    .concern-grid {
      gap: 8px;
      .concern-chip {
        min-width: 68px;
        min-height: 28px;
        padding: 0 11px;
        font-size: 12px;
      }
    }
    .skin-scroll,
    .pregnancy-scroll {
      gap: 8px;
      .select-chip {
        width: auto;
        flex: 1 0 72px;
        padding-right: 14px;
        padding-left: 14px;
      }
    }
    .tone-wrap {
      .tone-row {
        .tone-dot {
          width: 38px;
          height: 38px;
        }
      }
    }
    .face-scroll {
      gap: 13px;
    }
  }
}
.custom-datepicker-mask {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: grid;
  place-items: center;
  padding: 20px;
  animation: fadeIn 0.24s ease;
  .custom-datepicker-card {
    width: 100%;
    max-width: 340px;
    border-radius: 24px;
    background: #ffffff;
    border: 1px solid rgba(207, 238, 241, 0.95);
    box-shadow: 0 20px 50px rgba(17, 24, 39, 0.15);
    padding: 20px;
    animation: scaleIn 0.24s cubic-bezier(0.34, 1.56, 0.64, 1);
    .datepicker-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      h4 {
        color: rgba(31, 41, 43, 0.88);
        font-size: 16px;
        font-weight: 800;
        margin: 0;
      }
      button {
        width: 32px;
        height: 32px;
        border: 0;
        border-radius: 50%;
        background: rgba(210, 244, 245, 0.44);
        color: $mint-primary;
        font-size: 18px;
        font-weight: 800;
        cursor: pointer;
        display: grid;
        place-items: center;
        transition: $transition;
        &:hover {
          background: rgba(210, 244, 245, 0.8);
        }
      }
    }
    .datepicker-weekdays {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      text-align: center;
      margin-bottom: 8px;
      span {
        color: rgba(67, 82, 102, 0.54);
        font-size: 12px;
        font-weight: 800;
      }
    }
    .datepicker-days {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      row-gap: 6px;
      margin-bottom: 20px;
      .day-btn {
        aspect-ratio: 1;
        border: 0;
        background: transparent;
        border-radius: 50%;
        color: rgba(31, 41, 43, 0.88);
        font-family: inherit;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        display: grid;
        place-items: center;
        transition: $transition;
        &.other-month {
          color: rgba(122, 138, 157, 0.36);
        }
        &.active {
          background: $mint-primary;
          color: #ffffff;
          box-shadow: 0 8px 16px rgba(13, 124, 135, 0.28);
        }
        &:hover:not(.active) {
          background: rgba(230, 251, 250, 0.8);
        }
      }
    }
    .datepicker-footer {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      button {
        height: 40px;
        border-radius: 12px;
        font-family: inherit;
        font-size: 14px;
        font-weight: 800;
        cursor: pointer;
        transition: $transition;
      }
      .btn-cancel {
        border: 1.5px solid rgba(207, 238, 241, 0.95);
        background: #ffffff;
        color: rgba(67, 82, 102, 0.78);
      }
      .btn-confirm {
        border: 0;
        background: $mint-primary;
        color: #ffffff;
        box-shadow: 0 8px 20px rgba(13, 124, 135, 0.18);
      }
    }
  }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
