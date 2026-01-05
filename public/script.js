// Guardian Alert - Interactive Dashboard
const API_BASE = 'http://localhost:3000';

// Animate numbers on page load
function animateNumbers() {
    const alertsToday = document.getElementById('alertsToday');
    const activeLocations = document.getElementById('activeLocations');
    
    animateValue(alertsToday, 0, 127, 2000);
    animateValue(activeLocations, 0, 1247, 2500);
}

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString();
    }, 16);
}

// Smooth scroll
function scrollToStats() {
    document.getElementById('stats').scrollIntoView({ behavior: 'smooth' });
}

// Test Emergency Alert
async function triggerTestAlert() {
    const button = event.target;
    const originalText = button.textContent;
    
    button.textContent = '🚨 Sending Test Alert...';
    button.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            button.textContent = '✅ Test Alert Sent!';
            button.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            
            // Show success notification
            showNotification('Test alert sent successfully to all emergency contacts!', 'success');
            
            // Update live stats
            const alertsToday = document.getElementById('alertsToday');
            const current = parseInt(alertsToday.textContent.replace(',', ''));
            alertsToday.textContent = (current + 1).toLocaleString();
        } else {
            throw new Error(data.error || 'Failed to send alert');
        }
    } catch (error) {
        console.error('Error sending test alert:', error);
        button.textContent = '❌ Error - Try Again';
        button.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
        showNotification('Failed to send alert. Make sure WhatsApp service is running.', 'error');
    }
    
    // Reset button after 3 seconds
    setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
        button.style.background = '';
    }, 3000);
}

// Form submission
function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);
    
    // In production, this would send to a backend API
    console.log('Form submitted:', data);
    
    showNotification('Thank you! Your installation request has been submitted. Our team will contact you within 24 hours.', 'success');
    
    event.target.reset();
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'notification ' + type;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#6366f1'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Update stats periodically
function updateLiveStats() {
    fetch(`${API_BASE}/health`)
        .then(res => res.json())
        .then(data => {
            if (data.whatsappConnected) {
                // Update UI to show connected status
                console.log('WhatsApp service: Connected');
            }
        })
        .catch(err => {
            console.log('WhatsApp service: Not connected');
        });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    animateNumbers();
    updateLiveStats();
    
    // Update stats every 30 seconds
    setInterval(updateLiveStats, 30000);
    
    // Animate elements on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
            }
        });
    });
    
    document.querySelectorAll('.stat-card, .feature-card, .region-card').forEach(el => {
        observer.observe(el);
    });
});

// Add fade in animation
const fadeStyle = document.createElement('style');
fadeStyle.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .stat-card, .feature-card, .region-card {
        opacity: 0;
    }
`;
document.head.appendChild(fadeStyle);

// Simulate real-time updates for demo
setInterval(() => {
    const alertsToday = document.getElementById('alertsToday');
    const current = parseInt(alertsToday.textContent.replace(',', ''));
    
    // Randomly increment (10% chance per interval)
    if (Math.random() < 0.1) {
        alertsToday.textContent = (current + 1).toLocaleString();
        
        // Pulse animation
        alertsToday.style.animation = 'pulse 0.5s ease';
        setTimeout(() => alertsToday.style.animation = '', 500);
    }
}, 10000); // Check every 10 seconds

// Add pulse animation
const pulseStyle = document.createElement('style');
pulseStyle.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); color: #fbbf24; }
    }
`;
document.head.appendChild(pulseStyle);
