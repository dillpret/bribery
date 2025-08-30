<template>
  <div class="footer">
    <div class="copyright">© {{ currentYear }} Bribery Game</div>
    <div class="version">v{{ version }}</div>
  </div>
</template>

<script>
export default {
  name: 'FooterComponent',
  
  data() {
    return {
      version: process.env.VUE_APP_VERSION || '1.0.0'
    }
  },
  
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.footer {
  height: var(--footer-height);
  background-color: #333;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  font-size: 0.8rem;
}
</style>
