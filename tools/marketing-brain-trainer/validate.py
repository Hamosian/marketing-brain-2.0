#!/usr/bin/env python3
"""Validator for the Marketing Brain trainer (single self-contained HTML file).

usage: python3 validate.py index.html [--static-only] [--json out.json]

Needs Node (syntax checks) and, for the browser pass, Python Playwright with Chrome
(pip install playwright). --static-only skips the browser pass.

HARD failures (exit 1): script syntax errors, em or en dashes, product-palette colors,
undocumented Slack syntax, external resource loads,
duplicate ids, missing AI diligence statement, uncaught page errors or console
errors, controls that throw when clicked, horizontal clipping at phone or desktop width,
Space on a focused button changing slide, focus reaching hidden slides, router top-1
accuracy under 80% on evals/routing.jsonl.
WARNINGS (exit 0): exclamation marks / emoji in visible copy, low contrast text,
slides taller than the viewport, very long slides.
"""
import sys, os, re, json, subprocess, tempfile
from html.parser import HTMLParser

args = sys.argv[1:]
if not args:
    print(__doc__); sys.exit(2)
path = os.path.abspath(args[0])
static_only = '--static-only' in args
json_out = args[args.index('--json') + 1] if '--json' in args else None
src = open(path, encoding='utf-8').read()

hard, warn, info = [], [], []

# ---------- static ----------
# 1. JS syntax of every inline script
all_scripts = re.findall(r'<script(\s[^>]*)?>(.*?)</script>', src, flags=re.S)
scripts = [body for attrs, body in all_scripts if 'application/json' not in (attrs or '')]
for attrs, body in all_scripts:
    if 'application/json' in (attrs or ''):
        try: json.loads(body)
        except ValueError as e: hard.append(f'inline JSON block{attrs.strip()} does not parse: {e}')
for i, js in enumerate(scripts, 1):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as t:
        t.write(js); tp = t.name
    r = subprocess.run(['node', '--check', tp], capture_output=True, text=True)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout).strip().splitlines()
        hard.append(f'script #{i} syntax error: ' + ' | '.join(msg[:4]))
    os.unlink(tp)
info.append(f'{len(scripts)} script blocks, {len(src)} bytes, {src.count(chr(10))+1} lines')

# 2. em and en dashes anywhere (CLAUDE.md bans both)
n_em = src.count('—')
if n_em: hard.append(f'{n_em} em dash character(s) found')
n_en = src.count('–')
if n_en: hard.append(f'{n_en} en dash character(s) found')
if '&mdash;' in src or '&ndash;' in src or '\\u2014' in src or '\\u2013' in src:
    hard.append('dash entity or escape found (&mdash; &ndash; \\u2014 \\u2013)')

# 2b. product design-system palette must not appear in a marketing artifact
prod = sorted({m.lower() for m in re.findall(r'#(?:9671ff|7848ff|c9f273|b196ff)\b', src, flags=re.I)})
if prod: hard.append(f'product design-system colors found (marketing palette only): {prod}')

# 2c. undocumented Slack invocation syntax must not be taught
slack_syntax = re.findall(r'(?:/agent\s+marketing-os|@agent\s+marketing-os|@marketing-os\s+\w)', src, flags=re.I)
if slack_syntax: hard.append(f'undocumented Slack invocation syntax taught: {sorted(set(slack_syntax))[:4]}')

# 3. external resource loads (navigation links are allowed; resource loads are not)
ext = []
ext += re.findall(r'<script[^>]+src=["\']https?://[^"\']+', src)
ext += re.findall(r'<link[^>]+href=["\']https?://[^"\']+', src)
ext += re.findall(r'<img[^>]+src=["\']https?://[^"\']+', src)
ext += re.findall(r'url\(\s*["\']?https?://[^)]+\)', src)
ext += re.findall(r'@import\s+[^;]+', src)
ext += re.findall(r'fetch\(\s*["\']https?://[^"\']+', src)
if ext: hard.append(f'external resource load(s): {[e[:80] for e in ext]}')

# 4. duplicate ids
ids = re.findall(r'\sid=["\']([^"\']+)["\']', src)
dups = sorted({x for x in ids if ids.count(x) > 1})
if dups: hard.append(f'duplicate id(s): {dups}')

# 5. AI diligence statement
if not (re.search(r'AI diligence statement', src, flags=re.I) and re.search(r'full responsibility for the content', src, flags=re.I)):
    hard.append('canonical AI diligence statement not found (needs the "AI diligence statement" heading and the scripts/riverside_docx.py DILIGENCE text)')

# 6. visible copy checks (exclamation marks, emoji)
class TextGrab(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'svg'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'svg') and self.skip: self.skip -= 1
    def handle_data(self, d):
        if not self.skip and d.strip(): self.parts.append(d.strip())
tg = TextGrab(); tg.feed(src)
visible = ' \n'.join(tg.parts)
# JS-injected copy lives in string literals: scan quoted strings in scripts for sentences too
js_strings = []
for js in scripts:
    js_strings += re.findall(r"'([^'\\\n]{12,})'", js) + re.findall(r'"([^"\\\n]{12,})"', js)
copy_corpus = visible + '\n' + '\n'.join(js_strings)
excl = [m.group(0) for m in re.finditer(r'[A-Za-z][^\n!]{0,40}!(?![=])', copy_corpus)]
excl = [e for e in excl if not re.search(r'!important', e)]
if excl: warn.append(f'{len(excl)} exclamation mark(s) in copy, e.g. {excl[:4]}')
emoji_re = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF\U0001F000-\U0001F02F]')
emo = emoji_re.findall(copy_corpus)
if emo: warn.append(f'{len(emo)} emoji in copy: {sorted(set(emo))}')

# ---------- dynamic ----------
report_slides = []
if not static_only:
    from playwright.sync_api import sync_playwright
    url = 'file://' + path
    CONTRAST_JS = r"""
    () => {
      function parse(c){const m=c.match(/rgba?\(([^)]+)\)/); if(!m) return null; const p=m[1].split(',').map(s=>parseFloat(s)); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1};}
      function lum(c){const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)}; return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b);}
      function blend(top,bot){const a=top.a; return {r:top.r*a+bot.r*(1-a),g:top.g*a+bot.g*(1-a),b:top.b*a+bot.b*(1-a),a:1};}
      function bgOf(el){let stack=[]; let e=el; while(e && e.nodeType===1){const c=parse(getComputedStyle(e).backgroundColor); if(c && c.a>0){stack.push(c); if(c.a>=1) break;} e=e.parentElement;} let base={r:16,g:16,b:16,a:1}; for(let i=stack.length-1;i>=0;i--) base=blend(stack[i],base); return base;}
      const slide=document.querySelector('.slide.active')||document.body;
      const roots=[slide, document.querySelector('.header'), document.querySelector('.nav')].filter(Boolean);
      const out=[]; const seen=new Set();
      roots.forEach(root=>{ root.querySelectorAll('*').forEach(el=>{
        if(seen.has(el)) return; seen.add(el);
        const own=[...el.childNodes].some(n=>n.nodeType===3 && n.textContent.trim().length>1);
        if(!own) return;
        const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none'||parseFloat(cs.opacity)===0) return;
        const r=el.getBoundingClientRect(); if(r.width<2||r.height<2) return;
        const fg=parse(cs.color); if(!fg) return;
        if(cs.webkitTextFillColor && cs.webkitTextFillColor.indexOf('rgba(0, 0, 0, 0)')===0) return; // gradient text
        const bg=bgOf(el); const f=blend(fg,bg);
        const L1=lum(f), L2=lum(bg); const ratio=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
        const size=parseFloat(cs.fontSize), bold=parseInt(cs.fontWeight)>=700;
        const large=size>=24 || (bold && size>=18.66);
        const need=large?3:4.5;
        if(ratio<need) out.push({text:el.textContent.trim().slice(0,40), ratio:Math.round(ratio*100)/100, need, size, color:cs.color});
      });});
      return out;
    }"""
    CLIP_JS = r"""
    () => {
      const vw=window.innerWidth; const out=[];
      const slide=document.querySelector('.slide.active');
      const roots=[slide, document.querySelector('.header'), document.querySelector('.nav')].filter(Boolean);
      roots.forEach(root=>root.querySelectorAll('*').forEach(el=>{
        const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none') return;
        if(el.closest('canvas')) return;
        const r=el.getBoundingClientRect(); if(r.width<1||r.height<1) return;
        // ignore elements inside an intentional horizontal scroller
        let p=el.parentElement, scroller=false; while(p){const pc=getComputedStyle(p); const ox=pc.overflowX, oy=pc.overflowY; if((ox==='auto'||ox==='scroll') && (oy==='hidden'||oy==='visible'||oy==='clip')){scroller=true;break;} p=p.parentElement;}
        if(scroller) return;
        if(r.right>vw+1 || r.left<-1) out.push({el:el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ')[0]:''), left:Math.round(r.left), right:Math.round(r.right), text:(el.textContent||'').trim().slice(0,30)});
      }));
      if(slide && slide.scrollWidth > slide.clientWidth + 1) out.unshift({el:'slide-horizontal-overflow', left:0, right:slide.scrollWidth, text:''});
      return out.slice(0,12);
    }"""
    HEIGHT_JS = r"""
    () => { const s=document.querySelector('.slide.active'); if(!s) return null; return {scrollH:s.scrollHeight, clientH:s.clientHeight}; }"""
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        seen_con = set()
        for vpname, vp in (('desktop', {'width': 1440, 'height': 900}), ('phone', {'width': 390, 'height': 844})):
            ctx = b.new_context(viewport=vp, reduced_motion='no-preference')
            pg = ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
            pg.on('console', lambda m: errs.append('console.error: ' + m.text) if m.type == 'error' else None)
            pg.goto(url); pg.wait_for_timeout(900)
            n = pg.evaluate("document.querySelectorAll('.slide').length")
            info.append(f'{vpname}: {n} slides')
            for i in range(n):
                pg.goto('about:blank'); pg.goto(url + f'#slide-{i+1}'); pg.wait_for_timeout(700)
                # neutralise entrance animation for measurement
                pg.add_style_tag(content='.rise{opacity:1!important;transform:none!important;animation:none!important}')
                pg.wait_for_timeout(80)
                active_idx = pg.evaluate("[...document.querySelectorAll('.slide')].findIndex(s=>s.classList.contains('active'))")
                clip = pg.evaluate(CLIP_JS)
                h = pg.evaluate(HEIGHT_JS)
                con = pg.evaluate(CONTRAST_JS) if vpname == 'desktop' else []
                title = pg.evaluate("(()=>{const s=document.querySelector('.slide.active'); const h=s&&s.querySelector('h1,h2'); return h?h.textContent.trim().slice(0,60):''})()")
                words = pg.evaluate("(()=>{const s=document.querySelector('.slide.active'); return s? s.innerText.trim().split(/\\s+/).length:0})()")
                rec = {'viewport': vpname, 'slide': i + 1, 'active_ok': active_idx == i, 'title': title, 'words': words}
                if active_idx != i: hard.append(f'{vpname} slide {i+1}: deep link #slide-{i+1} activated index {active_idx}')
                if clip:
                    hard.append(f'{vpname} slide {i+1} "{title}": {len(clip)} element(s) clipped horizontally, e.g. {clip[:3]}')
                    rec['clipped'] = clip
                if h and h['scrollH'] > h['clientH'] + 4:
                    warn.append(f'{vpname} slide {i+1} "{title}": content taller than viewport ({h["scrollH"]} > {h["clientH"]}), needs scroll')
                if con:
                    key = tuple(sorted({(c['text'], c['ratio']) for c in con}))
                    if key in seen_con: con = []
                    seen_con.add(key)
                if con:
                    warn.append(f'desktop slide {i+1} "{title}": {len(con)} low-contrast text run(s), e.g. {con[:3]}')
                if words > 170 and vpname == 'desktop':
                    warn.append(f'slide {i+1} "{title}": {words} words visible (long)')
                # smoke: click every enabled visible button inside the active slide, then return
                btn_count = pg.evaluate("document.querySelectorAll('.slide.active button:not([disabled])').length")
                before = len(errs)
                for k in range(min(btn_count, 25)):
                    try:
                        loc = pg.locator('.slide.active button:not([disabled])').nth(k)
                        if loc.is_visible():
                            loc.click(timeout=1500, no_wait_after=True)
                            pg.wait_for_timeout(60)
                            # a click may navigate slides; restore
                            cur = pg.evaluate("[...document.querySelectorAll('.slide')].findIndex(s=>s.classList.contains('active'))")
                            if cur != i:
                                pg.goto('about:blank'); pg.goto(url + f'#slide-{i+1}'); pg.wait_for_timeout(400)
                    except Exception as e:
                        pass
                if len(errs) > before:
                    hard.append(f'{vpname} slide {i+1}: clicking controls raised: {errs[before:before+3]}')
                report_slides.append(rec)
            # keyboard smoke
            pg.goto('about:blank'); pg.goto(url + '#slide-1'); pg.wait_for_timeout(500)
            pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(300)
            k_idx = pg.evaluate("[...document.querySelectorAll('.slide')].findIndex(s=>s.classList.contains('active'))")
            if k_idx != 1: hard.append(f'{vpname}: ArrowRight from slide 1 landed on index {k_idx}')
            if vpname == 'desktop':
                # Space on a focused in-slide button must press the button, never change slide
                space_bad = []
                for i in range(n):
                    pg.goto('about:blank'); pg.goto(url + f'#slide-{i+1}'); pg.wait_for_timeout(350)
                    has = pg.evaluate("""(()=>{const b=[...document.querySelectorAll('.slide.active button:not([disabled]):not([data-nav])')].find(x=>x.offsetParent);
                        if(!b) return false; b.setAttribute('data-vt','1'); b.focus(); return document.activeElement===b;})()""")
                    if not has: continue
                    pg.keyboard.press('Space'); pg.wait_for_timeout(120)
                    cur = pg.evaluate("[...document.querySelectorAll('.slide')].findIndex(s=>s.classList.contains('active'))")
                    if cur != i: space_bad.append(i + 1)
                if space_bad: hard.append(f'Space on a focused button changed slide on slides {space_bad[:10]}')
                # the slide-dot navigation must be one tab stop, not one per slide
                pg.goto('about:blank'); pg.goto(url + '#slide-1'); pg.wait_for_timeout(400)
                pg.evaluate("document.activeElement && document.activeElement.blur()")
                stops = []
                for _ in range(80):
                    pg.keyboard.press('Tab')
                    d = pg.evaluate("""(()=>{const e=document.activeElement; if(!e||e===document.body) return null;
                        return {dot: !!e.closest('#dots, .dots'), hidden: !!(e.closest('.slide') && !e.closest('.slide.active'))};})()""")
                    if d: stops.append(d)
                dot_stops = sum(1 for d in stops if d['dot'])
                if dot_stops > 2: hard.append(f'slide dots take {dot_stops} tab stops (use one roving tab stop)')
                leaks = sum(1 for d in stops if d['hidden'])
                if leaks: hard.append(f'{leaks} tab stop(s) inside hidden slides')
                # router accuracy, when the page exposes MBT.route(text) -> [{name, score}]
                has_route = pg.evaluate("!!(window.MBT && typeof MBT.route==='function')")
                suite = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'evals', 'routing.jsonl')
                if has_route and os.path.isfile(suite):
                    cases = []
                    for line in open(suite, encoding='utf-8'):
                        line = line.strip()
                        if not line or line.startswith('//'): continue
                        try: cases.append(json.loads(line))
                        except ValueError: pass
                    res = pg.evaluate("""(cases)=>cases.map(c=>{const r=MBT.route(c.request)||[]; const i=r.findIndex(x=>x.name===c.expect); return i<0?99:i+1;})""", cases)
                    top1 = sum(1 for r in res if r == 1); top3 = sum(1 for r in res if r <= 3)
                    info.append(f'router: top-1 {top1}/{len(res)}, top-3 {top3}/{len(res)}')
                    if top1 < 0.8 * len(res): hard.append(f'router top-1 accuracy {top1}/{len(res)} is below 80% on evals/routing.jsonl')
                elif not has_route:
                    warn.append('page exposes no MBT.route(text); router accuracy not measured')
            load_errs = [e for e in errs if 'clicking' not in e]
            if errs:
                uniq = sorted(set(errs))
                hard.append(f'{vpname}: {len(uniq)} distinct runtime error(s): {uniq[:5]}')
            ctx.close()
        # reduced motion pass: page must still load without errors
        ctx = b.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
        pg = ctx.new_page(); rerr = []
        pg.on('pageerror', lambda e: rerr.append(str(e)))
        pg.goto(url); pg.wait_for_timeout(800)
        vis = pg.evaluate("(()=>{const s=document.querySelector('.slide.active .rise'); return s? getComputedStyle(s).opacity : '1'})()")
        if float(vis) < 0.99: hard.append(f'reduced-motion: entrance content not visible (opacity {vis})')
        if rerr: hard.append(f'reduced-motion: page errors {rerr[:3]}')
        ctx.close(); b.close()

status = 'FAIL' if hard else 'PASS'
print(f'=== {status}: {len(hard)} hard, {len(warn)} warnings ===')
for x in info: print('  info:', x)
for x in hard: print('  HARD:', x)
for x in warn: print('  warn:', x)
if json_out:
    json.dump({'status': status, 'hard': hard, 'warn': warn, 'info': info, 'slides': report_slides}, open(json_out, 'w'), indent=2)
sys.exit(1 if hard else 0)
