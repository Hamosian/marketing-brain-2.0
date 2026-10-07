/* 05-roles.js: the canonical role table (owned by the path area).
   MBT.ROLES   {key: role}      role = {key, org, label, short, example, exampleTitle, starters:[{cmd, prompt, why}], weights:[skill]}
   MBT.TEAMS   [{key, label, scope, roles:[roleKey]}]   display order for the path picker
   MBT.EXP     {new|some|fluent: {label, note}}          experience levels
   Every starter and weight was checked against .claude/skills/<name>/SKILL.md (rivermind:ask is the
   rivermind plugin skill named in CLAUDE.md). starters[0] is the recommended first run after
   "tell me about the team". Person-owned skills are never starters and never weights. */
(function () {
  'use strict';
  var MBT = window.MBT = window.MBT || {};

  var BRAIN_WHY = 'Start here for broad or cross-system asks: it picks the skills and pulls the answer together.';

  MBT.ROLES = {
    any: {
      key: 'any', org: 'Not sure yet', label: 'Not sure yet', short: 'The basics',
      example: 'any', exampleTitle: 'Tell me about the team',
      starters: [
        { cmd: '/team-intro', prompt: 'tell me about the team',
          why: 'A read-only overview built from the repo. If it answers with real team context, you are connected.' },
        { cmd: '/list-skills', prompt: 'what skills do you have?',
          why: 'Lists every workflow, read live from the skills folder.' },
        { cmd: '/marketing-brain', prompt: 'I need to [your task]. Where do I start?',
          why: BRAIN_WHY }
      ],
      weights: ['marketing-brain', 'rivermind:ask', 'riverside-product-knowledge', 'team-intro', 'list-skills', 'retro']
    },

    seo: {
      key: 'seo', org: 'Growth', label: 'SEO and AI search', short: 'SEO',
      example: 'seo', exampleTitle: 'How did organic search do last week?',
      starters: [
        { cmd: '/seo-ai-search-agent', prompt: 'why did organic traffic to [page] drop?',
          why: 'Diagnoses organic and AI-search visibility: Search Console, Ahrefs, indexing, content gaps. It changes nothing.' },
        { cmd: '/organic-dashboard', prompt: 'refresh the organic analytics dashboard',
          why: 'The monthly view: rankings, Search Console and the organic funnel. A refresh updates the team\'s shared dashboard page.' },
        { cmd: '/weekly-seo-report', prompt: 'run the weekly seo report',
          why: 'Updates the team\'s weekly report page and DMs Amir. It already runs every Thursday, so run it by hand only when asked.' }
      ],
      weights: ['weekly-seo-report', 'organic-dashboard', 'seo-ai-search-agent', 'seo-de-report', 'gsc-freshness-check', 'webflow-asset-audit', 'webflow-locale-publish-queue']
    },

    paid: {
      key: 'paid', org: 'Growth', label: 'Paid acquisition', short: 'Paid',
      example: 'paid', exampleTitle: 'Why did CPA jump on one Google Ads account?',
      starters: [
        { cmd: '/paid-acquisition-agent', prompt: 'check pacing and wasted spend across our paid campaigns',
          why: 'Campaign health, pacing and wasted spend across Google, Meta, LinkedIn and Bing. Any change waits for your yes.' },
        { cmd: '/page-cro', prompt: 'this page is not converting: [url]. What would you change?',
          why: 'Finds why a page is not converting and can shape the A/B test.' }
      ],
      weights: ['paid-acquisition-agent', 'page-cro', 'measurement-agent', 'campaign-agent', 'marketing-psychology', 'marketing-website-page-qa']
    },

    creator: {
      key: 'creator', org: 'Growth', label: 'Creator marketing and growth channels', short: 'Creator',
      example: 'creator', exampleTitle: 'Plan next month\'s creator affiliate push',
      starters: [
        { cmd: '/marketing-brain', prompt: 'help me plan [campaign]: what do we already know, and what should run it?',
          why: BRAIN_WHY },
        { cmd: '/content-agent', prompt: 'draft a newsletter announcing [launch], on brand',
          why: 'Drafts emails, newsletters, announcements and decks with the Riverside brand rules applied.' }
      ],
      weights: ['content-agent', 'script-doctor', 'marketing-brain', 'podcast-transcript', 'linkedin-best-practices-2026', 'marketing-psychology']
    },

    mops: {
      key: 'mops', org: 'Growth', label: 'Marketing operations', short: 'MOPs',
      example: 'mops', exampleTitle: 'Open a ticket for a homepage top bar',
      starters: [
        { cmd: '/pm-story', prompt: 'open a Marketing Ops ticket for [the ask]',
          why: 'Writes the ticket (why, what, done when, open questions) and files it on the board that does the work.' },
        { cmd: '/ticket-hygiene', prompt: 'run a ticket hygiene sweep',
          why: 'Flags duplicates, tickets on the wrong board and missing briefs. The sweep changes nothing without your approval.' },
        { cmd: '/hubspot-workflow-qa', prompt: 'QA this HubSpot workflow before launch: [link]',
          why: 'A structured review of enrollment, branching, sends and integrations, ending in a sign-off.' }
      ],
      weights: ['pm-story', 'ticket-hygiene', 'hubspot-workflow-qa', 'mops-backlog-review', 'marketing-ops-automation-agent', 'data-team-request', 'monday-agent', 'good-morning']
    },

    sdr: {
      key: 'sdr', org: 'Growth', label: 'Inbound SDR', short: 'SDR',
      example: 'sdr', exampleTitle: 'Fact-check a reply before it reaches a lead',
      starters: [
        { cmd: '/hubspot-agent', prompt: 'what do we have in HubSpot on [company]?',
          why: 'Looks up contacts, companies, deals and Pre-Ops. Nothing is written without your yes.' },
        { cmd: '/riverside-product-knowledge', prompt: 'what plan is Magic Clips on?',
          why: 'How a feature works and which plan it is on, from the Help Center. It cannot see a live account.' },
        { cmd: '/demo-reply-fact-check', prompt: 'fact-check the product claims in this draft: [paste]',
          why: 'Marks every product claim VERIFIED, UNVERIFIED or CONTRADICTED before it reaches a lead.' }
      ],
      weights: ['hubspot-agent', 'riverside-product-knowledge', 'demo-reply-fact-check', 'preop-data-intelligence', 'gong-calls-explorer', 'lifecycle-agent']
    },

    'brand-design': {
      key: 'brand-design', org: 'Brand', label: 'Design and creative direction', short: 'Design',
      example: 'brand-design', exampleTitle: 'Build a six-slide campaign readout deck',
      starters: [
        { cmd: '/riverside-presentation', prompt: 'build a Riverside deck from this outline: [paste]',
          why: 'Builds or edits a .pptx in the official Riverside look.' },
        { cmd: '/riverside-brand-guidelines', prompt: 'check this against the Riverside brand guidelines: [paste or attach]',
          why: 'The color, type and tone rules Brand owns, applied to anyone\'s deck or doc.' },
        { cmd: '/impeccable', prompt: '/impeccable critique [page or file]',
          why: 'A design pass on a built page or dashboard: critique, audit, layout, type, polish.' }
      ],
      weights: ['riverside-brand-guidelines', 'riverside-presentation', 'impeccable', 'riverside-ux-patterns', 'webflow-asset-audit', 'webflow-accessibility-audit']
    },

    'brand-video': {
      key: 'brand-video', org: 'Brand', label: 'Motion and performance video', short: 'Video',
      example: 'brand-video', exampleTitle: 'Take a new video brief to a live project',
      starters: [
        { cmd: '/script-doctor', prompt: 'review this ad script: where does the argument break? [paste]',
          why: 'Maps a script beat by beat, finds the holes and checks audience fit. No line edits.' },
        { cmd: '/video-project-intake', prompt: 'stress-test this video brief: [link or paste]',
          why: 'Check a brief is ready before it goes to Raz: it grades it against the Creative Video Brief template and lists the gaps.' }
      ],
      weights: ['script-doctor', 'video-project-intake', 'riverside-brand-guidelines', 'podcast-transcript', 'marketing-psychology', 'content-agent']
    },

    pmm: {
      key: 'pmm', org: 'Marketing', label: 'Product marketing', short: 'PMM',
      example: 'pmm', exampleTitle: 'A launch email with every product claim checked',
      starters: [
        { cmd: '/content-agent', prompt: 'draft the launch announcement for [feature], on brand',
          why: 'Drafts launch emails, announcements, docs and decks with the Riverside brand rules applied.' },
        { cmd: '/demo-reply-fact-check', prompt: 'fact-check the product claims in this launch copy: [paste]',
          why: 'The claim checker for any copy that says what Riverside does, not only demo replies.' },
        { cmd: '/value-proposition-canvas', prompt: 'build a value proposition canvas for [segment]',
          why: 'Jobs, pains and gains for a segment, seeded from our voice-of-customer research, then a fit check.' }
      ],
      weights: ['demo-reply-fact-check', 'value-proposition-canvas', 'content-agent', 'are-we-really-different', 'riverside-product-knowledge', 'marketing-council', 'launch-webinar', 'win-loss-pricing-analyzer']
    },

    content: {
      key: 'content', org: 'Marketing', label: 'Content, social, community', short: 'Content',
      example: 'content', exampleTitle: 'Write a newsletter intro, then make it sound human',
      starters: [
        { cmd: '/content-agent', prompt: 'draft a newsletter on [topic] for [audience]',
          why: 'Drafts newsletters, emails and announcements in the Riverside tone, with the brand rules applied.' },
        { cmd: '/linkedin-best-practices-2026', prompt: 'how should we structure LinkedIn posts for reach in 2026?',
          why: 'Current LinkedIn know-how: profiles, the algorithm, search and content strategy.' },
        { cmd: '/de-ai', prompt: 'make this sound human: [paste]',
          why: 'One cleaning pass that strips the AI tells from a finished draft.' }
      ],
      weights: ['content-agent', 'de-ai', 'linkedin-best-practices-2026', 'critique', 'script-doctor', 'podcast-transcript']
    },

    ai: {
      key: 'ai', org: 'AI Marketing', label: 'AI marketing', short: 'AI',
      example: 'ai', exampleTitle: 'Turn a weekly check into a routine',
      starters: [
        { cmd: '/agent-builder', prompt: 'turn this repeat task into a skill: [describe it]',
          why: 'Interviews you, writes a lint-clean skill, and opens the PR to ship it.' },
        { cmd: '/skill-eval', prompt: 'run the skill evals',
          why: 'Checks that requests still route to the skill that owns them, with a fix proposed for every miss.' },
        { cmd: '/marketing-brain', prompt: 'help me scope [initiative] across our systems',
          why: BRAIN_WHY }
      ],
      weights: ['agent-builder', 'skill-eval', 'skill-audit', 'retro', 'health-check', 'curious-intern', 'marketing-brain']
    },

    initiatives: {
      key: 'initiatives', org: 'Growth Initiatives', label: 'Growth initiatives', short: 'Initiatives',
      example: 'initiatives', exampleTitle: 'Why do sign-ups look soft this week?',
      starters: [
        { cmd: '/marketing-brain', prompt: 'size up [growth bet]: what do our systems already tell us?',
          why: BRAIN_WHY },
        { cmd: '/marketing-council', prompt: 'convene the council on [decision]',
          why: 'Debates a direction decision from opposing expert lenses, with a named dissenter, then recommends.' },
        { cmd: '/rivermind:ask', prompt: 'what moved sign-ups last month?',
          why: 'The analytics team\'s validated data layer. Every data question starts here.' }
      ],
      weights: ['marketing-council', 'rivermind:ask', 'marketing-brain', 'value-proposition-canvas', 'are-we-really-different', 'measurement-agent', 'win-loss-pricing-analyzer']
    }
  };

  MBT.TEAMS = [
    { key: 'growth', label: 'Growth', scope: 'SEO, paid, creator, MOPs, SDR', roles: ['seo', 'paid', 'creator', 'mops', 'sdr'] },
    { key: 'brand', label: 'Brand', scope: 'Design, motion, video', roles: ['brand-design', 'brand-video'] },
    { key: 'marketing', label: 'Marketing', scope: 'Product marketing, content, social', roles: ['pmm', 'content'] },
    { key: 'ai', label: 'AI Marketing', scope: 'AI-driven marketing work', roles: ['ai'] },
    { key: 'initiatives', label: 'Growth Initiatives', scope: 'Cross-cutting growth bets', roles: ['initiatives'] },
    { key: 'unsure', label: 'Not sure yet', scope: 'Start with the basics', roles: ['any'] }
  ];

  MBT.EXP = {
    'new': { label: 'New to Claude Code',
      note: 'Full path, about 15 minutes. Setup comes before your first command, so nothing is assumed.' },
    some: { label: 'I use Claude, not the Brain yet',
      note: 'You know Claude. Watch for what the repo adds: team context, skills, and the rules it follows.' },
    fluent: { label: 'I already run skills',
      note: 'Skip the story if you like and go straight to routing practice.' }
  };

  /* team key for a role key */
  MBT.teamOf = function (roleKey) {
    for (var i = 0; i < MBT.TEAMS.length; i++) {
      if (MBT.TEAMS[i].roles.indexOf(roleKey) !== -1) return MBT.TEAMS[i].key;
    }
    return null;
  };
})();
