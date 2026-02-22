/** Modul 6 – Kalkulation (Planung + Kassenkalkulation) */

import * as Store from '../../data/store.js';
import { formatCurrency, formatNum, formatPercent } from '../utils/format.js';
import { initSubTabs } from './tabs.js';

export function init() {
  const container = document.getElementById('kalkulation');
  if (!container) return;

  initSubTabs(container);

  // Live-Kalkulator
  const weInput = document.getElementById('kal-we-input');
  if (weInput) {
    weInput.addEventListener('input', updateLiveKalkulator);
    updateLiveKalkulator();
  }

  renderPlanung();
  renderKasse();
  document.addEventListener('erp:chargen-updated', () => { renderPlanung(); renderKasse(); });
}

function updateLiveKalkulator() {
  const we  = parseFloat(document.getElementById('kal-we-input')?.value) || 0;
  const { wareneinsatzZiel, umsatzsteuer } = Store.getSettings();
  const vkNetto  = we / (wareneinsatzZiel / 100);
  const vkBrutto = vkNetto * (1 + umsatzsteuer / 100);
  const vkRound  = Math.round(vkBrutto / 0.1) * 0.1;

  setEl('kal-vk-netto',   formatCurrency(vkNetto));
  setEl('kal-vk-brutto',  formatCurrency(vkBrutto));
  setEl('kal-vk-gerundet', formatCurrency(vkRound));
}

function renderPlanung() {
  const tbody = document.getElementById('kal-plan-tbody');
  if (!tbody) return;
  const { wareneinsatzZiel } = Store.getSettings();

  const rows = Store.getRezepturen().map(r => {
    const kal = Store.kalkuliereRezept(r);
    const diff = kal.weProz - wareneinsatzZiel;
    const klasse = Math.abs(diff) <= 1 ? 'success' : diff <= 3 ? 'warning' : 'danger';
    return `
      <tr>
        <td>${r.name}</td>
        <td>${r.kategorie}</td>
        <td>${formatCurrency(kal.weProPortion)}</td>
        <td>${formatCurrency(kal.vkGerundet)}</td>
        <td>${formatNum(kal.weProz)} %</td>
        <td><span class="badge badge-${klasse}">${diff > 0 ? '+' : ''}${formatNum(diff)} %</span></td>
      </tr>`;
  }).join('');

  tbody.innerHTML = rows || '<tr><td colspan="6" class="empty-state">Keine Rezepturen.</td></tr>';
}

function renderKasse() {
  const kal = Store.getKassenKalkulation();
  const { wareneinsatzZiel } = Store.getSettings();
  const diffKlasse = Math.abs(kal.abweichung) <= 1 ? 'success' : Math.abs(kal.abweichung) <= 3 ? 'warning' : 'danger';

  setEl('kasse-umsatz',     formatCurrency(kal.umsatz));
  setEl('kasse-verbrauch',  formatCurrency(kal.warenverbrauch));
  setEl('kasse-ist-we',     `${formatNum(kal.istWE)} %`);
  setEl('kasse-abw',        `${kal.abweichung >= 0 ? '+' : ''}${formatNum(kal.abweichung)} %`);
  setEl('kasse-db',         formatCurrency(kal.deckungsbeitrag));

  const abwEl = document.getElementById('kasse-abw');
  if (abwEl) {
    abwEl.className = `badge badge-${diffKlasse}`;
  }
}

function setEl(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; }
