<template>
  <div class="profile-form">
    <div class="form-row">
      <div class="form-group">
        <label>昵称</label>
        <input type="text" v-model="form.name" placeholder="怎么称呼你？" maxlength="20" />
      </div>
      <div class="form-group">
        <label>年龄</label>
        <input type="number" v-model.number="form.age" placeholder="例如：25" min="1" max="120" class="form-input-number" />
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

    <!-- 脸型图片选择器 -->
    <div class="form-group full-width-group">
      <label>脸型选择</label>
      <div class="image-select-grid">
        <div v-for="item in faceOptions" :key="item.value"
             class="image-select-card" :class="{ selected: form.face_shape === item.value }"
             @click="form.face_shape = item.value">
          <div class="card-img-wrapper">
            <div class="face-preview" :class="item.value" aria-hidden="true">
              <span class="neck"></span>
              <span class="hair"></span>
              <span class="head">
                <span class="eye left"></span>
                <span class="eye right"></span>
                <span class="nose"></span>
                <span class="mouth"></span>
              </span>
            </div>
          </div>
          <span class="card-label">{{ item.label }}</span>
        </div>
      </div>
    </div>

    <!-- 肤色图片选择器 -->
    <div class="form-group full-width-group">
      <label>肤色选择</label>
      <div class="image-select-grid">
        <div v-for="item in toneOptions" :key="item.value"
             class="image-select-card" :class="{ selected: form.skin_tone === item.value }"
             @click="form.skin_tone = item.value">
          <div class="card-img-wrapper">
            <div class="tone-preview" :style="{ '--skin': item.color, '--shade': item.shade }" aria-hidden="true">
              <span></span>
            </div>
          </div>
          <span class="card-label">{{ item.label }}</span>
        </div>
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

const faceOptions = [
  { value: 'oval', label: '鹅蛋脸' },
  { value: 'round', label: '圆脸' },
  { value: 'square', label: '方脸' },
  { value: 'heart', label: '心形脸' },
  { value: 'diamond', label: '菱形脸' },
]

const toneOptions = [
  { value: 'fair', label: '白皙', color: '#f8dfd2', shade: '#f0c5b2' },
  { value: 'light', label: '自然偏白', color: '#f1c9a5', shade: '#dca77c' },
  { value: 'medium', label: '自然肤色', color: '#d79a63', shade: '#b9773d' },
  { value: 'tan', label: '小麦色', color: '#ae6f37', shade: '#865024' },
  { value: 'dark', label: '深色肌肤', color: '#6a341f', shade: '#472013' },
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 20px;

  &.full-width-group {
    grid-column: span 2;
  }

  label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: $text-secondary;
    margin-bottom: 8px;
  }

  input[type="text"],
  input[type="number"],
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

.image-select-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;

  .image-select-card {
    border: 2px solid $mint-pale;
    border-radius: $radius;
    background: $white;
    padding: 12px;
    cursor: pointer;
    text-align: center;
    transition: $transition;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;

    .card-img-wrapper {
      width: 72px;
      height: 72px;
      border-radius: 50%;
      overflow: hidden;
      background: $bg-light;
      border: 1px solid rgba(0, 0, 0, 0.04);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: $transition;
    }

    .card-label {
      font-size: 13px;
      font-weight: 600;
      color: $text-secondary;
      white-space: nowrap;
    }

    &:hover {
      border-color: $mint-primary;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(26, 122, 92, 0.08);
      
      .card-img-wrapper {
        transform: scale(1.05);
      }
    }

    &.selected {
      border-color: $mint-primary;
      background: $mint-bg;
      box-shadow: 0 4px 15px rgba(26, 122, 92, 0.15);

      .card-img-wrapper {
        border-color: $mint-primary;
        box-shadow: 0 0 0 2px rgba(45, 143, 111, 0.2);
      }

      .card-label {
        color: $mint-dark;
      }
    }
  }
}

.face-preview {
  position: relative;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #fff8e8;
  display: flex;
  align-items: center;
  justify-content: center;

  .neck {
    position: absolute;
    left: 29px;
    bottom: 8px;
    width: 14px;
    height: 16px;
    background: #f2c7a8;
    border: 1px solid #b88066;
    border-radius: 0 0 8px 8px;
  }

  .hair {
    position: absolute;
    left: 18px;
    top: 13px;
    width: 36px;
    height: 28px;
    background: #4b2d24;
    border-radius: 22px 22px 12px 12px;
    z-index: 1;
  }

  .head {
    position: absolute;
    left: 50%;
    top: 17px;
    width: 36px;
    height: 46px;
    transform: translateX(-50%);
    background: #f2c7a8;
    border: 1.5px solid #9d6a54;
    border-radius: 48% 48% 46% 46%;
    z-index: 2;
    box-shadow: inset 0 6px 0 rgba(255, 255, 255, 0.22);
  }

  .eye {
    position: absolute;
    top: 20px;
    width: 4px;
    height: 2px;
    border-radius: 50%;
    background: #3a2a24;

    &.left { left: 10px; }
    &.right { right: 10px; }
  }

  .nose {
    position: absolute;
    left: 50%;
    top: 24px;
    width: 1px;
    height: 7px;
    background: #b98270;
    transform: translateX(-50%);
  }

  .mouth {
    position: absolute;
    left: 50%;
    bottom: 9px;
    width: 10px;
    height: 3px;
    border-bottom: 2px solid #b85f62;
    border-radius: 0 0 10px 10px;
    transform: translateX(-50%);
  }

  &.round .head {
    width: 42px;
    height: 42px;
    top: 19px;
    border-radius: 50%;
  }

  &.square .head {
    width: 40px;
    height: 44px;
    top: 18px;
    border-radius: 28% 28% 18% 18%;
  }

  &.heart .head {
    width: 40px;
    height: 46px;
    top: 17px;
    clip-path: polygon(50% 100%, 20% 78%, 10% 42%, 22% 12%, 50% 2%, 78% 12%, 90% 42%, 80% 78%);
    border-radius: 44% 44% 50% 50%;
  }

  &.diamond .head {
    width: 40px;
    height: 48px;
    top: 16px;
    clip-path: polygon(50% 0, 86% 28%, 74% 78%, 50% 100%, 26% 78%, 14% 28%);
    border-radius: 28%;
  }
}

.tone-preview {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #f8fbf8;
  display: flex;
  align-items: center;
  justify-content: center;

  span {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background:
      radial-gradient(circle at 32% 28%, rgba(255, 255, 255, 0.55), transparent 28%),
      linear-gradient(135deg, var(--skin), var(--shade));
    border: 2px solid rgba(255, 255, 255, 0.9);
    box-shadow:
      inset -7px -8px 14px rgba(0, 0, 0, 0.12),
      0 2px 8px rgba(26, 122, 92, 0.12);
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
  .form-group.full-width-group { grid-column: span 1; }

  .form-group {
    margin-bottom: 18px;

    input[type="text"],
    input[type="number"],
    select {
      min-height: 46px;
      border-radius: 12px;
      background: $white;
    }
  }

  .image-select-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;

    .image-select-card {
      min-height: 116px;
      padding: 10px 8px;

      .card-img-wrapper {
        width: 64px;
        height: 64px;
      }
    }
  }

  .radio-group,
  .checkbox-group {
    gap: 8px;
  }

  .radio-label,
  .checkbox-label {
    min-height: 42px;
    padding: 8px 13px;
  }
}

@media (max-width: 380px) {
  .image-select-grid {
    grid-template-columns: 1fr;
  }
}
</style>
