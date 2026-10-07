# New Company Setup

## Private Profile

Run `python3 scripts/company_config.py --init` and edit the generated local profile.
The example remains blank and is safe to commit. The local profile is ignored.

Fill company name, website, timezone, target audiences, positioning, and the tools
you actually use. Each integration records a provider, verified account identity,
and whether it is enabled. Credentials stay in the platform's credential store.

Run `python3 scripts/company_config.py --require-ready`. This checks structure and
basic readiness; it does not log in, verify permissions, or activate automation.

## First Week

1. Document the new audience, product, approved claims, and brand source.
2. Add your CRM, task system, analytics, and communication workspace only as needed.
3. Verify account identities with a read-only request before enabling each integration.
4. Define funnel stages, attribution, currency, timezone, and metric owners.
5. Try one draft workflow on synthetic data, then a small authorized real task.

Store private profiles, interview notes, 1:1s, reports, exports, and graphs in
approved private storage. `local/` is ignored for local artifacts.
Keeping private context outside Git makes the next company transition simpler.

## Shared Maintenance

Edit canonical skills, regenerate both managed blocks and the Codex mirror, then
run the preflight. Add synthetic regression cases when changing workflow behavior.
Never use real employees or customer records as test fixtures.

## Historical Copies

The current-file cleanup does not erase prior Git commits or outside copies.
A clean-history export or an approved history rewrite is a separate operation.
Published sites, wiki pages, Actions artifacts, releases, ZIPs, backups, and installed
plugins must be assessed separately if they previously copied the company context.
