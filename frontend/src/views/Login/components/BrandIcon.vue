<!-- 登录品牌标识：集中管理登录页 Logo 与品牌文字。 -->
<template>
  <header class="brand-area">
    <img class="brand-logo" src="@/assets/images/logo2.png" alt="智颜 AI" />
    <div class="brand-text">
      <h1>智颜 AI</h1>
      <p>精准护肤，定制专属美妆</p>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.brand-area {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  width: min(100%, 330px);
  margin: 0 auto;
}
.brand-logo {
  width: clamp(82px, 24vw, 98px);
  height: auto;
  filter: drop-shadow(0 16px 24px rgba(10, 166, 194, 0.18));
}
.brand-text {
  padding-bottom: 10px;
}
.brand-text h1 {
  color: rgba(31, 41, 43, 0.88);
  font-size: clamp(28px, 8vw, 36px);
  font-weight: 500;
  letter-spacing: 0.14em;
  line-height: 1.1;
}
.brand-text p {
  margin-top: 8px;
  color: rgba(77, 85, 88, 0.74);
  font-size: clamp(12px, 3.2vw, 14px);
  letter-spacing: 0.28em;
  white-space: nowrap;
}
@include respond(tablet-portrait) {
  .brand-area {
    width: 360px;
  }
}
@include respond(tablet-landscape) {
  .brand-area {
    width: 360px;
  }
}
@include respond(desktop) {
  .brand-area {
    width: 360px;
  }
}
</style>
