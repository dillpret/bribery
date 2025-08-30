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
  publicPath: process.env.NODE_ENV === 'production' ? '/static/vue/' : '/',
  
  // Production optimizations
  productionSourceMap: false,
  
  // Configure webpack
  chainWebpack: config => {
    // Split vendor chunks
    config.optimization.splitChunks({
      cacheGroups: {
        vendors: {
          name: 'chunk-vendors',
          test: /[\\/]node_modules[\\/]/,
          priority: -10,
          chunks: 'initial'
        },
        common: {
          name: 'chunk-common',
          minChunks: 2,
          priority: -20,
          chunks: 'initial',
          reuseExistingChunk: true
        }
      }
    })
  }
})
