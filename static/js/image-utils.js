/**
 * @fileoverview Image Utilities - Image processing and validation
 * @module image-utils
 * 
 * This module provides utilities for:
 * - Image validation
 * - Optimization and resizing
 * - GIF handling
 * - Error handling for media content
 */

/**
 * Image validation and processing utility
 * Handles validation, optimization and error handling for media content
 */
const ImageUtilsObj = {
    /**
     * Maximum image dimensions
     * Images larger than this will be resized
     */
    MAX_WIDTH: 1200,
    MAX_HEIGHT: 800,
    
    /**
     * Maximum file size in bytes (5MB)
     * Images larger than this will be rejected
     */
    MAX_FILE_SIZE: 5 * 1024 * 1024,
    
    /**
     * Validates that the file is an acceptable image or gif
     * @param {File} file The file to validate
     * @returns {Promise<{valid: boolean, message: string}>} Validation result
     */
    validateFile: async function(file) {
        // Check file size
        if (file.size > this.MAX_FILE_SIZE) {
            return {
                valid: false,
                message: `File size exceeds 5MB limit (${Math.round(file.size/1024/1024)}MB)`
            };
        }
        
        // Check file type
        if (!file.type.startsWith('image/')) {
            return {
                valid: false,
                message: 'Only image files are supported'
            };
        }
        
        // Further validation - ensure it's a valid image that can be loaded
        try {
            return new Promise((resolve) => {
                const img = new Image();
                const objectUrl = URL.createObjectURL(file);
                
                img.onload = () => {
                    URL.revokeObjectURL(objectUrl);
                    resolve({ valid: true, message: 'Valid image' });
                };
                
                img.onerror = () => {
                    URL.revokeObjectURL(objectUrl);
                    resolve({ 
                        valid: false, 
                        message: 'Invalid or corrupted image file'
                    });
                };
                
                img.src = objectUrl;
            });
        } catch (err) {
            return {
                valid: false,
                message: 'Error validating image: ' + err.message
            };
        }
    },
    
    /**
     * Process and optimize the image/gif before submission
     * - Detects if it's a GIF and preserves animation
     * - Resizes large images
     * - Returns appropriate type and data
     * 
     * @param {File} file The image file to process
     * @returns {Promise<{content: string, type: string, error: string|null}>} Processed image data
     */
    processImage: async function(file) {
        try {
            // Check for null or undefined file
            if (!file) {
                return { content: null, type: null, error: "No file provided" };
            }
            
            // Basic file type check
            const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
            if (!allowedTypes.includes(file.type)) {
                return { 
                    content: null, 
                    type: null, 
                    error: `Unsupported file type: ${file.type || 'unknown'}. Please use JPG, PNG, GIF, WebP or BMP.`
                };
            }
            
            // Validate file thoroughly
            const validation = await this.validateFile(file);
            if (!validation.valid) {
                return { content: null, type: null, error: validation.message };
            }
            
            // Special handling for GIFs to preserve animation
            if (file.type === 'image/gif') {
                return this.handleGif(file);
            }
            
            // For static images, resize if needed
            return this.handleStaticImage(file);
        } catch (err) {
            console.error('Image processing error:', err);
            return { 
                content: null, 
                type: null, 
                error: 'Error processing image: ' + (err.message || 'Unknown error')
            };
        }
    },
    
    /**
     * Handle GIF files specifically
     * @param {File} file The GIF file
     * @returns {Promise<{content: string, type: string, error: null}>} Processed GIF data
     */
    handleGif: async function(file) {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                resolve({
                    content: e.target.result,
                    type: 'gif',
                    error: null
                });
            };
            reader.onerror = () => {
                resolve({
                    content: null,
                    type: null,
                    error: 'Failed to read GIF file'
                });
            };
            reader.readAsDataURL(file);
        });
    },
    
    /**
     * Handle static image files with resizing if needed
     * @param {File} file The image file
     * @returns {Promise<{content: string, type: string, error: null}>} Processed image data
     */
    handleStaticImage: async function(file) {
        return new Promise((resolve) => {
            const img = new Image();
            const reader = new FileReader();
            
            reader.onload = (e) => {
                img.onload = () => {
                    // Check if resizing is needed
                    let width = img.width;
                    let height = img.height;
                    
                    if (width > this.MAX_WIDTH || height > this.MAX_HEIGHT) {
                        // Calculate new dimensions while maintaining aspect ratio
                        if (width > this.MAX_WIDTH) {
                            height = Math.round(height * (this.MAX_WIDTH / width));
                            width = this.MAX_WIDTH;
                        }
                        
                        if (height > this.MAX_HEIGHT) {
                            width = Math.round(width * (this.MAX_HEIGHT / height));
                            height = this.MAX_HEIGHT;
                        }
                        
                        // Resize the image
                        const canvas = document.createElement('canvas');
                        canvas.width = width;
                        canvas.height = height;
                        
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0, width, height);
                        
                        // Get resized image data with quality adjustment to reduce size
                        const quality = 0.85; // 85% quality - good balance between size and quality
                        const resizedData = canvas.toDataURL(file.type, quality);
                        
                        resolve({
                            content: resizedData,
                            type: 'image',
                            error: null
                        });
                    } else {
                        // No resizing needed but compress if file size is large
                        try {
                            // Check if we should compress the image
                            if (e.target.result.length > 500000) { // If over ~500KB
                                const canvas = document.createElement('canvas');
                                canvas.width = img.width;
                                canvas.height = img.height;
                                
                                const ctx = canvas.getContext('2d');
                                ctx.drawImage(img, 0, 0, img.width, img.height);
                                
                                // Use quality adjustment to reduce size
                                const quality = 0.75; // 75% quality for large images
                                const compressedData = canvas.toDataURL(file.type, quality);
                                
                                resolve({
                                    content: compressedData,
                                    type: 'image',
                                    error: null
                                });
                            } else {
                                // Use original if not too large
                                resolve({
                                    content: e.target.result,
                                    type: 'image',
                                    error: null
                                });
                            }
                        } catch (err) {
                            // Fallback to original if compression fails
                            resolve({
                                content: e.target.result,
                                type: 'image',
                                error: null
                            });
                        }
                    }
                };
                
                img.onerror = () => {
                    resolve({
                        content: null,
                        type: null,
                        error: 'Failed to load image for processing'
                    });
                };
                
                img.src = e.target.result;
            };
            
            reader.onerror = () => {
                resolve({
                    content: null,
                    type: null,
                    error: 'Failed to read image file'
                });
            };
            
            reader.readAsDataURL(file);
        });
    }
};

// ES6 module export
export const ImageUtils = ImageUtilsObj;

// Add to window for backwards compatibility
window.ImageUtils = ImageUtilsObj;
