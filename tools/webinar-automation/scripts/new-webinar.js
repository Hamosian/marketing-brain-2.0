#!/usr/bin/env node
// Webinar Orchestrator - creates the full HubSpot side of a webinar from config.
//
// Assembles the recipes proven live on 2026-07-29 (see webinar-hubspot-agent-scope.md):
//   1. ensureTemplate - create the branded CODED email template via Design Manager API
//                        (coded templates carry layout in their HTML; sidesteps the
//                        flexAreas API limitation entirely)
//   2. createEmails - clone an existing AUTOMATED_EMAIL (the only way to get that type),
//                        re-point each clone to the coded template, fill in copy.
//                        Copy is the config's `emailCopy` (drafted by the
//                        riverside-event-copy skill, approved by a human) or generic
//                        defaults. A re-run with changed copy updates emails that are
//                        still drafts and that nobody has edited in HubSpot since.
//   3. publishEmails - only with --publish-emails (explicit human gate)
//   4. createFlow - v4 flow: form-submission trigger → registration email →
//                        absolute-date delay → first reminder → delay → second reminder.
//                        Built on --create, while the emails are still drafts.
//                        Created DISABLED, always. Enabling stays a human step in the UI,
//                        after the emails are published.
//   5. createLists - 3 dynamic lists (Registered / Attended / No-show)
//   6. calendarLinks - Google/Outlook/Office365 add-to-calendar URLs, printed for email copy
//
// Usage:
//   node scripts/new-webinar.js "<eventStem>"                      # dry-run: print the plan
//   node scripts/new-webinar.js "<eventStem>" --create             # create template, draft emails, disabled flow, lists
//   node scripts/new-webinar.js "<eventStem>" --create --publish-emails
//   node scripts/new-webinar.js "<eventStem>" --create --force-copy   # overwrite hand edits on drafts
//
// Hard rules baked in: never enables a flow; never publishes without --publish-emails;
// PATCHes to emails always send the FULL widgets object (partial = silent wipe of the rest);
// never rewrites a published email, and never overwrites a draft someone edited in HubSpot
// unless --force-copy says so.
//
// Known API gotchas this script works around (all confirmed live):
//   - POST /marketing/v3/emails ignores "type": AUTOMATED_EMAIL only obtainable via clone.
//   - Template stored `path` is rewritten from the LABEL (spaces kept, .html stripped) -
//     always read back the real path after creation.
//   - v4 flow updates are full-body PUT with optimistic locking on revisionId.

require('./load-env');
const fs = require('fs');
const path = require('path');
const { ROLES, validateCopy, joinToken, renderRole, hashCopy, wordCount, htmlToText } = require('./email-copy');

const HUBSPOT_API_BASE = 'https://api.hubapi.com';
const CONFIG_PATH = path.join(__dirname, '..', 'config', 'webinars.json');

const SEED_AUTOMATED_EMAIL_ID = '218280960344'; // our published "Webinar 2026 agent" master - cloning preserves AUTOMATED type
const TEMPLATE_LABEL = 'Riverside Webinar Agent Template v1';
const TEMPLATE_FOLDER = 'agent-templates';

// Brand constants lifted from the real "Webinar 2026 agent" template source
const BRAND = {
  logo: 'https://9154210.fs1.hubspotusercontent-na1.net/hubfs/9154210/Main%20Logo-2.png',
  appStore: 'https://9154210.fs1.hubspotusercontent-na1.net/hubfs/9154210/appstore-1.png',
  googlePlay: 'https://9154210.fs1.hubspotusercontent-na1.net/hubfs/9154210/google%20play-1.png',
  purple: '#9671FF',
  background: '#fafafa',
};

function assertEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required env var: ${name} (set it in tools/webinar-automation/.env)`);
  return value;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

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

// --- Step 1: branded coded template (created once, reused for every webinar) ---

function templateSource() {
  return `<!--
  templateType: email
  isAvailableForNewContent: true
-->
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{{ content.body.subject }}</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  {{ email_standard_header_includes }}
</head>
<body style="margin:0; padding:0; background-color:${BRAND.background};">
  <div style="display:none; max-height:0; overflow:hidden;">{% module "preheader" path="@hubspot/rich_text", html="" %}</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:${BRAND.background};">
    <tr><td align="center" style="padding: 24px 12px;">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px; width:100%; background-color:#ffffff; border-radius:8px;">
        <tr><td align="center" style="padding: 30px;">
          <a href="https://riverside.com"><img src="${BRAND.logo}" width="160" alt="Riverside" style="display:block; border:0;"></a>
        </td></tr>
        <tr><td style="padding: 0 40px; font-family:Helvetica,Arial,sans-serif; color:#000000;">
          {% module "headline" path="@hubspot/rich_text", html="<h2 style='text-align:center; font-size:28px; line-height:125%;'>Headline</h2>" %}
        </td></tr>
        <tr><td style="padding: 10px 40px; font-family:Helvetica,Arial,sans-serif; font-size:15px; line-height:150%; color:#000000;">
          {% module "body_content" path="@hubspot/rich_text", html="<p>Body</p>" %}
        </td></tr>
        <tr><td align="center" style="padding: 20px 40px 10px 40px;">
          {% module "cta_button" path="@hubspot/button_email", text="Join the Webinar", destination="https://riverside.com", background_color="${BRAND.purple}", font_color="#ffffff", corner_radius=5 %}
        </td></tr>
        <tr><td style="padding: 10px 40px 30px 40px; font-family:Helvetica,Arial,sans-serif; font-size:14px; line-height:150%; color:#000000;">
          {% module "body_secondary" path="@hubspot/rich_text", html="" %}
        </td></tr>
      </table>
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px; width:100%;">
        <tr><td align="center" style="padding: 18px 12px 6px 12px;">
          <a href="https://apps.apple.com/us/app/riverside-fm/id1554443872"><img src="${BRAND.appStore}" width="110" alt="App Store" style="border:0; margin:0 6px;"></a>
          <a href="https://play.google.com/store/apps/details?id=riverside.fm"><img src="${BRAND.googlePlay}" width="110" alt="Google Play" style="border:0; margin:0 6px;"></a>
        </td></tr>
        <tr><td align="center" style="padding: 6px 20px 24px 20px; font-family:Helvetica,Arial,sans-serif; font-size:12px; color:#000000;">
          {% module "footer" path="@hubspot/email_footer" %}
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`;
}

async function ensureTemplate(config) {
  if (config.created?.templatePath) {
    console.log(`[template] reusing ${config.created.templatePath}`);
    return config.created.templatePath;
  }
  // the template is global (one per design, shared by every webinar): scan the portal
  // by label before creating, so a second webinar's config entry doesn't re-POST the
  // same path and collide with the first webinar's template
  // (HubSpot may store the label with the .html extension appended - match both)
  for (let offset = 0; ; offset += 200) {
    const page = await hubspotRequest(`/content/api/v2/templates?limit=200&offset=${offset}`);
    const hit = (page.objects || []).find((t) => (t.label === TEMPLATE_LABEL || t.label === `${TEMPLATE_LABEL}.html`) && !t.deleted);
    if (hit) {
      console.log(`[template] found existing id=${hit.id} path="${hit.path}"`);
      return hit.path;
    }
    if (!page.objects || page.objects.length < 200) break;
  }
  const created = await hubspotRequest('/content/api/v2/templates', {
    method: 'POST',
    body: {
      path: `${TEMPLATE_FOLDER}/${TEMPLATE_LABEL}.html`,
      filename: `${TEMPLATE_LABEL}.html`,
      folder: TEMPLATE_FOLDER,
      source: templateSource(),
      template_type: 2,
      category_id: 2,
      is_available_for_new_content: true,
      label: TEMPLATE_LABEL,
    },
  });
  // HubSpot rewrites the stored path from the label - re-read the real one
  const fresh = await hubspotRequest(`/content/api/v2/templates/${created.id}`);
  console.log(`[template] created id=${created.id} path="${fresh.path}"`);
  return fresh.path;
}

// --- Step 2: the three emails (clone AUTOMATED seed → re-point → fill copy) ---

function defaultCopy(config) {
  const stem = config.eventStem;
  const dateLabel = config.eventDateLabel || config.eventStartsAt || 'the scheduled date';
  // No cta here: renderRole() defaults every email's button to "Join the Webinar" -> [[JOIN_URL]].
  const replay = "Can't make it live? No worries - we'll send the replay to everyone who registered.";
  return {
    registration: {
      subject: `You're registered for ${stem}!`,
      preheader: `You're in! Here's your personal link to join ${stem}.`,
      headline: `<h2 style="text-align:center; font-size:28px; line-height:125%;">You are registered for<br>${stem}</h2>`,
      body: `<p>Hi {{ contact.firstname }},</p><p>Thanks for registering for <strong>${stem}</strong> on ${dateLabel}. Use the button below to join live - your link is personal to you.</p>`,
      secondary: `<p><strong>${replay}</strong></p><p>See you soon!</p>`,
    },
    firstReminder: {
      subject: `It's happening tomorrow: ${stem}`,
      preheader: `${stem} is tomorrow - your personal join link is inside.`,
      headline: `<h2 style="text-align:center; font-size:28px; line-height:125%;">${stem} is<br>happening tomorrow</h2>`,
      body: `<p>Hi {{ contact.firstname }},</p><p>Just a reminder - <strong>${stem}</strong> goes live tomorrow, ${dateLabel}. Save your seat by keeping this email handy.</p>`,
      secondary: `<p><strong>${replay}</strong></p>`,
    },
    secondReminder: {
      subject: `We're live soon! Join ${stem}`,
      preheader: `${stem} starts soon - join with your personal link.`,
      headline: `<h2 style="text-align:center; font-size:28px; line-height:125%;">Today's the day - <br>${stem} starts soon</h2>`,
      body: `<p>Hi {{ contact.firstname }},</p><p><strong>${stem}</strong> is starting soon. Click below to join the Riverside Studio.</p>`,
      secondary: `<p><strong>${replay}</strong></p>`,
    },
  };
}

// Defaults are replaced role by role by the config's `emailCopy`, then placeholders
// ([[JOIN_URL]], calendar links) are resolved against this webinar's schedule.
function resolveCopy(config) {
  const defaults = defaultCopy(config);
  const ctx = { join: joinToken(config), links: calendarLinks(config) };
  const rendered = {};
  for (const role of ROLES) {
    rendered[role] = renderRole({ ...defaults[role], ...(config.emailCopy?.[role] || {}) }, ctx);
  }
  return rendered;
}

function emailPatch(c, templatePath) {
  return {
    subject: c.subject,
    content: {
      templatePath,
      // full replacement by design: the clone's old dnd widgets are dropped,
      // leaving exactly the coded template's named slots
      widgets: {
        preheader: { body: { html: c.preheader } },
        headline: { body: { html: c.headline } },
        body_content: { body: { html: c.body } },
        cta_button: { body: { text: c.cta.text, destination: c.cta.url, url: c.cta.url } },
        body_secondary: { body: { html: c.secondary } },
      },
    },
  };
}

// Returns { ids, copy } where copy = { hash, updatedAt: {role: iso} } records which copy
// each email carries and when this script last wrote it. `persist` is called after every
// role so a run that dies halfway does not lose an email id or its baseline.
async function createEmails(config, templatePath, { forceCopy = false, persist = () => {} } = {}) {
  const copy = resolveCopy(config);
  const hash = hashCopy(copy);
  const names = {
    registration: `${config.eventStem} - registration`,
    firstReminder: `${config.eventStem} - first reminder`,
    secondReminder: `${config.eventStem} - second reminder`,
  };
  const ids = { ...(config.created?.emailIds || {}) };
  const prior = config.created?.copy || {};
  const applied = { hash: prior.hash || null, updatedAt: { ...(prior.updatedAt || {}) } };
  // Only drafted copy triggers updates. Generic defaults are never pushed over an
  // existing email, which keeps webinars built before this feature untouched.
  const wantsUpdate = Boolean(config.emailCopy) && prior.hash !== hash;
  let blocked = 0;

  for (const role of ROLES) {
    const c = copy[role];
    if (ids[role]) {
      if (!wantsUpdate) {
        console.log(`[email:${role}] reusing ${ids[role]}`);
        continue;
      }
      const current = await hubspotRequest(`/marketing/v3/emails/${ids[role]}`);
      if (current.isPublished) {
        console.warn(`[email:${role}] ${ids[role]} is published - copy NOT updated. A published email is changed by a person in HubSpot.`);
        blocked += 1;
        continue;
      }
      const baseline = applied.updatedAt[role];
      if (!forceCopy && (!baseline || current.updatedAt !== baseline)) {
        const why = baseline
          ? 'was edited in HubSpot after this script last wrote it'
          : 'has no recorded copy baseline (built before copy updates existed)';
        console.warn(`[email:${role}] ${ids[role]} ${why} - copy NOT updated. Re-run with --force-copy to overwrite.`);
        blocked += 1;
        continue;
      }
      await hubspotRequest(`/marketing/v3/emails/${ids[role]}`, { method: 'PATCH', body: emailPatch(c, templatePath) });
      const fresh = await hubspotRequest(`/marketing/v3/emails/${ids[role]}`);
      // A warning, not an abort: HubSpot may normalize the stored subject, and a cosmetic
      // difference must not stop a launch. The QA step reads every subject anyway.
      if (fresh.subject !== c.subject) console.warn(`[email:${role}] ${ids[role]} subject reads back as "${fresh.subject}" - check it in HubSpot`);
      applied.updatedAt[role] = fresh.updatedAt;
      console.log(`[email:${role}] copy updated on draft ${ids[role]}`);
      persist({ ids, copy: applied });
      continue;
    }
    const clone = await hubspotRequest('/marketing/v3/emails/clone', {
      method: 'POST',
      body: { id: config.seedEmailId || SEED_AUTOMATED_EMAIL_ID, cloneName: names[role] },
    });
    ids[role] = String(clone.id);
    persist({ ids, copy: applied });
    await hubspotRequest(`/marketing/v3/emails/${clone.id}`, { method: 'PATCH', body: emailPatch(c, templatePath) });
    const fresh = await hubspotRequest(`/marketing/v3/emails/${clone.id}`);
    if (fresh.type !== 'AUTOMATED_EMAIL') throw new Error(`email ${clone.id} is ${fresh.type}, expected AUTOMATED_EMAIL - aborting`);
    applied.updatedAt[role] = fresh.updatedAt;
    console.log(`[email:${role}] created ${clone.id} (${fresh.state})`);
    persist({ ids, copy: applied });
  }
  // The hash advances only when every email carries this copy, so a role that was
  // blocked is tried again on the next run instead of being marked done.
  if (blocked === 0) applied.hash = hash;
  else console.warn(`[email] ${blocked} email(s) kept their previous copy - see the warnings above.`);
  return { ids, copy: applied };
}

async function publishEmails(emailIds) {
  for (const [role, id] of Object.entries(emailIds)) {
    const email = await hubspotRequest(`/marketing/v3/emails/${id}`);
    if (email.isPublished) {
      console.log(`[publish:${role}] ${id} already published`);
      continue;
    }
    await hubspotRequest(`/marketing/v3/emails/${id}/publish`, { method: 'POST', body: {} });
    console.log(`[publish:${role}] ${id} published`);
  }
}

// --- Step 4: the v4 flow (disabled; enabling stays human) ---

function epochMidnightUTC(isoDate) {
  return String(Date.parse(`${isoDate}T00:00:00Z`));
}

// The flow is built while the emails are still drafts. HubSpot accepts send-email actions
// that point at unpublished emails (verified 2026-10-06, flow 1897261642); the emails
// still have to be published before a person turns the flow on.
async function createFlow(config, emailIds) {
  if (config.created?.flowId) {
    console.log(`[flow] reusing ${config.created.flowId}`);
    return config.created.flowId;
  }
  const r1 = config.reminders.first; // {date: 'YYYY-MM-DD', hour, minute}
  const r2 = config.reminders.second;
  const flow = await hubspotRequest('/automation/v4/flows', {
    method: 'POST',
    body: {
      name: `${config.eventStem} - webinar sequence`,
      type: 'CONTACT_FLOW',
      flowType: 'WORKFLOW',
      objectTypeId: '0-1',
      isEnabled: false,
      startActionId: '1',
      actions: [
        { actionId: '1', actionTypeId: '0-4', actionTypeVersion: 0, type: 'SINGLE_CONNECTION', fields: { content_id: emailIds.registration }, connection: { edgeType: 'STANDARD', nextActionId: '2' } },
        { actionId: '2', actionTypeId: '0-35', actionTypeVersion: 0, type: 'SINGLE_CONNECTION', fields: { date: { staticValue: epochMidnightUTC(r1.date), type: 'STATIC_VALUE' }, delta: '0', time_unit: 'DAYS', time_of_day: { hour: r1.hour, minute: r1.minute } }, connection: { edgeType: 'STANDARD', nextActionId: '3' } },
        { actionId: '3', actionTypeId: '0-4', actionTypeVersion: 0, type: 'SINGLE_CONNECTION', fields: { content_id: emailIds.firstReminder }, connection: { edgeType: 'STANDARD', nextActionId: '4' } },
        { actionId: '4', actionTypeId: '0-35', actionTypeVersion: 0, type: 'SINGLE_CONNECTION', fields: { date: { staticValue: epochMidnightUTC(r2.date), type: 'STATIC_VALUE' }, delta: '0', time_unit: 'DAYS', time_of_day: { hour: r2.hour, minute: r2.minute } }, connection: { edgeType: 'STANDARD', nextActionId: '5' } },
        { actionId: '5', actionTypeId: '0-4', actionTypeVersion: 0, type: 'SINGLE_CONNECTION', fields: { content_id: emailIds.secondReminder } },
      ],
      enrollmentCriteria: {
        type: 'LIST_BASED',
        shouldReEnroll: false,
        unEnrollObjectsNotMeetingCriteria: false,
        reEnrollmentTriggersFilterBranches: [],
        listFilterBranch: {
          filterBranchType: 'OR',
          filterBranchOperator: 'OR',
          filters: [],
          filterBranches: [{
            filterBranchType: 'AND',
            filterBranchOperator: 'AND',
            filterBranches: [],
            filters: [{ filterType: 'FORM_SUBMISSION', formId: config.hubspotFormId, operator: 'FILLED_OUT' }],
          }, {
            // Second path: Riverside-page registrants never touch the HubSpot form, but the
            // sync agent stamps webinar_name on them - enroll those too so they get reminders.
            filterBranchType: 'AND',
            filterBranchOperator: 'AND',
            filterBranches: [],
            filters: [{ filterType: 'PROPERTY', property: config.properties?.webinarName || 'webinar_name', operation: { operationType: 'STRING', operator: 'IS_EQUAL_TO', value: config.eventStem } }],
          }],
        },
      },
    },
  });
  console.log(`[flow] created ${flow.id} (DISABLED - enable manually in the UI after QA)`);
  // Verify what landed: the flow is off and each send-email action names our email.
  const fresh = await hubspotRequest(`/automation/v4/flows/${flow.id}`);
  const sent = (fresh.actions || []).filter((a) => a.actionTypeId === '0-4').map((a) => String(a.fields?.content_id));
  const expected = [emailIds.registration, emailIds.firstReminder, emailIds.secondReminder].map(String);
  console.log(`[flow] read back: enabled=${fresh.isEnabled}, send-email actions=${JSON.stringify(sent)}, expected=${JSON.stringify(expected)}`);
  if (fresh.isEnabled) throw new Error(`flow ${flow.id} reads back ENABLED - turn it off in HubSpot now`);
  if (JSON.stringify(sent) !== JSON.stringify(expected)) console.warn(`[flow] WARNING: send-email actions do not match the emails - check flow ${flow.id} in HubSpot`);
  return String(flow.id);
}

// --- Step 5: segmentation lists ---

async function createLists(config) {
  const existing = config.created?.listIds || {};
  const webinarNameProp = config.properties.webinarName || 'webinar_name';
  const defs = [
    { key: 'registered', name: `${config.eventStem} - Registered`, filters: [prop(webinarNameProp, 'STRING', config.eventStem)] },
    { key: 'attended', name: `${config.eventStem} - Attended`, filters: [prop(webinarNameProp, 'STRING', config.eventStem), prop(config.properties.attended, 'BOOL', true)] },
    { key: 'noShow', name: `${config.eventStem} - No-show`, filters: [prop(webinarNameProp, 'STRING', config.eventStem), prop(config.properties.noShow, 'BOOL', true)] },
  ];
  const ids = { ...existing };
  for (const def of defs) {
    if (ids[def.key]) { console.log(`[list:${def.key}] reusing ${ids[def.key]}`); continue; }
    const res = await hubspotRequest('/crm/v3/lists', {
      method: 'POST',
      body: {
        name: def.name,
        objectTypeId: '0-1',
        processingType: 'DYNAMIC',
        filterBranch: {
          filterBranchType: 'OR', filterBranches: [{ filterBranchType: 'AND', filterBranches: [], filters: def.filters }], filters: [],
        },
      },
    });
    ids[def.key] = res.list.listId;
    console.log(`[list:${def.key}] created ${res.list.listId}`);
  }
  return ids;

  function prop(property, operationType, value) {
    return { filterType: 'PROPERTY', property, operation: { operationType, operator: 'IS_EQUAL_TO', value } };
  }
}

// --- Step 6: calendar links ---

function calendarLinks(config) {
  const title = encodeURIComponent(config.eventStem);
  // A shared studio link is the only join link a calendar entry can carry: the
  // personal one is a per-contact token that a static URL cannot hold.
  const studio = config.joinUrlFallback ? `Studio link: ${config.joinUrlFallback}` : '';
  // Converted again here so entries stored before intake did it still give clean links.
  const description = htmlToText(config.eventDescription) || `Join us live for ${config.eventStem}.`;
  const details = encodeURIComponent(studio ? `${description}\n\n${studio}` : description);
  const location = studio ? `&location=${encodeURIComponent(studio)}` : '';
  const start = config.eventStartsAt.replace(/[-:]/g, '').replace('.000', '');
  const end = config.eventEndsAt.replace(/[-:]/g, '').replace('.000', '');
  return {
    google: `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}&dates=${start}/${end}${location}`,
    outlook: `https://outlook.live.com/calendar/0/deeplink/compose?subject=${title}&body=${details}&startdt=${config.eventStartsAt}&enddt=${config.eventEndsAt}${location}`,
    office365: `https://outlook.office.com/calendar/0/deeplink/compose?subject=${title}&body=${details}&startdt=${config.eventStartsAt}&enddt=${config.eventEndsAt}${location}`,
  };
}

// --- Entry point ---

async function main() {
  const args = process.argv.slice(2);
  const eventStem = args.find((a) => !a.startsWith('--'));
  const doCreate = args.includes('--create');
  const doPublish = args.includes('--publish-emails');
  const forceCopy = args.includes('--force-copy');
  if (!eventStem) throw new Error('Usage: node scripts/new-webinar.js "<eventStem|eventId>" [--create] [--publish-emails] [--force-copy]');

  const configs = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  // Accept either the config's eventStem or the Riverside event id, so a caller that
  // only ever holds the id (the launch workflow) never has to parse a stem out of stdout.
  const config = configs.find((c) => c.eventStem === eventStem)
    || configs.find((c) => c.riversideEventId === eventStem);
  if (!config) throw new Error(`No entry matching "${eventStem}" in ${CONFIG_PATH}`);
  for (const field of ['riversideEventId', 'hubspotFormId', 'eventStartsAt', 'eventEndsAt', 'reminders']) {
    if (!config[field]) throw new Error(`config entry is missing "${field}"`);
  }
  for (const key of ['first', 'second']) {
    const r = config.reminders[key];
    const valid = r && /^\d{4}-\d{2}-\d{2}$/.test(r.date || '')
      && Number.isInteger(r.hour) && r.hour >= 0 && r.hour <= 23
      && Number.isInteger(r.minute) && r.minute >= 0 && r.minute <= 59;
    if (!valid) throw new Error(`config reminders.${key} must be {date: 'YYYY-MM-DD', hour: 0-23, minute: 0-59}`);
  }
  // A placeholder form id would build a flow that triggers on a form that does not exist.
  if (doCreate && String(config.hubspotFormId).startsWith('TODO')) {
    throw new Error('hubspotFormId is still a placeholder. Run scripts/ensure-hubspot-intake.js "<id>" --create first.');
  }
  if (config.emailCopy) {
    const { errors, warnings } = validateCopy(config.emailCopy);
    for (const w of warnings) console.warn(`  copy warning: ${w}`);
    if (errors.length) throw new Error(`emailCopy in the config entry is invalid:\n  - ${errors.join('\n  - ')}`);
  }

  console.log(`Plan for "${config.eventStem}" (${doCreate ? 'CREATE' : 'DRY-RUN'}${doPublish ? ' + PUBLISH EMAILS' : ''}):`);
  console.log('  1. ensure branded coded template');
  console.log(`  2. create 3 AUTOMATED emails (clone seed → re-point → fill copy) as drafts, with ${config.emailCopy ? 'the drafted copy' : 'the generic default copy'}; existing drafts get the copy if it changed`);
  console.log(`  3. ${doPublish ? 'publish the 3 emails' : 'leave emails as drafts (no --publish-emails)'}`);
  console.log('  4. create v4 flow, DISABLED (form trigger → reg → delay → rem1 → delay → rem2), even while the emails are drafts');
  console.log('  5. create 3 dynamic lists (Registered/Attended/No-show)');
  console.log('  6. print add-to-calendar links');
  console.log('  Human gates that remain: review email copy/design, publish (gate 3), enable flow in UI.');

  // What each email will carry, so the plan run doubles as the copy review.
  const preview = resolveCopy(config);
  console.log(`\nEmail copy (${config.emailCopy ? 'drafted' : 'generic defaults'}; join link ${config.joinUrlFallback ? 'personal, falling back to the shared studio link' : 'personal only, no fallback'}):`);
  for (const role of ROLES) {
    const c = preview[role];
    console.log(`  [${role}] subject: ${c.subject}`);
    console.log(`  [${role}] preheader: ${c.preheader}`);
    console.log(`  [${role}] button: "${c.cta.text}" -> ${c.cta.url.length > 90 ? `${c.cta.url.slice(0, 90)}...` : c.cta.url}`);
    console.log(`  [${role}] words: ${wordCount(`${c.body} ${c.secondary}`)}`);
  }

  if (!doCreate) {
    console.log('\nDry-run only. Re-run with --create to execute.');
    console.log('\nCalendar links preview:', JSON.stringify(calendarLinks(config), null, 2));
    return;
  }

  config.created = config.created || {};
  config.created.templatePath = await ensureTemplate(config);
  save();
  const emails = await createEmails(config, config.created.templatePath, {
    forceCopy,
    persist: (state) => { config.created.emailIds = state.ids; config.created.copy = state.copy; save(); },
  });
  config.created.emailIds = emails.ids;
  config.created.copy = emails.copy;
  save();
  if (doPublish) await publishEmails(config.created.emailIds);
  const flowId = await createFlow(config, config.created.emailIds);
  if (flowId) { config.created.flowId = flowId; save(); }
  config.created.listIds = await createLists(config);
  save();
  console.log('\nCalendar links:', JSON.stringify(calendarLinks(config), null, 2));
  console.log('\nDone. Next human steps: QA the 3 emails in HubSpot, publish if not yet, then enable the flow in the UI.');

  function save() {
    // merge-on-write: re-read so a concurrently-run webinar's created.* ids survive.
    // Keyed on riversideEventId: eventStem comes from the Riverside title and repeats
    // across a webinar series, so a stem-keyed write can land on the wrong entry.
    const onDisk = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    let i = config.riversideEventId
      ? onDisk.findIndex((c) => c.riversideEventId === config.riversideEventId)
      : -1;
    if (i === -1) {
      const stemMatches = onDisk.filter((c) => c.eventStem === config.eventStem);
      if (stemMatches.length > 1) {
        throw new Error(`"${config.eventStem}" matches ${stemMatches.length} config entries and this entry has no riversideEventId. Refusing to guess which one to write.`);
      }
      i = onDisk.findIndex((c) => c.eventStem === config.eventStem);
    }
    if (i === -1) onDisk.push(config); else onDisk[i] = config;
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(onDisk, null, 2));
  }
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err.message || err);
    process.exit(1);
  });
}

module.exports = { ensureTemplate, createEmails, createFlow, createLists, calendarLinks, resolveCopy };
