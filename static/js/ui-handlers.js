// UI interaction handlers and helpers

function selectVote(brideId, element) {
    document.querySelectorAll('.bribe-option').forEach(el => el.classList.remove('selected'));
    element.classList.add('selected');
    selectedVote = brideId;
    document.getElementById('submit-vote-btn').disabled = false;
}

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

function handleFileUpload(file, targetId) {
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const dropArea = document.getElementById(`drop-${targetId}`);
            dropArea.innerHTML = `<img src="${e.target.result}" class="file-preview" alt="Uploaded image">`;
            submissions[targetId] = {
                content: e.target.result,
                type: 'image'
            };
        };
        reader.readAsDataURL(file);
    }
}

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
