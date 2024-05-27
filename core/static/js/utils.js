function startCountdown(seconds, elementId, onTimeout) {
    let countdownElement = document.getElementById(elementId);
    let endTime = Date.now() + seconds * 1000;

    function updateCountdown() {
        let remainingTime = Math.max(0, endTime - Date.now());
        let minutes = Math.floor((remainingTime / 1000) / 60);
        let seconds = Math.floor((remainingTime / 1000) % 60);

        countdownElement.textContent = `Remaining: ${minutes}m ${seconds}s`;

        if (remainingTime > 0) {
            setTimeout(updateCountdown, 1000);
        } else {
            onTimeout();
        }
    }

    updateCountdown();
}