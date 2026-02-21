/**
 * Gastro ERP – App-Einstiegspunkt
 * Initialisiert alle Module nach DOM-Ready.
 */

import { initTabs } from './modules/tabs.js';
import * as Wareneingang from './modules/wareneingang.js';
import * as MHD          from './modules/mhd.js';
import * as Warenstand   from './modules/warenstand.js';
import * as Menu         from './modules/menu.js';
import * as Kalkulation  from './modules/kalkulation.js';
import * as Inventur     from './modules/inventur.js';

document.addEventListener('DOMContentLoaded', () => {
  // Tab-Navigation initialisieren
  initTabs('#tab-nav', '.tab-panel');

  // Alle Module initialisieren
  Wareneingang.init();
  MHD.init();
  Warenstand.init();
  Menu.init();
  Kalkulation.init();
  Inventur.init();

  // Toast-Container sicherstellen
  if (!document.getElementById('toast-container')) {
    const tc = document.createElement('div');
    tc.id = 'toast-container';
    tc.setAttribute('aria-live', 'polite');
    document.body.appendChild(tc);
  }
});
