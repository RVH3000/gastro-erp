import { expect, test } from '@playwright/test';

function isoDate(daysOffset = 0): string {
  const d = new Date();
  d.setUTCDate(d.getUTCDate() + daysOffset);
  return d.toISOString().slice(0, 10);
}

test('gesundheitscheck erreichbar', async ({ request }) => {
  const res = await request.get('/api/v1/health');
  expect(res.ok()).toBeTruthy();
  await expect(res.json()).resolves.toMatchObject({ status: 'ok' });
});

test('wareneingang -> mhd -> kalkulation -> inventur', async ({ request }) => {
  const wareneingang = await request.post('/api/v1/wareneingang', {
    data: {
      lieferant_slug: 'transgourmet',
      lieferschein_nr: 'TG-E2E-1',
      lieferdatum: isoDate(0),
      positionen: [
        {
          artikel_code: 'E2E-100',
          bezeichnung: 'Lachsfilet',
          menge: 4,
          einheit: 'kg',
          ek_preis: 12.5,
          mhd: isoDate(2),
        },
      ],
    },
  });
  expect(wareneingang.ok()).toBeTruthy();

  const mhd = await request.get('/api/v1/mhd/critical');
  expect(mhd.ok()).toBeTruthy();
  const mhdJson = await mhd.json();
  expect(mhdJson.kritische_artikel.length).toBeGreaterThan(0);

  const calc = await request.post('/api/v1/kalkulation/planung', {
    data: { wareneinsatz: 11.14, ziel_we_prozent: 33, ust_prozent: 10 },
  });
  expect(calc.ok()).toBeTruthy();
  const calcJson = await calc.json();
  expect(calcJson.vk_brutto).toBeGreaterThan(0);

  const inv = await request.post('/api/v1/inventur/abschliessen', {
    data: {
      inventur_id: 'INV-E2E-1',
      tenant_id: 'tenant-e2e',
      trace_id: 'trace-e2e',
      differenz_summe: 0,
    },
  });
  expect(inv.ok()).toBeTruthy();
  await expect(inv.json()).resolves.toMatchObject({ status: 'abgeschlossen' });
});

test('integrations-vertrag: idempotency + rksv (BMD optional)', async ({ request }) => {
  const payload = {
    tenant_id: 'tenant-e2e',
    trace_id: 'trace-e2e',
    event_type: 'sale.posted',
    pos_reference: 'POS-1',
    amount_gross: 21.5,
    currency: 'EUR',
    metadata: {},
  };

  const first = await request.post('/v1/integrations/pos/events', {
    data: payload,
    headers: { 'Idempotency-Key': 'idem-e2e-1' },
  });
  expect(first.ok()).toBeTruthy();
  await expect(first.json()).resolves.toMatchObject({ status: 'accepted' });

  const second = await request.post('/v1/integrations/pos/events', {
    data: payload,
    headers: { 'Idempotency-Key': 'idem-e2e-1' },
  });
  expect(second.ok()).toBeTruthy();
  await expect(second.json()).resolves.toMatchObject({ status: 'duplicate' });

  const sign = await request.post('/v1/integrations/fiscal/sign', {
    data: {
      tenant_id: 'tenant-e2e',
      trace_id: 'trace-e2e',
      receipt_reference: 'RCPT-1',
      payload: {},
    },
  });
  expect(sign.ok()).toBeTruthy();

  const dep = await request.post('/v1/integrations/fiscal/dep-export', {
    data: {
      tenant_id: 'tenant-e2e',
      trace_id: 'trace-e2e',
      period_from: '2026-02-01T00:00:00Z',
      period_to: '2026-02-28T00:00:00Z',
    },
  });
  expect(dep.ok()).toBeTruthy();

  const jahresbeleg = await request.post('/v1/integrations/fiscal/jahresbeleg', {
    data: {
      tenant_id: 'tenant-e2e',
      trace_id: 'trace-e2e',
      year: 2026,
    },
  });
  expect(jahresbeleg.ok()).toBeTruthy();

  const exp = await request.post('/v1/integrations/accounting/exports/bmd', {
    data: {
      tenant_id: 'tenant-e2e',
      trace_id: 'trace-e2e',
      period_from: '2026-02-01T00:00:00Z',
      period_to: '2026-02-28T00:00:00Z',
      format: 'CSV',
    },
  });
  expect(exp.status()).toBe(503);
});
