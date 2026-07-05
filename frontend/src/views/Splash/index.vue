<!-- 开屏页面：展示品牌启动视觉。 -->
<template>
  <section class="splash-screen" aria-label="智颜 AI 开屏页">
    <img class="splash-bg" src="@/assets/images/开屏页背景.png" alt="" />
    <img class="splash-logo" src="@/assets/images/logo1.png" alt="智颜 AI" />
    <div class="splash-title">
      <h1>智颜AI</h1>
      <p>智算肌肤，定制之美</p>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.splash-screen {
  position: fixed;
  inset: 0;
  z-index: 5000;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #eefafa;
}
.splash-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
.splash-logo {
  position: absolute;
  left: 52%;
  top: 27%;
  width: min(38vw, 280px);
  height: auto;
  transform: translate(-50%, -50%);
  filter: drop-shadow(0 18px 28px rgba(10, 166, 194, 0.22));
}
.splash-title {
  position: absolute;
  left: 50%;
  top: 75%;
  width: min(58vw, 320px);
  transform: translate(-50%, -50%);
  text-align: center;
  color: rgba(38, 43, 44, 0.86);
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.7);
  h1 {
    font-size: clamp(34px, 9.6vw, 48px);
    line-height: 1.1;
    font-weight: 400;
    letter-spacing: 0.18em;
    white-space: nowrap;
  }
  p {
    margin-top: 16px;
    color: rgba(56, 66, 68, 0.72);
    font-size: clamp(14px, 3.7vw, 18px);
    font-weight: 500;
    letter-spacing: 0.34em;
    white-space: nowrap;
  }
}
@include respond(tablet-portrait) {
  .splash-screen {
    background:
      radial-gradient(circle at center, rgba(207, 238, 241, 0.72), transparent 52%),
      #f8feff;
  }
  .splash-bg {
    width: min(100vw, 430px);
    box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
  }
  .splash-logo {
    width: 126px;
  }
  .splash-title {
    width: 260px;
  }
  .splash-title h1 {
    font-size: 40px;
  }
  .splash-title p {
    font-size: 15px;
  }
}
@include respond(tablet-landscape) {
  .splash-screen {
    background:
      radial-gradient(circle at center, rgba(207, 238, 241, 0.72), transparent 52%),
      #f8feff;
  }
  .splash-bg {
    width: min(100vw, 430px);
    box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
  }
  .splash-logo {
    width: 126px;
  }
  .splash-title {
    width: 260px;
  }
  .splash-title h1 {
    font-size: 40px;
  }
  .splash-title p {
    font-size: 15px;
  }
}
@include respond(desktop) {
  .splash-screen {
    background:
      radial-gradient(circle at center, rgba(207, 238, 241, 0.72), transparent 52%),
      #f8feff;
  }
  .splash-bg {
    width: min(100vw, 430px);
    box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
  }
  .splash-logo {
    width: 126px;
  }
  .splash-title {
    width: 260px;
  }
  .splash-title h1 {
    font-size: 40px;
  }
  .splash-title p {
    font-size: 15px;
  }
}
</style>
