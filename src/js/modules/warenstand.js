/** Modul 3 – Aktueller Warenstand */

import * as Store from '../../data/store.js';
import { formatCurrency, formatNum } from '../utils/format.js';

const KATEGORIEN = ['Fleisch & Fisch', 'Gemüse & Obst', 'Milchprodukte', 'Trockenwaren'];

export function init() {
  render();
  document.addEventListener('erp:chargen-updated', render);
}

function render() {
  const daten = Store.getWarenstandMitArtikel();
  const warenwert = daten.reduce((s, d) => s + d.menge * d.ekPreis, 0);

  setEl('ws-wert',      formatCurrency(warenwert));
  setEl('ws-positionen', daten.length);
  setEl('ws-kategorien', new Set(daten.map(d => d.artikel?.kategorie)).size);

  renderKategorien(daten);
}

function renderKategorien(daten) {
  const container = document.getElementById('ws-kategorien-grid');
  if (!container) return;

  const byKat = {};
  for (const d of daten) {
    const kat = d.artikel?.kategorie ?? 'Sonstige';
    if (!byKat[kat]) byKat[kat] = { wert: 0, artikel: [] };
    byKat[kat].wert += d.menge * d.ekPreis;
    byKat[kat].artikel.push(d);
  }

  container.innerHTML = Object.entries(byKat).map(([kat, { wert, artikel }]) => {
    const icon = kat === 'Fleisch & Fisch' ? '🥩'
               : kat === 'Gemüse & Obst'   ? '🥬'
               : kat === 'Milchprodukte'    ? '🧀'
               : kat === 'Trockenwaren'     ? '🍝' : '📦';
    return `
      <div class="card">
        <h3>${icon} ${kat}</h3>
        <p style="font-size:12px;color:var(--color-text-secondary)">Warenwert: ${formatCurrency(wert)}</p>
        <ul style="margin-top:8px;font-size:14px;list-style:none">
          ${artikel.map(a => `<li>• ${a.artikel?.name} (${formatNum(a.menge,2)} ${a.artikel?.einheit})</li>`).join('')}
        </ul>
      </div>`;
  }).join('');
}

function setEl(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; }
