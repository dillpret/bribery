// Progress tracking event handlers
export function registerProgressHandlers(socket) {
    // Progress tracking events
    socket.on('submission_progress', (data) => {
        const progressText = document.getElementById('submission-progress-text');
        const progressContainer = document.getElementById('submission-progress');

        if (progressText) {
            progressText.textContent = data.message;

            // Style the progress indicator based on completion
            if (data.completed === data.total) {
                progressContainer.classList.add('waiting');
            } else {
                progressContainer.classList.remove('waiting');
            }
        }
    });

    socket.on('voting_progress', (data) => {
        const progressText = document.getElementById('voting-progress-text');
        const progressContainer = document.getElementById('voting-progress');

        if (progressText) {
            progressText.textContent = data.message;

            // Style the progress indicator based on completion
            if (data.completed === data.total) {
                progressContainer.classList.add('waiting');
            } else {
                progressContainer.classList.remove('waiting');
            }
        }
    });
}
