/* ======================================
   YourTable - Global JavaScript
   ====================================== */

/**
 * Helper function to show toast-like notifications.
 * It will dynamically create a small message box on the screen.
 */

function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.classList.add("toast-message", type);
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("show");
    }, 100);

    // Automatically remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

/**
 * Navbar background change on scroll (adds subtle depth)
 */
window.addEventListener("scroll", () => {
    const navbar = document.querySelector(".navbar");
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    }
});

/**
 * Confirmation dialog for actions like deleting or cancelling reservations
 */

document.addEventListener("click", (event) => {
    if (event.target.matches(".confirm-action")) {
        const message = event.target.dataset.message || "Are you sure?";
        if (!confirm(message)) {
            event.preventDefault();
        }
    }
});

/**
 * Success and error flash messages auto-dismiss
 */
window.addEventListener("DOMContentLoaded", () => {
    const flashMessages = document.querySelectorAll(".alert");
    flashMessages.forEach((msg) => {
        setTimeout(() => {
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 400);
        }, 4000);
    });
});

/**
 * Toast styles (injected for convenience)
 */

const style = document.createElement("style");
style.textContent = `
.toast-message {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: var(--accent-color, #E27D60);
  color: white;
  padding: 0.8rem 1.2rem;
  border-radius: 8px;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.4s ease;
  font-weight: 500;
  z-index: 9999;
}
.toast-message.show {
  opacity: 1;
  transform: translateY(0);
}
.toast-message.success {
  background: var(--secondary-color, #85A392);
}
.toast-message.error {
  background: #e74c3c;
}
`;
document.head.appendChild(style);
