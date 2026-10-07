# Evaluations

All cases are synthetic. Routing cases test whether targets exist and descriptions
overlap; output cases describe expected behavior and optional deterministic checks.
Neither structural check proves real task quality.

Run:
```sh
python3 scripts/eval_routing.py
python3 scripts/eval_output_lift.py
python3 scripts/test_eval_output_lift.py
```

See `docs/skill-evals.md`. Never copy private records into fixtures.
