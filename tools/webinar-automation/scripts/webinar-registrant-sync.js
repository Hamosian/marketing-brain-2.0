#!/usr/bin/env node
// Webinar Registrant Sync Agent - v1 (polling)
//
// What it does, per configured webinar:
//   1. Finds HubSpot contacts already in this webinar's list that don't yet have a
//      Riverside join URL, registers them via Riverside's create-registrant API,
//      and writes the personalized join_url back onto the contact.
//   2. Polls Riverside's get-registrants API (incremental, via updated_after) and
//      syncs attendance data (attended / no-show / duration / rate) back to HubSpot.
//
// Run on a schedule (cron / CronCreate / GitHub Actions), e.g. every 15-30 min
// during an active registration window, plus one run ~1hr after the event ends.
//
// Required env vars:
//   RIVERSIDE_API_KEY          Bearer token (Business API - restricted access, get via CSM)
//   RIVERSIDE_API_BASE         Default https://platform.riverside.com - confirmed live 2026-07-29
//   HUBSPOT_PRIVATE_APP_TOKEN  HubSpot private app token with crm.objects.contacts read/write scope
//
// Config: config/webinars.json - one entry per active webinar (see WEBINAR_CONFIG_EXAMPLE below).
//
// CONFIRMED LIVE 2026-07-29: RIVERSIDE_API_BASE, API key, and create-registrant all work -
// a real test call against event 6a69df3222b8ed2814e4d843 returned 201 with a join_url,
// and the documented 1 req/sec rate limit is real (x-ratelimit-* headers confirmed it).
//
// STILL NOT VERIFIED (flag to Galilei's audit before relying on this in production):
//   - Whether create-registrant can be called for a contact who will join later
//     without them ever visiting Riverside's own hosted registration page at all.
//   - Exact PATCH semantics / required scopes on the HubSpot contacts endpoint.
//   - The HubSpot Lists API path used in fetchListMemberIds() (join-order memberships) -
//     not yet tested against a live list.

require('./load-env');
const RIVERSIDE_API_BASE = process.env.RIVERSIDE_API_BASE || 'https://platform.riverside.com';
const HUBSPOT_API_BASE = 'https://api.hubapi.com';

const WEBINAR_CONFIG_EXAMPLE = {
  // Copy one block per live webinar into config/webinars.json
  eventStem: 'Webinar: Example Event',
  riversideEventId: 'REPLACE_WITH_EVENT_ID', // "Copy event ID" in the Riverside Studio event menu
  hubspotListId: 'REPLACE_WITH_LIST_ID', // the list this webinar's registrants land in
  properties: {
    webinarName: 'webinar_name',
    joinUrl: 'riverside_join_url', // productionized version of test_gal__webinar_join_url - confirm naming/migration with Galilei first
    attended: 'webinar_attended',
    noShow: 'webinar_no_show',
    attendanceDuration: 'webinar_attendance_duration',
    attendanceRate: 'webinar_attendance_rate',
    registeredAt: 'webinar_registered_at',
  },
  stateFile: 'state/example-event.json',
};

function assertEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required env var: ${name}`);
  return value;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function riversideRequest(path, { method = 'GET', query, body } = {}) {
  const apiKey = assertEnv('RIVERSIDE_API_KEY');
  const url = new URL(`${RIVERSIDE_API_BASE}${path}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null) url.searchParams.set(key, value);
    }
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Riverside ${method} ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

async function hubspotRequest(path, { method = 'GET', body } = {}) {
  const token = assertEnv('HUBSPOT_PRIVATE_APP_TOKEN');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  let res;
  try {
    res = await fetch(`${HUBSPOT_API_BASE}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HubSpot ${method} ${path} failed: ${res.status} ${text}`);
  }
  return res.status === 204 ? null : res.json();
}

// --- Step 1: register HubSpot contacts into Riverside, backfill join_url ---

async function fetchListMemberIds(listId) {
  const ids = [];
  let after;
  do {
    const page = await hubspotRequest(
      `/crm/v3/lists/${listId}/memberships/join-order${after ? `?after=${after}` : ''}`,
    );
    ids.push(...page.results.map((r) => r.recordId));
    after = page.paging?.next?.after;
  } while (after);
  return ids;
}

async function batchReadContacts(contactIds, propertyNames) {
  const contacts = [];
  for (let i = 0; i < contactIds.length; i += 100) {
    const chunk = contactIds.slice(i, i + 100);
    const page = await hubspotRequest('/crm/v3/objects/contacts/batch/read', {
      method: 'POST',
      body: { properties: propertyNames, inputs: chunk.map((id) => ({ id: String(id) })) },
    });
    contacts.push(...page.results);
  }
  return contacts;
}

async function findContactsAwaitingRegistration(config) {
  const memberIds = await fetchListMemberIds(config.hubspotListId);
  const contacts = await batchReadContacts(memberIds, [
    'email',
    'firstname',
    'lastname',
    'phone',
    config.properties.joinUrl,
  ]);
  return contacts.filter((contact) => !contact.properties[config.properties.joinUrl]);
}

async function registerInRiverside(config, contact) {
  const body = {
    email: contact.properties.email,
    first_name: contact.properties.firstname,
    last_name: contact.properties.lastname,
  };
  const registrant = await riversideRequest(`/api/v3/events/${config.riversideEventId}/registrants`, {
    method: 'POST',
    body,
  });
  await hubspotRequest(`/crm/v3/objects/contacts/${contact.id}`, {
    method: 'PATCH',
    body: {
      properties: {
        [config.properties.joinUrl]: registrant.join_url,
        [config.properties.webinarName]: config.eventStem,
      },
    },
  });
  return registrant;
}

async function backfillJoinUrls(config) {
  const pending = await findContactsAwaitingRegistration(config);
  console.log(`[${config.eventStem}] ${pending.length} contact(s) awaiting Riverside registration`);
  for (const contact of pending) {
    try {
      await registerInRiverside(config, contact);
      console.log(`  registered contact ${contact.id}`);
    } catch (err) {
      console.error(`  FAILED to register contact ${contact.id}: ${err.message}`);
    }
    await sleep(1100); // Riverside: 1 registration request/sec
  }
}

// --- Step 2: sync attendance data back from Riverside ---

const TOOL_ROOT = require('path').join(__dirname, '..');

function resolveToolPath(p) {
  const path = require('path');
  return path.isAbsolute(p) ? p : path.join(TOOL_ROOT, p);
}

function loadState(config) {
  try {
    const fs = require('fs');
    return JSON.parse(fs.readFileSync(resolveToolPath(config.stateFile), 'utf8'));
  } catch {
    return { lastSyncedAt: null };
  }
}

function saveState(config, state) {
  const fs = require('fs');
  const path = require('path');
  const stateFile = resolveToolPath(config.stateFile);
  fs.mkdirSync(path.dirname(stateFile), { recursive: true });
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
}

async function fetchUpdatedRegistrants(config, updatedAfter) {
  const items = [];
  let cursor;
  do {
    const page = await riversideRequest(`/api/v3/events/${config.riversideEventId}/registrants`, {
      query: { limit: 500, updated_after: updatedAfter, cursor },
    });
    items.push(...page.items);
    cursor = page.page?.next_cursor || null;
    if (cursor) await sleep(1100); // Riverside: 1 req/sec per unique URL
  } while (cursor);
  return items;
}

function parseDurationToSeconds(duration) {
  if (duration === null || duration === undefined) return null;
  if (typeof duration === 'number') return duration;
  const parts = String(duration).split(':').map(Number);
  if (parts.some(Number.isNaN)) return null;
  return parts.reduce((total, part) => total * 60 + part, 0);
}

async function findHubspotContactByEmail(email) {
  const body = {
    filterGroups: [{ filters: [{ propertyName: 'email', operator: 'EQ', value: email }] }],
    properties: ['email'],
    limit: 1,
  };
  const page = await hubspotRequest('/crm/v3/objects/contacts/search', { method: 'POST', body });
  return page.results[0] || null;
}

function buildAttendanceProperties(config, registrant) {
  // "hasn't joined yet" only means no-show once the event has actually ended - otherwise
  // every registrant looks like a no-show before the webinar has even started. Without a
  // configured eventEndsAt we can't tell, so we skip the no-show property entirely rather
  // than risk mislabeling someone who just hasn't had the chance to join yet.
  const eventHasEnded = config.eventEndsAt ? Date.now() >= new Date(config.eventEndsAt).getTime() : false;

  return {
    [config.properties.webinarName]: config.eventStem,
    // get-registrants returns join_url too - backfill it here for anyone who registered
    // in Riverside outside the HubSpot-list-driven path (e.g. registered directly).
    ...(registrant.join_url ? { [config.properties.joinUrl]: registrant.join_url } : {}),
    [config.properties.attended]: registrant.participated ? 'true' : 'false',
    ...(eventHasEnded ? { [config.properties.noShow]: registrant.participated === false ? 'true' : 'false' } : {}),
    [config.properties.attendanceDuration]: parseDurationToSeconds(registrant.duration),
    [config.properties.attendanceRate]: registrant.attendance_rate ?? null,
    [config.properties.registeredAt]: registrant.registered_at,
  };
}

async function syncAttendance(config) {
  const state = loadState(config);
  const registrants = await fetchUpdatedRegistrants(config, state.lastSyncedAt);
  console.log(`[${config.eventStem}] ${registrants.length} registrant(s) changed since ${state.lastSyncedAt || 'the beginning'}`);

  let maxSeen = state.lastSyncedAt;
  const created = [];

  for (const registrant of registrants) {
    const contact = await findHubspotContactByEmail(registrant.email);
    const properties = buildAttendanceProperties(config, registrant);

    if (contact) {
      await hubspotRequest(`/crm/v3/objects/contacts/${contact.id}`, {
        method: 'PATCH',
        body: { properties },
      });
    } else {
      // Registered in Riverside under an email HubSpot doesn't know yet (e.g. registered
      // directly on Riverside's own page instead of the HubSpot form) - create the contact
      // instead of silently dropping the registration/attendance data.
      const newContact = await hubspotRequest('/crm/v3/objects/contacts', {
        method: 'POST',
        body: {
          properties: {
            email: registrant.email,
            firstname: registrant.first_name,
            lastname: registrant.last_name,
            ...properties,
          },
        },
      });
      created.push(newContact.id);
    }
    if (!maxSeen || registrant.registered_at > maxSeen) maxSeen = registrant.registered_at;
  }

  if (created.length) {
    console.log(`[${config.eventStem}] ${created.length} new HubSpot contact(s) created for unmatched registrants:`, created);
  }

  saveState(config, { lastSyncedAt: maxSeen || new Date().toISOString() });
}

// --- Entry point ---

async function runForWebinar(config) {
  await backfillJoinUrls(config);
  await syncAttendance(config);
}

async function main() {
  const fs = require('fs');
  const configs = JSON.parse(fs.readFileSync(resolveToolPath('config/webinars.json'), 'utf8'));
  for (const config of configs) {
    if (config.archived) {
      console.log(`[${config.eventStem}] archived - skipped`);
      continue;
    }
    try {
      await runForWebinar(config);
    } catch (err) {
      console.error(`[${config.eventStem}] run failed:`, err);
      process.exitCode = 1;
    }
  }
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = { backfillJoinUrls, syncAttendance, runForWebinar };
