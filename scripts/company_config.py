#!/usr/bin/env python3
"""Initialize and validate local company context; never activate integrations."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "config/company.example.json"
LOCAL = ROOT / "config/company.local.json"


def validate(config, require_ready=False):
    errors = []
    if not isinstance(config, dict):
        return ["profile must be an object"]
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        errors.append("schema_version must be 1")
    company = config.get("company")
    if not isinstance(company, dict):
        errors.append("company must be an object")
    else:
        for field in ("name", "website", "timezone", "positioning"):
            value = company.get(field)
            if not isinstance(value, str):
                errors.append(f"company.{field} must be a string")
            elif require_ready and not value.strip():
                errors.append(f"company.{field} is required")
        audiences = company.get("audiences")
        if not isinstance(audiences, list) or any(not isinstance(x, str) or not x.strip() for x in audiences):
            errors.append("company.audiences must be an array of nonempty strings")
        elif require_ready and not audiences:
            errors.append("company.audiences needs at least one audience")
        website = company.get("website")
        if isinstance(website, str) and website:
            parsed = urlparse(website)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                errors.append("company.website must be an HTTPS URL without embedded credentials")
        timezone = company.get("timezone")
        if isinstance(timezone, str) and timezone:
            try:
                ZoneInfo(timezone)
            except (ValueError, ZoneInfoNotFoundError):
                errors.append("company.timezone must be a valid IANA timezone")
    if not isinstance(config.get("team"), list) or any(not isinstance(x, dict) for x in config.get("team", [])):
        errors.append("team must be an array of objects")
    sources = config.get("sources")
    if not isinstance(sources, dict) or any(not isinstance(sources.get(k), str) for k in ("brand", "product", "messaging", "metrics")):
        errors.append("sources must provide brand, product, messaging, and metrics strings")
    integrations = config.get("integrations")
    if not isinstance(integrations, dict):
        errors.append("integrations must be an object")
    else:
        for name, integration in integrations.items():
            if not isinstance(integration, dict) or type(integration.get("enabled")) is not bool:
                errors.append(f"integration {name}: enabled must be a boolean")
            elif integration["enabled"] and any(not isinstance(integration.get(k), str) or not integration[k].strip() for k in ("provider", "account")):
                errors.append(f"integration {name}: enabled integrations need provider and verified account")
    automation = config.get("automation")
    if not isinstance(automation, dict) or type(automation.get("enabled")) is not bool:
        errors.append("automation.enabled must be a boolean")
    elif automation["enabled"]:
        errors.append("automation is unsupported by the neutral template; leave it disabled")
    return errors


def initialize(example=EXAMPLE, local=LOCAL):
    content = example.read_text()
    errors = validate(json.loads(content))
    if errors:
        raise ValueError("invalid example configuration")
    # Exclusive creation preserves private context on subsequent runs.
    with local.open("x", encoding="utf-8") as handle:
        handle.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--init", action="store_true")
    mode.add_argument("--template", action="store_true")
    mode.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    if args.init:
        try:
            initialize()
        except FileExistsError:
            print("Local profile already exists; preserved without changes.")
            return 0
        except (OSError, ValueError):
            print("Could not initialize the local profile.", file=sys.stderr)
            return 2
        print("Created ignored config/company.local.json. Fill it in, then run --require-ready.")
        return 0
    path = EXAMPLE if args.template else LOCAL
    try:
        errors = validate(json.loads(path.read_text()), args.require_ready)
    except (OSError, ValueError):
        print("Profile missing or invalid JSON. Run --init to create a local profile.", file=sys.stderr)
        return 2
    for error in errors:
        print(error)
    if not errors:
        print("Configuration valid. No integration or automation was activated.")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
