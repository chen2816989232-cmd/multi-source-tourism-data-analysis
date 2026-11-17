<script setup></script>
<template>
  <el-button class="login-btn" native-type="submit" type="primary">登录</el-button>
</template>
<style>
.login-btn {
  border: 0px solid transparent;
  border-radius: 45px;
  padding: 4px 15px;
  margin-bottom: 20px;
  width: 100%;
  font-size: 24px;
  height: 45px;

  background: var(--btn-bg-color-);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgb(from var(--btn-bg-color-) r g b / 0.3);

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
      45deg,
      transparent 30%,
      rgba(255, 255, 255, 0.3) 50%,
      transparent 70%
    );
    transform: rotate(45deg);
    transition: all 0.6s;
    animation: liquid-flow 3s infinite;
  }

  &:hover {
    background: var(--btn-bg-hover-color-);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgb(from var(--btn-bg-color-) r g b / 0.5);

    &::before {
      animation-duration: 1s;
    }
  }
}
@keyframes liquid-flow {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
  100% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
  }
}
</style>

