#!/usr/bin/env python3
"""Build the Marketing Brain trainer into one self-contained index.html.

The claude.ai Artifact runtime blocks every external request, so the published
page must inline everything. This script assembles it from editable sources:

  src/index.template.html   page shell (markers below)
  src/slides/NN-*.html      one <section class="slide"> per file, in filename order
  src/css/NN-*.css          styles, concatenated in filename order
  src/js/NN-*.js            scripts, concatenated in filename order
  assets/*.woff2, *.png     font and logo, base64-inlined at build time
  ../../.claude/skills/     skill catalog, generated so counts and commands
                            never drift from the repo

Markers: __SLIDES__ __STYLES__ __SCRIPTS__ __FONT_B64__ __LOGO_B64__
         __ROUTING_CASES__ (JSON [{request, expect, why}] from evals/routing.jsonl)
         __SKILL_CATALOG__ (JSON array) __SKILL_COUNT__ __BUILD_DATE__
         __BRAIN_GRAPH__ (JSON {nodes, links}) __GRAPH_SKILLS__ __GRAPH_DOCS__
         __GRAPH_LINKS__
         __ROUTING_N__ __ROUTING_TOP1__ __ROUTING_TOP3__ (scripts/eval_routing.py)

usage:
  python3 build.py            write index.html
  python3 build.py --check    exit 1 if index.html is stale (for CI or pre-commit)
"""
import base64
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SKILLS = os.path.join(REPO, '.claude', 'skills')


def read(rel):
    with open(os.path.join(HERE, rel), encoding='utf-8') as f:
        return f.read()


def b64(rel):
    with open(os.path.join(HERE, rel), 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')


def _frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---', text, re.S)
    return m.group(1).split('\n') if m else []


def _field(lines, key):
    """Plain, quoted, or folded/literal (> >- | |-) YAML scalar, no PyYAML needed."""
    for i, line in enumerate(lines):
        m = re.match(r'^%s:\s*(.*)$' % re.escape(key), line)
        if not m:
            continue
        v = m.group(1).strip()
        if v in ('>', '>-', '>+', '|', '|-', '|+'):
            buf = []
            for nxt in lines[i + 1:]:
                if nxt.strip() == '' or nxt.startswith((' ', '\t')):
                    buf.append(nxt.strip())
                else:
                    break
            return ' '.join(x for x in buf if x)
        if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
            v = v[1:-1]
        return v
    return ''


def skill_catalog():
    out = []
    if not os.path.isdir(SKILLS):
        return out
    for d in sorted(os.listdir(SKILLS)):
        path = os.path.join(SKILLS, d, 'SKILL.md')
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as f:
            lines = _frontmatter(f.read())
        name = _field(lines, 'name') or d
        desc = ' '.join(_field(lines, 'description').split())
        out.append({'name': name, 'description': desc})
    return out


def brain_graph(catalog):
    """Skill -> skill and skill -> reference/system doc links, parsed from each SKILL.md.

    Only links a skill file actually states count, so the trainer's graph is the
    repo's real wiring rather than a drawing of it.
    """
    names = {s['name'] for s in catalog}
    dirs = {}
    for d in sorted(os.listdir(SKILLS)) if os.path.isdir(SKILLS) else []:
        path = os.path.join(SKILLS, d, 'SKILL.md')
        if os.path.isfile(path):
            dirs[d] = path
    links = set()
    for d, path in dirs.items():
        with open(path, encoding='utf-8') as f:
            text = f.read()
        src = _field(_frontmatter(text), 'name') or d
        for m in re.findall(r'(?<![\w.-])/([a-z][a-z0-9-]+)', text):
            if m in names and m != src:
                links.add((src, m))
        for m in re.findall(r'((?:references|systems)/[A-Za-z0-9_./-]+?\.md)', text):
            if os.path.isfile(os.path.join(REPO, m)):
                links.add((src, m))
    used = {a for a, _ in links} | {b for _, b in links}
    nodes = [{'id': s['name'], 'kind': 'skill'} for s in catalog]
    nodes += [{'id': p, 'kind': 'system' if p.startswith('systems/') else 'reference'}
              for p in sorted(x for x in used if '/' in x)]
    return {'nodes': nodes, 'links': [{'s': a, 't': b} for a, b in sorted(links)]}


def routing_score():
    """Top-1 / top-3 hit counts from the repo's own routing eval, or None if it cannot run."""
    script = os.path.join(REPO, 'scripts', 'eval_routing.py')
    if not os.path.isfile(script):
        return None
    try:
        out = subprocess.run([sys.executable, script, '--json'], cwd=REPO,
                             capture_output=True, text=True, timeout=120).stdout
        results = json.loads(out)['results']
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return None
    pos = [r.get('position') for r in results]
    return {'n': len(results),
            'top1': sum(1 for p in pos if p == 1),
            'top3': sum(1 for p in pos if p and p <= 3)}


def _inline_json(obj):
    # "</" inside inline JSON would close the <script>; escape it
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def routing_cases():
    """evals/routing.jsonl as [{request, expect, why}], comment lines skipped."""
    path = os.path.join(REPO, 'evals', 'routing.jsonl')
    out = []
    if not os.path.isfile(path):
        return out
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            try:
                c = json.loads(line)
            except ValueError:
                continue
            out.append({'request': c.get('request', ''), 'expect': c.get('expect', ''), 'why': c.get('why', '')})
    return out


def _parts(sub, ext):
    d = os.path.join(HERE, 'src', sub)
    return [read(os.path.join('src', sub, f)) for f in sorted(os.listdir(d)) if f.endswith(ext)] if os.path.isdir(d) else []


def build():
    html = read('src/index.template.html')
    scripts = _parts('js', '.js')
    styles = '\n\n'.join(s.rstrip('\n') for s in _parts('css', '.css'))
    slides = '\n\n'.join(s.rstrip('\n') for s in _parts('slides', '.html'))
    html = html.replace('__SLIDES__', slides)
    catalog = skill_catalog()
    catalog_json = _inline_json(catalog)
    graph = brain_graph(catalog)
    score = routing_score()
    if score is None:
        sys.exit('scripts/eval_routing.py did not run; the trainer quotes its score')
    html = html.replace('__STYLES__', styles)
    html = html.replace('__SCRIPTS__', '\n\n'.join('<script>\n' + s.rstrip('\n') + '\n</script>' for s in scripts))
    html = html.replace('__FONT_B64__', b64('assets/instrument-sans-latin.woff2'))
    html = html.replace('__LOGO_B64__', b64('assets/riverside-logo.png'))
    html = html.replace('__SKILL_CATALOG__', catalog_json)
    html = html.replace('__SKILL_COUNT__', str(len(catalog)))
    html = html.replace('__BRAIN_GRAPH__', _inline_json(graph))
    html = html.replace('__ROUTING_CASES__', _inline_json(routing_cases()))
    html = html.replace('__GRAPH_SKILLS__', str(sum(1 for n in graph['nodes'] if n['kind'] == 'skill')))
    html = html.replace('__GRAPH_DOCS__', str(sum(1 for n in graph['nodes'] if n['kind'] != 'skill')))
    html = html.replace('__GRAPH_LINKS__', str(len(graph['links'])))
    html = html.replace('__ROUTING_N__', str(score['n']))
    html = html.replace('__ROUTING_TOP1__', str(score['top1']))
    html = html.replace('__ROUTING_TOP3__', str(score['top3']))
    html = html.replace('__BUILD_DATE__', datetime.date.today().strftime('%b %d, %Y'))
    # The Artifact host wraps the page in its own doctype/html/head/body skeleton,
    # so the published file must not carry a second one.
    html = re.sub(r'(?i)<!doctype html>\s*|</?html(\s[^>]*)?>\s*|</?head>\s*|</?body(\s[^>]*)?>\s*', '', html)
    left = re.findall(r'__[A-Z][A-Z0-9_]+__', html)
    if left:
        sys.exit('unreplaced markers: %s' % sorted(set(left)))
    return html


def main():
    html = build()
    target = os.path.join(HERE, 'index.html')
    if '--check' in sys.argv:
        current = open(target, encoding='utf-8').read() if os.path.exists(target) else ''
        # the build date is the only field allowed to differ
        norm = lambda s: re.sub(r'[A-Z][a-z]{2} \d{2}, \d{4}', 'DATE', s)
        if norm(current) != norm(html):
            sys.exit('index.html is stale: run python3 tools/marketing-brain-trainer/build.py')
        print('index.html is up to date')
        return
    with open(target, 'w', encoding='utf-8') as f:
        f.write(html)
    print('wrote index.html (%d bytes, %d skills in catalog)' % (len(html), len(skill_catalog())))


if __name__ == '__main__':
    main()
