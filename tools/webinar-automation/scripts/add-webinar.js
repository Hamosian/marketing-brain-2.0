#!/usr/bin/env node
// Webinar intake - turn a Riverside registration link (or bare event ID) into a
// ready-to-run config entry, using Riverside's public registration metadata.
//
// Usage:
//   node scripts/add-webinar.js "https://riverside.com/webinar/registration/<base64>"
//   node scripts/add-webinar.js 6a69df3222b8ed2814e4d843
//   node scripts/add-webinar.js <link-or-id> --expect-start 2026-10-22T16:00:00Z \
//        --copy-file copy.json --join-fallback https://riverside.com/studio/...
//
// Optional flags:
//   --expect-start <ISO>    the start time the requestor gave. If Riverside disagrees,
//                           intake stops: one of them is wrong and a person decides which.
//   --copy-file <path>      approved email copy (the `emailCopy` object, keyed by role).
//                           Validated here, stored on the entry, applied by new-webinar.js.
//   --join-fallback <url>   shared studio audience link, used when a registrant has no
//                           personal join link yet.
//
// Where the data comes from: the public registration page loads its event details
// through an unauthenticated GraphQL query (publicWebinarRegistrationData) - title,
// host, description, exact start/end times. Verified live 2026-07-29; no API key
// and no guest token required.
//
// What it writes: creates (or updates, matched by riversideEventId) an entry in
// config/webinars.json with schedule fields and derived reminder times. It never
// touches HubSpot or Riverside state - review the entry, fill hubspotFormId and
// hubspotListId, then run new-webinar.js.

const fs = require('fs');
const path = require('path');
const { validateCopy, isValidFallbackUrl, htmlToText } = require('./email-copy');

const CONFIG_PATH = path.join(__dirname, '..', 'config', 'webinars.json');
// HubSpot Flows v4 time_of_day values are interpreted in the portal's default
// timezone; reminder clock times below are computed in this zone to match.
const PORTAL_TIMEZONE = 'America/New_York';

function parseInput(raw) {
  if (!raw) throw new Error('Usage: node scripts/add-webinar.js <registration URL or event ID>');
  const idMatch = raw.trim().match(/^[0-9a-f]{24}$/i);
  if (idMatch) return { eventId: raw.trim(), slug: null };
  const urlMatch = raw.match(/\/webinar\/registration\/([A-Za-z0-9_\-=%]+)/);
  if (!urlMatch) throw new Error('Input is neither a 24-hex event ID nor a riverside.com/webinar/registration/... URL');
  const b64 = decodeURIComponent(urlMatch[1]).replace(/-/g, '+').replace(/_/g, '/');
  const decoded = JSON.parse(Buffer.from(b64, 'base64').toString('utf8'));
  if (!decoded.eventId) throw new Error(`Decoded registration payload has no eventId: ${JSON.stringify(decoded)}`);
  return { eventId: decoded.eventId, slug: decoded.slug || null };
}

async function fetchEventMeta(eventId) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  let res;
  try {
    res = await fetch('https://riverside.com/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `query { publicWebinarRegistrationData(eventId: "${eventId}") { eventId title description hostedBy startDate endDate language } }`,
      }),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
  const json = await res.json();
  const meta = json?.data?.publicWebinarRegistrationData;
  if (!meta || !meta.title || !meta.startDate) {
    throw new Error(`Could not resolve event ${eventId} from Riverside's public registration data: ${JSON.stringify(json).slice(0, 300)}`);
  }
  return meta;
}

function partsInTz(iso, timeZone) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone, year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false,
  }).formatToParts(new Date(iso));
  const get = (type) => parts.find((p) => p.type === type).value;
  return { date: `${get('year')}-${get('month')}-${get('day')}`, hour: Number(get('hour')) % 24, minute: Number(get('minute')) };
}

function shiftDate(yyyyMmDd, days) {
  const d = new Date(`${yyyyMmDd}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

function deriveReminders(startIso) {
  const eventDay = partsInTz(startIso, PORTAL_TIMEZONE);
  const twoHoursBefore = partsInTz(new Date(new Date(startIso).getTime() - 2 * 3600 * 1000).toISOString(), PORTAL_TIMEZONE);
  return {
    first: { date: shiftDate(eventDay.date, -1), hour: 10, minute: 0 },
    second: { date: twoHoursBefore.date, hour: twoHoursBefore.hour, minute: twoHoursBefore.minute },
  };
}

function dateLabel(startIso) {
  return new Intl.DateTimeFormat('en-US', { timeZone: PORTAL_TIMEZONE, month: 'long', day: 'numeric', year: 'numeric' }).format(new Date(startIso));
}

function slugify(title) {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'webinar';
}

const VALUE_FLAGS = ['--emit-env', '--expect-start', '--copy-file', '--join-fallback'];

function parseArgs(argv) {
  const flags = {};
  const positional = [];
  for (let i = 0; i < argv.length; i += 1) {
    if (VALUE_FLAGS.includes(argv[i])) {
      const value = argv[i + 1];
      if (value === undefined || value.startsWith('--')) throw new Error(`${argv[i]} needs a value`);
      flags[argv[i].slice(2)] = value;
      i += 1;
    } else if (argv[i].startsWith('--')) {
      throw new Error(`Unknown flag ${argv[i]}`);
    } else {
      positional.push(argv[i]);
    }
  }
  return { flags, input: positional[0] };
}

// Compared to the minute: the requestor's time and Riverside's must name the same moment.
function checkExpectedStart(expected, actual) {
  const e = Date.parse(expected);
  if (Number.isNaN(e)) throw new Error(`--expect-start "${expected}" is not an ISO date-time (e.g. 2026-10-22T16:00:00Z)`);
  if (Math.floor(e / 60000) !== Math.floor(Date.parse(actual) / 60000)) {
    throw new Error(`Start time mismatch: the requestor gave ${new Date(e).toISOString()}, Riverside has ${actual}. Nothing was written. Confirm the right time with the requestor, fix the Riverside event if it is the one that is wrong, then re-run.`);
  }
}

function loadCopy(file) {
  let copy;
  try {
    copy = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (err) {
    throw new Error(`--copy-file ${file}: not readable JSON (${err.message})`);
  }
  const { errors, warnings } = validateCopy(copy);
  for (const w of warnings) console.warn(`  copy warning: ${w}`);
  if (errors.length) throw new Error(`--copy-file ${file} is invalid. Nothing was written:\n  - ${errors.join('\n  - ')}`);
  return copy;
}

async function main() {
  const { flags, input } = parseArgs(process.argv.slice(2));
  const emitPath = flags['emit-env'] || null;
  // Validate every optional input before touching the network or the config, so a bad
  // copy file or link fails the run with the config untouched.
  const copy = flags['copy-file'] ? loadCopy(flags['copy-file']) : null;
  if (flags['join-fallback'] && !isValidFallbackUrl(flags['join-fallback'])) {
    throw new Error(`--join-fallback must be a plain https://riverside.com/... or https://riverside.fm/... link, got "${flags['join-fallback']}"`);
  }
  const { eventId, slug } = parseInput(input);
  console.log(`Resolving event ${eventId}${slug ? ` (studio: ${slug})` : ''}...`);
  const meta = await fetchEventMeta(eventId);
  console.log(`  title:  ${meta.title}`);
  console.log(`  host:   ${meta.hostedBy}`);
  console.log(`  starts: ${meta.startDate} | ends: ${meta.endDate}`);
  if (flags['expect-start']) {
    checkExpectedStart(flags['expect-start'], meta.startDate);
    console.log('  start time matches what the requestor gave');
  }

  const reminders = deriveReminders(meta.startDate);
  if (new Date(meta.startDate) < new Date()) {
    console.warn('  WARNING: event start is in the past - reminder times will need manual attention.');
  }

  const configs = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  let entry = configs.find((c) => c.riversideEventId === eventId);
  const isNew = !entry;
  if (isNew) {
    entry = {
      eventStem: meta.title,
      riversideEventId: eventId,
      hubspotFormId: 'TODO - clone/create the registration form, paste its GUID',
      hubspotListId: 'TODO - the list this webinar\'s form submissions land in',
      properties: {
        webinarName: 'webinar_name',
        joinUrl: 'riverside_join_url',
        attended: 'webinar_attended',
        noShow: 'webinar_no_show',
        attendanceDuration: 'webinar_attendance_duration',
        attendanceRate: 'webinar_attendance_rate',
        registeredAt: 'webinar_registered_at',
      },
      stateFile: `state/${slugify(meta.title)}.json`,
    };
    configs.push(entry);
  } else if (entry.eventStem !== meta.title) {
    // The stem names every HubSpot record, and the reminder flow enrolls on
    // webinar_name equal to it, so it may only follow a rename while nothing is built.
    const built = (entry.created && Object.keys(entry.created).length > 0)
      || (entry.hubspotFormId && !String(entry.hubspotFormId).startsWith('TODO'));
    if (built) {
      throw new Error(`Title mismatch: Riverside now calls this event "${meta.title}", but it is already built in HubSpot as "${entry.eventStem}". Nothing was written. Set the title back in the event's registration form in Studio, or treat the new title as a new launch.`);
    }
    console.log(`  title changed on Riverside: "${entry.eventStem}" -> "${meta.title}". Nothing is built yet, so the entry follows it.`);
    entry.eventStem = meta.title;
    entry.stateFile = `state/${slugify(meta.title)}.json`;
  }
  entry.eventStartsAt = meta.startDate;
  entry.eventEndsAt = meta.endDate;
  entry.eventDateLabel = dateLabel(meta.startDate);
  // Riverside sends editor HTML; calendar entries need the words, not the markup.
  entry.eventDescription = htmlToText(meta.description) || `Join us live for ${meta.title}, hosted by ${meta.hostedBy}.`;
  entry.hostedBy = meta.hostedBy;
  entry.reminders = reminders;
  if (copy) {
    entry.emailCopy = copy;
    console.log('  email copy: drafted copy stored for all 3 emails');
  }
  if (flags['join-fallback']) {
    entry.joinUrlFallback = flags['join-fallback'];
    console.log('  join link fallback: shared studio link stored');
  }

  // The description feeds attendee-facing assets (calendar links, email copy), so
  // placeholder text on the Riverside event should be fixed there, then re-run intake.
  if (/^\s*(bla+\s*)+$|^\s*(tbd|test|todo|placeholder|lorem\b.*)\s*$/i.test(entry.eventDescription) || entry.eventDescription.trim().length < 10) {
    console.warn(`  WARNING: event description looks like placeholder text (${JSON.stringify(String(entry.eventDescription))}). It appears in calendar links and attendee-facing copy - update it on the Riverside event, then re-run this intake.`);
  }

  fs.writeFileSync(CONFIG_PATH, JSON.stringify(configs, null, 2));
  console.log(`\n${isNew ? 'Created' : 'Updated'} config entry "${entry.eventStem}" in config/webinars.json`);
  console.log(`  reminders: day-before ${reminders.first.date} ${String(reminders.first.hour).padStart(2, '0')}:${String(reminders.first.minute).padStart(2, '0')}, day-of ${reminders.second.date} ${String(reminders.second.hour).padStart(2, '0')}:${String(reminders.second.minute).padStart(2, '0')} (${PORTAL_TIMEZONE})`);

  const todos = [];
  if (String(entry.hubspotFormId).startsWith('TODO')) todos.push('hubspotFormId');
  if (String(entry.hubspotListId).startsWith('TODO')) todos.push('hubspotListId');
  if (todos.length) console.log(`  still needed before --create: ${todos.join(', ')}`);
  console.log(`\nNext: node scripts/new-webinar.js "${entry.eventStem}"   (dry-run, then add --create)`);

  // A registration URL hides the event id inside a base64 payload, so a caller that
  // started from a link has no way to name the entry for the next step. Hand it back
  // as a file of KEY=value lines (shape of $GITHUB_OUTPUT). Only the hex id is emitted:
  // the title is attacker-adjacent free text and would need multiline escaping.
  if (emitPath) {
    fs.appendFileSync(emitPath, `WEBINAR_EVENT_ID=${eventId}\n`);
    console.log(`  emitted WEBINAR_EVENT_ID to ${emitPath}`);
  }
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err.message || err);
    process.exit(1);
  });
}

module.exports = { parseInput, parseArgs, checkExpectedStart, fetchEventMeta, deriveReminders };
