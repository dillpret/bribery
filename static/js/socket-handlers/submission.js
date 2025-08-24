// Submission phase event handlers
export function registerSubmissionHandlers(socket, GameState, hideAllScreens, updateStatus, startTimer, setupDragDrop, setupMobileImageUpload) {
    // Game round events
    socket.on('round_started', (data) => {
        hideAllScreens();
        document.getElementById('submission-phase').classList.remove('hidden');

        document.getElementById('round-title').textContent = `Round ${data.round} of ${data.total_rounds}`;

        if (data.custom_prompts_enabled) {
            document.getElementById('current-prompt').textContent = 'Custom prompts enabled - each player has their own prompt';
        } else {
            document.getElementById('current-prompt').textContent = data.prompt;
        }

        updateStatus('Submit your bribes!');
        startTimer(data.time_limit);

        // Clear previous submissions
        window.submissions = {};

        // Re-enable all form elements for new round
        document.querySelectorAll('textarea[id^="submission-"]').forEach(textarea => {
            textarea.disabled = false;
            textarea.style.backgroundColor = '';
            textarea.style.cursor = '';
            textarea.value = '';
        });

        document.querySelectorAll('div[id^="drop-"]').forEach(dropArea => {
            dropArea.style.pointerEvents = '';
            dropArea.style.opacity = '';
        });

        document.querySelectorAll('input[id^="file-input-"]').forEach(fileInput => {
            fileInput.disabled = false;
        });

        document.querySelectorAll('button[id^="upload-btn-"]').forEach(uploadBtn => {
            uploadBtn.disabled = false;
            uploadBtn.style.backgroundColor = '';
            uploadBtn.style.cursor = '';
        });

        document.querySelectorAll('button[onclick^="submitTargetBribe"]').forEach(button => {
            button.disabled = false;
            button.textContent = 'Submit Bribe';
            button.style.background = '';
        });
    });

    socket.on('your_targets', (data) => {
        const container = document.getElementById('targets-container');
        container.innerHTML = '<h3>Create bribes for these players:</h3>';

        data.targets.forEach((target) => {
            const targetEl = document.createElement('div');
            targetEl.className = 'target-item';
            targetEl.innerHTML = `
                <h4>Bribe for: ${target.name}</h4>
                <p class="target-prompt"><strong>Their prompt:</strong> "${target.prompt}"</p>
                <div class="submission-area">
                    <textarea class="submission-input" id="submission-${target.id}" 
                            placeholder="Enter your bribe for this prompt (text, link, or paste an image)..."></textarea>
                    <div class="image-upload-container">
                        <div class="drag-drop-area" id="drop-${target.id}">
                            <span class="drag-drop-text">Or drag and drop an image here</span>
                            <span class="mobile-upload-text">Or tap to add an image</span>
                        </div>
                        <input type="file" 
                               id="file-input-${target.id}" 
                               accept="image/*,image/gif" 
                               capture="environment"
                               style="display: none;">
                        <button type="button" class="image-upload-btn" id="upload-btn-${target.id}">
                            📷 Add Image
                        </button>
                    </div>
                    <button class="submit-btn" onclick="submitTargetBribe('${target.id}')">
                        Submit Bribe
                    </button>
                </div>
            `;
            container.appendChild(targetEl);

            setupDragDrop(target.id);
            setupMobileImageUpload(target.id);
        });
    });

    socket.on('bribe_submitted', (data) => {
        const button = document.querySelector(`button[onclick="submitTargetBribe('${data.target_id}')"]`);
        if (button) {
            button.textContent = 'Submitted ✓';
            button.disabled = true;
            button.style.background = '#28a745';
        }

        // Disable the text input field for this target
        const textarea = document.getElementById(`submission-${data.target_id}`);
        if (textarea) {
            textarea.disabled = true;
            textarea.style.backgroundColor = '#f8f9fa';
            textarea.style.cursor = 'not-allowed';
        }

        // Also disable the image upload components for this target
        const fileInput = document.getElementById(`file-input-${data.target_id}`);
        const uploadBtn = document.getElementById(`upload-btn-${data.target_id}`);
        const dropArea = document.getElementById(`drop-${data.target_id}`);

        if (fileInput) fileInput.disabled = true;
        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.style.backgroundColor = '#6c757d';
            uploadBtn.style.cursor = 'not-allowed';
        }
        if (dropArea) {
            dropArea.style.pointerEvents = 'none';
            dropArea.style.opacity = '0.6';
        }
    });
}
