const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/socket.io': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  // Output to the main Flask static directory
  outputDir: '../static/vue',
  // Adjust public path for Flask integration
  publicPath: process.env.NODE_ENV === 'production' ? '/static/vue/' : '/'
})
