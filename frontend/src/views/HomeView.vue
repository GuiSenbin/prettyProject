<template>
  <div class="home">
    <!-- Hero -->
    <div class="hero">
      <div class="hero-content">
        <h1 class="hero-title">发现属于你的 <span class="highlight">美</span></h1>
        <p class="hero-subtitle">用算力解析肌理状态，以光影重塑面部轮廓</p>
        <div class="hero-actions">
          <router-link to="/chat" class="btn btn-primary">开始咨询</router-link>
          <router-link to="/profile" class="btn btn-secondary">建立档案</router-link>
        </div>
      </div>
      <div class="hero-graphic">
        <div class="graphic-grid">
          <span class="graphic-item">🌸</span>
          <span class="graphic-item">✨</span>
          <span class="graphic-item">💄</span>
          <span class="graphic-item">🧴</span>
        </div>
      </div>
    </div>

    <!-- 功能卡片 -->
    <section class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <router-link v-for="f in features" :key="f.title" :to="f.path" class="feature-card">
          <div class="feature-icon">{{ f.icon }}</div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </router-link>
      </div>
    </section>

    <!-- 小贴士 -->
    <section class="quick-tips">
      <h2 class="section-title">今日美妆小贴士</h2>
      <div class="tips-carousel">
        <div v-for="(tip, i) in tips" :key="i" class="tip-card">💡 {{ tip }}</div>
      </div>
    </section>
  </div>
</template>

<script setup>
const features = [
  { icon: '📋', title: '个人档案', desc: '记录肤质、年龄、脸型等信息，获取精准推荐', path: '/profile' },
  { icon: '🤖', title: 'AI 美妆助手', desc: '智能对话，根据你的资料推荐妆容与产品', path: '/chat' },
  { icon: '⭐', title: '达人推荐', desc: '精选美妆达人分享的护肤心得与妆容教程', path: '/influencers' },
  { icon: '📚', title: '产品百科', desc: '海量美妆护肤产品信息，一键了解', path: '/products' },
]

const tips = [
  '不管什么肤质，防晒都是一年四季必不可少的护肤步骤',
  '卸妆要彻底，但也不要过度清洁，会破坏皮肤屏障',
  '化妆前做好保湿，底妆才会更服帖持久',
  '油性肌肤也需要保湿，选择清爽型即可',
]
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.hero {
  display: flex;
  align-items: center;
  gap: 48px;
  padding: 40px 0 60px;

  .hero-content { flex: 1; }

  .hero-title {
    font-size: 44px;
    font-weight: 900;
    line-height: 1.2;
    margin-bottom: 16px;

    .highlight {
      background: $gradient-primary;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  .hero-subtitle {
    font-size: 17px;
    color: $text-secondary;
    line-height: 1.7;
    margin-bottom: 32px;
    max-width: 520px;
  }

  .hero-actions { display: flex; gap: 16px; }

  .hero-graphic { flex: 0 0 280px; }

  .graphic-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;

    .graphic-item {
      width: 120px;
      height: 120px;
      background: $mint-bg;
      border-radius: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 48px;
      box-shadow: $shadow;
      transition: $transition;

      &:hover {
        transform: scale(1.05) rotate(-3deg);
        box-shadow: $shadow-hover;
      }
    }
  }
}

.features-section, .quick-tips { margin-bottom: 48px; }

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 20px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;

  .feature-card {
    background: $white;
    border-radius: $radius;
    padding: 28px 24px;
    text-align: center;
    box-shadow: $shadow;
    transition: $transition;
    border: 1px solid transparent;
    display: block;

    &:hover {
      transform: translateY(-4px);
      box-shadow: $shadow-hover;
      border-color: $mint-pale;
    }

    .feature-icon { font-size: 40px; margin-bottom: 12px; }

    h3 {
      font-size: 18px;
      font-weight: 700;
      color: $mint-dark;
      margin-bottom: 8px;
    }

    p {
      color: $text-light;
      font-size: 14px;
      line-height: 1.6;
    }
  }
}

.tips-carousel {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding: 16px 0;
  scroll-snap-type: x mandatory;

  .tip-card {
    flex: 0 0 320px;
    scroll-snap-align: start;
    background: linear-gradient(135deg, $mint-bg, $white);
    border: 1px solid $mint-pale;
    border-radius: $radius-sm;
    padding: 20px 24px;
    font-size: 15px;
    color: $text-secondary;
    line-height: 1.6;
  }
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    text-align: center;
    padding: 24px 0 40px;

    .hero-title { font-size: 32px; }
    .hero-subtitle { max-width: 100%; }
    .hero-actions { justify-content: center; }
    .hero-graphic { display: none; }
  }
}
</style>
