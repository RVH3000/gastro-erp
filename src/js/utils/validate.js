/** Formular-Validierung */

export function validateWI(data) {
  const errors = {};
  if (!data.artikelId) errors.artikel = 'Bitte Artikel auswählen';
  if (!data.menge || data.menge <= 0 || data.menge > 9999)
    errors.menge = 'Menge muss zwischen 0,001 und 9999 liegen';
  if (!data.ekPreis || data.ekPreis <= 0 || data.ekPreis > 99999)
    errors.ekPreis = 'Ungültiger Einkaufspreis';
  if (!data.mhd) {
    errors.mhd = 'MHD ist erforderlich';
  } else if (new Date(data.mhd) < new Date(new Date().toDateString())) {
    errors.mhd = 'MHD liegt in der Vergangenheit – trotzdem buchen?';
    errors.mhdWarnung = true;
  }
  if (!data.lieferant) errors.lieferant = 'Bitte Lieferant auswählen';
  return errors;
}

export function validateRezept(data) {
  const errors = {};
  if (!data.name?.trim()) errors.name = 'Gerichtname ist erforderlich';
  if (!data.portionen || data.portionen < 1 || data.portionen > 999)
    errors.portionen = 'Portionen müssen zwischen 1 und 999 liegen';
  if (!data.zutaten?.length) errors.zutaten = 'Mindestens eine Zutat erforderlich';
  return errors;
}

/** Zeigt Fehler im DOM an */
export function showFieldErrors(formEl, errors) {
  formEl.querySelectorAll('.field-error').forEach(el => {
    el.classList.remove('visible');
    el.textContent = '';
  });
  formEl.querySelectorAll('input, select').forEach(el => el.classList.remove('invalid'));

  for (const [field, msg] of Object.entries(errors)) {
    if (field === 'mhdWarnung') continue;
    const errEl = formEl.querySelector(`[data-error="${field}"]`);
    const input = formEl.querySelector(`[name="${field}"]`);
    if (errEl) { errEl.textContent = msg; errEl.classList.add('visible'); }
    if (input) input.classList.add('invalid');
  }
}

export function clearFieldErrors(formEl) {
  formEl.querySelectorAll('.field-error').forEach(el => {
    el.classList.remove('visible');
    el.textContent = '';
  });
  formEl.querySelectorAll('.invalid').forEach(el => el.classList.remove('invalid'));
}
