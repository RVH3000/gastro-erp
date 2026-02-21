/** Formatierungs-Utilities (lokalisiert auf de-AT) */

const currencyFmt = new Intl.NumberFormat('de-AT', { style: 'currency', currency: 'EUR' });
const numFmt      = new Intl.NumberFormat('de-AT', { maximumFractionDigits: 2 });
const dateFmt     = new Intl.DateTimeFormat('de-AT', { day: '2-digit', month: '2-digit', year: 'numeric' });

export const formatCurrency = v => currencyFmt.format(v);
export const formatNum      = (v, decimals = 2) =>
  new Intl.NumberFormat('de-AT', { maximumFractionDigits: decimals }).format(v);
export const formatDate     = isoStr => dateFmt.format(new Date(isoStr));
export const formatPercent  = v => `${numFmt.format(v)} %`;

/** Rundet auf nächsten netten VK (z.B. x.90) */
export function roundVK(preis) {
  const base = Math.floor(preis);
  const cents = preis - base;
  return cents < 0.45 ? base - 0.10 : cents < 0.95 ? base + 0.90 : base + 0.90;
}

/** Gibt heute als ISO-String zurück */
export const today = () => new Date().toISOString().slice(0, 10);
