#!/usr/bin/env node
// Registration form + intake list factory - the last step that used to need a human
// typing API calls. Implements the recipes live-verified 2026-07-30 (see
// webinar-hubspot-agent-scope.md § "Form clone + intake list factory") so the whole
// launch can run unattended in CI.
//
// Usage:
//   node scripts/ensure-hubspot-intake.js "<eventStem|eventId>"            # dry-run
//   node scripts/ensure-hubspot-intake.js "<eventStem|eventId>" --create
//   ... [--seed-form <guid>]   # override the auto-picked seed form
//
// Neither POST is idempotent, so every create is preceded by a search-by-name
// reconcile and each id is written to config/webinars.json the moment it exists.
// If the search itself fails we stop rather than POST blind - a duplicate form
// silently splits a webinar's registrations across two lists.

require('./load-env');
const fs = require('fs');
const path = require('path');

const HUBSPOT_API_BASE = 'https://api.hubapi.com';
const CONFIG_PATH = path.join(__dirname, '..', 'config', 'webinars.json');
const TODO = /^TODO/i;

function assertEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required env var: ${name}`);
  return value;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function hubspotRequest(reqPath, { method = 'GET', body } = {}) {
  const token = assertEnv('HUBSPOT_PRIVATE_APP_TOKEN');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  let res;
  try {
    res = await fetch(`${HUBSPOT_API_BASE}${reqPath}`, {
      method,
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
  const text = await res.text();
  if (!res.ok) throw new Error(`HubSpot ${method} ${reqPath} failed: ${res.status} ${text.slice(0, 500)}`);
  await sleep(1000);
  return text ? JSON.parse(text) : null;
}

function loadConfigs() {
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

// Merge-on-write: re-read first so a concurrently-running launch keeps its ids.
// Keyed on riversideEventId, never on eventStem: two webinars in a series share a title,
// and a stem-keyed write would stamp this event's form and list onto the other one.
function locate(configs, entry) {
  if (entry.riversideEventId) {
    const i = configs.findIndex((c) => c.riversideEventId === entry.riversideEventId);
    if (i !== -1) return i;
  }
  const matches = configs
    .map((c, i) => ({ c, i }))
    .filter(({ c }) => c.eventStem === entry.eventStem);
  if (matches.length > 1) {
    throw new Error(`"${entry.eventStem}" matches ${matches.length} config entries and the entry has no riversideEventId. Refusing to guess which one to write.`);
  }
  return matches.length === 1 ? matches[0].i : -1;
}

function saveEntry(entry) {
  const onDisk = loadConfigs();
  const i = locate(onDisk, entry);
  if (i === -1) onDisk.push(entry); else onDisk[i] = entry;
  fs.writeFileSync(CONFIG_PATH, `${JSON.stringify(onDisk, null, 2)}\n`);
}

function findEntry(configs, needle) {
  return configs.find((c) => c.eventStem === needle)
    || configs.find((c) => c.riversideEventId === needle);
}

function isFilled(value) {
  return Boolean(value) && !TODO.test(String(value));
}

// Names are how existing resources are reconciled before a create, so they have to be
// unique per EVENT, not per title. eventStem stays the readable prefix; the tail of the
// Riverside event id disambiguates a repeated title.
function nameSuffix(entry) {
  const id = String(entry.riversideEventId || '');
  return id ? ` [${id.slice(-6)}]` : '';
}

// Seed = the most recently scheduled non-archived webinar that already has a real
// form. Falls back to any entry with one, so a first run in a fresh portal still works.
function pickSeedForm(configs, entry) {
  const candidates = configs
    .filter((c) => c !== entry && !c.archived && isFilled(c.hubspotFormId))
    .sort((a, b) => String(b.eventStartsAt || '').localeCompare(String(a.eventStartsAt || '')));
  const fallback = configs.filter((c) => c !== entry && isFilled(c.hubspotFormId));
  return (candidates[0] || fallback[0] || {}).hubspotFormId || null;
}

async function findFormByName(name) {
  let after;
  do {
    const qs = new URLSearchParams({ limit: '100' });
    if (after) qs.set('after', after);
    const page = await hubspotRequest(`/marketing/v3/forms?${qs}`);
    const hit = (page.results || []).find((f) => f.name === name);
    if (hit) return hit;
    after = page.paging?.next?.after;
  } while (after);
  return null;
}

async function ensureForm(entry, { seedOverride, doCreate, configs }) {
  if (isFilled(entry.hubspotFormId)) {
    console.log(`[form] already set: ${entry.hubspotFormId}`);
    return entry.hubspotFormId;
  }
  const name = `Webinar: ${entry.eventStem}${nameSuffix(entry)}`;
  const seedGuid = seedOverride || pickSeedForm(configs, entry);
  if (!seedGuid) throw new Error('No seed form available to clone. Pass --seed-form <guid>.');

  const existing = await findFormByName(name);
  if (existing) {
    console.log(`[form] reconciled to existing "${name}" (${existing.id})`);
    entry.hubspotFormId = existing.id;
    saveEntry(entry);
    return existing.id;
  }
  if (!doCreate) {
    console.log(`[form] would clone seed ${seedGuid} into "${name}"`);
    return null;
  }

  const seed = await hubspotRequest(`/marketing/v3/forms/${seedGuid}`);
  // Strip ONLY id and archived. createdAt/updatedAt must stay present or the POST
  // 400s ("Some required fields were not set"); HubSpot stamps its own values.
  const { id: _id, archived: _archived, ...clone } = seed;
  clone.name = name;
  const created = await hubspotRequest('/marketing/v3/forms', { method: 'POST', body: clone });
  entry.hubspotFormId = created.id;
  saveEntry(entry);
  console.log(`[form] created "${name}" (${created.id}) from seed ${seedGuid}`);
  return created.id;
}

async function findListByName(name) {
  const res = await hubspotRequest('/crm/v3/lists/search', {
    method: 'POST',
    body: { query: name, count: 100, offset: 0 },
  });
  return (res.lists || []).find((l) => l.name === name) || null;
}

async function ensureList(entry, { doCreate }) {
  if (isFilled(entry.hubspotListId)) {
    console.log(`[list] already set: ${entry.hubspotListId}`);
    return entry.hubspotListId;
  }
  if (!isFilled(entry.hubspotFormId)) {
    console.log('[list] skipped - no form id yet');
    return null;
  }
  const name = `${entry.eventStem}${nameSuffix(entry)} - Form Submissions`;

  const existing = await findListByName(name);
  if (existing) {
    console.log(`[list] reconciled to existing "${name}" (${existing.listId})`);
    entry.hubspotListId = String(existing.listId);
    saveEntry(entry);
    return entry.hubspotListId;
  }
  if (!doCreate) {
    console.log(`[list] would create DYNAMIC "${name}" on form ${entry.hubspotFormId}`);
    return null;
  }

  const res = await hubspotRequest('/crm/v3/lists', {
    method: 'POST',
    body: {
      name,
      objectTypeId: '0-1',
      processingType: 'DYNAMIC',
      filterBranch: {
        filterBranchType: 'OR',
        filterBranches: [{
          filterBranchType: 'AND',
          filterBranches: [],
          filters: [{ filterType: 'FORM_SUBMISSION', formId: entry.hubspotFormId, operator: 'FILLED_OUT' }],
        }],
        filters: [],
      },
    },
  });
  entry.hubspotListId = String(res.list.listId);
  saveEntry(entry);
  console.log(`[list] created "${name}" (${entry.hubspotListId})`);
  return entry.hubspotListId;
}

async function main() {
  const args = process.argv.slice(2);
  const doCreate = args.includes('--create');
  const seedIdx = args.indexOf('--seed-form');
  const seedOverride = seedIdx === -1 ? null : args[seedIdx + 1];
  const seedValueIdx = seedIdx === -1 ? -1 : seedIdx + 1;
  const needle = args.filter((a, i) => !a.startsWith('--') && i !== seedValueIdx)[0];
  if (!needle) throw new Error('Usage: node scripts/ensure-hubspot-intake.js "<eventStem|eventId>" [--create] [--seed-form <guid>]');

  const configs = loadConfigs();
  const entry = findEntry(configs, needle);
  if (!entry) throw new Error(`No config entry matching "${needle}"`);

  console.log(`Intake for "${entry.eventStem}" (${doCreate ? 'CREATE' : 'DRY-RUN'}):`);
  await ensureForm(entry, { seedOverride, doCreate, configs });
  await ensureList(entry, { doCreate });

  if (!doCreate) console.log('\nDry-run only. Re-run with --create to execute.');
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err.message || err);
    process.exit(1);
  });
}

module.exports = { ensureForm, ensureList };
