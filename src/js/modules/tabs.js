/**
 * Tab-Navigation.
 * Verwendet data-tab / data-panel Attribute + ARIA für Accessibility.
 * Kein globales `event` Objekt – sauber event-gebunden.
 */

export function initTabs(navSelector, panelSelector) {
  const nav    = document.querySelector(navSelector);
  const panels = document.querySelectorAll(panelSelector);
  if (!nav) return;

  nav.addEventListener('click', e => {
    const btn = e.target.closest('[data-tab]');
    if (!btn) return;
    activateTab(nav, panels, btn.dataset.tab);
  });

  // Keyboard navigation
  nav.addEventListener('keydown', e => {
    const btns = [...nav.querySelectorAll('[data-tab]')];
    const idx  = btns.indexOf(document.activeElement);
    if (e.key === 'ArrowRight' && idx < btns.length - 1) btns[idx + 1].focus();
    if (e.key === 'ArrowLeft'  && idx > 0)              btns[idx - 1].focus();
  });
}

export function activateTab(nav, panels, tabId) {
  nav.querySelectorAll('[data-tab]').forEach(btn => {
    const active = btn.dataset.tab === tabId;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-selected', active);
  });
  panels.forEach(panel => {
    const active = panel.id === tabId;
    panel.classList.toggle('active', active);
    panel.hidden = !active;
  });
}

/** Sub-tabs (für Kalkulation) */
export function initSubTabs(container) {
  container.addEventListener('click', e => {
    const btn = e.target.closest('[data-subtab]');
    if (!btn) return;
    const subId = btn.dataset.subtab;
    container.querySelectorAll('[data-subtab]').forEach(b => b.classList.toggle('active', b === btn));
    container.querySelectorAll('[data-subpanel]').forEach(p => {
      p.classList.toggle('active', p.dataset.subpanel === subId);
    });
  });
}
