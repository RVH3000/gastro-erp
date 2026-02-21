/**
 * Modul 2 – MHD-Datenbank
 * Dynamische MHD-Berechnung ab heute, FEFO-sortiert.
 */

import * as Store from '../../data/store.js';
import { formatCurrency, formatDate, formatNum } from '../utils/format.js';

export function init() {
  render();
  document.addEventListener('erp:chargen-updated', render);
}

function render() {
  renderStats();
  renderTabelle();
}

function renderStats() {
  const daten = Store.getMhdUebersicht();
  const kritisch = daten.filter(d => d.mhdStatus.klasse === 'danger' && d.mhdStatus.tage >= 0);
  const abgelaufen = daten.filter(d => d.mhdStatus.tage < 0);
  const warnung  = daten.filter(d => d.mhdStatus.klasse === 'warning');

  setEl('mhd-stat-gesamt',     daten.length);
  setEl('mhd-stat-warnung',    kritisch.length + warnung.length);
  setEl('mhd-stat-kritisch',   kritisch.length);
  setEl('mhd-stat-abgelaufen', abgelaufen.length);

  const warnBanner = document.getElementById('mhd-warn-banner');
  if (warnBanner) {
    if (kritisch.length) {
      warnBanner.className = 'alert alert-warning';
      warnBanner.innerHTML = `<strong>⚠️ Warnung:</strong> ${kritisch.length} Artikel erreichen in den nächsten
        ${Store.getSettings().mhdKritischTage} Tagen ihr MHD:
        ${kritisch.map(k => `<strong>${k.artikel?.name}</strong>`).join(', ')}.
        Empfehlung: Sofortige Verwendung oder Preisreduktion.`;
      warnBanner.hidden = false;
    } else if (warnung.length) {
      warnBanner.className = 'alert alert-info';
      warnBanner.innerHTML = `<strong>ℹ️ Hinweis:</strong> ${warnung.length} Artikel werden bald ablaufen.`;
      warnBanner.hidden = false;
    } else {
      warnBanner.hidden = true;
    }
  }
}

function renderTabelle() {
  const tbody = document.getElementById('mhd-tbody');
  if (!tbody) return;

  const daten = Store.getMhdUebersicht();
  if (!daten.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Keine Bestände erfasst.</td></tr>';
    return;
  }

  const settings = Store.getSettings();
  tbody.innerHTML = daten.map(d => {
    const { tage, label, klasse } = d.mhdStatus;
    const tageText = tage < 0 ? `${Math.abs(tage)} Tage überschritten` : `${tage} Tage`;
    // Balken: wie viele Tage bis MHD relativ zu 90 Tagen
    const pct = Math.max(0, Math.min(100, (tage / 90) * 100));
    const empfehlung = tage < 0          ? 'Sofort entsorgen / Kontrolle!'
                     : tage <= settings.mhdKritischTage ? 'Heute verwenden'
                     : tage <= settings.mhdWarnungTage  ? 'Diese Woche verwenden'
                     : 'Reguläre Verwendung';

    return `
      <tr>
        <td>
          <strong>${d.artikel?.name ?? d.artikelId}</strong>
          <div class="mhd-bar"><div class="mhd-bar-fill ${klasse}" style="width:${pct}%"></div></div>
        </td>
        <td>${d.artikel?.kategorie ?? '–'}</td>
        <td>${formatNum(d.menge, 2)} ${d.artikel?.einheit ?? ''}</td>
        <td>${formatDate(d.mhd)}</td>
        <td>${tageText}</td>
        <td><span class="badge badge-${klasse}">${label}</span></td>
        <td style="font-size:13px;color:var(--color-text-secondary)">${empfehlung}</td>
      </tr>`;
  }).join('');
}

function setEl(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}
