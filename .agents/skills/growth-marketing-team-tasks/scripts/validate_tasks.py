#!/usr/bin/env python3
"""Fail loudly if the dashboard's baked TASKS array will not parse in a browser."""
import re, json, sys
from collections import Counter
path = sys.argv[1] if len(sys.argv) > 1 else 'assets/dashboard.html'
s = open(path, encoding='utf-8').read()
m = re.search(r'var TASKS = (\[.*?\n  \]);', s, re.S)
if not m: sys.exit('FAIL: TASKS array not found')
arr = m.group(1)
for i, l in enumerate(arr.split('\n')):
    t = l.rstrip()
    if not t or t in ('[', ']', '  ]'): continue
    if t.endswith('}'):
        sys.exit(f'FAIL: line {i+1} of the array ends with }} and no comma -> "}} {{" breaks the whole array:\n  {t[:120]}')
    if not t.endswith('},'):
        sys.exit(f'FAIL: line {i+1} has no row terminator:\n  {t[:120]}')
j = re.sub(r'(?m)(?<=[{,]\s)([A-Za-z_][A-Za-z0-9_]*):', r'"\1":', arr)
j = re.sub(r',(\s*\])', r'\1', j)
j = re.sub(r'\n\s*\n', '\n', j)
try: data = json.loads(j)
except json.JSONDecodeError as e: sys.exit(f'FAIL: array does not parse: {e}')
ids = [d['id'] for d in data]
dupes = [k for k, v in Counter(ids).items() if v > 1]
if dupes: sys.exit(f'FAIL: duplicate ids: {dupes}')

# A typo'd status is silent and nasty: the row is not "Done" or "Watch list", so every count
# treats it as open work forever, and no badge or filter ever matches it. Pin the vocabulary
# to the dashboard's own STATUSES array so the two cannot drift.
m2 = re.search(r'var STATUSES = (\[[^\]]*\]);', s)
if not m2: sys.exit('FAIL: STATUSES array not found')
allowed = set(json.loads(m2.group(1))) | {None}
bad = [(d['id'], d.get('status')) for d in data if d.get('status') not in allowed]
if bad: sys.exit(f'FAIL: unknown status values (allowed {sorted(allowed - {None})} or omitted): {bad}')

status_counts = Counter(d.get('status') or 'Open (implicit)' for d in data)
print(f'OK: {len(data)} rows, {len(set(ids))} unique ids, teams={dict(Counter(d["team"] for d in data))}')
print(f'    statuses={dict(status_counts)}')
