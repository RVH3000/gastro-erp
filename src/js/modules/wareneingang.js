/**
 * Modul 1 – Wareneingang
 * Formular + Tabelle mit echter Store-Integration.
 */

import * as Store from '../../data/store.js';
import { formatCurrency, formatDate, today } from '../utils/format.js';
import { validateWI, showFieldErrors, clearFieldErrors } from '../utils/validate.js';
import { toastSuccess, toastError } from '../utils/toast.js';

export function init() {
  const form  = document.getElementById('wi-form');
  const tbody = document.getElementById('wi-tbody');
  const artikelSelect = document.getElementById('wi-artikel');

  if (!form) return;

  // Artikel-Dropdown befüllen
  populateArtikel(artikelSelect);

  // Tabelle initial rendern
  renderTabelle(tbody);

  form.addEventListener('submit', e => {
    e.preventDefault();
    clearFieldErrors(form);

    const data = {
      artikelId: form.elements['artikel'].value,
      lieferant: form.elements['lieferant'].value,
      menge:     parseFloat(form.elements['menge'].value),
      ekPreis:   parseFloat(form.elements['ekPreis'].value),
      mhd:       form.elements['mhd'].value,
      datum:     today(),
    };

    const errors = validateWI(data);
    if (Object.keys(errors).filter(k => k !== 'mhdWarnung').length > 0) {
      showFieldErrors(form, errors);
      if (errors.mhdWarnung) {
        toastError('MHD liegt in der Vergangenheit!');
      }
      return;
    }

    // Chargennummer generieren
    const artikel = Store.getArtikelById(data.artikelId);
    const chargennr = `WE-${Date.now().toString(36).toUpperCase()}`;

    Store.addCharge({
      artikelId: data.artikelId,
      menge:     data.menge,
      ekPreis:   data.ekPreis,
      mhd:       data.mhd,
      lieferant: data.lieferant,
      datum:     data.datum,
      chargennr,
    });

    toastSuccess(`✓ ${artikel?.name} (${data.menge} ${artikel?.einheit}) gebucht`);
    form.reset();
    document.getElementById('wi-mhd').value = '';
    renderTabelle(tbody);
  });

  // Store-Events lauschen
  document.addEventListener('erp:chargen-updated', () => renderTabelle(tbody));
}

function populateArtikel(select) {
  if (!select) return;
  const artikel = Store.getArtikel();
  select.innerHTML = '<option value="">-- Artikel wählen --</option>' +
    artikel.map(a => `<option value="${a.id}">${a.name} (${a.einheit})</option>`).join('');
}

function renderTabelle(tbody) {
  if (!tbody) return;
  const chargen = Store.getChargen().slice(0, 50); // Max 50 letzte Einträge

  if (!chargen.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Noch keine Wareneingänge erfasst.</td></tr>';
    return;
  }

  // Wareneingang-Tabelle: neueste Buchungen zuerst (nach Eingabedatum)
  const html = [...chargen]
    .sort((a, b) => new Date(b.datum) - new Date(a.datum) || b.id.localeCompare(a.id))
    .slice(0, 20).map(c => {
    const artikel = Store.getArtikelById(c.artikelId);
    const status  = Store.getMhdStatus(c.mhd);
    return `
      <tr>
        <td>${formatDate(c.datum)}</td>
        <td><strong>${artikel?.name ?? c.artikelId}</strong><br>
            <small style="color:var(--color-text-secondary)">${c.chargennr}</small></td>
        <td>${c.lieferant}</td>
        <td>${c.menge} ${artikel?.einheit ?? ''}</td>
        <td>${formatCurrency(c.menge * c.ekPreis)}</td>
        <td>${formatDate(c.mhd)}</td>
        <td><span class="badge badge-${status.klasse}">${status.label}</span></td>
      </tr>`;
  }).join('');

  tbody.innerHTML = html;
}
