// Offline tests for drafted email copy: email-copy.js, createEmails() in
// new-webinar.js, and the add-webinar.js intake flags. HubSpot and Riverside are
// faked, so this needs no token and no network.
//
//   node tools/webinar-automation/scripts/test-email-copy.js
//
// The end-to-end checks run the scripts inside a temporary copy of this tool, so the
// real config/webinars.json is never written.
const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const TOOL_DIR = path.join(__dirname, '..');
const SANDBOX = fs.mkdtempSync(path.join(os.tmpdir(), 'webinar-copy-test-'));
for (const dir of ['scripts', 'config']) fs.cpSync(path.join(TOOL_DIR, dir), path.join(SANDBOX, dir), { recursive: true });
process.on('exit', () => fs.rmSync(SANDBOX, { recursive: true, force: true }));

global.setTimeout = (fn) => { fn(); return 0; };
global.clearTimeout = () => {};
process.env.HUBSPOT_PRIVATE_APP_TOKEN = 'test';

const ec = require('./email-copy');
const nw = require('./new-webinar');

let passed = 0;
const ok = (name) => { passed += 1; console.log(`  ok  ${name}`); };

const good = {
  registration: {
    subject: "you're in, here's what to expect",
    preheader: 'Your spot for Better Audio on a Budget is saved for Oct 22.',
    headline: '<h2>Better Audio on a Budget</h2>',
    body: '<p>Hey!</p><p>You\'re all set to join us for Better Audio on a Budget.</p>',
    cta: { text: 'Save to Google Calendar', url: '[[GOOGLE_CALENDAR_URL]]' },
    secondary: '<p><a href="[[OUTLOOK_CALENDAR_URL]]">Save to Outlook</a></p><p>Kendall<br>Head of Community, Riverside</p>',
  },
  firstReminder: {
    subject: 'quick reminder for tomorrow',
    preheader: 'Tomorrow at 12:00 PM EDT: better audio without new gear.',
    headline: '<h2>Better Audio on a Budget</h2>',
    body: '<p>Hey there!</p><p>Just a quick reminder that tomorrow we\'re going live.</p>',
    cta: { text: 'Join the studio live here', url: '[[JOIN_URL]]' },
    secondary: '<p>Hope to see you there!</p><p>Kendall<br>Head of Community, Riverside</p>',
  },
  secondReminder: {
    subject: "we're live in a few hours",
    preheader: 'We start at 12:00 PM EDT. Your join link is right inside.',
    headline: '',
    body: '<p>Hey!</p><p>Just a quick reminder: We\'re going live in just a few hours.</p>',
    cta: { text: 'Join the studio here', url: '[[JOIN_URL]]' },
  },
};

// ---- validateCopy ----
console.log('validateCopy');
{
  const r = ec.validateCopy(good);
  assert.deepStrictEqual(r.errors, []);
  ok('good copy has no errors');
}
const mutate = (fn) => { const c = JSON.parse(JSON.stringify(good)); fn(c); return ec.validateCopy(c).errors; };
assert.ok(mutate((c) => { c.registration.body += '<p>one \u2014 two</p>'; }).some((e) => /em or en dash/.test(e))); ok('em dash rejected');
assert.ok(mutate((c) => { c.registration.subject = 'a \u2013 b'; }).some((e) => /em or en dash/.test(e))); ok('en dash rejected');
assert.ok(mutate((c) => { delete c.secondReminder; }).some((e) => /Supply all three/.test(e))); ok('missing role rejected');
assert.ok(mutate((c) => { c.invite = { subject: 'x' }; }).some((e) => /unknown role "invite"/.test(e))); ok('unknown role rejected');
assert.ok(mutate((c) => { c.registration.body = '<p>[[STUDIO_LINK]]</p>'; }).some((e) => /unknown placeholder/.test(e))); ok('unknown placeholder rejected');
assert.ok(mutate((c) => { c.registration.body = '<p>{% if x %}y{% endif %}</p>'; }).some((e) => /HubL statement/.test(e))); ok('HubL statement rejected');
assert.ok(mutate((c) => { c.registration.body = '<p>Yay \u{1F389}</p>'; }).some((e) => /emoji/.test(e))); ok('emoji rejected');
assert.deepStrictEqual(mutate((c) => { c.registration.body = '<p>Riverside\u00ae and \u00a9 2026</p>'; }), []); ok('(R) and (C) allowed');
assert.ok(mutate((c) => { c.registration.body = '<p><img src=x onerror=alert(1)></p>'; }).some((e) => /event handler/.test(e))); ok('inline handler rejected');
assert.deepStrictEqual(mutate((c) => { c.registration.cta.url = 'https://example.com/?online=1&x=2'; }), []); ok('URL with "online=" not mistaken for a handler');
assert.ok(mutate((c) => { c.registration.cta = { text: 'x' }; }).some((e) => /cta/.test(e))); ok('incomplete cta rejected');
assert.ok(mutate((c) => { c.registration.cta.url = 'http://insecure'; }).some((e) => /cta.url/.test(e))); ok('non-https cta rejected');
assert.ok(mutate((c) => { c.registration.subject = '   '; }).some((e) => /subject: is empty/.test(e))); ok('blank subject rejected');
assert.deepStrictEqual(mutate((c) => { c.secondReminder.headline = ''; }), []); ok('empty headline allowed');
assert.ok(mutate((c) => { c.registration.extra = 'x'; }).some((e) => /unknown field/.test(e))); ok('unknown field rejected');
{
  const c = JSON.parse(JSON.stringify(good));
  c.firstReminder.preheader = 'short';
  c.firstReminder.body = `<p>${'word '.repeat(120)}</p>`;
  const r = ec.validateCopy(c);
  assert.deepStrictEqual(r.errors, []);
  assert.ok(r.warnings.some((w) => /preheader: 5 characters/.test(w)));
  assert.ok(r.warnings.some((w) => /firstReminder: body is \d+ words \(target under 100\)/.test(w)));
  ok('length rules warn, do not block');
}

// ---- fallback URL + join token ----
console.log('join link');
assert.ok(ec.isValidFallbackUrl('https://riverside.com/studio/kendall-community?audienceToken=abc-123'));
assert.ok(!ec.isValidFallbackUrl("https://riverside.com/studio/x'); alert(1)//"));
assert.ok(!ec.isValidFallbackUrl('https://evil.com/riverside.com/'));
assert.ok(!ec.isValidFallbackUrl('http://riverside.com/studio/x'));
ok('fallback URL allow-list');
const baseConfig = {
  eventStem: 'Better Audio on a Budget',
  riversideEventId: 'a'.repeat(24),
  hubspotFormId: 'form-guid',
  eventStartsAt: '2026-10-22T16:00:00.000Z',
  eventEndsAt: '2026-10-22T17:00:00.000Z',
  eventDateLabel: 'October 22, 2026',
  eventDescription: 'Better audio without buying new gear.',
  reminders: { first: { date: '2026-10-21', hour: 10, minute: 0 }, second: { date: '2026-10-22', hour: 10, minute: 0 } },
  properties: { joinUrl: 'riverside_join_url' },
};
assert.strictEqual(ec.joinToken(baseConfig), '{{ contact.riverside_join_url }}');
assert.strictEqual(
  ec.joinToken({ ...baseConfig, joinUrlFallback: 'https://riverside.com/studio/k?audienceToken=1' }),
  "{{ contact.riverside_join_url|default('https://riverside.com/studio/k?audienceToken=1', true) }}",
);
ok('join token with and without fallback');

// ---- Riverside description HTML ----
console.log('htmlToText');
assert.strictEqual(
  ec.htmlToText('<p class="paragraph--v_1_171_0--yFudM8k-"><span style="white-space: pre-wrap;">Learn how to use Marketing Brain</span></p>'),
  'Learn how to use Marketing Brain',
);
assert.strictEqual(ec.htmlToText('<p>One &amp; two</p><p>Three<br>four&nbsp;five</p>'), 'One & two\nThree\nfour five');
assert.strictEqual(ec.htmlToText(''), '');
assert.strictEqual(ec.htmlToText(null), '');
ok('editor HTML becomes plain text');
{
  const links = nw.calendarLinks({ ...{
    eventStem: 'X', eventStartsAt: '2026-10-22T08:00:00.000Z', eventEndsAt: '2026-10-22T09:00:00.000Z',
  }, eventDescription: '<p class="c"><span>Plain words</span></p>' });
  assert.ok(decodeURIComponent(links.google).includes('details=Plain words'));
  assert.ok(!decodeURIComponent(links.google).includes('<'));
  ok('calendar links carry no markup');
}

// ---- rendering ----
console.log('resolveCopy');
{
  const r = nw.resolveCopy({ ...baseConfig, emailCopy: good });
  assert.ok(r.registration.cta.url.startsWith('https://calendar.google.com/calendar/render?action=TEMPLATE&text='), 'gcal url raw in cta');
  assert.ok(!r.registration.cta.url.includes('&amp;'), 'cta url not html-escaped');
  assert.ok(r.registration.secondary.includes('href="https://outlook.live.com/calendar/0/deeplink/compose?subject='), 'outlook in html');
  assert.ok(r.registration.secondary.includes('&amp;body='), 'html href ampersands escaped');
  assert.strictEqual(r.firstReminder.cta.url, '{{ contact.riverside_join_url }}');
  assert.ok(!JSON.stringify(r).includes('[['), 'no placeholder left');
  ok('placeholders resolved, html vs field escaping');
}
{
  const r = nw.resolveCopy(baseConfig);
  assert.strictEqual(r.registration.cta.text, 'Join the Webinar');
  assert.strictEqual(r.registration.cta.url, '{{ contact.riverside_join_url }}');
  assert.ok(r.registration.subject.includes('Better Audio on a Budget'));
  ok('defaults keep the old join button');
}
{
  const fb = 'https://riverside.com/studio/k?audienceToken=1';
  const links = nw.calendarLinks({ ...baseConfig, joinUrlFallback: fb });
  assert.ok(links.google.includes(`&location=${encodeURIComponent(`Studio link: ${fb}`)}`));
  assert.ok(decodeURIComponent(links.google).includes(`Studio link: ${fb}`));
  assert.ok(!nw.calendarLinks(baseConfig).google.includes('location='));
  ok('calendar links carry the shared studio link only when set');
}

// ---- createEmails against a fake HubSpot ----
console.log('createEmails');
function fakeHubspot() {
  const emails = {};
  let nextId = 900;
  const log = [];
  global.fetch = async (url, { method = 'GET', body } = {}) => {
    const p = url.replace('https://api.hubapi.com', '');
    const b = body ? JSON.parse(body) : null;
    log.push(`${method} ${p}`);
    let out;
    if (method === 'POST' && p === '/marketing/v3/emails/clone') {
      const id = String(nextId++);
      emails[id] = { id, type: 'AUTOMATED_EMAIL', state: 'AUTOMATED_DRAFT', isPublished: false, updatedAt: `t${nextId}-0`, subject: '', widgets: {} };
      out = { id };
    } else if (method === 'PATCH') {
      const id = p.split('/').pop();
      const e = emails[id];
      e.subject = b.subject; e.widgets = b.content.widgets; e.updatedAt = `${id}-${log.length}`;
      out = e;
    } else if (method === 'GET') {
      out = emails[p.split('/').pop()];
    }
    return { ok: true, status: 200, text: async () => JSON.stringify(out) };
  };
  return { emails, log };
}

(async () => {
  // 1. first build with drafted copy
  let hs = fakeHubspot();
  let cfg = { ...baseConfig, emailCopy: good, created: {} };
  let persisted = 0;
  let res = await nw.createEmails(cfg, 'tpl', { persist: () => { persisted += 1; } });
  assert.strictEqual(Object.keys(res.ids).length, 3);
  assert.ok(res.copy.hash);
  assert.strictEqual(hs.emails[res.ids.registration].subject, good.registration.subject);
  assert.strictEqual(hs.emails[res.ids.registration].widgets.cta_button.body.text, 'Save to Google Calendar');
  assert.ok(persisted >= 6, 'persist after clone and after patch');
  ok('new emails are created with the drafted copy');

  // 2. rerun, same copy: no writes
  cfg.created = { emailIds: res.ids, copy: res.copy };
  hs.log.length = 0;
  res = await nw.createEmails(cfg, 'tpl');
  assert.ok(!hs.log.some((l) => l.startsWith('PATCH') || l.startsWith('POST')), 'no writes on unchanged copy');
  ok('unchanged copy: nothing written');

  // 3. new copy on untouched drafts: patched
  cfg.emailCopy = JSON.parse(JSON.stringify(good));
  cfg.emailCopy.firstReminder.subject = 'see you tomorrow';
  hs.log.length = 0;
  const before = res.copy.hash;
  res = await nw.createEmails(cfg, 'tpl');
  assert.strictEqual(hs.emails[res.ids.firstReminder].subject, 'see you tomorrow');
  assert.notStrictEqual(res.copy.hash, before);
  assert.strictEqual(hs.log.filter((l) => l.startsWith('PATCH')).length, 3);
  ok('changed copy updates untouched drafts');

  // 4. someone edits a draft in HubSpot, then new copy arrives: that one is protected
  cfg.created = { emailIds: res.ids, copy: res.copy };
  hs.emails[res.ids.registration].updatedAt = 'edited-by-hand';
  hs.emails[res.ids.registration].subject = 'hand edit';
  cfg.emailCopy = JSON.parse(JSON.stringify(cfg.emailCopy));
  cfg.emailCopy.secondReminder.subject = 'happening today';
  const hashBefore = res.copy.hash;
  res = await nw.createEmails(cfg, 'tpl');
  assert.strictEqual(hs.emails[res.ids.registration].subject, 'hand edit', 'hand edit kept');
  assert.strictEqual(hs.emails[res.ids.secondReminder].subject, 'happening today', 'others updated');
  assert.strictEqual(res.copy.hash, hashBefore, 'hash not advanced while a role is blocked');
  ok('hand-edited draft is not overwritten, hash held back');

  // 5. --force-copy overwrites it
  cfg.created = { emailIds: res.ids, copy: res.copy };
  res = await nw.createEmails(cfg, 'tpl', { forceCopy: true });
  assert.strictEqual(hs.emails[res.ids.registration].subject, good.registration.subject);
  assert.notStrictEqual(res.copy.hash, hashBefore);
  ok('--force-copy overwrites the hand edit');

  // 6. published email is never rewritten, even with force
  cfg.created = { emailIds: res.ids, copy: res.copy };
  hs.emails[res.ids.firstReminder].isPublished = true;
  cfg.emailCopy = JSON.parse(JSON.stringify(cfg.emailCopy));
  cfg.emailCopy.firstReminder.subject = 'do not land';
  res = await nw.createEmails(cfg, 'tpl', { forceCopy: true });
  assert.strictEqual(hs.emails[res.ids.firstReminder].subject, 'see you tomorrow');
  ok('published email untouched even with --force-copy');

  // 7. legacy webinar (built before copy updates, no baseline) + new copy: blocked without force
  hs = fakeHubspot();
  cfg = { ...baseConfig, created: {} };
  res = await nw.createEmails(cfg, 'tpl');
  const legacy = { emailIds: res.ids }; // simulate an entry from before this change: no copy record
  cfg = { ...baseConfig, emailCopy: good, created: legacy };
  hs.log.length = 0;
  res = await nw.createEmails(cfg, 'tpl');
  assert.ok(!hs.log.some((l) => l.startsWith('PATCH')), 'no patch without baseline');
  ok('legacy drafts without a baseline need --force-copy');

  // 8. default copy only, existing emails: never re-patched
  hs = fakeHubspot();
  cfg = { ...baseConfig, created: {} };
  res = await nw.createEmails(cfg, 'tpl');
  cfg.created = { emailIds: res.ids, copy: res.copy };
  cfg.eventDateLabel = 'October 23, 2026';
  hs.log.length = 0;
  await nw.createEmails(cfg, 'tpl');
  assert.ok(!hs.log.some((l) => l.startsWith('PATCH') || l.startsWith('POST')));
  ok('generic defaults never overwrite an existing email');

  // ---- add-webinar.js flags ----
  console.log('add-webinar.js');
  const aw = require('./add-webinar');
  assert.deepStrictEqual(aw.parseArgs(['abc', '--copy-file', 'x.json']).flags, { 'copy-file': 'x.json' });
  assert.throws(() => aw.parseArgs(['abc', '--copy-file']), /needs a value/);
  assert.throws(() => aw.parseArgs(['abc', '--bogus']), /Unknown flag/);
  assert.throws(() => aw.parseArgs(['abc', '--emit-env', '--copy-file']), /needs a value/);
  ok('flag parsing');
  aw.checkExpectedStart('2026-10-22T12:00:00-04:00', '2026-10-22T16:00:00.000Z');
  aw.checkExpectedStart('2026-10-22T16:00:30Z', '2026-10-22T16:00:00.000Z');
  assert.throws(() => aw.checkExpectedStart('2026-10-22T17:00:00Z', '2026-10-22T16:00:00.000Z'), /Start time mismatch/);
  assert.throws(() => aw.checkExpectedStart('next tuesday', '2026-10-22T16:00:00.000Z'), /not an ISO/);
  ok('start-time cross-check');

  // end to end through main() with a stubbed Riverside GraphQL
  const cfgPath = path.join(SANDBOX, 'config', 'webinars.json');
  const original = fs.readFileSync(cfgPath, 'utf8');
  fs.writeFileSync(path.join(SANDBOX, 'good.json'), JSON.stringify(good));
  const bad = JSON.parse(JSON.stringify(good)); bad.registration.body += '\u2014';
  fs.writeFileSync(path.join(SANDBOX, 'bad.json'), JSON.stringify(bad));
  const stub = path.join(SANDBOX, 'stub-fetch.js');
  fs.writeFileSync(stub, `global.fetch = async () => ({ json: async () => ({ data: { publicWebinarRegistrationData: { eventId: 'b'.repeat(24), title: process.env.STUB_TITLE || 'Better Audio on a Budget', description: '<p class="x"><span>Better audio without buying new gear.</span></p>', hostedBy: 'Kendall Breitman', startDate: '2026-10-22T16:00:00.000Z', endDate: '2026-10-22T17:00:00.000Z', language: 'en' } } }) });`);
  const run = (args, title) => execFileSync('node', ['-r', stub, 'scripts/add-webinar.js', 'b'.repeat(24), ...args], { cwd: SANDBOX, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], env: { ...process.env, STUB_TITLE: title || '' } });
  const fails = (args, re) => {
    try { run(args); assert.fail('expected failure'); } catch (e) { assert.match(String(e.stderr), re); }
    assert.strictEqual(fs.readFileSync(cfgPath, 'utf8'), original, 'config untouched on failure');
  };
  fails(['--copy-file', 'bad.json'], /em or en dash/);
  fails(['--join-fallback', 'https://evil.com/x'], /--join-fallback must be/);
  fails(['--expect-start', '2026-10-22T17:00:00Z'], /Start time mismatch/);
  ok('bad copy, bad link, wrong time: fail with config untouched');
  const out = run(['--copy-file', 'good.json', '--join-fallback', 'https://riverside.com/studio/k?audienceToken=1', '--expect-start', '2026-10-22T12:00:00-04:00']);
  assert.match(out, /start time matches/);
  const entry = JSON.parse(fs.readFileSync(cfgPath, 'utf8')).find((c) => c.riversideEventId === 'b'.repeat(24));
  assert.deepStrictEqual(entry.emailCopy, good);
  assert.strictEqual(entry.joinUrlFallback, 'https://riverside.com/studio/k?audienceToken=1');
  ok('valid inputs land on the config entry');
  const plain = run([]);
  assert.match(plain, /Updated config entry/);
  const again = JSON.parse(fs.readFileSync(cfgPath, 'utf8')).find((c) => c.riversideEventId === 'b'.repeat(24));
  assert.deepStrictEqual(again.emailCopy, good, 're-intake without --copy-file keeps stored copy');
  ok('re-intake without flags keeps stored copy and link');
  assert.strictEqual(again.eventDescription, 'Better audio without buying new gear.');
  ok('intake stores the description as plain text');

  // title drift: follows a rename while nothing is built, refuses once something is
  const renamed = run([], 'Better Audio, Renamed');
  assert.match(renamed, /title changed on Riverside/);
  const followed = JSON.parse(fs.readFileSync(cfgPath, 'utf8')).find((c) => c.riversideEventId === 'b'.repeat(24));
  assert.strictEqual(followed.eventStem, 'Better Audio, Renamed');
  ok('unbuilt entry follows a Riverside rename');
  const builtCfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  builtCfg.find((c) => c.riversideEventId === 'b'.repeat(24)).created = { emailIds: { registration: '1' } };
  fs.writeFileSync(cfgPath, JSON.stringify(builtCfg, null, 2));
  const beforeDrift = fs.readFileSync(cfgPath, 'utf8');
  try { run([], 'Another Title'); assert.fail('expected failure'); } catch (e) { assert.match(String(e.stderr), /Title mismatch/); }
  assert.strictEqual(fs.readFileSync(cfgPath, 'utf8'), beforeDrift, 'config untouched on title mismatch');
  ok('built entry refuses a rename, config untouched');
  fs.writeFileSync(cfgPath, original);

  // new-webinar dry run prints the copy review
  entry.hubspotFormId = 'form-guid';
  const cfgs = JSON.parse(original); cfgs.push(entry); fs.writeFileSync(cfgPath, JSON.stringify(cfgs));
  const dry = execFileSync('node', ['scripts/new-webinar.js', 'b'.repeat(24)], { cwd: SANDBOX, encoding: 'utf8', env: { ...process.env, HUBSPOT_PRIVATE_APP_TOKEN: '' } });
  assert.match(dry, /\[registration\] button: "Save to Google Calendar" -> https:\/\/calendar.google.com/);
  assert.match(dry, /falling back to the shared studio link/);
  assert.match(dry, /Dry-run only/);
  ok('dry run shows the copy review without a token');
  const badEntry = { ...entry, emailCopy: bad };
  fs.writeFileSync(cfgPath, JSON.stringify([...JSON.parse(original), badEntry]));
  assert.throws(() => execFileSync('node', ['scripts/new-webinar.js', 'b'.repeat(24)], { cwd: SANDBOX, encoding: 'utf8', stdio: 'pipe' }), /invalid/);
  ok('orchestrator refuses invalid stored copy');
  const todoEntry = { ...entry, hubspotFormId: 'TODO - clone/create the registration form, paste its GUID' };
  fs.writeFileSync(cfgPath, JSON.stringify([...JSON.parse(original), todoEntry]));
  assert.throws(() => execFileSync('node', ['scripts/new-webinar.js', 'b'.repeat(24), '--create'], { cwd: SANDBOX, encoding: 'utf8', stdio: 'pipe', env: { ...process.env, HUBSPOT_PRIVATE_APP_TOKEN: 'unused' } }), /ensure-hubspot-intake/);
  ok('orchestrator refuses to build on a placeholder form id');
  fs.writeFileSync(cfgPath, original);

  console.log(`\n${passed} checks passed`);
})().catch((e) => { console.error(e); process.exit(1); });
