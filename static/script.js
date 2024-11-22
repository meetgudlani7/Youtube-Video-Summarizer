document.addEventListener('DOMContentLoaded', () => {
    const videoUrlInput = document.getElementById('video-url');
    const summarizeBtn = document.getElementById('summarize-btn');
    const summaryContent = document.getElementById('summary-content');

    summarizeBtn.addEventListener('click', async () => {
        const videoUrl = videoUrlInput.value.trim();
        
        if (videoUrl === '') {
            alert('Please enter a valid YouTube video URL');
            return;
        }

        // Show loading state with steps
        summarizeBtn.disabled = true;
        summaryContent.innerHTML = `
            <div class="loading-steps">
                <p>⏳ Processing your video...</p>
                <ul>
                    <li>Checking for available captions...</li>
                    <li>If no captions found, downloading audio...</li>
                    <li>Converting speech to text...</li>
                    <li>Generating summary...</li>
                </ul>
                <p>This may take a few minutes for longer videos.</p>
            </div>
        `;

        try {
            const response = await fetch('/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: videoUrl })
            });

            const data = await response.json();

            if (response.ok) {
                summaryContent.innerHTML = data.summary.replace(/\n/g, '<br>');
            } else {
                summaryContent.innerHTML = `
                    <div class="error-message">
                        <p>❌ Error: ${data.error}</p>
                        <p>Please try another video or check the URL.</p>
                    </div>
                `;
            }
        } catch (error) {
            summaryContent.innerHTML = `
                <div class="error-message">
                    <p>❌ Error: ${error.message}</p>
                    <p>Please try again later.</p>
                </div>
            `;
        } finally {
            summarizeBtn.disabled = false;
        }
    });
});