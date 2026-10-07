const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber, TableOfContents, PageBreak, ExternalHyperlink
} = require('docx');

// Riverside brand (light-mode print tints)
const PURPLE='7C5CFF', NEAR_BLACK='0F0F14', WHITE='FFFFFF', DARK_GRAY='1C1C24',
      MID_GRAY='2A2A35', LIGHT_GRAY='E6E6EB', PURPLE_LIGHT='EDE8FF', PURPLE_MIST='F7F5FF';
const FONT='Inter';
const CONTENT_W=9360;

const border = c => ({ style: BorderStyle.SINGLE, size: 1, color: c||LIGHT_GRAY });
const cellBorders = { top:border(), bottom:border(), left:border(), right:border() };
const cellMargins = { top:60, bottom:60, left:100, right:100 };

function body(text, opts={}) {
  return new Paragraph({ spacing:{after:120, line:276}, ...opts.par,
    children:[ new TextRun({ text, font:FONT, size:21, color:NEAR_BLACK, ...opts.run }) ] });
}
// rich paragraph: array of [text, {bold,color}]
function rich(parts, opts={}) {
  return new Paragraph({ spacing:{after:120, line:276}, ...opts.par,
    children: parts.map(([t,o={}]) => new TextRun({ text:t, font:FONT, size:21,
      color:o.color||NEAR_BLACK, bold:!!o.bold })) });
}
function h1(text){
  return new Paragraph({ heading:HeadingLevel.HEADING_1, spacing:{before:300, after:120},
    border:{ bottom:{ style:BorderStyle.SINGLE, size:18, color:PURPLE, space:4 } },
    children:[ new TextRun({ text, font:FONT, size:30, bold:true, color:NEAR_BLACK }) ] });
}
function h2(text){
  return new Paragraph({ heading:HeadingLevel.HEADING_2, spacing:{before:260, after:100},
    children:[ new TextRun({ text, font:FONT, size:24, bold:true, color:PURPLE }) ] });
}
function h3(text){
  return new Paragraph({ heading:HeadingLevel.HEADING_3, spacing:{before:180, after:80},
    children:[ new TextRun({ text, font:FONT, size:21, bold:true, color:DARK_GRAY }) ] });
}
function bullet(parts){
  const arr = Array.isArray(parts)?parts:[[parts,{}]];
  return new Paragraph({ numbering:{reference:'b', level:0}, spacing:{after:80, line:276},
    children: arr.map(([t,o={}]) => new TextRun({ text:t, font:FONT, size:21, color:o.color||NEAR_BLACK, bold:!!o.bold })) });
}
function numbered(text){
  return new Paragraph({ numbering:{reference:'n', level:0}, spacing:{after:80, line:276},
    children:[ new TextRun({ text, font:FONT, size:21, color:NEAR_BLACK }) ] });
}
function tcell(text, widthDxa, {head=false, alt=false, boldText=false, alignRight=false, color}={}) {
  return new TableCell({
    borders:cellBorders, margins:cellMargins, width:{size:widthDxa, type:WidthType.DXA},
    verticalAlign: VerticalAlign.CENTER,
    shading: head ? {fill:NEAR_BLACK, type:ShadingType.CLEAR} : (alt ? {fill:PURPLE_LIGHT, type:ShadingType.CLEAR} : undefined),
    children:[ new Paragraph({ alignment: alignRight?AlignmentType.RIGHT:AlignmentType.LEFT, spacing:{after:0, line:264},
      children:[ new TextRun({ text:String(text), font:FONT, size:18,
        bold: head||boldText, color: color || (head?WHITE:NEAR_BLACK) }) ] }) ]
  });
}
// rows: array of arrays; rightCols: set of column indices to right-align
function table(headers, rows, colWidths, {rightCols=[]}={}) {
  const headRow = new TableRow({ tableHeader:true, children: headers.map((h,i)=> tcell(h, colWidths[i], {head:true, alignRight:rightCols.includes(i)})) });
  const bodyRows = rows.map((r,ri)=> new TableRow({ children: r.map((c,i)=> tcell(c, colWidths[i], {alt: ri%2===1, alignRight:rightCols.includes(i)})) }));
  return new Table({ width:{size:CONTENT_W, type:WidthType.DXA}, columnWidths:colWidths, rows:[headRow, ...bodyRows] });
}
const spacer = () => new Paragraph({ spacing:{after:60}, children:[] });

const logoPath = path.join(__dirname, 'riverside_logo.png');
const outPath = path.join(__dirname, 'INBOUND-SQL-WITHOUT-MQL-ANALYSIS.docx');

let logo;
try {
  logo = fs.readFileSync(logoPath);
} catch (err) {
  console.error(`Error: could not load logo file (${logoPath}):`, err.message);
  process.exit(1);
}

const children = [];

// Title block
children.push(new Paragraph({ spacing:{after:60}, children:[
  new TextRun({ text:'Inbound SQLs without MQLs', font:FONT, size:40, bold:true, color:NEAR_BLACK })
]}));
children.push(new Paragraph({ spacing:{after:40}, border:{ bottom:{style:BorderStyle.SINGLE, size:18, color:PURPLE, space:4} }, children:[
  new TextRun({ text:'Root-cause analysis and attribution framework', font:FONT, size:24, color:PURPLE, bold:true })
]}));
children.push(rich([
  ['Prepared 2026-06-14. Source data: ',{color:MID_GRAY}],
  ['Results_2026-06-08-1117.csv',{color:MID_GRAY,bold:true}],
  [' (652 inbound-classified SQLs with no linked marketing MQL). Analysis artifacts in sql-mql-attribution/.',{color:MID_GRAY}]
]));

// Exec summary
children.push(h1('Executive summary'));
children.push(body('We analyzed all 652 inbound SQLs (completed intro meetings, Last Touch Source = Inbound) that have no linked marketing MQL record. Every MQL field in the export is null for all 652 rows, confirming the join to the marketing-lead record fails for the entire population.'));
children.push(body('The single most important finding is that "inbound SQL without an MQL" is largely a definitional and data-capture problem, not a tracking-pixel problem. Riverside runs two different "MQL" concepts that are being treated as one:'));
children.push(numbered('Funnel-stage MQL: a Pre-Op whose Last Touch Source = Inbound. By this definition every one of these 652 SQLs already is an MQL.'));
children.push(numbered('Marketing-attribution MQL: a separate form-submission record carrying first-visit UTM and channel, linked to the SQL by identity (email, anonymous_id, product user_id). This record is missing for all 652.'));
children.push(body('When we classify the 37% of records that carry an AE "how did they hear about us" note, only about 5% of the population are genuine marketing inbound that should have a form-MQL and failed to join. The rest never had a form-MQL by nature: existing product users, referrals, mis-tagged outbound, events, re-engaged old deals.'));
children.push(h3('The honest headline'));
children.push(bullet([['Recoverable to an actual campaign or channel: ',{}],['roughly 31 records (4.8%), about $5.1K won MRR per month. Small.',{bold:true}]]));
children.push(bullet([['The real win is de-polluting the inbound number: ',{}],['about 109 records (16.7%) are not marketing inbound at all and currently distort the Inbound MQL count, MQL-to-SQL conversion, and any CAC or ROAS.',{bold:true}]]));
children.push(bullet([['The durable fix is forward capture: ',{}],['63% of records have no AE source note at all. That capture gap, not a channel mystery, is the largest category.',{bold:true}]]));
children.push(body('The problem is also accelerating: orphan inbound SQLs grew 118 (2023), 134 (2024), 214 (2025), 186 in the first five-and-a-half months of 2026 (about 370 annualized).'));

// Section 1
children.push(h1('1. What the data shows (root-cause analysis)'));
children.push(h2('1.1 The population is genuinely MQL-less and growing'));
children.push(bullet('652 records, all classified inbound, all with completed intro meetings.'));
children.push(bullet('100% have a null MQL across every MQL column. This is a clean left-join miss, not partial data.'));
children.push(bullet('94.5% (616) carry a contact email, so they are identity-joinable. Only 36 (5.5%) have no email and are structurally unrecoverable by identity.'));
children.push(bullet('Funnel outcome: 187 promoted to a deal (28.7%), of which 110 closed won, 61 closed lost, 16 still open.'));
children.push(bullet([['Won revenue with zero marketing attribution: ',{}],['$130,829 MRR per month across the 110 wins, roughly $1.57M ARR.',{bold:true}]]));
children.push(spacer());
children.push(table(
  ['Year','Orphan SQLs','Promoted','Won'],
  [['2023','118','36','21'],['2024','134','43','28'],['2025','214','68','44'],['2026 (to mid-June)','186','40','17']],
  [3360,2200,1900,1900], {rightCols:[1,2,3]}
));
children.push(spacer());
children.push(body('Sized against the funnel (Omni, topic "MQLs to SQLs to Deals", FY2023 to FY2026): there are 14,934 inbound SQLs and 283 outbound SQLs in the period, 15,217 total. The 652 orphans are therefore about 4.4% of all inbound SQLs, roughly 1 in 23. The absolute count grows with the funnel while the rate stays in a 3 to 6% band with a 2026 uptick. The very low outbound SQL count (283, under 2% of the funnel) is itself a symptom: outbound is being under-tagged and absorbed into Inbound.'));
children.push(rich([['Note: ',{bold:true}],['2023-05 alone holds 50 records (36 closed lost), which has the signature of a one-time historical migration batch and should be excluded from trend baselines.',{}]]));

children.push(h2('1.2 Root-cause categories with volume and impact'));
children.push(body('The only attribution signal that survives in this export is the AE free-text field AE_DISCOVERY_HOW_DID_THEY_HEAR_ABOUT_US, populated on 37% (241) of records. We classified those 241 with an LLM pass plus a deterministic keyword pass; the two methods agree on 86.7% of records. The 411 blank records are reported as their own category.'));
children.push(spacer());
children.push(table(
  ['Category','Records','%','Promoted','Won','Won MRR/mo','Email'],
  [
    ['Existing/self-serve product user (PLG)','72','11.0%','32','21','$22,072','68'],
    ['Referral, word of mouth, dark social','58','8.9%','22','14','$17,040','56'],
    ['Outbound mis-sourced as inbound','36','5.5%','3','1','$1,155','36'],
    ['Re-engagement of past or closed-lost','16','2.5%','9','7','$13,442','16'],
    ['Event or field marketing','14','2.1%','2','0','$0','14'],
    ['Digital inbound, MQL join failed','31','4.8%','7','4','$5,104','31'],
    ['AI or LLM sourced','1','0.2%','0','0','$0','0'],
    ['Customer Success sourced','1','0.2%','1','0','$0','1'],
    ['Captured but uninformative','12','1.8%','1','1','$675','12'],
    ['No discovery captured (blank field)','411','63.0%','110','62','$71,342','382'],
    ['Total','652','100%','187','110','$130,829','616'],
  ],
  [2660,920,820,1150,820,1490,500], {rightCols:[1,2,3,4,5,6]}
));
children.push(spacer());
children.push(h3('What each category means and why no MQL exists'));
const catDefs = [
  ['A. PLG existing user. ','Already on Pro, self-serve, or Individual before sales engaged. No marketing form by nature. Examples: "using Pro", "churned account that switched to PRO".'],
  ['B. Referral and word of mouth. ','Personal recommendation, investor or colleague intro, partner or producer referral. Untrackable. Examples: "Recommended by Alexis Ohanian", "investor introduction".'],
  ['C. Outbound mis-sourced. ','Reached via BD or AE cold outreach but the Pre-Op was tagged Inbound. The source label is wrong. Examples: "Cold outreach email from Lauren", "Received a cold call".'],
  ['D. Re-engagement of past deal. ','A prior sales relationship revived, a new Pre-Op cycle. Any MQL sits on a prior cycle. Examples: "Old deal that is reopening", "Past Deal that was marked as Closed-Lost".'],
  ['E. Event and field marketing. ','Met at NAB or conferences, usually a manually created Pre-Op, no digital form. NAB alone appears 8 times.'],
  ['F. Digital inbound, join failed. ','Genuine self-driven digital discovery where an MQL should exist but the identity join failed. The only truly campaign-recoverable category. Examples: "Google Search for podcast recording software".'],
  ['G. AI or LLM sourced. ','Discovery via ChatGPT, Grok. Small today, fastest-growing discovery channel industry-wide.'],
  ['H. Customer Success sourced. ','Existing-customer expansion driven by CS ("CSMQL").'],
  ['I. Uninformative. ','Discovery captured but no usable signal: "Unsure", "Unknown", generic intent with no channel.'],
  ['J. No discovery captured. ','The AE left the field blank. The largest category at 63% and the largest single revenue contributor among orphans. 382 of 411 still have an email, so they are identity-joinable.'],
];
catDefs.forEach(([lab,txt]) => children.push(bullet([[lab,{bold:true,color:PURPLE}],[txt,{}]])));

children.push(h2('1.3 Strategic grouping by what we can do about each'));
children.push(spacer());
children.push(table(
  ['Group','Categories','Records','%','Won MRR/mo'],
  [
    ['Campaign-recoverable (true inbound, join failed)','F','31','4.8%','$5,104'],
    ['De-pollution: remove from inbound credit (debit)','C, H','37','5.7%','$1,155'],
    ['De-pollution: relabel as Product-Led, keep in funnel','A','72','11.0%','$22,072'],
    ['Marketing-influenced, non-form source','B, E, G','73','11.2%','$17,040'],
    ['Inherit prior-cycle attribution','D','16','2.5%','$13,442'],
    ['Capture gap (fix forward)','I, J','423','64.9%','$72,017'],
    ['Structurally unrecoverable (no email)','subset','36','5.5%','n/a'],
  ],
  [3700,1300,1100,860,2400], {rightCols:[2,3,4]}
));
children.push(spacer());
children.push(rich([['Two cautions: ',{bold:true}],['debit versus relabel are different operations. Outbound (36) and CS (1) should be removed from the inbound-marketing credit. PLG (72) should not be deleted, it should stay in the full-funnel SQL count and only be excluded from the marketing-attributable view by filter. Also, the outbound mis-tag is overwhelmingly a 2026 phenomenon: 32 of 36 records were created in 2026, so it must not be subtracted uniformly across history.',{}]]));

// Section 2
children.push(new Paragraph({ children:[new PageBreak()] }));
children.push(h1('2. Recommended attribution framework'));
children.push(body('A tiered waterfall assigns an auditable basis to every one of the 652 SQLs without inventing a channel to fill a cell. Each record lands in exactly one tier. Inferred values are written only to inference columns, never over the locked Pre-Op Last Touch Source or the genuine form-MQL fields.'));
children.push(spacer());
children.push(table(
  ['Tier','Name','Matches on','Assigns','Coverage'],
  [
    ['1','Hard identity stitch','Email, anonymous_id, or product user_id joined to product, web session, and ad-click data. Ad-click id, then signup-before-create, then organic session','Paid (only via ad-click id), Product-Led, or Organic at HIGH. Populates INFERRED_MQL_ID','~99 records (15%); campaign-recoverable slice = 31 digital'],
    ['2','Structural CRM reclassification','BD Owner populated (mis-tag), prior Pre-Op cycle, or CS creator / active subscription','Reclassify to Outbound (debit), inherit prior cycle, or Customer Success. HIGH','~53 records (8%)'],
    ['3','Keyword classification','AE discovery text, unambiguous lexical signatures only','Referral, Event, AI Search at MED. Never Paid','~73 records (11%)'],
    ['4','LLM tie-breaker','Same discovery text, second opinion on Tier 3','Agreement upgrades confidence, disagreement keeps conservative label and flags review','0 net new (quality layer)'],
    ['5','Re-join of blank residual','The 382 blank records with an email','Real form-MQL raises a data-quality alarm. Otherwise Sales-Direct or Unknown, confidence NONE','~382 records (59%)'],
    ['6','Uninformative sink','Discovery present, no usable signal','Sales-Direct or Unknown, retain text','~12 records (2%)'],
    ['7','Unrecoverable flag','No email and no identity key','Flag Unrecoverable, never guessed','~36 records (5.5%)'],
  ],
  [560,1500,2700,2700,1900]
));
children.push(spacer());
children.push(h2('Core business rules'));
const rules = [
  'Disambiguate the two MQLs. Redefine reporting MQL as acquisition_type = Marketing Inbound, not Last Touch Source = Inbound. The current definition is structurally polluted.',
  'Inference never touches source-of-truth fields. Write only to INFERRED_MQL_ID and sibling columns. INFERRED_MQL_ID is populated only where the true MQL_ID is null.',
  'Paid is quarantined behind deterministic evidence. Paid or a campaign can be assigned only via a hard ad-click id timestamped before Pre-Op creation. No free-text, LLM, or aggregate prior may ever write Paid.',
  'Debit versus relabel. Outbound and CS are debited out of the inbound credit. PLG is relabeled but kept in the full-funnel SQL count. Never delete a completed-meeting SQL.',
  'Two report views, never conflated. Marketing-attributable (true form-MQL plus HIGH and MED inferred only) feeds CAC, ROAS, MQL-to-SQL by campaign. Full-funnel (all 652 with basis visible) feeds pipeline and exec funnel volume.',
  'Forward capture beats backfill. Split Last Touch Source into a locked acquisition_type plus a required source_detail enum, auto-detect PLG, outbound, and CS at creation, gate stage advancement on a non-blank source_detail, and add re-engagement inheritance.',
  'Required field alone is not enough. A required picklist gives a non-null value, not a true one. Pair it with auto-detection and a published monthly accuracy match-rate against call notes.',
];
rules.forEach(r=>children.push(numbered(r)));

// Section 3
children.push(h1('3. Estimated reporting improvement'));
children.push(h3('Before'));
children.push(bullet('0 of 652 (0%) carry any source attribution.'));
children.push(bullet('$130,829 won MRR per month sits entirely unattributed.'));
children.push(bullet('The Inbound MQL count includes at least 109 non-marketing records (PLG, outbound, CS) that overstate marketing and depress measured MQL-to-SQL quality.'));
children.push(h3('After'));
children.push(bullet([['Every one of the 652 SQLs carries an auditable attribution_basis. None are silently dropped from the funnel.',{}]]));
children.push(bullet([['Campaign or channel recoverable via identity: ',{}],['about 31 records (4.8%), about $5.1K won MRR per month (3.9% of total). The only slice that returns true campaign credit.',{bold:true}]]));
children.push(bullet([['Correctly removed or relabeled out of marketing inbound: ',{}],['109 records (16.7%), about $23.2K won MRR. The highest-value outcome.',{bold:true}]]));
children.push(bullet([['Assigned a real non-campaign source (referral, event, AI, re-engagement): ',{}],['about 89 records (13.7%), about $30.5K won MRR.',{}]]));
children.push(bullet([['Capture-gap residual that only forward capture fixes durably: ',{}],['about 423 records (64.9%), about $72.0K won MRR.',{}]]));
children.push(body('Sizing against the funnel: the 652 orphans are about 4.4% of the 14,934 inbound SQLs in FY2023 to FY2026, so this is a contained, fixable gap. It is worth fixing because the orphans skew to high-value deals ($1.57M ARR won with no attribution) and the same root causes distort the much larger inbound population too. The Omni funnel topic currently reports every inbound SQL as "MQL present," so it cannot surface the form-MQL gap at all. That blind spot is itself part of the fix.'));

// Section 4
children.push(h1('4. Technical requirements'));
children.push(body('Effort: S small, M medium, L large.'));
children.push(spacer());
children.push(table(
  ['Area','Requirement','Effort'],
  [
    ['Identity layer (dbt)','Build an identity spine keyed on a person surrogate, unioning HubSpot email (normalized, with a review allow-list for role addresses), web anonymous_id, product user_id, contact id. Handle multi-contact Pre-Ops with a canonical contact.','L'],
    ['Candidate model (dbt)','Inferred-MQL candidate model implementing the precedence ladder (ad-click, signup-before-create, first-visit channel, anonymous-id, temporal-nearest within a bounded window). One winner per Pre-Op.','M'],
    ['Backfill and columns (dbt)','Populate INFERRED_MQL_ID only where true MQL_ID is null. Add inferred_channel_group, inferred_source, attribution_confidence, attribution_basis, inference_evidence, inferred_at. Encode the category-to-basis map as a versioned seed.','M'],
    ['Funnel re-point (dbt)','Left-join the funnel model from the SQL grain: attributed_channel_group = coalesce(true, inferred, unattributed). Test that SQL count equals completed-meeting Pre-Op count. Ship the two report views.','M'],
    ['Classification jobs','Productionize the keyword and LLM passes over records with discovery text, with agreement gating and a hard non-paid output constraint. Both passes already exist as artifacts.','M'],
    ['HubSpot fields','Add a locked acquisition_type single-select and a required source_detail enum (~16 values). Keep a small optional free-text note. Migrate the 652 by Record-ID import. Redefine reporting MQL.','M'],
    ['HubSpot workflows','Creation-time auto-detect of PLG, outbound (also non-BD outbound), and CS, re-engagement inheritance on Pre-Op Number Count > 1, and required-property-on-stage gating.','L'],
    ['Validation harness','Held-out test masking true form-MQL links to measure inferred-versus-true channel match rate, stratified to resemble the orphan population. Alarm on any exact form-MQL hit inside this gap.','M'],
    ['Ops and governance','Incremental models on Pre-Op create date, weekly source-quality exceptions view (target under 5%), monthly high-MRR confidence-NONE list. Map every downstream dashboard affected by the MQL redefinition. Assign owners per references/team.md.','S'],
  ],
  [2000,6560,800]
));

// Section 5
children.push(h1('5. Risks, guardrails, and open questions'));
children.push(h3('From adversarial review of the framework'));
const risks = [
  ['Identity presence is not campaign recovery. ','94.5% have an email, but that is joinability, not a form-MQL. Realistic campaign recovery is the ~5% digital slice. Do not promise recovered ad credit beyond that.'],
  ['Ban unbounded temporal joins from record writes. ','A nearest-session match within a long window can attach an unrelated visit. Keep it at LOW confidence, exclude from CAC and ROAS, set a precision floor.'],
  ['Dual-track the time series at cutover. ','Keep the legacy MQL definition alongside the new one, restate at least a trailing 12 months on both, never splice pre-change against post-change on one axis. Fix the 2026 outbound mis-tag forward, not by uniform historical subtraction.'],
  ['Required field can relocate the gap. ','Without auto-detection and a measured adoption and completion-quality KPI, blanks become "Other" selections.'],
  ['Re-engagement inheritance needs guards. ','The prior cycle may itself be an orphan, the inherited campaign may be defunct (needs a recency cap), and crediting the original channel for a revived deal is debatable.'],
  ['AI and LLM should not be dead-ended. ','Carve out an AI Search inferred channel detectable from referrer domains and add a forward-capture enum value.'],
  ['No human-labeled ground truth yet. ','The 86.7% agreement measures consistency, not correctness. Hand-label a 50 to 100 record sample, publish precision and recall, resource the ~13% review queue.'],
];
risks.forEach(([lab,txt])=>children.push(bullet([[lab,{bold:true}],[txt,{}]])));
children.push(h3('Open inputs needed before publishing numbers to leadership'));
children.push(numbered('Total SQL population: resolved. 14,934 inbound SQLs in FY2023 to FY2026 (Omni), so the 652 orphans are about 4.4% of inbound SQLs.'));
children.push(numbered('Confirmation of the 2023-05 batch as a migration artifact (against HubSpot import history).'));
children.push(numbered('Currency basis of DEAL_MRR. This export has no currency column, so MRR is summed as exported. Confirm it is USD-normalized before MRR-based prioritization.'));
children.push(numbered('Whether the 2026 outbound mis-tag reflects a real new BD motion or a detection change, to choose forward-only fix versus restatement.'));

// Appendix
children.push(h1('Appendix: method and artifacts'));
children.push(bullet([['classified_orphan_sqls.csv: ',{bold:true}],['all 652 records with root-cause category, suggested source, funnel outcome, and MRR.',{}]]));
children.push(bullet([['crosstab.json: ',{bold:true}],['category-by-impact aggregates.',{}]]));
children.push(bullet([['llm_classification.json, keyword_classification.json: ',{bold:true}],['the two classification passes (canonical is the LLM pass).',{}]]));
children.push(bullet([['Classification method: ',{bold:true}],['LLM pass over the 241 non-blank discovery strings into a fixed 9-category taxonomy with a single-auditor reconciliation, cross-checked against an independent keyword classifier (86.7% agreement). Blank records form their own category. All financial and timing figures computed deterministically.',{}]]));
children.push(bullet([['Definitions ',{bold:true}],['follow the preop-data-intelligence skill: MQL = inbound Pre-Op, SQL = Pre-Op with a completed intro meeting, Last Touch Source set at Pre-Op creation and locked.',{}]]));

const doc = new Document({
  creator:'Riverside Growth, Marketing Ops',
  title:'Inbound SQLs without MQLs',
  styles:{
    default:{ document:{ run:{ font:FONT, size:21, color:NEAR_BLACK } } },
    paragraphStyles:[
      { id:'Heading1', name:'Heading 1', basedOn:'Normal', next:'Normal', quickFormat:true,
        run:{ font:FONT, size:30, bold:true, color:NEAR_BLACK }, paragraph:{ spacing:{before:300, after:120}, outlineLevel:0 } },
      { id:'Heading2', name:'Heading 2', basedOn:'Normal', next:'Normal', quickFormat:true,
        run:{ font:FONT, size:24, bold:true, color:PURPLE }, paragraph:{ spacing:{before:260, after:100}, outlineLevel:1 } },
      { id:'Heading3', name:'Heading 3', basedOn:'Normal', next:'Normal', quickFormat:true,
        run:{ font:FONT, size:21, bold:true, color:DARK_GRAY }, paragraph:{ spacing:{before:180, after:80}, outlineLevel:2 } },
    ],
  },
  numbering:{ config:[
    { reference:'b', levels:[{ level:0, format:LevelFormat.BULLET, text:'•', alignment:AlignmentType.LEFT, style:{ paragraph:{ indent:{ left:460, hanging:280 } } } }] },
    { reference:'n', levels:[{ level:0, format:LevelFormat.DECIMAL, text:'%1.', alignment:AlignmentType.LEFT, style:{ paragraph:{ indent:{ left:460, hanging:280 } } } }] },
  ]},
  sections:[{
    properties:{ page:{ size:{ width:12240, height:15840 }, margin:{ top:1440, right:1440, bottom:1440, left:1440 } } },
    headers:{ default: new Header({ children:[ new Paragraph({ spacing:{after:0}, children:[
      new ImageRun({ type:'png', data:logo, transformation:{ width:128, height:30 }, altText:{ title:'Riverside', description:'Riverside logo', name:'Riverside' } })
    ]}) ] }) },
    footers:{ default: new Footer({ children:[ new Paragraph({ alignment:AlignmentType.RIGHT, spacing:{after:0}, children:[
      new TextRun({ text:'Riverside Growth, Marketing Ops   |   Page ', font:FONT, size:16, color:MID_GRAY }),
      new TextRun({ children:[PageNumber.CURRENT], font:FONT, size:16, color:MID_GRAY }),
    ]}) ] }) },
    children,
  }],
});

Packer.toBuffer(doc)
  .then(buf => {
    fs.writeFileSync(outPath, buf);
    console.log('wrote docx', buf.length, 'bytes');
  })
  .catch(err => {
    console.error('Error building DOCX:', err.message);
    process.exit(1);
  });
