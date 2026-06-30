<template>
  <div class="profile-form">
    <div class="form-row">
      <div class="form-group">
        <label>昵称</label>
        <input type="text" v-model="form.name" placeholder="怎么称呼你？" maxlength="20" />
      </div>
      <div class="form-group">
        <label>年龄</label>
        <select v-model="form.age">
          <option value="">请选择年龄段</option>
          <option value="under18">18岁以下</option>
          <option value="18-22">18-22岁</option>
          <option value="23-28">23-28岁</option>
          <option value="29-35">29-35岁</option>
          <option value="36-45">36-45岁</option>
          <option value="over45">45岁以上</option>
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>性别</label>
        <div class="radio-group">
          <label v-for="g in genderOptions" :key="g.value" class="radio-label"
                 :class="{ checked: form.gender === g.value }">
            <input type="radio" :value="g.value" v-model="form.gender" />
            {{ g.label }}
          </label>
        </div>
      </div>
      <div class="form-group">
        <label>肤质类型</label>
        <select v-model="form.skin_type">
          <option value="">请选择肤质</option>
          <option value="dry">干性肌肤</option>
          <option value="oily">油性肌肤</option>
          <option value="combination">混合性肌肤</option>
          <option value="normal">中性肌肤</option>
          <option value="sensitive">敏感性肌肤</option>
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>脸型</label>
        <select v-model="form.face_shape">
          <option value="">请选择脸型</option>
          <option value="round">圆脸</option>
          <option value="square">方脸</option>
          <option value="oval">鹅蛋脸/长脸</option>
          <option value="heart">心形脸</option>
          <option value="diamond">菱形脸</option>
        </select>
      </div>
      <div class="form-group">
        <label>肤色</label>
        <select v-model="form.skin_tone">
          <option value="">请选择肤色</option>
          <option value="fair">白皙</option>
          <option value="light">自然偏白</option>
          <option value="medium">自然肤色</option>
          <option value="tan">小麦色</option>
          <option value="dark">深色肌肤</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label>护肤关注点（可多选）</label>
      <div class="checkbox-group">
        <label v-for="c in concernOptions" :key="c.value" class="checkbox-label"
               :class="{ checked: form.concerns.includes(c.value) }">
          <input type="checkbox" :value="c.value" v-model="form.concerns" />
          {{ c.label }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue'])

const genderOptions = [
  { value: 'female', label: '女性' },
  { value: 'male', label: '男性' },
  { value: 'other', label: '其他' },
]

const concernOptions = [
  { value: 'acne', label: '痘痘/痘印' },
  { value: 'blackhead', label: '黑头/白头' },
  { value: 'wrinkle', label: '细纹/抗衰' },
  { value: 'dullness', label: '暗沉/提亮' },
  { value: 'darkcircle', label: '黑眼圈' },
  { value: 'pore', label: '毛孔粗大' },
  { value: 'hydration', label: '保湿补水' },
  { value: 'sensitive', label: '屏障修护' },
]

const form = reactive({
  name: props.modelValue?.name || '',
  age: props.modelValue?.age || '',
  gender: props.modelValue?.gender || '',
  skin_type: props.modelValue?.skin_type || '',
  face_shape: props.modelValue?.face_shape || '',
  skin_tone: props.modelValue?.skin_tone || '',
  concerns: props.modelValue?.concerns || [],
})

watch(() => props.modelValue, (val) => {
  if (val) Object.assign(form, val)
}, { deep: true })

watch(form, () => {
  emit('update:modelValue', { ...form })
}, { deep: true })
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;

  label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: $text-secondary;
    margin-bottom: 6px;
  }

  input[type="text"],
  select {
    width: 100%;
    padding: 12px 16px;
    border: 1.5px solid $mint-pale;
    border-radius: $radius-sm;
    font-size: 14px;
    color: $text-primary;
    background: $bg-light;
    transition: $transition;
    font-family: inherit;

    &:focus {
      outline: none;
      border-color: $mint-primary;
      box-shadow: 0 0 0 3px rgba(45, 143, 111, 0.15);
      background: $white;
    }
  }
}

.radio-group {
  display: flex;
  gap: 12px;
  padding-top: 4px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1.5px solid $mint-pale;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: $transition;

  &.checked {
    border-color: $mint-primary;
    background: $mint-bg;
    color: $mint-dark;
  }

  input { accent-color: $mint-primary; }
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1.5px solid $mint-pale;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: $transition;

  &.checked {
    border-color: $mint-primary;
    background: $mint-bg;
    color: $mint-dark;
  }

  input { accent-color: $mint-primary; }
}

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>
