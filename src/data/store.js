/**
 * Zentraler Datenspeicher – Single Source of Truth.
 * Alle Module lesen und schreiben über diesen Store.
 * Änderungen werden per CustomEvent an die UI kommuniziert.
 */

const STORAGE_KEY = 'gastro_erp_v1';

const defaultState = {
  artikel: [
    { id: 'A001', name: 'Rinderlende',         kategorie: 'Fleisch & Fisch',  einheit: 'kg',   ekPreis: 42.00 },
    { id: 'A002', name: 'Lachsfilet',          kategorie: 'Fleisch & Fisch',  einheit: 'kg',   ekPreis: 28.00 },
    { id: 'A003', name: 'Hühnerbrust',         kategorie: 'Fleisch & Fisch',  einheit: 'kg',   ekPreis: 9.50  },
    { id: 'A004', name: 'Kalbsrücken',         kategorie: 'Fleisch & Fisch',  einheit: 'kg',   ekPreis: 38.00 },
    { id: 'A005', name: 'Babyspinat',          kategorie: 'Gemüse & Obst',    einheit: 'kg',   ekPreis: 8.00  },
    { id: 'A006', name: 'Kürbis',              kategorie: 'Gemüse & Obst',    einheit: 'kg',   ekPreis: 2.50  },
    { id: 'A007', name: 'Champignons',         kategorie: 'Gemüse & Obst',    einheit: 'kg',   ekPreis: 6.50  },
    { id: 'A008', name: 'Tomaten',             kategorie: 'Gemüse & Obst',    einheit: 'kg',   ekPreis: 3.20  },
    { id: 'A009', name: 'Steinpilze getrocknet', kategorie: 'Gemüse & Obst', einheit: 'kg',   ekPreis: 156.00},
    { id: 'A010', name: 'Sahne 33%',           kategorie: 'Milchprodukte',    einheit: 'L',    ekPreis: 4.20  },
    { id: 'A011', name: 'Bergkäse gereift',    kategorie: 'Milchprodukte',    einheit: 'kg',   ekPreis: 15.00 },
    { id: 'A012', name: 'Butter',              kategorie: 'Milchprodukte',    einheit: 'kg',   ekPreis: 12.80 },
    { id: 'A013', name: 'Parmesan',            kategorie: 'Milchprodukte',    einheit: 'kg',   ekPreis: 24.00 },
    { id: 'A014', name: 'Risotto-Reis',        kategorie: 'Trockenwaren',     einheit: 'kg',   ekPreis: 8.50  },
    { id: 'A015', name: 'Pasta',               kategorie: 'Trockenwaren',     einheit: 'kg',   ekPreis: 3.20  },
    { id: 'A016', name: 'Mehl Type 480',       kategorie: 'Trockenwaren',     einheit: 'kg',   ekPreis: 1.80  },
    { id: 'A017', name: 'Bio-Rinderfond',      kategorie: 'Trockenwaren',     einheit: 'kg',   ekPreis: 12.50 },
  ],

  // Chargen: { id, artikelId, menge, ekPreis, mhd, lieferant, datum, chargennr }
  chargen: [
    { id: 'C001', artikelId: 'A001', menge: 1.8,  ekPreis: 42.00, mhd: '2026-03-10', lieferant: 'Fleischerei Karner',  datum: '2026-02-15', chargennr: 'FL-001' },
    { id: 'C002', artikelId: 'A002', menge: 1.2,  ekPreis: 28.00, mhd: '2026-02-23', lieferant: 'Metro Cash & Carry',  datum: '2026-02-18', chargennr: 'MC-042' },
    { id: 'C003', artikelId: 'A003', menge: 2.5,  ekPreis: 9.50,  mhd: '2026-02-27', lieferant: 'Transgourmet',        datum: '2026-02-17', chargennr: 'TG-117' },
    { id: 'C004', artikelId: 'A004', menge: 1.0,  ekPreis: 38.00, mhd: '2026-03-05', lieferant: 'Fleischerei Karner',  datum: '2026-02-16', chargennr: 'FL-002' },
    { id: 'C005', artikelId: 'A005', menge: 0.5,  ekPreis: 8.00,  mhd: '2026-02-25', lieferant: 'Gemüse Müller',       datum: '2026-02-19', chargennr: 'GM-033' },
    { id: 'C006', artikelId: 'A006', menge: 3.2,  ekPreis: 2.50,  mhd: '2026-03-20', lieferant: 'Biohof Steiermark',   datum: '2026-02-15', chargennr: 'BS-008' },
    { id: 'C007', artikelId: 'A007', menge: 1.8,  ekPreis: 6.50,  mhd: '2026-02-28', lieferant: 'Gemüse Müller',       datum: '2026-02-18', chargennr: 'GM-034' },
    { id: 'C008', artikelId: 'A008', menge: 2.5,  ekPreis: 3.20,  mhd: '2026-03-01', lieferant: 'Gemüse Müller',       datum: '2026-02-17', chargennr: 'GM-035' },
    { id: 'C009', artikelId: 'A009', menge: 0.4,  ekPreis: 156.00,mhd: '2027-02-20', lieferant: 'Transgourmet',        datum: '2026-02-17', chargennr: 'TG-118' },
    { id: 'C010', artikelId: 'A010', menge: 2.0,  ekPreis: 4.20,  mhd: '2026-02-22', lieferant: 'Metro Cash & Carry',  datum: '2026-02-15', chargennr: 'MC-043' },
    { id: 'C011', artikelId: 'A011', menge: 2.8,  ekPreis: 15.00, mhd: '2026-04-30', lieferant: 'Käserei Alm',         datum: '2026-02-18', chargennr: 'KA-019' },
    { id: 'C012', artikelId: 'A012', menge: 3.5,  ekPreis: 12.80, mhd: '2026-04-15', lieferant: 'Metro Cash & Carry',  datum: '2026-02-16', chargennr: 'MC-044' },
    { id: 'C013', artikelId: 'A013', menge: 1.2,  ekPreis: 24.00, mhd: '2026-06-30', lieferant: 'Transgourmet',        datum: '2026-02-16', chargennr: 'TG-119' },
    { id: 'C014', artikelId: 'A014', menge: 4.5,  ekPreis: 8.50,  mhd: '2027-01-01', lieferant: 'Metro Cash & Carry',  datum: '2026-02-10', chargennr: 'MC-040' },
    { id: 'C015', artikelId: 'A015', menge: 8.0,  ekPreis: 3.20,  mhd: '2026-12-31', lieferant: 'Metro Cash & Carry',  datum: '2026-02-10', chargennr: 'MC-041' },
    { id: 'C016', artikelId: 'A016', menge: 12.0, ekPreis: 1.80,  mhd: '2027-06-01', lieferant: 'Metro Cash & Carry',  datum: '2026-02-05', chargennr: 'MC-039' },
    { id: 'C017', artikelId: 'A017', menge: 4.8,  ekPreis: 12.50, mhd: '2026-03-15', lieferant: 'Biohof Steiermark',   datum: '2026-02-19', chargennr: 'BS-009' },
  ],

  rezepturen: [
    {
      id: 'R001',
      name: 'Kalbsrücken mit Steinpilz-Risotto',
      kategorie: 'Hauptspeise',
      portionen: 4,
      zutaten: [
        { artikelId: 'A004', menge: 0.720, einheit: 'kg' },
        { artikelId: 'A009', menge: 0.060, einheit: 'kg' },
        { artikelId: 'A014', menge: 0.320, einheit: 'kg' },
        { artikelId: 'A010', menge: 0.200, einheit: 'L'  },
        { artikelId: 'A012', menge: 0.080, einheit: 'kg' },
        { artikelId: 'A013', menge: 0.060, einheit: 'kg' },
      ],
      gewuerze: 0.45,
    },
    {
      id: 'R002',
      name: 'Lachs auf Babyspinat-Bett',
      kategorie: 'Vorspeise',
      portionen: 4,
      zutaten: [
        { artikelId: 'A002', menge: 0.600, einheit: 'kg' },
        { artikelId: 'A005', menge: 0.400, einheit: 'kg' },
        { artikelId: 'A010', menge: 0.100, einheit: 'L'  },
        { artikelId: 'A012', menge: 0.040, einheit: 'kg' },
      ],
      gewuerze: 0.30,
    },
    {
      id: 'R003',
      name: 'Bergkäse-Auswahl mit Kürbiskompott',
      kategorie: 'Dessert',
      portionen: 4,
      zutaten: [
        { artikelId: 'A011', menge: 0.480, einheit: 'kg' },
        { artikelId: 'A006', menge: 0.600, einheit: 'kg' },
      ],
      gewuerze: 0.20,
    },
  ],

  verkäufe: [
    { datum: '2026-02-19', rezeptId: 'R001', anzahl: 8, umsatz: 295.20 },
    { datum: '2026-02-19', rezeptId: 'R002', anzahl: 6, umsatz: 113.40 },
    { datum: '2026-02-18', rezeptId: 'R001', anzahl: 10, umsatz: 369.00 },
    { datum: '2026-02-18', rezeptId: 'R002', anzahl: 8, umsatz: 151.20 },
    { datum: '2026-02-18', rezeptId: 'R003', anzahl: 5, umsatz: 64.50  },
  ],

  inventuren: [],

  settings: {
    wareneinsatzZiel: 33,
    umsatzsteuer: 10,
    mhdWarnungTage: 7,
    mhdKritischTage: 3,
    schwundBenchmark: 3,
  },
};

// ── State ──────────────────────────────────────────────────────────────────

function loadState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? { ...defaultState, ...JSON.parse(saved) } : structuredClone(defaultState);
  } catch {
    return structuredClone(defaultState);
  }
}

let state = loadState();

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.warn('localStorage nicht verfügbar:', e);
  }
}

function emit(event, detail = {}) {
  document.dispatchEvent(new CustomEvent(`erp:${event}`, { detail }));
}

// ── Artikel ────────────────────────────────────────────────────────────────

export function getArtikel() {
  return state.artikel;
}

export function getArtikelById(id) {
  return state.artikel.find(a => a.id === id);
}

// ── Chargen & Warenstand ───────────────────────────────────────────────────

export function getChargen() {
  // FEFO-sortiert: ältestes MHD zuerst
  return [...state.chargen].sort((a, b) => new Date(a.mhd) - new Date(b.mhd));
}

export function addCharge(charge) {
  const id = `C${String(state.chargen.length + 1).padStart(3, '0')}`;
  const neue = { ...charge, id };
  state.chargen.push(neue);
  saveState();
  emit('chargen-updated');
  return neue;
}

/** Aggregierter Warenstand: { artikelId, menge, mhd (frühestes), ekPreis } */
export function getWarenstand() {
  const map = new Map();

  for (const charge of getChargen()) {
    if (!map.has(charge.artikelId)) {
      map.set(charge.artikelId, {
        artikelId: charge.artikelId,
        menge: 0,
        mhd: charge.mhd,       // FEFO: frühestes MHD
        ekPreis: charge.ekPreis,
        chargen: [],
      });
    }
    const eintrag = map.get(charge.artikelId);
    eintrag.menge += charge.menge;
    eintrag.chargen.push(charge);
    if (new Date(charge.mhd) < new Date(eintrag.mhd)) {
      eintrag.mhd = charge.mhd;
    }
  }

  return [...map.values()];
}

export function getWarenstandMitArtikel() {
  return getWarenstand().map(ws => ({
    ...ws,
    artikel: getArtikelById(ws.artikelId),
  }));
}

// ── MHD-Analyse ───────────────────────────────────────────────────────────

export function getMhdStatus(mhd) {
  const heute = new Date();
  heute.setHours(0, 0, 0, 0);
  const ablauf = new Date(mhd);
  ablauf.setHours(0, 0, 0, 0);
  const tage = Math.round((ablauf - heute) / 86400000);
  const { mhdWarnungTage, mhdKritischTage } = state.settings;

  if (tage < 0)   return { tage, label: 'Abgelaufen',  klasse: 'danger' };
  if (tage <= mhdKritischTage) return { tage, label: 'Kritisch',   klasse: 'danger' };
  if (tage <= mhdWarnungTage)  return { tage, label: 'Priorität',  klasse: 'warning' };
  return { tage, label: 'Gut', klasse: 'success' };
}

export function getMhdUebersicht() {
  return getWarenstandMitArtikel()
    .map(ws => ({ ...ws, mhdStatus: getMhdStatus(ws.mhd) }))
    .sort((a, b) => new Date(a.mhd) - new Date(b.mhd));
}

// ── Rezepturen & Kalkulation ──────────────────────────────────────────────

export function getRezepturen() {
  return state.rezepturen;
}

export function getRezeptById(id) {
  return state.rezepturen.find(r => r.id === id);
}

export function kalkuliereRezept(rezept) {
  const ws = new Map(getWarenstand().map(w => [w.artikelId, w]));
  const { wareneinsatzZiel, umsatzsteuer } = state.settings;

  let weGesamt = rezept.gewuerze || 0;
  const zutatenKalkuliert = rezept.zutaten.map(z => {
    const bestand = ws.get(z.artikelId);
    const ekPreis = bestand?.ekPreis ?? getArtikelById(z.artikelId)?.ekPreis ?? 0;
    const kosten = z.menge * ekPreis;
    weGesamt += kosten;
    return {
      ...z,
      artikel: getArtikelById(z.artikelId),
      ekPreis,
      kosten,
      verfuegbar: bestand?.menge ?? 0,
      ausreichend: (bestand?.menge ?? 0) >= z.menge,
    };
  });

  const weProPortion = weGesamt / rezept.portionen;
  const vkNetto = weProPortion / (wareneinsatzZiel / 100);
  const vkBrutto = vkNetto * (1 + umsatzsteuer / 100);
  const vkGerundet = Math.round(vkBrutto / 0.1) * 0.1;
  const weProz = (weProPortion / vkGerundet) * (1 + umsatzsteuer / 100) * 100;

  return {
    rezept,
    zutatenKalkuliert,
    weProPortion,
    weGesamt,
    vkNetto,
    vkBrutto,
    vkGerundet,
    weProz,
    istOptimal: weProz <= wareneinsatzZiel + 1,
  };
}

export function addRezeptur(rezept) {
  const id = `R${String(state.rezepturen.length + 1).padStart(3, '0')}`;
  const neue = { ...rezept, id };
  state.rezepturen.push(neue);
  saveState();
  emit('rezepturen-updated');
  return neue;
}

// ── Spontane Menüentwicklung ──────────────────────────────────────────────

/** Schlägt Gerichte vor, die mit aktuellem Warenstand realisierbar sind.
 *  Priorisiert Rezepte, die kritische MHD-Artikel verwenden.
 */
export function generiereMenuvorschlaege() {
  const ws = new Map(getWarenstand().map(w => [w.artikelId, w]));
  const kritischeMhds = new Set(
    getMhdUebersicht()
      .filter(w => w.mhdStatus.klasse === 'danger' || w.mhdStatus.klasse === 'warning')
      .map(w => w.artikelId)
  );

  return state.rezepturen
    .map(rezept => {
      const kal = kalkuliereRezept(rezept);
      const kritischVerwendet = rezept.zutaten.filter(z => kritischeMhds.has(z.artikelId)).length;
      const allVerfuegbar = kal.zutatenKalkuliert.every(z => z.ausreichend);
      return { ...kal, kritischVerwendet, allVerfuegbar };
    })
    .filter(v => v.allVerfuegbar)
    .sort((a, b) => b.kritischVerwendet - a.kritischVerwendet);
}

// ── Verkäufe ──────────────────────────────────────────────────────────────

export function getVerkäufe() {
  return state.verkäufe;
}

export function getKassenKalkulation() {
  const { wareneinsatzZiel } = state.settings;
  const umsatz = state.verkäufe.reduce((s, v) => s + v.umsatz, 0);

  let warenverbrauch = 0;
  for (const v of state.verkäufe) {
    const rezept = getRezeptById(v.rezeptId);
    if (!rezept) continue;
    const kal = kalkuliereRezept(rezept);
    warenverbrauch += kal.weProPortion * v.anzahl;
  }

  const istWE = umsatz > 0 ? (warenverbrauch / umsatz) * 100 : 0;
  return {
    umsatz,
    warenverbrauch,
    istWE,
    abweichung: istWE - wareneinsatzZiel,
    deckungsbeitrag: umsatz - warenverbrauch,
  };
}

// ── Inventur ──────────────────────────────────────────────────────────────

export function startInventur() {
  const soll = getWarenstandMitArtikel().map(ws => ({
    artikelId: ws.artikelId,
    sollMenge: ws.menge,
    istMenge: null,
    ekPreis: ws.ekPreis,
    mhd: ws.mhd,
  }));
  return soll;
}

export function abschliessenInventur(eintraege) {
  const inv = {
    id: `INV${Date.now()}`,
    datum: new Date().toISOString().slice(0, 10),
    eintraege,
    abgeschlossen: true,
  };
  state.inventuren.push(inv);

  // Bestände korrigieren: Differenz auf Chargen anwenden
  for (const e of eintraege) {
    if (e.istMenge === null) continue;
    const diff = e.istMenge - e.sollMenge;
    if (Math.abs(diff) < 0.001) continue;
    // Einfachste Korrektur: Korrektur-Charge hinzufügen
    state.chargen.push({
      id: `KORR${Date.now()}${e.artikelId}`,
      artikelId: e.artikelId,
      menge: diff,
      ekPreis: e.ekPreis,
      mhd: e.mhd,
      lieferant: 'Inventurkorrektur',
      datum: inv.datum,
      chargennr: `INV-${inv.id}`,
    });
  }

  saveState();
  emit('inventur-abgeschlossen', { inventurId: inv.id });
  return inv;
}

export function getSchwundAnalyse(eintraege) {
  let sollWert = 0, istWert = 0;
  const positionen = eintraege
    .filter(e => e.istMenge !== null)
    .map(e => {
      const differenz = e.istMenge - e.sollMenge;
      const wertDiff = differenz * e.ekPreis;
      sollWert += e.sollMenge * e.ekPreis;
      istWert  += e.istMenge  * e.ekPreis;
      return { ...e, differenz, wertDiff };
    });

  const schwundWert = istWert - sollWert;
  const schwundQuote = sollWert > 0 ? (schwundWert / sollWert) * 100 : 0;
  return { positionen, sollWert, istWert, schwundWert, schwundQuote };
}

// ── Settings ──────────────────────────────────────────────────────────────

export function getSettings() {
  return { ...state.settings };
}

export function updateSettings(partial) {
  state.settings = { ...state.settings, ...partial };
  saveState();
  emit('settings-updated');
}

// ── Reset ─────────────────────────────────────────────────────────────────

export function resetState() {
  state = structuredClone(defaultState);
  saveState();
  emit('state-reset');
}
