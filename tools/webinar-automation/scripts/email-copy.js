// Drafted email copy for the three webinar emails: validation and rendering.
//
// The copy is drafted in-session by the `riverside-event-copy` skill, approved by a
// human, and handed to the launch workflow as JSON. It lands in the webinar's config
// entry as `emailCopy`, keyed by role:
//
//   { "registration":   { subject, preheader, headline, body, secondary?, cta? },
//     "firstReminder":  { ... },
//     "secondReminder": { ... } }
//
// `cta` is { text, url }. Links the copy cannot know at drafting time are written as
// placeholders and resolved here at build time:
//
//   [[JOIN_URL]]                personal join link token (with the shared fallback, if set)
//   [[GOOGLE_CALENDAR_URL]]     add-to-calendar links computed from the event schedule
//   [[OUTLOOK_CALENDAR_URL]]
//   [[OFFICE365_CALENDAR_URL]]
//
// Kept separate from new-webinar.js so intake (add-webinar.js) can validate copy without
// loading HubSpot code, and so both scripts apply exactly one set of rules.

const crypto = require('crypto');

const ROLES = ['registration', 'firstReminder', 'secondReminder'];
const REQUIRED_FIELDS = ['subject', 'preheader', 'headline', 'body'];
const OPTIONAL_FIELDS = ['secondary', 'cta'];
const PLACEHOLDERS = ['JOIN_URL', 'GOOGLE_CALENDAR_URL', 'OUTLOOK_CALENDAR_URL', 'OFFICE365_CALENDAR_URL'];

// A shared studio link is written into email HTML and a HubL filter argument, so only
// a plain riverside.com / riverside.fm URL with no quotes, spaces or angle brackets passes.
const FALLBACK_URL = /^https:\/\/(www\.)?riverside\.(com|fm)\/[^\s'"<>`\\]*$/;

function isValidFallbackUrl(url) {
  return typeof url === 'string' && FALLBACK_URL.test(url);
}

function stripTags(html) {
  return String(html).replace(/<[^>]*>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
}

// Riverside returns the event description as editor HTML (classed <p>/<span> markup).
// Calendar entries and the reminder plan want plain text, so paragraphs become line
// breaks, tags go, and the common entities are decoded.
function htmlToText(html) {
  return String(html || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>\s*/gi, '\n')
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&amp;/g, '&')
    .split('\n')
    .map((line) => line.replace(/\s+/g, ' ').trim())
    .filter(Boolean)
    .join('\n');
}

function wordCount(html) {
  const text = stripTags(html);
  return text ? text.split(' ').length : 0;
}

// Every string a role carries, so the content checks cannot miss a slot.
function roleStrings(c) {
  const out = [];
  for (const f of [...REQUIRED_FIELDS, 'secondary']) if (typeof c[f] === 'string') out.push([f, c[f]]);
  if (c.cta && typeof c.cta === 'object') {
    if (typeof c.cta.text === 'string') out.push(['cta.text', c.cta.text]);
    if (typeof c.cta.url === 'string') out.push(['cta.url', c.cta.url]);
  }
  return out;
}

// Returns { errors, warnings }. Errors block the build; warnings are printed for the
// reviewer and do not.
function validateCopy(copy) {
  const errors = [];
  const warnings = [];
  if (!copy || typeof copy !== 'object' || Array.isArray(copy)) {
    return { errors: ['email copy must be a JSON object keyed by role'], warnings };
  }
  for (const key of Object.keys(copy)) {
    if (!ROLES.includes(key)) errors.push(`unknown role "${key}" (expected ${ROLES.join(', ')})`);
  }
  for (const role of ROLES) {
    const c = copy[role];
    if (!c || typeof c !== 'object') {
      // All three or none: a sequence that mixes drafted copy with the generic defaults
      // reads like two different senders.
      errors.push(`${role}: missing. Supply all three emails or none.`);
      continue;
    }
    for (const key of Object.keys(c)) {
      if (![...REQUIRED_FIELDS, ...OPTIONAL_FIELDS].includes(key)) errors.push(`${role}: unknown field "${key}"`);
    }
    for (const f of REQUIRED_FIELDS) {
      if (typeof c[f] !== 'string') errors.push(`${role}.${f}: must be a string`);
      else if (f !== 'headline' && !c[f].trim()) errors.push(`${role}.${f}: is empty`);
    }
    if (c.secondary !== undefined && typeof c.secondary !== 'string') errors.push(`${role}.secondary: must be a string`);
    if (c.cta !== undefined) {
      if (!c.cta || typeof c.cta.text !== 'string' || !c.cta.text.trim() || typeof c.cta.url !== 'string') {
        errors.push(`${role}.cta: must be { "text": "...", "url": "..." }`);
      } else if (!/^\[\[[A-Z0-9_]+\]\]$/.test(c.cta.url) && !/^https:\/\/\S+$/.test(c.cta.url)) {
        errors.push(`${role}.cta.url: must be a placeholder like [[JOIN_URL]] or an https:// URL`);
      }
    }

    for (const [field, value] of roleStrings(c)) {
      if (/[\u2013\u2014]/.test(value)) errors.push(`${role}.${field}: contains an em or en dash`);
      if (/<\s*script|<[^>]*\son\w+\s*=|javascript:/i.test(value)) errors.push(`${role}.${field}: contains script or an inline event handler`);
      // HubL statements would execute inside the email template. Personalization
      // expressions ({{ contact.firstname }}) are fine; {% ... %} blocks are not.
      if (/\{%/.test(value)) errors.push(`${role}.${field}: contains a HubL statement ({% ... %})`);
      const emoji = value.match(/\p{Extended_Pictographic}/gu);
      if (emoji && emoji.some((ch) => !'\u00a9\u00ae\u2122'.includes(ch))) errors.push(`${role}.${field}: contains an emoji`);
      for (const m of value.matchAll(/\[\[([A-Z0-9_]+)\]\]/g)) {
        if (!PLACEHOLDERS.includes(m[1])) errors.push(`${role}.${field}: unknown placeholder [[${m[1]}]] (known: ${PLACEHOLDERS.join(', ')})`);
      }
    }

    if (typeof c.preheader === 'string') {
      const n = c.preheader.trim().length;
      if (n < 40 || n > 90) warnings.push(`${role}.preheader: ${n} characters (target 40-90)`);
    }
    const words = wordCount(`${c.body || ''} ${c.secondary || ''}`);
    const limit = role === 'firstReminder' ? 100 : 200;
    if (words > limit) warnings.push(`${role}: body is ${words} words (target under ${limit})`);
  }
  return { errors, warnings };
}

function joinToken(config) {
  const prop = `contact.${config.properties.joinUrl}`;
  // HubL's default filter only covers undefined unless the second argument is true;
  // an empty contact property is falsy, so `true` is what makes the fallback apply.
  return config.joinUrlFallback
    ? `{{ ${prop}|default('${config.joinUrlFallback}', true) }}`
    : `{{ ${prop} }}`;
}

function escapeAttr(url) {
  return String(url).replace(/&(?!amp;)/g, '&amp;');
}

// Resolve placeholders. In HTML fields a link lands inside an href, so ampersands are
// escaped; the CTA url is a module field value, not HTML, and is passed through raw.
function renderRole(c, { join, links }) {
  const values = {
    JOIN_URL: join,
    GOOGLE_CALENDAR_URL: links.google,
    OUTLOOK_CALENDAR_URL: links.outlook,
    OFFICE365_CALENDAR_URL: links.office365,
  };
  const sub = (s, html) => String(s).replace(/\[\[([A-Z0-9_]+)\]\]/g, (whole, key) => {
    if (!(key in values)) throw new Error(`unknown placeholder ${whole}`);
    return html ? escapeAttr(values[key]) : values[key];
  });
  const cta = c.cta || { text: 'Join the Webinar', url: '[[JOIN_URL]]' };
  return {
    subject: sub(c.subject, false),
    preheader: sub(c.preheader, true),
    headline: sub(c.headline, true),
    body: sub(c.body, true),
    secondary: sub(c.secondary || '', true),
    cta: { text: sub(cta.text, false), url: sub(cta.url, false) },
  };
}

function hashCopy(rendered) {
  return crypto.createHash('sha256').update(JSON.stringify(rendered)).digest('hex').slice(0, 16);
}

module.exports = {
  ROLES,
  PLACEHOLDERS,
  validateCopy,
  isValidFallbackUrl,
  joinToken,
  renderRole,
  hashCopy,
  wordCount,
  htmlToText,
};
