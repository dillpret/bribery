export default {
  MAX_WIDTH: 1200,
  MAX_HEIGHT: 800,
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  
  async validateFile(file) {
    // Check file size
    if (file.size > this.MAX_FILE_SIZE) {
      return {
        valid: false,
        message: `File size exceeds 5MB limit (${Math.round(file.size/1024/1024)}MB)`
      }
    }
    
    // Check file type
    if (!file.type.startsWith('image/')) {
      return {
        valid: false,
        message: 'Only image files are supported'
      }
    }
    
    // Further validation
    return new Promise((resolve) => {
      const img = new Image()
      const objectUrl = URL.createObjectURL(file)
      
      img.onload = () => {
        URL.revokeObjectURL(objectUrl)
        resolve({ valid: true, message: 'Valid image' })
      }
      
      img.onerror = () => {
        URL.revokeObjectURL(objectUrl)
        resolve({ 
          valid: false, 
          message: 'Invalid or corrupted image file'
        })
      }
      
      img.src = objectUrl
    })
  },
  
  async processImage(file) {
    // Check if the file is valid
    const validation = await this.validateFile(file)
    if (!validation.valid) {
      throw new Error(validation.message)
    }
    
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (event) => {
        const img = new Image()
        img.onload = () => {
          // Determine if we need to resize
          let width = img.width
          let height = img.height
          
          // Resize if needed while maintaining aspect ratio
          if (width > this.MAX_WIDTH || height > this.MAX_HEIGHT) {
            const aspectRatio = width / height
            
            if (width > this.MAX_WIDTH) {
              width = this.MAX_WIDTH
              height = width / aspectRatio
            }
            
            if (height > this.MAX_HEIGHT) {
              height = this.MAX_HEIGHT
              width = height * aspectRatio
            }
          }
          
          // Create canvas for image processing
          const canvas = document.createElement('canvas')
          canvas.width = width
          canvas.height = height
          
          const ctx = canvas.getContext('2d')
          ctx.drawImage(img, 0, 0, width, height)
          
          // Convert to base64
          const dataUrl = canvas.toDataURL('image/jpeg', 0.85)
          
          resolve({
            dataUrl,
            width,
            height,
            originalSize: file.size,
            processedSize: Math.round(dataUrl.length * 0.75) // Approximate size calculation
          })
        }
        
        img.onerror = () => {
          reject(new Error('Failed to process image'))
        }
        
        img.src = event.target.result
      }
      
      reader.onerror = () => {
        reject(new Error('Failed to read file'))
      }
      
      reader.readAsDataURL(file)
    })
  }
}
