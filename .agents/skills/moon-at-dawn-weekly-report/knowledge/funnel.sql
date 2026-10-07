-- Moon at Dawn full funnel, one row per post (creator slug + link month).
-- Replace the four dates before running. Windows are half-open [start, end).
--   :start       report window start      e.g. '2025-09-28'
--   :end         report window end        e.g. '2026-09-28' (the Monday the report runs)
--   :wk_start    this week start (Monday) e.g. '2026-09-21'
--   :prev_start  last week start (Monday) e.g. '2026-09-14'
-- The slug list is knowledge/creators.md. Keep the two in sync.
WITH s AS (SELECT column1 slug, column2 creator FROM VALUES
  ('adamknorr','Adam Knorr'),('phillagnew','Phill Agnew'),('philagnew','Phill Agnew'),
  ('shannonsmith','Shannon Smith'),('jasonvana','Jason Vana'),('jasanvana','Jason Vana'),
  ('kamyamarwah','Kamya Marwah'),('arpitsingh','Arpit Singh'),('anthonykennada','Anthony Kennada'),
  ('divyanshisharma','Divyanshi Sharma'),('danimarkovits','Dani Markovits'),('kylelacy','Kyle Lacy'),
  ('jonevans','Jon Evans'),('mattvillage','Matt Village'),('jonathanparsons','Jonathan Parsons'),
  ('andrewtindall','Andrew Tindall'),('maticpogladic','Matic Pogladic'),('beccachambers','Becca Chambers'),
  ('sedgebeswick','Sedge Beswick'),('ashleyfaus','Ashley Faus'),('mariagharib','Maria Gharib'),
  ('sabreenhaziq','Sabreen Haziq'),('margaretmolloy','Margaret Molloy'),('roxanairimia','Roxana Irimia'),
  ('danielkorenblum','Daniel Korenblum'),('lottieunwin','Lottie Unwin'),('lukasotompasis','Lukas Otompasis'),
  ('kobiomenaka','Kobi Omenaka'),('jeremylaight','Jeremy Laight'),('charlottelloyd','Charlotte Lloyd'),
  ('christinegoos','Christine Goos'),('christinegoeoes','Christine Goos'),('allisonrossi','Allison Rossi'),
  ('samkuehnle','Sam Kuehnle'),('lindsayrios','Lindsay Rios'),('briannachapman','Brianna Chapman'),
  ('heatherbarnett','Heather Barnett'),('katieparkes','Katie Parkes'),('alexvacca','Alex Vacca'),
  ('sonkevenjacob','Sonke Venjacob'),('soenkevenjacob','Sonke Venjacob'),('rebeccashaddix','Rebecca Shaddix'),
  ('nickbennett','Nick Bennett'),('richardvanderblom','Richard van der Blom'),
  ('victoriabanaszczyk','Victoria Banaszczyk'),('renayeedwards','Renaye Edwards')),
-- link month: 'may2026' / 'sept2026' / 'june2026' -> 'may2026' / 'sep2026' / 'jun2026'
v AS (SELECT s.creator, LEFT(LOWER(p.ORIGINAL_UTM_TERM),3)||RIGHT(p.ORIGINAL_UTM_TERM,4) mth, p.ANONYMOUS_ID, p.TIMESTAMP ts
  FROM ANALYTICS.TRF.INT_SEGMENT__PAGES_UNIONED p JOIN s ON LOWER(p.ORIGINAL_UTM_CAMPAIGN)=s.slug
  WHERE p.TIMESTAMP >= :start AND p.TIMESTAMP < :end AND LOWER(p.ORIGINAL_UTM_MEDIUM)='creator'),
u AS (SELECT s.creator, LEFT(LOWER(f.UTM_TERM),3)||RIGHT(f.UTM_TERM,4) mth, f.USER_ID, LOWER(f.EMAIL) email, f.SIGN_UP_AT, f.TRIAL_STARTED_AT, f.SUBSCRIPTION_STARTED_AT
  FROM ANALYTICS.BI.MARKETING_FUNNEL_ANALYSIS f JOIN s ON LOWER(f.UTM_CAMPAIGN)=s.slug
  WHERE f.SIGN_UP_AT >= :start AND f.SIGN_UP_AT < :end AND LOWER(f.UTM_MEDIUM)='creator'),
-- B2B: HubSpot First Page Seen carries the UTM; the contact utm_campaign field is usually empty
h AS (SELECT s.creator, LEFT(LOWER(REGEXP_SUBSTR(c.HS_FIRST_URL,'utm_term=([^&]+)',1,1,'ie')),3)||RIGHT(REGEXP_SUBSTR(c.HS_FIRST_URL,'utm_term=([^&]+)',1,1,'ie'),4) mth,
    c.CONTACT_ID::varchar cid, LOWER(c.EMAIL) email, c.CREATED_AT, c.LIFECYCLE_STAGE_BECAME_MQL_AT mql_at, c.LIFECYCLE_STAGE_BECAME_SQL_AT sql_at
  FROM ANALYTICS.TRF.HUBSPOT__CONTACTS c JOIN s ON LOWER(REGEXP_SUBSTR(c.HS_FIRST_URL,'utm_campaign=([^&]+)',1,1,'ie'))=s.slug
  WHERE c.CREATED_AT >= :start AND c.CREATED_AT < :end AND c.HS_FIRST_URL ILIKE '%utm_medium=creator%' AND COALESCE(c.EMAIL_DOMAIN,'') NOT IN ('riverside.fm','riverside.com')),
dl AS (SELECT q.HUBSPOT_CONTACT_ID::varchar cid, COUNT(DISTINCT d.DEAL_ID) deals, COUNT_IF(d.IS_WON) won, SUM(IFF(d.IS_WON,d.DEAL_MRR,0)) won_mrr
  FROM ANALYTICS.FS.SQLS q LEFT JOIN ANALYTICS.FS.DEALS d ON d.SQL_ID=q.SQL_ID
  WHERE q.HUBSPOT_CONTACT_ID::varchar IN (SELECT cid FROM h) GROUP BY 1),
-- paid = anyone reached through the post (self-serve sign-up or HubSpot lead) with a subscription
ppl AS (SELECT creator, mth, email FROM u UNION SELECT creator, mth, email FROM h),
paid AS (SELECT p.creator, p.mth, COUNT(DISTINCT p.email) paid, COUNT(DISTINCT IFF(f.SUBSCRIPTION_STARTED_AT >= :wk_start, p.email, NULL)) paid_wk,
    COUNT(DISTINCT IFF(f.SUBSCRIPTION_STARTED_AT >= :prev_start AND f.SUBSCRIPTION_STARTED_AT < :wk_start, p.email, NULL)) paid_prev
  FROM ppl p JOIN (SELECT LOWER(EMAIL) email, SUBSCRIPTION_STARTED_AT FROM ANALYTICS.BI.MARKETING_FUNNEL_ANALYSIS
    WHERE SUBSCRIPTION_STARTED_AT IS NOT NULL AND LOWER(EMAIL) IN (SELECT email FROM ppl)) f ON f.email=p.email GROUP BY 1,2),
keys AS (SELECT creator, COALESCE(mth,'') mth FROM v UNION SELECT creator, COALESCE(mth,'') FROM u UNION SELECT creator, COALESCE(mth,'') FROM h),
va AS (SELECT creator, COALESCE(mth,'') mth, MIN(ts)::date first_visit, COUNT(DISTINCT ANONYMOUS_ID) visits,
    COUNT(DISTINCT IFF(ts >= :wk_start, ANONYMOUS_ID, NULL)) visits_wk,
    COUNT(DISTINCT IFF(ts >= :prev_start AND ts < :wk_start, ANONYMOUS_ID, NULL)) visits_prev
  FROM v GROUP BY 1,2),
ua AS (SELECT creator, COALESCE(mth,'') mth, COUNT(DISTINCT USER_ID) signups,
    COUNT(DISTINCT IFF(SIGN_UP_AT >= :wk_start, USER_ID, NULL)) signups_wk,
    COUNT(DISTINCT IFF(SIGN_UP_AT >= :prev_start AND SIGN_UP_AT < :wk_start, USER_ID, NULL)) signups_prev,
    COUNT_IF(TRIAL_STARTED_AT IS NOT NULL) trials, COUNT_IF(TRIAL_STARTED_AT >= :wk_start) trials_wk,
    COUNT_IF(TRIAL_STARTED_AT >= :prev_start AND TRIAL_STARTED_AT < :wk_start) trials_prev
  FROM u GROUP BY 1,2),
ha AS (SELECT h.creator, COALESCE(h.mth,'') mth, COUNT(*) leads, COUNT_IF(h.CREATED_AT >= :wk_start) leads_wk,
    COUNT_IF(h.CREATED_AT >= :prev_start AND h.CREATED_AT < :wk_start) leads_prev,
    COUNT_IF(h.mql_at IS NOT NULL) mqls, COUNT_IF(h.mql_at >= :wk_start) mqls_wk, COUNT_IF(h.mql_at >= :prev_start AND h.mql_at < :wk_start) mqls_prev,
    COUNT_IF(h.sql_at IS NOT NULL) sqls, COUNT_IF(h.sql_at >= :wk_start) sqls_wk, COUNT_IF(h.sql_at >= :prev_start AND h.sql_at < :wk_start) sqls_prev,
    COALESCE(SUM(dl.won),0) won, COALESCE(SUM(dl.won_mrr),0) won_mrr
  FROM h LEFT JOIN dl ON dl.cid=h.cid GROUP BY 1,2)
SELECT k.creator, k.mth, va.first_visit,
  COALESCE(va.visits,0) visits, COALESCE(va.visits_wk,0) visits_wk, COALESCE(va.visits_prev,0) visits_prev,
  COALESCE(ua.signups,0) signups, COALESCE(ua.signups_wk,0) signups_wk, COALESCE(ua.signups_prev,0) signups_prev,
  COALESCE(ua.trials,0) trials, COALESCE(ua.trials_wk,0) trials_wk, COALESCE(ua.trials_prev,0) trials_prev,
  COALESCE(pd.paid,0) paid, COALESCE(pd.paid_wk,0) paid_wk, COALESCE(pd.paid_prev,0) paid_prev,
  COALESCE(ha.leads,0) leads, COALESCE(ha.leads_wk,0) leads_wk, COALESCE(ha.leads_prev,0) leads_prev,
  COALESCE(ha.mqls,0) mqls, COALESCE(ha.mqls_wk,0) mqls_wk, COALESCE(ha.mqls_prev,0) mqls_prev,
  COALESCE(ha.sqls,0) sqls, COALESCE(ha.sqls_wk,0) sqls_wk, COALESCE(ha.sqls_prev,0) sqls_prev,
  COALESCE(ha.won,0) won, COALESCE(ha.won_mrr,0) won_mrr
FROM keys k
LEFT JOIN va ON va.creator=k.creator AND va.mth=k.mth
LEFT JOIN ua ON ua.creator=k.creator AND ua.mth=k.mth
LEFT JOIN ha ON ha.creator=k.creator AND ha.mth=k.mth
LEFT JOIN paid pd ON pd.creator=k.creator AND COALESCE(pd.mth,'')=k.mth
ORDER BY visits DESC;
