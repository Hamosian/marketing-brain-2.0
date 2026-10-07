# Skill Evaluations

Use `python3 scripts/eval_routing.py` for structural routing validation.
Description similarity is advisory; it does not prove how a model will route.

Use `python3 scripts/eval_output_lift.py` to validate output cases.
Optional model-backed runs require deliberate setup and are not part of CI.

Every fixture must be synthetic, without employee names, customer data, real account
identifiers, or copied operational reports. Add tests for missing context and ambiguous
scope. Verify both the workflow output and what the skill must not do.

Keep actual run outputs under ignored `evals/runs/`.
