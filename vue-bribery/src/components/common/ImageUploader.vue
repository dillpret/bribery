<template>
  <div class="image-uploader">
    <div 
      ref="uploadArea"
      class="upload-area" 
      :class="{ 'has-image': hasImage, 'drag-over': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <div v-if="!hasImage" class="upload-instructions">
        <div class="icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
          </svg>
        </div>
        <p>Click or drag image here</p>
        <small>PNG, JPG or GIF (max {{ maxSizeMB }}MB)</small>
      </div>
      <div v-else class="image-preview">
        <img :src="previewUrl" alt="Preview" />
        <button class="remove-btn" @click.stop="removeImage">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
      <input 
        ref="fileInput"
        type="file"
        accept="image/*"
        class="file-input"
        @change="handleFileSelect"
      />
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import imageProcessingUtil from '@/utils/image-processing';

export default {
  name: 'ImageUploader',
  
  props: {
    maxSize: {
      type: Number,
      default: 2 * 1024 * 1024 // 2MB
    },
    initialImage: {
      type: String,
      default: ''
    }
  },
  
  emits: ['update:image', 'upload-error'],
  
  setup(props, { emit }) {
    const fileInput = ref(null);
    const previewUrl = ref('');
    const isDragging = ref(false);
    const error = ref('');
    const uploadArea = ref(null);
    
    const maxSizeMB = computed(() => props.maxSize / (1024 * 1024));
    const hasImage = computed(() => !!previewUrl.value);
    
    onMounted(() => {
      if (props.initialImage) {
        previewUrl.value = props.initialImage;
      }
      
      // Add touch events for mobile devices
      if ('ontouchstart' in window) {
        const element = uploadArea.value || document.querySelector('.upload-area');
        if (element) {
          element.addEventListener('touchstart', handleTouchStart);
          element.addEventListener('touchend', handleTouchEnd);
        }
      }
    });
    
    const handleTouchStart = (event) => {
      // Prevent default only if we're already showing an image
      // to enable remove button clicks
      if (hasImage.value) {
        const touch = event.touches[0];
        const removeBtn = document.querySelector('.remove-btn');
        
        if (removeBtn) {
          const rect = removeBtn.getBoundingClientRect();
          const isRemoveButtonTouch = (
            touch.clientX >= rect.left && 
            touch.clientX <= rect.right && 
            touch.clientY >= rect.top && 
            touch.clientY <= rect.bottom
          );
          
          if (!isRemoveButtonTouch) {
            event.preventDefault();
          }
        }
      }
    };
    
    const handleTouchEnd = (event) => {
      // Only trigger the file input if we're not on the remove button
      const touch = event.changedTouches[0];
      const removeBtn = document.querySelector('.remove-btn');
      
      if (removeBtn) {
        const rect = removeBtn.getBoundingClientRect();
        const isRemoveButtonTouch = (
          touch.clientX >= rect.left && 
          touch.clientX <= rect.right && 
          touch.clientY >= rect.top && 
          touch.clientY <= rect.bottom
        );
        
        if (isRemoveButtonTouch) {
          removeImage();
          event.preventDefault();
          return;
        }
      }
      
      if (!hasImage.value) {
        triggerFileInput();
      }
    };
    
    const triggerFileInput = () => {
      fileInput.value.click();
    };
    
    const validateAndProcessImage = async (file) => {
      // Clear previous errors
      error.value = '';
      
      // Validate file size
      if (file.size > props.maxSize) {
        error.value = `Image too large. Maximum size is ${maxSizeMB.value}MB.`;
        emit('upload-error', error.value);
        return null;
      }
      
      try {
        // Process image using utility function
        const processedImage = await imageProcessingUtil.optimizeImage(file);
        return processedImage;
      } catch (err) {
        error.value = 'Error processing image. Please try another.';
        emit('upload-error', error.value);
        return null;
      }
    };
    
    const handleFileSelect = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      
      const processedImage = await validateAndProcessImage(file);
      if (processedImage) {
        previewUrl.value = processedImage.dataUrl;
        emit('update:image', processedImage.dataUrl);
      }
      
      // Reset file input to allow selecting the same file again
      fileInput.value.value = '';
    };
    
    const handleDrop = async (event) => {
      isDragging.value = false;
      
      const file = event.dataTransfer.files[0];
      if (!file || !file.type.startsWith('image/')) {
        error.value = 'Please drop an image file.';
        emit('upload-error', error.value);
        return;
      }
      
      const processedImage = await validateAndProcessImage(file);
      if (processedImage) {
        previewUrl.value = processedImage.dataUrl;
        emit('update:image', processedImage.dataUrl);
      }
    };
    
    const removeImage = () => {
      previewUrl.value = '';
      emit('update:image', '');
    };
    
    return {
      fileInput,
      uploadArea,
      previewUrl,
      isDragging,
      error,
      maxSizeMB,
      hasImage,
      triggerFileInput,
      handleFileSelect,
      handleDrop,
      removeImage,
      handleTouchStart,
      handleTouchEnd
    };
  }
}
</script>

<style scoped>
.image-uploader {
  width: 100%;
  margin-bottom: 1rem;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #0080ff;
  background-color: rgba(0, 128, 255, 0.05);
}

.upload-area.drag-over {
  border-color: #0080ff;
  background-color: rgba(0, 128, 255, 0.1);
}

.upload-instructions {
  color: #666;
}

.upload-instructions .icon {
  margin-bottom: 0.5rem;
}

.upload-instructions .icon svg {
  width: 48px;
  height: 48px;
  fill: #999;
}

.upload-instructions p {
  margin: 0.5rem 0;
  font-size: 1rem;
}

.upload-instructions small {
  font-size: 0.8rem;
  opacity: 0.7;
}

.file-input {
  display: none;
}

.image-preview {
  width: 100%;
  position: relative;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 4px;
}

.remove-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #ff4081;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: #f50057;
  transform: scale(1.1);
}

.remove-btn svg {
  width: 18px;
  height: 18px;
  fill: white;
}

.error-message {
  color: #f44336;
  font-size: 0.85rem;
  margin-top: 0.5rem;
  text-align: left;
}

.has-image {
  border-style: solid;
  padding: 0.5rem;
}
</style>
