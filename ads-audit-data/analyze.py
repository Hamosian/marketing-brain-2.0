import json

with open('google_keywords_30d.json') as f: kw = json.load(f)['result']
with open('google_searchterms_30d.json') as f: st = json.load(f)['result']

def num(x):
    return x if isinstance(x,(int,float)) else 0.0

# ---------- QS diagnostics ----------
qs_vals = [r['quality_score'] for r in kw if r.get('quality_score') is not None]
print("=== QUALITY SCORE DIAGNOSTIC ===")
print(f"keywords with non-null QS: {len(qs_vals)} / {len(kw)}")
if qs_vals:
    print(f"QS min={min(qs_vals)} max={max(qs_vals)} sample(sorted desc top10)={sorted(qs_vals,reverse=True)[:10]}")
    print(f"QS sample(sorted asc bottom10)={sorted(qs_vals)[:10]}")
    in_1_10 = [v for v in qs_vals if 1<=v<=10]
    print(f"values in 1-10 range: {len(in_1_10)} ({100*len(in_1_10)/len(qs_vals):.0f}%)")

# ---------- KEYWORD ANALYSIS ----------
print("\n=== KEYWORD ANALYSIS (active kws, clicks>=1) ===")
tot_kw = len(kw)
tot_kw_spend = sum(num(r['spend']) for r in kw)
print(f"active keywords: {tot_kw}, total kw spend: ${tot_kw_spend:,.0f}")

# zero-conversion keywords with >100 clicks (G-WS1)
zc = [r for r in kw if num(r['clicks'])>100 and num(r['conversions'])==0]
zc_spend = sum(num(r['spend']) for r in zc)
print(f"\nG-WS1: keywords >100 clicks & 0 conv: {len(zc)}, wasted spend ${zc_spend:,.0f}")
for r in sorted(zc,key=lambda x:num(x['spend']),reverse=True)[:15]:
    print(f"  ${num(r['spend']):>9,.0f} | {int(num(r['clicks'])):>6} clk | {r['account_name'][:12]:12} | {r['campaign'][:38]:38} | {r['keyword_text'][:40]} [{r['match_type']}]")

# match type distribution
from collections import Counter
mt = Counter(r['match_type'] for r in kw)
mt_spend = {}
for r in kw: mt_spend[r['match_type']] = mt_spend.get(r['match_type'],0)+num(r['spend'])
print(f"\nMatch type counts: {dict(mt)}")
print(f"Match type spend: {{ {', '.join(f'{k}: ${v:,.0f}' for k,v in mt_spend.items())} }}")

# ---------- SEARCH TERM ANALYSIS ----------
print("\n=== SEARCH TERM ANALYSIS (spend>10) ===")
tot_st = len(st)
tot_st_spend = sum(num(r['spend']) for r in st)
print(f"search terms (>$10): {tot_st}, total spend in these terms: ${tot_st_spend:,.0f}")
# wasted: spend>10 & 0 conv (G16/G-WS1)
waste = [r for r in st if num(r['conversions'])==0]
waste_spend = sum(num(r['spend']) for r in waste)
waste_pct = (100*waste_spend/tot_st_spend) if tot_st_spend else 0.0
print(f"G16: terms >$10 & 0 conv: {len(waste)}, wasted ${waste_spend:,.0f} = {waste_pct:.1f}% of >$10-term spend")
print("Top 20 wasted search terms:")
for r in sorted(waste,key=lambda x:num(x['spend']),reverse=True)[:20]:
    print(f"  ${num(r['spend']):>9,.0f} | {int(num(r['clicks'])):>5} clk | {r['account_name'][:11]:11} | {r['campaign'][:34]:34} | {r['search_term'][:45]}")

# spend>50 0 conv (higher confidence waste)
waste50 = [r for r in st if num(r['conversions'])==0 and num(r['spend'])>50]
print(f"\nHigher-confidence: terms >$50 & 0 conv: {len(waste50)}, wasted ${sum(num(r['spend']) for r in waste50):,.0f}")
