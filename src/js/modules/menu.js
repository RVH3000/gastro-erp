/** Modul 4 – Spontane Menüentwicklung */

import * as Store from '../../data/store.js';
import { formatCurrency, formatNum } from '../utils/format.js';
import { toastInfo } from '../utils/toast.js';

export function init() {
  render();
  document.getElementById('btn-neues-menu')?.addEventListener('click', render);
  document.addEventListener('erp:chargen-updated', render);
}

function render() {
  const vorschlaege = Store.generiereMenuvorschlaege();
  const container   = document.getElementById('menu-vorschlaege');
  if (!container) return;

  if (!vorschlaege.length) {
    container.innerHTML = `<div class="alert alert-warning">
      Kein vollständiges Menü aus aktuellem Warenbestand realisierbar. Wareneingang erfassen.
    </div>`;
    return;
  }

  container.innerHTML = vorschlaege.map(v => {
    const weKlasse = v.weProz <= 33 ? 'success' : v.weProz <= 36 ? 'warning' : 'danger';
    return `
      <div class="recipe-suggestion">
        <h4>${v.rezept.name}</h4>
        <span class="badge badge-info">${v.rezept.kategorie}</span>
        ${v.kritischVerwendet ? `<span class="badge badge-warning">Verwertet ${v.kritischVerwendet} kritische MHD-Artikel</span>` : ''}
        <div class="recipe-meta">
          <span>WE/Portion: <strong>${formatCurrency(v.weProPortion)}</strong></span>
          <span>Empf. VK: <strong>${formatCurrency(v.vkGerundet)}</strong></span>
          <span>WE%: <strong style="color:var(--color-${weKlasse})">${formatNum(v.weProz)}%</strong></span>
          <span>Portionen: <strong>${v.rezept.portionen}</strong></span>
        </div>
        <div class="actions">
          <button class="btn btn-primary btn-sm" data-rezept="${v.rezept.id}" data-action="kalkulation">
            Kalkulieren
          </button>
        </div>
      </div>`;
  }).join('');

  // Delegierter Event für Kalkulations-Button
  container.addEventListener('click', e => {
    const btn = e.target.closest('[data-action="kalkulation"]');
    if (!btn) return;
    // Tab zu Rezeptur wechseln
    document.querySelector('[data-tab="rezeptur"]')?.click();
    toastInfo('Rezeptur-Modul geöffnet');
  }, { once: false });
}
