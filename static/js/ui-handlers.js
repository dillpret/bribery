/**
 * @fileoverview UI Handlers - User interface interaction handlers
 * @module ui-handlers
 * 
 * This module provides functions for handling UI interactions in the game:
 * - Vote selection and submission
 * - Bribe submission handling
 * - Image upload and processing
 * - Drag and drop functionality
 * - Scoreboard display
 */
import { ImageUtils } from './image-utils.js';

// Keep track of image submissions
let submissions = {};
let selectedVote = null;

/**
 * Select a vote in the voting phase
 * @param {string} brideId - ID of the selected bribe
 * @param {HTMLElement} element - DOM element that was clicked
 */
function selectVote(brideId, element) {
    document.querySelectorAll('.bribe-option').forEach(el => el.classList.remove('selected'));
    element.classList.add('selected');
    selectedVote = brideId;
    document.getElementById('submit-vote-btn').disabled = false;
}

/**
 * Submit a bribe for a specific target
 * @param {string} targetId - ID of the target
 */
function submitTargetBribe(targetId) {
    let content, type = 'text';

    if (submissions[targetId]) {
        content = submissions[targetId].content;
        type = submissions[targetId].type;
    } else {
        content = document.getElementById(`submission-${targetId}`).value.trim();
    }

    if (!content) {
        alert('Please enter a bribe before submitting!');
        return;
    }

    submitBribe(targetId, content, type);
}

/**
 * Auto-submits any non-empty bribes when the timer expires
 */
function autoSubmitPendingBribes() {
    // Get all target areas that haven't been submitted yet
    const allTargetButtons = document.querySelectorAll('button[onclick^="submitTargetBribe"]');
    
    allTargetButtons.forEach(button => {
        // Skip already submitted bribes (button will be disabled)
        if (button.disabled) {
            return;
        }
        
        // Extract target ID from the onclick attribute
        const targetIdMatch = button.getAttribute('onclick').match(/submitTargetBribe\('([^']+)'\)/);
        if (!targetIdMatch) {
            return;
        }
        
        const targetId = targetIdMatch[1];
        
        // Check if there's content to submit
        let content = '';
        
        // Check if there's already a submission object (e.g., from image upload)
        if (submissions[targetId]) {
            content = submissions[targetId].content;
            const type = submissions[targetId].type;
            submitBribe(targetId, content, type);
        } else {
            // Otherwise check if there's text in the textarea
            const textarea = document.getElementById(`submission-${targetId}`);
            if (textarea && textarea.value.trim()) {
                content = textarea.value.trim();
                submitBribe(targetId, content, 'text');
            }
        }
        
        // If content was found and submitted, update the UI
        if (content) {
            button.textContent = 'Auto-Submitted';
            button.disabled = true;
            button.style.background = '#ff9800'; // Different color to show auto-submission
            
            // Also disable the textarea
            const textarea = document.getElementById(`submission-${targetId}`);
            if (textarea) {
                textarea.disabled = true;
                textarea.style.backgroundColor = '#f0f0f0';
                textarea.style.cursor = 'not-allowed';
            }
        }
    });
}

/**
 * Set up drag and drop functionality for image uploads
 * @param {string} targetId - ID of the target
 */
function setupDragDrop(targetId) {
    const dropArea = document.getElementById(`drop-${targetId}`);
    const textarea = document.getElementById(`submission-${targetId}`);

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
    });

    dropArea.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0], targetId);
        }
    });

    // Handle paste events in textarea
    textarea.addEventListener('paste', (e) => {
        const items = e.clipboardData.items;
        for (let item of items) {
            if (item.type.indexOf('image') !== -1) {
                const file = item.getAsFile();
                handleFileUpload(file, targetId);
                e.preventDefault();
            }
        }
    });
}

/**
 * Set up mobile-friendly image upload
 * @param {string} targetId - ID of the target
 */
function setupMobileImageUpload(targetId) {
    const fileInput = document.getElementById(`file-input-${targetId}`);
    const uploadBtn = document.getElementById(`upload-btn-${targetId}`);
    const dropArea = document.getElementById(`drop-${targetId}`);

    // Handle upload button click
    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle drop area click on mobile
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0], targetId);
        }
    });
}

/**
 * Handle file upload and processing
 * @param {File} file - The file to upload
 * @param {string} targetId - ID of the target
 */
function handleFileUpload(file, targetId) {
    if (!file) {
        return;
    }
    
    // Show loading state
    const dropArea = document.getElementById(`drop-${targetId}`);
    const submitBtn = document.getElementById(`submit-btn-${targetId}`);
    
    // Disable submit button during processing
    if (submitBtn) submitBtn.disabled = true;
    
    dropArea.innerHTML = `<div class="upload-loading">Processing image...</div>`;
    
    // Process the image using our utility
    ImageUtils.processImage(file).then(result => {
        if (result.error) {
            // Show error message
            dropArea.innerHTML = `<div class="upload-error">${result.error}</div>`;
            // Re-enable submit button on error
            if (submitBtn) submitBtn.disabled = false;
            return;
        }
        
        // Display image preview with appropriate handling for GIFs
        const isGif = result.type === 'gif';
        
        // Create an image element to verify it loads correctly
        const img = new Image();
        img.onload = function() {
            // Image loaded successfully
            dropArea.innerHTML = `<img src="${result.content}" class="file-preview${isGif ? ' gif-preview' : ''}" alt="Uploaded ${isGif ? 'GIF' : 'image'}">`;
            
            // Store submission data
            submissions[targetId] = {
                content: result.content,
                type: result.type
            };
            
            // Re-enable submit button
            if (submitBtn) submitBtn.disabled = false;
        };
        
        img.onerror = function() {
            // Image failed to load
            dropArea.innerHTML = `<div class="upload-error">Failed to load image. Please try another.</div>`;
            if (submitBtn) submitBtn.disabled = false;
        };
        
        // Set source to trigger load/error events
        img.src = result.content;
    }).catch(error => {
        // Handle any unexpected errors in the promise chain
        console.error('Image processing error:', error);
        dropArea.innerHTML = `<div class="upload-error">Failed to process image. Please try another.</div>`;
        if (submitBtn) submitBtn.disabled = false;
    });
}

/**
 * Prevent default browser behavior for drag and drop
 * @param {Event} e - The event object
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Display scoreboard with player scores
 * @param {Array<Object>} scores - Array of player score objects
 * @param {string} containerId - ID of the container element
 * @param {boolean} isFinal - Whether this is the final scoreboard
 */
function displayScoreboard(scores, containerId, isFinal = false) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    scores.forEach((player, index) => {
        const scoreItem = document.createElement('div');
        let className = 'score-item';

        if (isFinal && player.podium_position) {
            className += ` podium-${player.podium_position}`;
        }

        scoreItem.className = className;

        let scoreDisplay = `<div class="total-score">${player.total_score} pts</div>`;
        if (!isFinal && player.round_score !== undefined) {
            scoreDisplay = `
                <div class="scores">
                    <div class="round-score">+${player.round_score}</div>
                    <div class="total-score">${player.total_score} pts</div>
                </div>
            `;
        }

        let position = '';
        if (isFinal) {
            position = `<span class="position-indicator">${index + 1}.</span>`;
            if (player.podium_position === 1) position = '🥇 ';
            else if (player.podium_position === 2) position = '🥈 ';
            else if (player.podium_position === 3) position = '🥉 ';
        }

        scoreItem.innerHTML = `
            <div class="player-name">${position}${player.username}</div>
            <div class="player-score">${scoreDisplay}</div>
        `;

        container.appendChild(scoreItem);
    });
}

// Create the UIHandlers object
const UIHandlers = {
    selectVote,
    submitTargetBribe,
    autoSubmitPendingBribes,
    setupDragDrop,
    setupMobileImageUpload,
    handleFileUpload,
    displayScoreboard,
    getSelectedVote: () => selectedVote,
    resetSubmissions: () => { submissions = {}; },
    resetSelectedVote: () => { selectedVote = null; }
};

// Export as ES6 module
export default UIHandlers;

// Also add to window for backwards compatibility
window.UIHandlers = UIHandlers;

// Legacy function exports for inline event handlers
window.selectVote = selectVote;
window.submitTargetBribe = submitTargetBribe;
window.setupDragDrop = setupDragDrop;
window.setupMobileImageUpload = setupMobileImageUpload;
