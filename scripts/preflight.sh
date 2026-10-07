#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 scripts/privacy_check.py
python3 scripts/company_config.py --template
python3 -m unittest discover -s tests -v
python3 scripts/lint_skill_frontmatter.py
python3 scripts/lint_references.py
python3 scripts/lint_agents.py
python3 scripts/harmonize_agents.py --check
python3 scripts/eval_routing.py
python3 scripts/eval_output_lift.py
python3 scripts/test_eval_output_lift.py
python3 scripts/sync-codex.py --check
