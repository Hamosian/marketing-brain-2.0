/* 40-worked.js: slide 8, a role-aware replay of one real request.
   Every step, trigger phrase and file path below is taken from the named
   skill's SKILL.md. Outputs are mocks of each skill's documented format and
   use [placeholders] instead of figures. Id prefix: w-. */
(function () {
  'use strict';

  var root = document.querySelector('.slide[data-id="worked"]');
  if (!root) return;

  function $(id) { return document.getElementById(id); }
  var tablist = $('w-tabs');
  var panel = $('w-panel');
  var whoEl = $('w-who');
  var skillsEl = $('w-skills');
  var stepsEl = $('w-steps');
  var narrEl = $('w-narr');
  var logEl = $('w-log');
  var playBtn = $('w-play');
  var nextBtn = $('w-next');
  var replayBtn = $('w-replay');
  var rmNote = $('w-rm-note');
  if (!tablist || !panel || !logEl || !stepsEl) return;
  var tabs = [].slice.call(tablist.querySelectorAll('[role="tab"]'));

  function M() { return window.MBT || null; }

  var STEP_T = ['The request', 'Who picks it up', 'What it reads', 'Where it stops', 'What comes back'];
  var N = STEP_T.length;

  /* ---------- icons (decorative, currentColor) ---------- */
  function svg(body, fill) {
    return '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false" fill="' +
      (fill ? 'currentColor' : 'none') + '" stroke="' + (fill ? 'none' : 'currentColor') +
      '" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>';
  }
  var I = {
    check: svg('<path d="M20 6 9 17l-5-5"/>'),
    file: svg('<path d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>'),
    skill: svg('<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><path d="M14 7.5 10 16.5"/>'),
    tool: svg('<path d="m5 17 5-5-5-5M12 19h7"/>'),
    script: svg('<path d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="m9 12 2 2-2 2M13 17h3"/>'),
    none: svg('<circle cx="12" cy="12" r="8.5"/><path d="m8.5 12.2 2.4 2.4 4.6-5"/>'),
    ask: svg('<path d="M4.5 5.5h15v10h-9l-4.5 3.5v-3.5h-1.5z"/><path d="M12 12.6v.1M10.3 8.9a1.8 1.8 0 1 1 2.4 1.7c-.5.2-.7.6-.7 1.1"/>'),
    confirm: svg('<path d="M9 5v14M15 5v14"/>'),
    rule: svg('<path d="M12 3.5 19 6v5.5c0 4.4-3 7.6-7 9-4-1.4-7-4.6-7-9V6z"/><path d="M9.5 12h5"/>'),
    info: svg('<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5M12 8h.01"/>'),
    play: svg('<path d="M8 5.5v13l10.5-6.5z"/>', true),
    pause: svg('<path d="M8 5.5h3v13H8zM13 5.5h3v13h-3z"/>', true),
    next: svg('<path d="m9 6 6 6-6 6"/>'),
    replay: svg('<path d="M4 12a8 8 0 1 0 2.6-5.9L4 8.5"/><path d="M4 4v4.5h4.5"/>')
  };

  /* ---------- the examples ---------- */
  var EX = {
    seo: {
      org: 'Growth', label: 'SEO and AI search', skills: ['weekly-seo-report'],
      request: 'How did organic search do last week?',
      s1: 'Plain words, no command needed',
      n1: 'You type it in Claude Code with the repo open. Plain words are enough; the command name is optional.',
      picks: [{ s: 'weekly-seo-report', m: 'how did organic search do last week' }],
      note: 'Not /organic-dashboard: rank tracking and AI-overview share are monthly questions, and they live there.',
      n2: 'Its description lists this phrase as a trigger, so Claude hands it the job. The same skill also runs by itself every Thursday as a cloud routine.',
      reads: [
        ['.claude/skills/weekly-seo-report/scripts/resolve_week.py', 'Picks the 7 complete days ending yesterday, and the 7 before', 'script'],
        ['.claude/skills/weekly-seo-report/knowledge/data-dictionary.md', 'The Snowflake query and the Search Console pulls'],
        ['.claude/skills/weekly-seo-report/knowledge/build-and-render.md', 'The fixed layout and the rules that keep a week honest'],
        ['.claude/skills/weekly-seo-report/knowledge/stable-url.md', 'The one URL it always updates']
      ],
      n3: 'For the numbers it tries /rivermind:ask first, as the data rule says. The per-page weekly funnel is a known gap there, so it falls back to /data-agent and says so in the run summary.',
      stop: {
        kind: 'none', sum: 'Does not stop', title: 'It does not stop to ask',
        lines: [
          'It is built to run unattended, so every unclear branch has a default instead of a question.',
          'Snowflake more than two days behind: it does not publish, and it DMs Amir why.',
          'Nothing moved: it says so. Cause unknown: it writes "cause not established".'
        ]
      },
      n4: 'It is read-only. The only side effects are updating the report page and sending one Slack DM.',
      out: 'seo', s5: 'Report page and a DM',
      n5: 'One page at a stable URL, updated in place each week, so the link people bookmarked keeps working. Amir gets the headlines by DM.'
    },

    paid: {
      org: 'Growth', label: 'Paid acquisition', skills: ['paid-acquisition-agent'],
      request: 'CPA on the Riverside.com Google Ads account jumped this week. What happened?',
      s1: 'A diagnosis question',
      n1: 'A question about one account and one metric. Naming the account helps, because the skill keeps accounts apart.',
      picks: [{ s: 'paid-acquisition-agent', m: 'Google Ads' }],
      note: 'For a deep pass it can hand the data it pulled to a specialist, such as the Tracking & Measurement Specialist.',
      n2: 'Its description covers Google Ads, spend pacing and campaign health. It owns paid analysis and recommendations, not the ad accounts themselves.',
      reads: [
        ['systems/owned/paid-acquisition.md', 'Accounts, owners, Windsor.ai fields and known quirks'],
        ['/data-agent', 'Pulls spend and conversion metrics through Windsor.ai', 'skill'],
        ['/hubspot-agent or /measurement-agent', 'Only if the question reaches leads or revenue', 'skill']
      ],
      n3: 'It keeps the Brand, Riverside.com and YouTube accounts separate unless you ask for a total.',
      stop: {
        kind: 'rule', sum: 'Never edits the ad account', title: 'It will not touch the ad account',
        lines: [
          'It never changes ad platform settings. A pause or a budget move comes back to you as a recommendation.',
          'Before calling a campaign bad, it checks which conversion event is counted.',
          'It names the data gaps before it makes a strong recommendation.'
        ]
      },
      n4: 'Every change stays yours to make, in the ad platform itself.',
      out: 'paid', s5: 'An eight-field result',
      n5: 'The same eight fields every time, so a result reads the same whoever asked.'
    },

    creator: {
      org: 'Growth', label: 'Creator marketing and growth channels', skills: ['marketing-brain'],
      request: "Plan next month's creator affiliate push: who owns what, what we measure, and the first three actions.",
      s1: 'A broad, cross-team ask',
      n1: 'A broad ask that touches content, data and the task board at once.',
      picks: [{ s: 'marketing-brain', m: 'planning' }],
      note: 'Parts go to /content-agent (which can bring in its Creator Marketing Strategist), /rivermind:ask for numbers, and /pm-story for tasks.',
      n2: 'Broad or cross-system work starts at /marketing-brain. It classifies the request (this one is a plan), then routes each part to the skill that owns it.',
      reads: [
        ['CLAUDE.md', 'Always first: the routing map and the house rules'],
        ['references/team.md', 'To resolve owners. Creator Marketing sits with Savion Ron Shemesh'],
        ['systems/owned/partnerstack.md', 'Only because the ask touches the affiliate program']
      ],
      n3: 'It loads only what the request needs. Team and system docs come in when the request names a person or a system.',
      stop: {
        kind: 'confirm', sum: 'Asks before it writes', title: 'It asks before it writes',
        lines: [
          'Tasks from the plan are drafted through /pm-story, which confirms each section with you.',
          'Nothing is created in monday or sent in Slack without your yes.'
        ]
      },
      n4: 'Exploring and planning are safe. Writes wait for you.',
      out: 'plan', s5: 'A plan with owners',
      n5: 'It ends with owners and first actions, not only a report. Every figure carries a source and an as-of date.'
    },

    mops: {
      org: 'Growth', label: 'Marketing operations', skills: ['pm-story'],
      request: 'Open a ticket: the homepage top bar should promote the October webinar.',
      s1: 'One ticket, in plain words',
      n1: 'One ticket, described the way you would say it to a teammate.',
      picks: [{ s: 'pm-story', m: 'open a ticket for X' }],
      note: 'A top bar is served by Trendemon, so it goes to Marketing Operations Tasks as Messaging, not to Website Development.',
      n2: 'Every task goes through /pm-story, never straight to monday. Its description names banners and top bars outright.',
      reads: [
        ['CLAUDE.md', 'The systems table, to see which system this touches'],
        ['systems/owned/trendemon.md', 'How on-site messages are served'],
        ['references/monday_boards.md', 'Board ids and column keys'],
        ['.claude/skills/ticket-hygiene/knowledge/config.md', 'What each board needs before work can start']
      ],
      n3: 'It exhausts context before asking you anything: the system doc, board history, recent Slack threads, and the 2026 MKT Planning board for the initiative this belongs to.',
      stop: {
        kind: 'ask', sum: 'Walks you through it', title: 'It walks you through it',
        lines: [
          'Why, then What, then Done when: one section at a time, each confirmed before the next.',
          'One batch of questions for board, bucket, owner, priority and POC.',
          'It shows the planning-board match and waits for you to accept or reject it.'
        ]
      },
      n4: 'Questions come in one batch, never a drip.',
      out: 'ticket', s5: 'A ticket with a brief',
      n5: 'The brief lands as an update on the item, with your exact words kept beside it. It reads the ticket back to check every field, then gives you the link.'
    },

    sdr: {
      org: 'Growth', label: 'Inbound SDR', skills: ['demo-reply-fact-check'],
      request: 'Fact-check this draft before I send it. [your draft reply to the lead]',
      s1: 'Paste the draft',
      n1: "Paste the draft, plus the lead's plan and what they actually asked. It needs both.",
      picks: [{ s: 'demo-reply-fact-check', m: 'fact-check this draft' }],
      note: 'Default verdict is UNVERIFIED: a claim passes only when a source says so, at the right plan tier.',
      n2: 'Its trigger phrases include "fact-check this draft" and "check the product claims". It grades every product claim, then checks fit and voice.',
      reads: [
        ['.claude/skills/demo-reply-fact-check/verified-claims.md', 'Claims already checked, with source and date'],
        ['references/product/help-center-reference.md', 'Which plan each feature sits on'],
        ['references/messaging/', 'Product facts the help-center summary leaves out'],
        ['/rivermind:ask', 'The synced help center and internal knowledge base', 'skill']
      ],
      n3: 'It works the sources in a fixed order and stops at the first clean answer. Ledger entries older than 90 days get checked again.',
      stop: {
        kind: 'ask', sum: "Asks for the lead's context", title: 'It needs context, not just the draft',
        lines: [
          "The lead's title, company size, plan, and their own words. A claim can be true in general and wrong on this lead's plan.",
          'Pricing never gets VERIFIED here. Prices are checked against the live pricing page.'
        ]
      },
      n4: 'The gate is scored both ways. A wrong block costs a day, so every block has to name its source.',
      out: 'verdict', s5: 'A verdict per claim',
      n5: 'One row per claim, then a fit row, a voice row and one result line. A CONTRADICTED claim blocks the draft until it is fixed and checked again.'
    },

    'brand-design': {
      org: 'Brand', label: 'Design and creative direction', skills: ['riverside-presentation'],
      request: "Build a six-slide deck for the October campaign readout, for Abel's staff meeting.",
      s1: 'Purpose, audience, length',
      n1: 'A deck request that already says what it is for, who sees it, and how long it is. That saves a round of questions.',
      picks: [{ s: 'riverside-presentation', m: 'slide deck' }],
      note: "The rules are Brand's: Near Black backgrounds, purple as an accent only, Instrument Sans throughout.",
      n2: "Any Riverside deck goes to /riverside-presentation. It layers Brand's rules on top of the general slide-building mechanics.",
      reads: [
        ['.claude/skills/riverside-presentation/SKILL.md', 'Layouts, color tokens, logo placement'],
        ['/riverside-brand-guidelines', 'The palette and type Brand owns', 'skill']
      ],
      n3: 'It checks which slide tools this computer has before promising a .pptx. The brand rules are the same either way.',
      stop: {
        kind: 'ask', sum: 'Asks what is missing', title: 'It clarifies before it builds',
        lines: [
          'Purpose, audience, number of slides, and any content you already have.',
          'It checks it can build the file before it promises one.'
        ]
      },
      n4: 'You gave purpose, audience and length up front, so the only open question is content.',
      out: 'slides', s5: 'A branded .pptx',
      n5: 'A .pptx, checked for overlaps, overflow, contrast and brand slips, ending with the AI diligence statement the department asks for. For Google Slides, drag it into Drive and open it with Slides.'
    },

    'brand-video': {
      org: 'Brand', label: 'Motion and performance video', skills: ['video-project-intake'],
      request: "Here's the brief for the new launch video: [Google Doc link]. Let's get it going.",
      s1: 'Raz hands over a brief',
      n1: "Raz Messing hands over a brief: a Doc link, pasted text, or a rough idea. Anyone can write a brief. Only Raz's go creates a project.",
      picks: [{ s: 'video-project-intake', m: "here's the brief" }],
      note: 'If someone other than Raz asks, it still stress-tests the brief and offers to hand Raz the verdict. It creates nothing.',
      n2: 'A video project is a group on the Video Projects board, not a task, so this is not /pm-story.',
      reads: [
        ['.claude/skills/video-project-intake/knowledge/board-schema.md', 'The live board and the exact write plan'],
        ['.claude/skills/video-project-intake/knowledge/brief-stress-test.md', 'The fourteen checks and the verdicts'],
        ['references/video-creative-brief-templates.md', 'Which brief template applies'],
        ['references/team.md', 'To resolve every name to a person']
      ],
      n3: 'It reads the brief and works out owner, type and deadline itself before asking anyone anything.',
      stop: {
        kind: 'confirm', sum: "Waits for Raz's yes", title: 'It waits for an explicit yes',
        lines: [
          'A verdict first: Sound, Sound with gaps, or Not ready. Gaps go to the Brief Owner by name, and nothing is on the board yet.',
          'Then the exact write plan, every call and value, ending in "Confirm?"',
          '"Looks good" on the proposal is not a yes to write, and silence is not consent.'
        ],
        reply: ['Raz', 'yes']
      },
      n4: 'A yes covers one plan. If a value changes after it, the plan is shown again and the question asked again.',
      out: 'project', s5: 'One report after the read-back',
      n5: 'One report once it has read the board back, not a stream of updates. If any write fails, it stops and tells Raz instead of carrying on.'
    },

    pmm: {
      org: 'Marketing', label: 'Product marketing', skills: ['content-agent', 'demo-reply-fact-check'],
      request: 'Draft the launch email for [feature] to existing customers, then check every product claim.',
      s1: 'Write it, then prove it',
      n1: 'Two jobs in one ask: write the email, then check what it says about the product.',
      picks: [{ s: 'content-agent', m: 'email' }, { s: 'demo-reply-fact-check', m: 'check the product claims' }],
      note: 'Website page copy has a different owner: /page-cro.',
      n2: '/content-agent writes it, because it owns branded emails, docs and decks. /demo-reply-fact-check then grades each claim, because the email states what Riverside does.',
      reads: [
        ['references/messaging/README.md', 'Approved positioning, loaded first'],
        ['.claude/skills/riverside-brand-guidelines/SKILL.md', 'Tone and brand rules'],
        ['references/messaging/ai-writing-tells.md', 'The last human-quality pass'],
        ['references/product/help-center-reference.md', 'Where the fact-check looks up each plan tier']
      ],
      n3: 'It matches claims and phrases to the messaging framework instead of inventing positioning.',
      stop: {
        kind: 'ask', sum: 'Hands gaps back to you', title: 'Where it hands back to you',
        lines: [
          'Numbers that are not final stay as [placeholders], and it tells you that filling them in will do more than any copy change.',
          'A claim it cannot find in a source comes out before the email ships.'
        ]
      },
      n4: 'You approve the draft before anything is sent.',
      out: 'email', s5: 'Three angles, claims marked',
      n5: 'For a launch it drafts two or three angles: outcome-led for the main send, a short peer-to-peer version, and one whose subject line carries the whole pitch.'
    },

    content: {
      org: 'Marketing', label: 'Content, social, community', skills: ['content-agent', 'de-ai'],
      request: "Write the intro for this month's creator newsletter, then make it sound human.",
      s1: 'A draft plus a cleanup',
      n1: 'A draft and a cleaning pass, asked for in one go.',
      picks: [{ s: 'content-agent', m: 'newsletter' }, { s: 'de-ai', m: 'make it sound human' }],
      note: 'For anything high-stakes, /critique runs last and returns SHIP or REVISE.',
      n2: '/content-agent drafts it in the creator tone: casual, outcome-focused, peer to peer. /de-ai then strips the AI tells.',
      reads: [
        ['references/messaging/README.md', 'Approved blurbs and messaging, loaded first'],
        ['.claude/skills/riverside-brand-guidelines/SKILL.md', 'Brand and tone rules'],
        ['references/messaging/ai-writing-tells.md', 'The checklist behind the final pass'],
        ['.claude/skills/de-ai/SKILL.md', 'The patterns and their replacements']
      ],
      n3: 'The cleaning pass needs no research. It is a checklist over finished text.',
      stop: {
        kind: 'rule', sum: 'Counts before it fixes', title: 'It counts before it fixes',
        lines: [
          'About ten or more tells per 500 words: it stops editing and sends the draft back for a rewrite.',
          'Under that, it fixes them in place, worst first.'
        ]
      },
      n4: 'Polishing a draft that is mostly AI patterns only gives you AI patterns with nicer words.',
      out: 'diff', s5: 'A cleaner draft',
      n5: 'Each find is scored: kills credibility, softens impact, or polish only. The worst go first, and a flagged word gets a replacement, not just a deletion.'
    },

    ai: {
      org: 'AI Marketing', label: 'AI marketing', skills: ['agent-builder'],
      request: 'Turn my weekly competitor-page check into a routine.',
      s1: 'A job you do by hand',
      n1: 'You describe a job you keep doing by hand.',
      picks: [{ s: 'agent-builder', m: 'turn this into a skill' }],
      note: 'It classifies first. There are five types, each with its own home and deploy path; this one is a cloud routine.',
      n2: 'Building or deploying any new skill, agent or routine goes to /agent-builder.',
      reads: [
        ['.claude/skills/agent-builder/knowledge/skill-anatomy.md', 'The five types and the frontmatter rules'],
        ['.claude/skills/agent-builder/knowledge/routine-design.md', 'Cadence, plus the Acts when, Self-check and Stop sections'],
        ['.claude/skills/agent-builder/knowledge/templates.md', 'The template for this type'],
        ['.claude/skills/agent-builder/scripts/validate_skill.py', 'Mirrors the checks CI runs on every PR', 'script']
      ],
      n3: 'It opens each knowledge file only when it reaches the step that needs it.',
      stop: {
        kind: 'ask', sum: 'Option cards, then your go', title: 'It asks with option cards',
        lines: [
          'The interview comes as clickable cards: what it writes to, which systems it touches, how fast the signal changes.',
          'Your answer sets the cadence. Competitor pages move over a week or more.',
          'Last card: commit and open the PR, review the files first, or change something.'
        ]
      },
      n4: 'Nothing is committed until you pick "Commit and open the PR".',
      out: 'build', s5: 'Files, a test, a draft PR',
      n5: 'On merge, the wiki and the knowledge graph regenerate by themselves. The schedule is added only after one tested real run.'
    },

    initiatives: {
      org: 'Growth Initiatives', label: 'Growth initiatives', skills: ['marketing-brain'],
      request: "Sign-ups look soft this week across paid and organic. What's going on?",
      s1: 'One question, many causes',
      n1: 'One question with several possible causes across teams.',
      picks: [{ s: 'marketing-brain', m: 'cross-system investigations' }],
      note: "Numbers come from /rivermind:ask first, the analytics team's validated layer.",
      n2: 'It classifies this as an investigation with a depth-first shape: several lenses on the same question, then reconciled.',
      reads: [
        ['CLAUDE.md', 'Always first'],
        ['systems/owned/paid-acquisition.md', 'The paid lens'],
        ['systems/owned/seo-organic-dashboard.md', 'The organic lens'],
        ['references/evidence-standards.md', 'How to settle two sources that disagree']
      ],
      n3: 'Each specialist gets one objective and a data snapshot with sources and as-of dates. They reason over what it hands them; they cannot reach live systems.',
      stop: {
        kind: 'rule', sum: 'Names limits first', title: 'It names its limits before it recommends',
        lines: [
          'The source and its limitation come before any recommendation.',
          'When two lenses disagree on a number, it reconciles them against the data instead of averaging.'
        ]
      },
      n4: 'The final call stays with /marketing-brain. It never hands the synthesis to a specialist.',
      out: 'investigation', s5: 'Answer, evidence, gaps',
      n5: 'The answer first, then evidence with sources, the likely cause, the action, and the gaps it could not close.'
    },

    any: {
      org: 'Everyone', label: 'Not sure yet', skills: ['team-intro'],
      request: 'tell me about the team',
      s1: 'The first thing to type',
      n1: 'The first thing to type once you are set up. If it answers with real team context, the brain is live.',
      picks: [{ s: 'team-intro', m: 'tell me about the team' }],
      note: 'Next, "what skills do you have?" lists every workflow.',
      n2: 'Its description lists this exact phrase. It builds the answer from repo files only, never from memory.',
      reads: [
        ['CLAUDE.md', 'Who the team is, the systems table, task routing'],
        ['references/team.md', 'The full roster'],
        ['references/slack.md', 'The channel directory'],
        ['PHILOSOPHY.md', 'How the team context works, and why']
      ],
      n3: 'The same four files, read fresh each time, so the answer changes when the repo does.',
      stop: {
        kind: 'none', sum: 'Nothing to confirm', title: 'Nothing to confirm',
        lines: ['It only reads. Exploring like this is always safe.']
      },
      n4: 'Writes are where it pauses: monday, Slack and HubSpot changes wait for your yes.',
      out: 'overview', s5: 'A team overview',
      n5: 'A structured overview: who the team is and what it owns, the systems, the working conventions, what Claude can do, and where to start.'
    }
  };

  // Short titles, shared so the path slide can name the example it promises.
  var TITLES = {
    seo: 'How did organic search do last week?',
    paid: 'Why did CPA jump on one Google Ads account?',
    creator: "Plan next month's creator affiliate push",
    mops: 'Open a ticket for a homepage top bar',
    sdr: 'Fact-check a reply before it reaches a lead',
    'brand-design': 'Build a six-slide campaign readout deck',
    'brand-video': 'Take a new video brief to a live project',
    pmm: 'A launch email with every product claim checked',
    content: 'Write a newsletter intro, then make it sound human',
    ai: 'Turn a weekly check into a routine',
    initiatives: 'Why do sign-ups look soft this week?',
    any: 'Tell me about the team'
  };
  (function exportWorked() {
    var m = window.MBT;
    if (!m) return;
    var out = {};
    Object.keys(EX).forEach(function (k) {
      out[k] = { title: TITLES[k], request: EX[k].request, skills: EX[k].skills.slice() };
    });
    m.WORKED = out;
  })();

  /* ---------- helpers ---------- */
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  // Escape, then style every [placeholder] so sample slots read as slots.
  function fmt(s) {
    return esc(s).replace(/\[[^\]]+\]/g, function (x) { return '<span class="w-ph">' + x + '</span>'; });
  }
  function cmd(name) { return '<span class="cmd">/' + esc(name) + '</span>'; }
  // Narration: escape, style placeholders, turn /skill-name tokens into command chips.
  function prose(s) {
    return fmt(s).replace(/(^|[\s(])\/([a-z][a-z0-9:-]*[a-z0-9])/g, function (all, pre, name) {
      return pre + cmd(name);
    });
  }
  function announce(t) {
    var m = M();
    if (m && typeof m.announce === 'function') { try { m.announce(t); } catch (e) { /* ignore */ } }
  }
  var mq = null;
  try { mq = window.matchMedia('(prefers-reduced-motion: reduce)'); } catch (e) { mq = null; }
  function reduced() {
    var m = M();
    if (m && m.reduced === true) return true;
    return !!(mq && mq.matches);
  }
  function roleKey() {
    try {
      var m = M();
      var r = m && typeof m.role === 'function' ? m.role() : null;
      if (r && r.example && EX[r.example]) return r.example;
      if (r && r.key && EX[r.key]) return r.key;
    } catch (e) { /* fall through */ }
    return 'any';
  }
  function meta(key) {
    var m = M();
    var R = m && m.ROLES ? m.ROLES[key] : null;
    return { org: (R && R.org) || EX[key].org, label: (R && R.label) || EX[key].label };
  }

  /* ---------- output mocks: formats from each SKILL.md ---------- */
  function sec(h, body) { return '<div class="w-sec"><p class="w-sec-h">' + esc(h) + '</p>' + body + '</div>'; }
  function lines(arr) { return arr.map(function (t) { return '<p>' + fmt(t) + '</p>'; }).join(''); }
  function vchip(kind, text) { return '<span class="w-vchip w-v-' + kind + '">' + esc(text) + '</span>'; }

  var OUT = {
    seo: function () {
      var tiles = ['First visits', 'Sign-ups', 'Trials', 'New subs', 'First MRR'].map(function (t) {
        return '<div class="w-tile"><span class="w-tile-l">' + esc(t) + '</span><b>' + fmt('[n]') + '</b><span class="w-tile-d">' + fmt('[±%] vs prior 7') + '</span></div>';
      }).join('');
      var rows = ['Non-brand', 'Brand', 'LLM'].map(function (c) {
        return '<tr><th scope="row">' + c + '</th><td>' + fmt('[n]') + '</td><td>' + fmt('[n]') + '</td><td>' + fmt('[n]') + '</td></tr>';
      }).join('');
      return '<div class="w-rep">' +
        '<div class="w-rep-hd"><b>Weekly SEO report</b><span>7 complete days ending yesterday, against the 7 before</span></div>' +
        '<div class="w-rep-tabs" aria-hidden="true"><span class="is-on">Snowflake funnel</span><span>Search Console, on its own window</span></div>' +
        '<div class="w-tiles">' + tiles + '</div>' +
        '<table class="w-tbl"><caption>Split by channel, then data notes ordered by how much each would change a decision</caption>' +
        '<thead><tr><th scope="col">Channel</th><th scope="col">Sign-ups</th><th scope="col">Trials</th><th scope="col">New subs</th></tr></thead>' +
        '<tbody>' + rows + '<tr class="w-tot"><th scope="row">Total</th><td>' + fmt('[n]') + '</td><td>' + fmt('[n]') + '</td><td>' + fmt('[n]') + '</td></tr></tbody></table>' +
        '</div>' +
        '<div class="w-dm"><p class="w-dm-to">Slack DM to Amir</p><p>Funnel direction first, then the one thing that needs attention, then anything broken in the data. The link is the detail.</p><p class="w-dm-f">Posted by the Marketing OS agent</p></div>';
    },

    paid: function () {
      var rows = [
        ['Scope', 'Google Ads, Riverside.com account, this week against last'],
        ['Source', 'Windsor.ai via /data-agent, as of [date]'],
        ['Finding', '[what moved, and which conversion event is counted]'],
        ['Spend or impact', '[amount]'],
        ['Recommendation', '[pause, investigate, reallocate, test, fix tracking, or create a task]'],
        ['Owner', 'Raz Navon, who owns Paid Acquisition'],
        ['Approval needed', 'Yes, for any change in the ad platform'],
        ['Data gaps', '[named before any strong call]']
      ];
      return '<div class="w-paper"><p class="w-paper-h">Paid Acquisition Result</p><dl class="w-dl">' +
        rows.map(function (r) { return '<div><dt>' + esc(r[0]) + '</dt><dd>' + fmt(r[1]) + '</dd></div>'; }).join('') +
        '</dl></div>';
    },

    plan: function () {
      return '<div class="w-paper"><div class="w-paper-top"><p class="w-paper-h">Plan</p><span class="w-state">State: planned</span></div>' +
        '<div class="w-secs">' +
        sec('Goal', lines(['[What the push should achieve, and by when]'])) +
        sec('Workstreams', lines(['[Partner recruiting]', '[Creative for partners]', '[Tracking and payouts]'])) +
        sec('Owners', lines(['Savion Ron Shemesh, Creator Marketing', '[a named owner per workstream]'])) +
        sec('Success metrics', lines(['[metric], source, as of [date]'])) +
        sec('Risks', lines(['[risk, with an owner]'])) +
        sec('First 3 actions', '<ol class="w-ol"><li>' + fmt('[action, owner]') + '</li><li>' + fmt('[action, owner]') + '</li><li>' + fmt('[action, owner]') + '</li></ol>') +
        '</div></div>';
    },

    ticket: function () {
      var done = ['[Top bar live on the homepage for the chosen audience]', '[Links to the webinar sign-up page]', '[Comes down after the event]'];
      return '<div class="w-paper w-ticket">' +
        '<p class="w-tk-board">Marketing Operations Tasks</p>' +
        '<p class="w-tk-name">promote october webinar in homepage top bar</p>' +
        '<div class="w-tk-cols"><span><i>Type</i>Messaging</span><span><i>Status</i>New</span><span><i>Planned?</i>' + fmt('[Planned or Unplanned]') + '</span><span><i>Owner</i>' + fmt('[from your answers]') + '</span></div>' +
        '<div class="w-tk-upd">' +
        sec('Why', lines(['[1 to 2 sentences: what drives this]'])) +
        sec('What', lines(['[1 to 3 sentences: what changes, and for whom]'])) +
        sec('Done when', '<ul class="w-checks">' + done.map(function (d) { return '<li>' + fmt(d) + '</li>'; }).join('') + '</ul>') +
        sec('Open questions', lines(['[one line per question, or left out]'])) +
        '<div class="w-verbatim"><p class="w-sec-h">Request (verbatim)</p><p>the homepage top bar should promote the October webinar</p><p class="w-src">' + fmt('Asked directly, [you], [date]') + '</p></div>' +
        '<p class="w-tk-foot">' + fmt('Documented via Claude Code on [date]') + '</p>' +
        '</div></div>';
    },

    verdict: function () {
      var rows = [
        ['“Your plan already includes [feature].”', 'ok', 'VERIFIED', 'help-center-reference.md, plan-tier breakdown'],
        ['“The Business plan adds [feature].”', 'bad', 'CONTRADICTED', 'help-center-reference.md, plan-tier breakdown. Real feature, wrong tier.'],
        ['“[Plan] gives you [n] hours a month.”', 'warn', 'UNVERIFIED', 'Searched: [concept and three synonyms] in [files and FAQ titles]. Cut before shipping.']
      ];
      return '<div class="w-vt">' + rows.map(function (r) {
        return '<div class="w-vr"><p class="w-vq">' + fmt(r[0]) + '</p>' + vchip(r[1], r[2]) + '<p class="w-vs">' + fmt(r[3]) + '</p></div>';
      }).join('') + '</div>' +
        '<dl class="w-vsum"><div><dt>Fit</dt><dd>FITS: the lead named this use case</dd></div><div><dt>Voice</dt><dd>PASS</dd></div><div class="w-vres"><dt>Result</dt><dd>BLOCK: 1 claim needs fixing</dd></div></dl>';
    },

    slides: function () {
      var logo = document.querySelector('.topbar .logo, .brandmark img');
      var src = logo ? logo.getAttribute('src') : '';
      var mark = src ? '<img class="w-sl-logo" src="' + esc(src) + '" alt="">' : '<span class="w-sl-word">Riverside</span>';
      var bars = [58, 34, 72, 46, 86].map(function (h, i) {
        return '<i class="' + (i % 2 ? 'w-b2' : 'w-b1') + '" style="height:' + h + '%"></i>';
      }).join('');
      return '<div class="w-thumbs">' +
        '<figure class="w-thumb"><div class="w-sl w-sl-cover">' + mark + '<b>' + fmt('[October campaign readout]') + '</b><span class="w-sl-rule"></span><span class="w-sl-sub">' + fmt('[Staff meeting, date]') + '</span></div><figcaption>Cover</figcaption></figure>' +
        '<figure class="w-thumb"><div class="w-sl w-sl-stats"><span><b>' + fmt('[stat]') + '</b><i>' + fmt('[label]') + '</i></span><span><b>' + fmt('[stat]') + '</b><i>' + fmt('[label]') + '</i></span><span><b>' + fmt('[stat]') + '</b><i>' + fmt('[label]') + '</i></span></div><figcaption>Stats callout</figcaption></figure>' +
        '<figure class="w-thumb"><div class="w-sl w-sl-two"><div class="w-sl-txt"><b>' + fmt('[Title]') + '</b><i></i><i></i><i></i></div><div class="w-sl-chart">' + bars + '</div></div><figcaption>Two-column with chart</figcaption></figure>' +
        '<figure class="w-thumb"><div class="w-sl w-sl-end"><b>AI diligence statement</b><i></i><i></i><i></i></div><figcaption>Closing</figcaption></figure>' +
        '</div>';
    },

    project: function () {
      return '<div class="w-msg">' +
        '<p class="w-msg-h">' + fmt('[Name]_2026_[MM] is live') + ' <span class="w-msg-link">' + fmt('[board link]') + '</span></p>' +
        '<p>' + fmt('Owner [name] | Type [label] | Approver Abel | Deadline [date]') + '</p>' +
        '<p>Brief attached to “Brief (and Scope)”.</p>' +
        '<p>Stage values not set: gating is not built yet.</p>' +
        '<p>' + fmt('Open with the Brief Owner: [gaps, or nothing]') + '</p>' +
        '</div>' +
        '<div class="w-readback"><p class="w-rb-l">Read back from the board before reporting</p>' +
        '<span class="w-rb">' + I.check + '32 template items copied</span>' +
        '<span class="w-rb">' + I.check + '3 ownership sub-items named</span>' +
        '<span class="w-rb">' + I.check + 'Brief linked</span></div>';
    },

    email: function () {
      return '<div class="w-paper w-mail">' +
        '<div class="w-angles" aria-label="Angles drafted"><span class="is-on">Outcome-led, main send</span><span>Peer to peer</span><span>The math</span></div>' +
        '<p class="w-mail-meta"><i>From</i><span class="w-mv">' + fmt('[Named sender], [role]') + '</span></p>' +
        '<p class="w-mail-meta"><i>Subject</i><span class="w-mv">' + fmt('[What the reader gets]') + '</span></p>' +
        '<div class="w-mail-body">' +
        '<p>' + fmt('Hi [first name],') + '</p>' +
        '<p>' + fmt('[What they get, and how much, in the first two lines.]') + '</p>' +
        '<p><span class="w-claim">' + fmt('[Feature] is already on your plan.') + '</span> ' + vchip('ok', 'VERIFIED') + '</p>' +
        '<p><del class="w-claim">' + fmt('[It saves you n hours a week.]') + '</del> ' + vchip('warn', 'UNVERIFIED, cut') + '</p>' +
        '<p><span class="w-cta">' + fmt('[Action verb + outcome]') + '</span></p>' +
        '</div></div>';
    },

    diff: function () {
      var fixes = [
        ["It's worth mentioning that", 'cut', 'Hedging chain', 'hi'],
        ['delve into', 'look at', 'AI vocabulary', 'hi'],
        ['leverage', 'use', 'AI vocabulary', 'hi'],
        ["Don't hesitate to reply", 'Reply', 'AI vocabulary', 'hi'],
        ['In essence, creators are the heart of everything we do.', 'cut', 'Neat closing', 'mid']
      ];
      var before = "<mark>It's worth mentioning that</mark> this month we <mark>delve into</mark> " + fmt('[three creator stories]') +
        ' that <mark>leverage</mark> remote recording. <mark>Don&#39;t hesitate to reply</mark> with your ideas. <mark>In essence, creators are the heart of everything we do.</mark>';
      return '<div class="w-diff">' +
        '<p class="w-diff-h">Before</p><p class="w-diff-p">' + before + '</p>' +
        '<ul class="w-fixes">' + fixes.map(function (f) {
          return '<li><span class="w-sev w-sev-' + f[3] + '">' + (f[3] === 'hi' ? 'kills credibility' : 'softens impact') + '</span>' +
            '<span class="w-fx"><s>' + esc(f[0]) + '</s> <span class="w-to">to</span> <b>' + esc(f[1]) + '</b></span>' +
            '<span class="w-pat">' + esc(f[2]) + '</span></li>';
        }).join('') + '</ul>' +
        '<p class="w-diff-h">After</p><p class="w-diff-p w-after">' + fmt('This month we look at [three creator stories] that use remote recording. Reply with your ideas.') + '</p>' +
        '<p class="w-dens">' + fmt('[n] tells in [n] words: under the rewrite line, so it fixed them in place.') + '</p>' +
        '</div>';
    },

    build: function () {
      var name = '[competitor-page-watch]';
      function tl(cls, glyph, html) {
        return '<p class="w-tl' + (cls ? ' w-tl-' + cls : '') + '">' +
          (glyph ? '<span class="w-tl-g" aria-hidden="true">' + glyph + '</span>' : '') +
          '<span class="w-tl-x">' + html + '</span></p>';
      }
      return '<div class="w-term" role="group" aria-label="Files and checks">' +
        tl('add', '+', fmt('.claude/skills/' + name + '/SKILL.md')) +
        tl('add', '+', 'evals/routing.jsonl <em>one new routing case</em>') +
        tl('mod', '~', 'CLAUDE.md <em>one new Task Routing row</em>') +
        tl('cmd', '$', fmt('python3 .claude/skills/agent-builder/scripts/validate_skill.py .claude/skills/' + name)) +
        tl('ok', '', 'RESULT: PASS (0 warning(s))') +
        tl('cmd', '$', 'python3 scripts/eval_routing.py') +
        tl('', '', 'Draft PR opened. Schedule added after one tested real run.') +
        '</div><p class="w-cap">The skill name is a sample.</p>';
    },

    investigation: function () {
      return '<div class="w-paper"><div class="w-paper-top"><p class="w-paper-h">Investigation</p><span class="w-state">Depth-first: paid, organic, website</span></div>' +
        '<div class="w-secs w-secs-1">' +
        sec('Answer', lines(['[One line: what moved, and the most likely reason]'])) +
        sec('Evidence', lines(['[figure], from Rivermind, as of [date]', '[figure], from Windsor.ai, as of [date]'])) +
        sec('Likely cause', lines(['[cause, or "not established"]'])) +
        sec('Recommended action', lines(['[action], owner [name]'])) +
        sec('Gaps', lines(['[what it could not check, and why]'])) +
        '</div></div>';
    },

    overview: function () {
      return '<div class="w-paper"><p class="w-paper-h">About your team</p><div class="w-secs w-secs-1">' +
        sec('Who the team is', lines(["Abel Grünfeld's marketing org: Growth, Brand, Marketing, AI Marketing and Growth Initiatives"])) +
        sec('Systems', lines(['Owned, such as HubSpot, Chili Piper and Trendemon. Depended on, such as Rivermind and the Data Team.'])) +
        sec('How we work', '<p>Tasks go through ' + cmd('pm-story') + '. Writes wait for your yes. Data questions go to ' + cmd('rivermind:ask') + ' first.</p>') +
        sec('What Claude can do', lines(['[skill categories, from the routing table]'])) +
        sec('Where to start', lines(['PHILOSOPHY.md, then the system docs you need'])) +
        '</div></div>';
    }
  };

  /* ---------- state ---------- */
  var cur = null;       // example key
  var step = 1;         // 1..N
  var playing = false;
  var timer = 0;
  var typer = 0;
  var manual = false;   // true once the viewer picks a tab by hand (reset on role change)

  /* ---------- rendering ---------- */
  function readCount(ex, joiner) {
    var files = 0, skills = 0, checks = 0;
    ex.reads.forEach(function (r) {
      if (r[2] === 'skill') skills++;
      else if (r[2] === 'check') checks++;
      else files++;
    });
    var parts = [];
    if (files) parts.push(files + (files === 1 ? ' file' : ' files'));
    if (skills) parts.push(skills + (skills === 1 ? ' skill' : ' skills'));
    if (checks) parts.push('a toolchain check');
    return parts.join(joiner || ', ');
  }
  function sums(ex) {
    return [ex.s1, ex.skills.map(function (s) { return '/' + s; }).join(' then '), readCount(ex), ex.stop.sum, ex.s5];
  }
  function narrs(ex) { return [ex.n1, ex.n2, ex.n3, ex.n4, ex.n5]; }

  function renderSide() {
    var ex = EX[cur];
    var mt = meta(cur);
    var mine = roleKey() === cur;
    var who = mt.org === mt.label ? mt.label : mt.org + ' · ' + mt.label;
    whoEl.innerHTML = esc(who) + (mine ? ' <span class="w-yours">Your role</span>' : '');
    skillsEl.innerHTML = ex.skills.map(cmd).join('<span class="w-then">then</span>');
    var s = sums(ex);
    stepsEl.innerHTML = STEP_T.map(function (t, i) {
      return '<li class="w-step" data-i="' + (i + 1) + '"><button type="button" class="w-step-btn" data-step="' + (i + 1) + '">' +
        '<span class="w-num" aria-hidden="true"><span class="w-n">' + (i + 1) + '</span><span class="w-c">' + I.check + '</span></span>' +
        '<span class="w-step-txt"><span class="sr-only">Step ' + (i + 1) + ': </span><span class="w-step-t">' + esc(t) + '</span>' +
        '<span class="w-step-s">' + esc(s[i]) + '</span></span></button></li>';
    }).join('');
  }

  function renderSteps() {
    var all = reduced();
    [].forEach.call(stepsEl.children, function (li) {
      var i = +li.getAttribute('data-i');
      li.classList.toggle('is-active', i === step);
      li.classList.toggle('is-done', all ? i !== step : i < step);
      li.classList.toggle('is-todo', !all && i > step);
      var b = li.firstChild;
      if (i === step) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
    });
  }

  function renderNarr() {
    var ex = EX[cur];
    narrEl.innerHTML = '<p class="w-narr-k">Step ' + step + ' of ' + N + '</p>' +
      '<h3 class="w-narr-t">' + esc(STEP_T[step - 1]) + '</h3>' +
      '<p class="w-narr-b">' + prose(narrs(ex)[step - 1]) + '</p>';
  }

  function blockReq(ex, typed) {
    var vis = typed === undefined ? fmt(ex.request) : esc(typed);
    return '<p class="w-lbl">You</p><p class="w-req"><span class="w-prompt" aria-hidden="true">&gt;</span>' +
      (typed === undefined
        ? '<span class="w-req-t">' + vis + '</span>'
        : '<span class="sr-only">' + esc(ex.request) + '</span><span class="w-req-t" aria-hidden="true">' + vis + '</span><span class="w-caret" aria-hidden="true"></span>') +
      '</p>';
  }
  function blockRoute(ex) {
    return '<p class="w-lbl">Picked up by</p><div class="w-picks">' + ex.picks.map(function (p, i) {
      return (i ? '<span class="w-then w-then-b">then</span>' : '') +
        '<div class="w-pick"><span class="cmd w-cmd-lg">/' + esc(p.s) + '</span>' +
        '<span class="w-match">Its description lists <mark>“' + esc(p.m) + '”</mark></span></div>';
    }).join('') + '</div><p class="w-bnote">' + prose(ex.note) + '</p>';
  }
  function blockReads(ex) {
    return '<p class="w-lbl">Reads</p><ul class="w-reads">' + ex.reads.map(function (r, i) {
      var k = r[2] || 'file';
      return '<li class="w-read w-read-' + k + '" style="--k:' + i + '"><span class="w-ri">' + (k === 'check' ? I.tool : (I[k] || I.file)) + '</span>' +
        '<span class="w-rt"><span class="w-rp">' + esc(r[0]) + '</span><span class="w-rn">' + esc(r[1]) + '</span></span></li>';
    }).join('') + '</ul>';
  }
  function blockStop(ex) {
    var st = ex.stop;
    return '<div class="w-stop-h"><span class="w-stop-i">' + (I[st.kind] || I.ask) + '</span>' + esc(st.title) + '</div>' +
      '<ul class="w-stop-l">' + st.lines.map(function (l) { return '<li>' + prose(l) + '</li>'; }).join('') + '</ul>' +
      (st.reply ? '<p class="w-reply"><span>' + esc(st.reply[0]) + '</span>' + esc(st.reply[1]) + '</p>' : '');
  }
  function blockOut(ex) {
    return '<p class="w-illus">' + I.info + 'Illustrative. Format taken from the skill file.</p>' + OUT[ex.out]();
  }
  function compact(i, ex) {
    var t;
    if (i === 2) t = 'Picked up by ' + ex.skills.map(cmd).join(' then ');
    else if (i === 3) t = 'Loaded ' + esc(readCount(ex, ' and '));
    else t = esc(ex.stop.sum);
    return '<div class="w-blk w-compact" data-b="' + i + '"><span class="w-ck">' + I.check + '</span><span>' + t + '</span></div>';
  }
  function full(i, ex, extra) {
    var kind = ['req', 'route', 'reads', 'stop', 'out'][i - 1];
    var body = i === 1 ? blockReq(ex) : i === 2 ? blockRoute(ex) : i === 3 ? blockReads(ex) : i === 4 ? blockStop(ex) : blockOut(ex);
    var cls = 'w-blk w-b-' + kind + (i === 4 ? ' w-stop-' + ex.stop.kind : '') + (extra || '');
    return '<div class="' + cls + '" data-b="' + i + '">' + body + '</div>';
  }

  function stopTyping() { if (typer) { clearInterval(typer); typer = 0; } }

  // The log scrolls internally on wide screens. Keep the current block in view,
  // showing the history above it when it fits. On phones the log does not
  // scroll, so only a viewer's own click (reduced motion) moves the page.
  function revealCurrent(fromClick) {
    var b = logEl.querySelector('.is-current');
    if (!b) return;
    if (logEl.scrollHeight > logEl.clientHeight + 1) {
      var want = b.offsetTop + b.offsetHeight - logEl.clientHeight + 14;
      if (b.offsetHeight > logEl.clientHeight - 28) want = b.offsetTop - 14;
      logEl.scrollTop = Math.max(0, want);
    } else if (fromClick && reduced() && b.scrollIntoView) {
      b.scrollIntoView({ block: 'nearest' });
    }
  }

  function renderLog(animate, typeIt, fromClick) {
    stopTyping();
    var ex = EX[cur];
    var html = '';
    if (reduced()) {
      for (var a = 1; a <= N; a++) html += full(a, ex, a === step ? ' is-current' : '');
      logEl.innerHTML = html;
      revealCurrent(fromClick);
      return;
    }
    for (var i = 1; i <= step; i++) {
      if (i === step) html += full(i, ex, ' is-current' + (animate ? ' w-in' : ''));
      else if (i === 1) html += full(1, ex, ' is-past');
      else html += compact(i, ex);
    }
    for (var g = step + 1; g <= N; g++) {
      html += '<div class="w-blk w-ghost" aria-hidden="true"><span class="w-gn">' + g + '</span>' + esc(STEP_T[g - 1]) + '</div>';
    }
    if (step === 1) html += '<p class="w-ghost-hint">Press Play to run the rest, or pick a step.</p>';
    logEl.innerHTML = html;
    revealCurrent(fromClick);
    if (typeIt && step === 1) typeRequest(ex);
  }

  function typeRequest(ex) {
    var blk = logEl.querySelector('.w-b-req');
    if (!blk) return;
    var text = ex.request;
    var n = 0;
    var per = Math.max(14, Math.min(34, 1100 / text.length));
    blk.innerHTML = blockReq(ex, '');
    var vis = blk.querySelector('.w-req-t');
    typer = setInterval(function () {
      n += 1;
      if (n >= text.length) {
        stopTyping();
        blk.innerHTML = blockReq(ex);
        return;
      }
      vis.textContent = text.slice(0, n);
    }, per);
  }
  function typeDuration(ex) { return Math.max(14, Math.min(34, 1100 / ex.request.length)) * ex.request.length; }

  function renderControls() {
    var rm = reduced();
    playBtn.hidden = rm;
    replayBtn.hidden = rm;
    if (rmNote) rmNote.hidden = !rm;
    var atEnd = step >= N;
    playBtn.innerHTML = (playing ? I.pause + '<span>Pause</span>' : I.play + '<span>Play</span>');
    playBtn.setAttribute('aria-disabled', !playing && atEnd ? 'true' : 'false');
    nextBtn.innerHTML = '<span>Next step</span>' + I.next;
    nextBtn.setAttribute('aria-disabled', atEnd ? 'true' : 'false');
    replayBtn.innerHTML = I.replay + '<span>Replay</span>';
  }

  function go(n, opts) {
    opts = opts || {};
    step = Math.max(1, Math.min(N, n));
    renderSteps();
    renderNarr();
    renderLog(!!opts.animate, !!opts.type, !!opts.click);
    renderControls();
    if (!opts.silent) announce('Step ' + step + ' of ' + N + ': ' + STEP_T[step - 1] + '. ' + sums(EX[cur])[step - 1]);
  }

  /* ---------- playback ---------- */
  function dwell(n) {
    var ex = EX[cur];
    if (n === 1) return 1700;
    if (n === 3) return 1500 + 260 * ex.reads.length;
    if (n === 4) return 3000;
    return 2300;
  }
  function stopPlay() {
    playing = false;
    if (timer) { clearTimeout(timer); timer = 0; }
    renderControls();
  }
  function schedule(ms) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(function () {
      timer = 0;
      if (!playing) return;
      if (step < N) {
        go(step + 1, { animate: true });
        if (step < N) schedule(dwell(step));
        else stopPlay();
      } else {
        stopPlay();
      }
    }, ms);
  }
  function play() {
    if (reduced()) return;
    if (step >= N) { replay(); return; }
    playing = true;
    renderControls();
    schedule(650);
  }
  function replay() {
    if (reduced()) { go(1); return; }
    stopPlay();
    go(1, { animate: true, type: true });
    playing = true;
    renderControls();
    schedule(typeDuration(EX[cur]) + dwell(1));
  }

  /* ---------- tabs ---------- */
  function markMine() {
    var mk = roleKey();
    tabs.forEach(function (t) {
      var on = t.getAttribute('data-w') === mk;
      t.classList.toggle('is-mine', on);
      var sr = t.querySelector('.w-mine-sr');
      if (on && !sr) {
        sr = document.createElement('span');
        sr.className = 'sr-only w-mine-sr';
        sr.textContent = ', your role';
        t.appendChild(sr);
      } else if (!on && sr) {
        t.removeChild(sr);
      }
    });
  }

  // Scroll only the tab strip (never the page) so the selected tab is in view.
  function keepTabVisible(t) {
    var box = tablist;
    if (box.scrollWidth <= box.clientWidth + 1) return;
    var br = box.getBoundingClientRect();
    var tr = t.getBoundingClientRect();
    if (!br.width) return;
    if (tr.left < br.left + 8) box.scrollLeft -= (br.left - tr.left) + 24;
    else if (tr.right > br.right - 8) box.scrollLeft += (tr.right - br.right) + 24;
  }

  function select(key, opts) {
    opts = opts || {};
    if (!EX[key]) key = 'any';
    stopPlay();
    cur = key;
    var selTab = null;
    tabs.forEach(function (t) {
      var on = t.getAttribute('data-w') === key;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      if (on) selTab = t;
    });
    if (selTab) {
      panel.setAttribute('aria-labelledby', selTab.id);
      keepTabVisible(selTab);
    }
    renderSide();
    // Reduced motion shows every step at once; otherwise start on the request.
    go(1, { silent: true });
    if (opts.announce) {
      announce('Showing the ' + meta(key).label + ' example, ' + EX[key].skills.map(function (s) { return '/' + s; }).join(' then ') + '. Step 1 of ' + N + ': ' + STEP_T[0] + '.');
    }
  }

  tablist.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[role="tab"]') : null;
    if (!t || !tablist.contains(t)) return;
    manual = true;
    if (t.getAttribute('data-w') !== cur) select(t.getAttribute('data-w'), { announce: true });
  });
  tablist.addEventListener('keydown', function (e) {
    var t = e.target.closest ? e.target.closest('[role="tab"]') : null;
    if (!t || e.altKey || e.ctrlKey || e.metaKey) return;
    var i = tabs.indexOf(t);
    var j = -1;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') j = (i + 1) % tabs.length;
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') j = (i - 1 + tabs.length) % tabs.length;
    else if (e.key === 'Home') j = 0;
    else if (e.key === 'End') j = tabs.length - 1;
    if (j < 0) return;
    e.preventDefault();
    e.stopPropagation();
    manual = true;
    tabs[j].focus();
    select(tabs[j].getAttribute('data-w'), { announce: true });
  });

  /* ---------- controls ---------- */
  stepsEl.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-step]') : null;
    if (!b) return;
    stopPlay();
    go(+b.getAttribute('data-step'), { animate: true, click: true });
  });
  playBtn.addEventListener('click', function () {
    if (playing) { stopPlay(); announce('Paused at step ' + step + ' of ' + N + '.'); return; }
    if (playBtn.getAttribute('aria-disabled') === 'true') return;
    play();
  });
  nextBtn.addEventListener('click', function () {
    if (nextBtn.getAttribute('aria-disabled') === 'true') return;
    stopPlay();
    go(step + 1, { animate: true, click: true });
  });
  replayBtn.addEventListener('click', function () { replay(); });

  /* ---------- wiring to the deck ---------- */
  function syncToRole() {
    markMine();
    var k = roleKey();
    if (k !== cur) select(k);
    else renderSide(), go(step, { silent: true });
  }

  var m = M();
  if (m && typeof m.on === 'function') {
    m.on('slide', function (e) {
      if (e && e.id === 'worked') {
        markMine();
        if (!manual) syncToRole();
        else renderSide(), renderSteps();
      } else {
        stopPlay();
        stopTyping();
      }
    });
    m.on('role', function () {
      manual = false;
      syncToRole();
    });
  }
  var onMotion = function () { stopPlay(); if (cur) { renderSteps(); renderLog(false); renderControls(); } };
  if (m && typeof m.on === 'function') m.on('motion', onMotion);
  else if (mq) {
    if (mq.addEventListener) mq.addEventListener('change', onMotion);
    else if (mq.addListener) mq.addListener(onMotion);
  }

  markMine();
  select(roleKey());
})();
