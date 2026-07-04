<template>
  <div class="home">
    <!-- Hero -->
    <div class="hero">
      <div class="hero-content">
        <div class="hero-kicker">AI Beauty Intelligence</div>
        <h1 class="hero-title">把每一次种草，变成可解释的<span class="highlight">美妆决策</span></h1>
        <p class="hero-subtitle">基于肤质档案、产品风险与已有囤货，给出更克制、更个性化的护肤与妆容建议。</p>
        <div class="hero-actions">
          <router-link to="/chat" class="btn btn-primary">开始咨询</router-link>
          <router-link to="/profile" class="btn btn-secondary">建立档案</router-link>
        </div>
        <div class="trust-row">
          <span>肤质匹配</span>
          <span>成分避雷</span>
          <span>产品库搭配</span>
        </div>
      </div>
      <div class="hero-graphic">
        <div class="beauty-panel">
          <div class="panel-header">
            <span>AI BEAUTY</span>
            <strong>92</strong>
          </div>
          <div class="scan-orbit">
            <span class="face-mark"></span>
            <span class="scan-line"></span>
          </div>
          <div class="panel-metrics">
            <span>肤质匹配</span>
            <strong>高</strong>
          </div>
          <div class="panel-metrics">
            <span>产品风险</span>
            <strong>低</strong>
          </div>
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
  { icon: '01', title: '个人档案', desc: '记录肤质、年龄、脸型等信息，获取精准推荐', path: '/profile' },
  { icon: '02', title: 'AI 美妆助手', desc: '智能对话，根据你的资料推荐妆容与产品', path: '/chat' },
  { icon: '03', title: '达人推荐', desc: '精选美妆达人分享的护肤心得与妆容教程', path: '/influencers' },
  { icon: '04', title: '产品百科', desc: '海量美妆护肤产品信息，一键了解', path: '/products' },
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

  .hero-kicker {
    display: inline-flex;
    align-items: center;
    height: 30px;
    padding: 0 12px;
    margin-bottom: 14px;
    border: 1px solid rgba(10, 166, 194, 0.18);
    border-radius: 999px;
    background: rgba(240, 251, 252, 0.82);
    color: $mint-primary;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0;
  }

  .hero-title {
    max-width: 620px;
    font-size: 46px;
    font-weight: 900;
    line-height: 1.12;
    margin-bottom: 16px;

    .highlight {
      display: block;
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

  .trust-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;

    span {
      padding: 7px 12px;
      border: 1px solid rgba(207, 238, 241, 0.92);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.76);
      color: $text-secondary;
      font-size: 13px;
      font-weight: 700;
    }
  }

  .hero-graphic {
    flex: 0 0 320px;
  }

  .beauty-panel {
    min-height: 340px;
    padding: 24px;
    border: 1px solid rgba(207, 238, 241, 0.9);
    border-radius: 28px;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(240, 251, 252, 0.86));
    box-shadow: $shadow-hover;
  }

  .panel-header,
  .panel-metrics {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .panel-header {
    color: $text-light;
    font-size: 12px;
    font-weight: 800;

    strong {
      color: $text-primary;
      font-size: 32px;
      line-height: 1;
    }
  }

  .scan-orbit {
    position: relative;
    width: 180px;
    height: 180px;
    margin: 32px auto;
    border: 1px solid rgba(10, 166, 194, 0.18);
    border-radius: 50%;
    background:
      radial-gradient(circle, rgba(114, 215, 220, 0.18) 0 38%, transparent 39%),
      linear-gradient(180deg, $white, $mint-bg);
    overflow: hidden;
  }

  .face-mark {
    position: absolute;
    inset: 34px 48px 28px;
    border: 2px solid rgba(24, 58, 67, 0.2);
    border-radius: 48% 48% 44% 44%;
    background: rgba(255, 255, 255, 0.46);
  }

  .scan-line {
    position: absolute;
    left: 24px;
    right: 24px;
    top: 50%;
    height: 2px;
    background: linear-gradient(90deg, transparent, $mint-primary, transparent);
    box-shadow: 0 0 16px rgba(10, 166, 194, 0.45);
  }

  .panel-metrics {
    padding: 13px 0;
    border-top: 1px solid rgba(207, 238, 241, 0.9);

    span {
      color: $text-light;
      font-size: 13px;
    }

    strong {
      color: $mint-dark;
      font-size: 15px;
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
    border: 1px solid rgba(207, 238, 241, 0.78);
    display: block;

    &:hover {
      transform: translateY(-4px);
      box-shadow: $shadow-hover;
      border-color: $mint-pale;
    }

    .feature-icon {
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      margin: 0 auto 14px;
      border-radius: 14px;
      background: $mint-bg;
      color: $mint-primary;
      font-size: 14px;
      font-weight: 900;
      letter-spacing: 0;
    }

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
  .home {
    padding-bottom: 4px;
  }

  .hero {
    flex-direction: column;
    align-items: stretch;
    text-align: left;
    gap: 20px;
    padding: 8px 0 28px;

    .hero-title {
      font-size: 33px;
      margin-bottom: 12px;
    }

    .hero-subtitle {
      max-width: 100%;
      font-size: 15px;
      margin-bottom: 22px;
    }

    .hero-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .trust-row {
      margin-top: 14px;
      gap: 8px;

      span {
        padding: 6px 10px;
        font-size: 12px;
      }
    }

    .hero-graphic {
      display: block;
      flex: none;
    }

    .beauty-panel {
      min-height: 198px;
      padding: 18px;
      border-radius: 18px;
      box-shadow: none;
    }

    .scan-orbit {
      width: 92px;
      height: 92px;
      margin: 14px auto;
    }

    .face-mark {
      inset: 18px 26px 14px;
    }

    .panel-header strong {
      font-size: 24px;
    }

    .panel-metrics {
      padding: 8px 0;
    }
  }

  .features-section,
  .quick-tips {
    margin-bottom: 30px;
  }

  .section-title {
    font-size: 21px;
    margin-bottom: 14px;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 12px;

    .feature-card {
      display: grid;
      grid-template-columns: 44px 1fr;
      gap: 4px 14px;
      text-align: left;
      padding: 18px;
      border: 1px solid $mint-pale;
      box-shadow: none;

      .feature-icon {
        grid-row: span 2;
        font-size: 30px;
        margin-bottom: 0;
      }

      h3 {
        font-size: 16px;
        margin-bottom: 0;
      }
    }
  }

  .tips-carousel {
    margin-left: -14px;
    margin-right: -14px;
    padding: 4px 14px 14px;

    .tip-card {
      flex-basis: min(82vw, 320px);
      padding: 16px 18px;
      font-size: 14px;
    }
  }
}

@media (max-width: 380px) {
  .hero .hero-actions {
    grid-template-columns: 1fr;
  }
}
</style>
