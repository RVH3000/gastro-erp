/** Non-blocking Toast-Benachrichtigungen statt alert() */

export function toast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.setAttribute('role', 'status');
  el.setAttribute('aria-live', 'polite');
  el.textContent = message;
  container.appendChild(el);

  setTimeout(() => {
    el.classList.add('out');
    el.addEventListener('animationend', () => el.remove(), { once: true });
  }, duration);
}

export const toastSuccess = msg => toast(msg, 'success');
export const toastError   = msg => toast(msg, 'error', 5000);
export const toastInfo    = msg => toast(msg, 'info');
