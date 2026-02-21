/** Modul 7 – Inventur */

import * as Store from '../../data/store.js';
import { formatCurrency, formatNum, formatDate } from '../utils/format.js';
import { toastSuccess, toastError } from '../utils/toast.js';

let currentEintraege = [];

export function init() {
  render();
  document.getElementById('btn-inventur-start')?.addEventListener('click', startInventur);
  document.getElementById('btn-inventur-abschluss')?.addEventListener('click', abschliessenInventur);
  document.addEventListener('erp:chargen-updated', render);
}

function render() {
  const daten = Store.getWarenstandMitArtikel();
  const gesamt = daten.reduce((s, d) => s + d.menge * d.ekPreis, 0);
  setEl('inv-soll-wert', formatCurrency(gesamt));
  setEl('inv-artikel',   daten.length);
}

function startInventur() {
  currentEintraege = Store.startInventur();
  const container = document.getElementById('inv-eingabe');
  if (!container) return;

  container.innerHTML = `
    <h3 style="margin-bottom:12px">Ist-Bestand eingeben</h3>
    <table class="data-table">
      <thead>
        <tr>
          <th>Artikel</th><th>Soll</th><th>Einheit</th>
          <th>MHD</th><th>Ist-Menge</th>
        </tr>
      </thead>
      <tbody>
        ${currentEintraege.map((e, i) => {
          const art = Store.getArtikelById(e.artikelId);
          return `
            <tr>
              <td>${art?.name ?? e.artikelId}</td>
              <td>${formatNum(e.sollMenge, 3)}</td>
              <td>${art?.einheit ?? ''}</td>
              <td>${formatDate(e.mhd)}</td>
              <td>
                <input type="number" step="0.001" min="0"
                  data-idx="${i}" class="inv-ist"
                  placeholder="${formatNum(e.sollMenge, 3)}"
                  style="width:100px">
              </td>
            </tr>`;
        }).join('')}
      </tbody>
    </table>
    <div class="actions">
      <button id="btn-inventur-abschluss" class="btn btn-success">Inventur abschließen</button>
    </div>`;

  document.getElementById('btn-inventur-abschluss')?.addEventListener('click', abschliessenInventur);
  container.hidden = false;
}

function abschliessenInventur() {
  const istInputs = document.querySelectorAll('.inv-ist');
  istInputs.forEach(inp => {
    const idx = parseInt(inp.dataset.idx);
    const val = inp.value !== '' ? parseFloat(inp.value) : null;
    if (currentEintraege[idx]) currentEintraege[idx].istMenge = val;
  });

  const analyse = Store.getSchwundAnalyse(currentEintraege.filter(e => e.istMenge !== null));
  const inv     = Store.abschliessenInventur(currentEintraege);

  renderErgebnis(analyse);
  toastSuccess(`Inventur ${inv.id} abgeschlossen`);
  document.getElementById('inv-eingabe').hidden = true;
}

function renderErgebnis(analyse) {
  const container = document.getElementById('inv-ergebnis');
  if (!container) return;

  const diffKlasse = analyse.schwundQuote < -Store.getSettings().schwundBenchmark
    ? 'danger' : analyse.schwundQuote < -1 ? 'warning' : 'success';

  setEl('inv-ist-wert',     formatCurrency(analyse.istWert));
  setEl('inv-differenz',    formatCurrency(analyse.schwundWert));
  setEl('inv-schwund-pct',  `${formatNum(analyse.schwundQuote)} %`);

  const tbody = document.getElementById('inv-diff-tbody');
  if (tbody) {
    tbody.innerHTML = analyse.positionen.map(p => {
      const art = Store.getArtikelById(p.artikelId);
      const klasse = p.wertDiff >= 0 ? 'success' : p.wertDiff > -10 ? 'warning' : 'danger';
      return `
        <tr>
          <td>${art?.name ?? p.artikelId}</td>
          <td>${formatNum(p.sollMenge, 3)} ${art?.einheit ?? ''}</td>
          <td>${formatNum(p.istMenge, 3)} ${art?.einheit ?? ''}</td>
          <td style="color:var(--color-${klasse})">${p.differenz >= 0 ? '+' : ''}${formatNum(p.differenz, 3)}</td>
          <td>${formatCurrency(p.ekPreis)}</td>
          <td style="color:var(--color-${klasse})">${formatCurrency(p.wertDiff)}</td>
        </tr>`;
    }).join('');
  }
  container.hidden = false;
}

function setEl(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; }
