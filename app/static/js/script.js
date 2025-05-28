// Copy password to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Password copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

// Password strength meter
function checkPasswordStrength(password) {
    const strengthMeter = document.getElementById('strength-meter');
    const feedback = document.getElementById('strength-feedback');
    
    if (!strengthMeter || !feedback) return;

    const result = zxcvbn(password);
    const score = result.score;

    const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
    const strengthColors = ['#dc3545', '#ffc107', '#fd7e14', '#20c997', '#198754'];

    strengthMeter.style.width = `${(score + 1) * 20}%`;
    strengthMeter.style.backgroundColor = strengthColors[score];
    feedback.textContent = `Strength: ${strengthLabels[score]}`;

    if (result.feedback.warning) {
        feedback.textContent += ` - ${result.feedback.warning}`;
    }
}

// Initialize password strength meter for password fields
document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.querySelector('input[type="password"]');
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }
}); 