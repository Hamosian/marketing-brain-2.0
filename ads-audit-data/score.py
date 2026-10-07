SEV={'Critical':5.0,'High':3.0,'Medium':1.5,'Low':0.5}
RES={'PASS':1.0,'WARNING':0.5,'FAIL':0.0}

def score(checks):
    earned=poss=0.0
    for cid,sev,wcat,res in checks:
        w=SEV[sev]*wcat
        poss+=w
        earned+=w*RES[res]
    return earned,poss,100*earned/poss

# (id, severity, category_weight, result)  -- only Windsor-observable checks
google=[
 ('G42','Critical',0.25,'PASS'),    # conversion actions firing
 ('G49','High',0.25,'FAIL'),        # conversion value missing on ~99% non-brand spend
 ('G-CT3','Critical',0.25,'WARNING'),# tag firing (conv flow) but page completeness unverified
 ('G16','Critical',0.20,'FAIL'),    # 17.3% search-term spend on 0-conv terms
 ('G-WS1','High',0.20,'PASS'),      # only 1 keyword >100clk 0conv
 ('G17','Critical',0.20,'PASS'),    # broad match paired with smart bidding, not manual
 ('G01','Medium',0.15,'PASS'),      # strong naming convention
 ('G04','High',0.15,'WARNING'),     # fragmentation (many tiny competitor campaigns)
 ('G05','Critical',0.15,'PASS'),    # brand/non-brand separated (dedicated Brand acct)
 ('G06','Medium',0.15,'PASS'),      # PMax present
 ('G08','High',0.15,'WARNING'),     # allocation skewed to poor performers
 ('G-AD2','High',0.15,'PASS'),      # strong search CTRs
 ('G36','High',0.10,'WARNING'),     # Target Spend on some competitor/retarget campaigns
 ('G40','Medium',0.10,'WARNING'),   # brand on Manual CPC w/ high conv (defensible)
 ('G39','High',0.10,'WARNING'),     # high-spend campaigns budget-limited (low IS)
]
meta=[
 ('M01','Critical',0.30,'PASS'),    # pixel firing
 ('M07','High',0.30,'FAIL'),        # standard Lead event not firing (a standard event is dead)
 ('M25','Critical',0.30,'FAIL'),    # only 2 formats acct-wide, no carousel, single-format adsets
 ('M26','High',0.30,'WARNING'),     # main adsets stocked; App/Brand adsets <5
 ('M27','High',0.30,'PASS'),        # 9:16 vertical present
 ('M-CR2','High',0.30,'WARNING'),   # Newsletter prospecting freq 4.85
 ('M-CR3','Medium',0.30,'FAIL'),    # Event_SignedUp retarget freq 16.7
 ('M-CR4','High',0.30,'WARNING'),   # several adsets CTR <1%
 ('M37','High',0.30,'WARNING'),     # campaign freq high on remarket
 ('M11','High',0.20,'WARNING'),     # 5 campaigns
 ('M12','High',0.20,'PASS'),        # CBO on >$100/day adsets
 ('M17','High',0.20,'PASS'),        # adsets >$10/day
]
ge,gp,gs=score(google)
me,mp,ms=score(meta)

# budget share (last 30d, all spend incl paused)
g_spend=206715.8673+67403.1724+169114.9965+721827.1691+23521.8702
m_spend=6288.76+4487.85+7195.49+2401.52+2034.92
tot=g_spend+m_spend
g_share=g_spend/tot; m_share=m_spend/tot
agg=gs*g_share+ms*m_share

def grade(s):
    return 'A' if s>=90 else 'B' if s>=75 else 'C' if s>=60 else 'D' if s>=40 else 'F'

print(f"GOOGLE: {gs:.1f}  grade {grade(gs)}  | scored {len(google)}/80 checks | earned {ge:.2f}/{gp:.2f}")
print(f"META:   {ms:.1f}  grade {grade(ms)}  | scored {len(meta)}/50 checks | earned {me:.2f}/{mp:.2f}")
print(f"\nSpend 30d: Google ${g_spend:,.0f} ({g_share*100:.1f}%) | Meta ${m_spend:,.0f} ({m_share*100:.1f}%) | total ${tot:,.0f}")
print(f"AGGREGATE (budget-weighted): {agg:.1f}  grade {grade(agg)}")

# Google enabled high-CPA kill/fix list
kill=[
 ("US_B2C_Broad_Desktop",172512.27,185.09,932.05,0.2201),
 ("US_PMax_DescriptEditing_Desktop",69281.53,169.48,408.79,0.1537),
 ("US_Generic_Webinar_Desktop",58826.81,265.53,221.54,0.5609),
 ("UK_PMax_Podcasting_Desktop",51986.63,66.58,780.80,0.1925),
 ("US_Generic_Podcast_Recording_Desktop",38027.48,183.63,207.09,0.818),
 ("CAUKAU_B2C_Alpha_Desktop",36732.69,164.06,223.90,0.7204),
 ("TopGEOs_B2C_Alpha_Mobile",16044.64,35.51,451.88,0.9385),
 ("US_PMax_Podcasting_Desktop_Clean",14274.40,28.00,509.80,0.2661),
]
ks=sum(k[1] for k in kill)
print(f"\nEnabled campaigns with CPA>$200: spend ${ks:,.0f}/30d ({ks/g_spend*100:.0f}% of Google spend), {len(kill)} campaigns")
for n,s,c,cpa,is_ in sorted(kill,key=lambda x:-x[1]):
    print(f"  ${s:>11,.0f} | {c:>7.0f} conv | ${cpa:>7.0f} CPA | IS {is_*100:>4.0f}% | {n}")
