<template>
  <section class="not-found-page">
    <div class="shell">
      <img src="@/assets/images/404.png" alt="404" />
      <div class="content">
        <div class="message-card">
          <p>你访问的页面暂时不存在，或已被移除</p>
          <p>别担心，智颜AI 仍可继续为你提供专属护肤建议</p>
        </div>
        <button class="btn btn-primary" type="button" @click="goHome">返回AI问答</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function goHome() {
  router.replace('/chat')
}
</script>

<style lang="scss" scoped>
.not-found-page {
  min-height: 100dvh;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #f4fbfb;
  .shell {
    position: relative;
    width: min(100vw, 430px);
    height: 100dvh;
    max-height: 932px;
    min-height: 667px;
    overflow: hidden;
    background: #f4fbfb;
    img {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center;
    }
    .content {
      position: relative;
      z-index: 1;
      height: 90%;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 0 32px clamp(60px, 8dvh, 96px);
      gap: 32px;
      .message-card {
        text-align: center;
        p {
          color: rgba(25, 39, 42, 0.6);
          font-size: 14px;
          font-weight: 500;
          line-height: 2;
          margin: 0;
        }
      }
      button {
        width: 100%;
      }
    }
  }
}
</style>
