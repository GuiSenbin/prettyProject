<template>
  <section class="splash-screen" aria-label="智颜 AI 开屏页">
    <img src="@/assets/images/开屏页背景.png" alt="" />
    <img src="@/assets/images/logo1.png" alt="智颜 AI" />
    <div>
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
  background: #f4fbfb;
  img:first-of-type {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
    @include respond(tablet-portrait) {
      width: min(100vw, 430px);
      height: 100dvh;
      box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
    }
    @include respond(tablet-landscape) {
      width: min(100vw, 430px);
      height: 100dvh;
      box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
    }
    @include respond(desktop) {
      width: min(100vw, 430px);
      height: 100dvh;
      box-shadow: 0 28px 80px rgba(17, 24, 39, 0.14);
    }
  }
  img:last-of-type {
    position: absolute;
    left: 52%;
    top: 27%;
    width: min(38vw, 280px);
    height: auto;
    transform: translate(-50%, -50%);
    filter: drop-shadow(0 18px 28px rgba(10, 166, 194, 0.22));
    @include respond(tablet-portrait) {
      width: 126px;
    }
    @include respond(tablet-landscape) {
      width: 126px;
    }
    @include respond(desktop) {
      width: 126px;
    }
  }
  div {
    position: absolute;
    left: 50%;
    top: 75%;
    width: min(58vw, 320px);
    transform: translate(-50%, -50%);
    text-align: center;
    color: rgba(38, 43, 44, 0.86);
    text-shadow: 0 2px 10px rgba(255, 255, 255, 0.7);
    @include respond(tablet-portrait) {
      width: 260px;
    }
    @include respond(tablet-landscape) {
      width: 260px;
    }
    @include respond(desktop) {
      width: 260px;
    }
    h1 {
      font-size: clamp(34px, 9.6vw, 48px);
      line-height: 1.1;
      font-weight: 400;
      letter-spacing: 0.18em;
      white-space: nowrap;
      @include respond(tablet-portrait) {
        font-size: 40px;
      }
      @include respond(tablet-landscape) {
        font-size: 40px;
      }
      @include respond(desktop) {
        font-size: 40px;
      }
    }
    p {
      margin-top: 16px;
      color: rgba(56, 66, 68, 0.72);
      font-size: clamp(14px, 3.7vw, 18px);
      font-weight: 500;
      letter-spacing: 0.34em;
      white-space: nowrap;
      @include respond(tablet-portrait) {
        font-size: 15px;
      }
      @include respond(tablet-landscape) {
        font-size: 15px;
      }
      @include respond(desktop) {
        font-size: 15px;
      }
    }
  }
}
</style>
