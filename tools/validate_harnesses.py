#!/usr/bin/env python3
"""Validate the harness directory entries.

Stdlib-only. This is the repo's declared publish check (ADR-0036): it runs on
the staged tree before anything is pushed.

What it enforces (the security contract, see STANDARD.md + CONTRIBUTING.md):
  * schema   — every required field present, correct types, repo_url well-formed
  * threat   — threat_coverage values are from the allowed set
  * risk     — risk_note is present, non-empty, and not instruction-like
  * stale    — an entry older than STALE_DAYS drops to "unverified" (reported)
  * url      — with --check-url, each repo_url must resolve (HTTP 200/301/302)

It NEVER downloads or executes any listed project's code. It only reads the
entry files (and, optionally, the HTTP status of the URL).

Exit codes: 0 = all entries valid (stale entries are warnings, not failures),
1 = one or more schema/risk failures, 2 = a --check-url URL did not resolve.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
import urllib.request
from pathlib import Path

REQUIRED_FIELDS = {
    "name": str,
    "repo_url": str,
    "owner": str,
    "license": str,
    "language": str,
    "last_verified": str,
    "verified_by": str,
    "threat_coverage": list,
    "local_first": bool,
    "risk_note": str,
    "status": str,
}
ALLOWED_THREATS = {"injection", "exfil", "destructive", "supply-chain", "mcp", "other"}
ALLOWED_STATUS = {"verified", "unverified"}
REPO_URL_RE = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STALE_DAYS = 90

# Instruction-like content that must not appear in a risk_note (the directory is
# structured data, not a prompt-injection payload).
INJECTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "disregard your",
    "you are now",
    "new instructions",
    "system:",
    "<system",
    "assistant:",
    "curl | sh",
    "curl |bash",
    "wget | sh",
    "eval(",
    "exec(",
)


def _parse_scalar(raw: str):
    raw = raw.strip()
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    if (raw.startswith('"') and raw.endswith('"')) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        return raw[1:-1]
    return raw


def _parse_entry(path: Path) -> dict:
    """Minimal YAML-subset parser: top-level `key: value` and `- item` lists.

    Deliberately small — the schema is flat. Anything it cannot parse is a
    failure, not a guess.
    """
    data: dict = {}
    current_list_key = None
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(" ") or line.startswith("\t"):
            # continuation of a list
            stripped = line.strip()
            if stripped.startswith("- ") and current_list_key is not None:
                data[current_list_key].append(_parse_scalar(stripped[2:]))
            elif stripped == "-" and current_list_key is not None:
                data[current_list_key].append("")
            else:
                raise ValueError(f"{path.name}:{lineno}: unexpected indented line {line!r}")
            continue
        if ":" not in line:
            raise ValueError(f"{path.name}:{lineno}: expected 'key: value', got {line!r}")
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            # start of a list (or empty)
            data[key] = []
            current_list_key = key
        else:
            data[key] = _parse_scalar(val)
            current_list_key = None
    return data


def _is_instruction_like(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in INJECTION_MARKERS)


def validate_entry(path: Path, today: _dt.date, check_url: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = _parse_entry(path)
    except ValueError as exc:
        return [f"{path.name}: parse error: {exc}"], warnings

    # schema
    for field, ftype in REQUIRED_FIELDS.items():
        if field not in data:
            errors.append(f"{path.name}: missing required field '{field}'")
            continue
        val = data[field]
        if ftype is bool:
            if not isinstance(val, bool):
                errors.append(f"{path.name}: '{field}' must be a bool, got {val!r}")
        elif ftype is list:
            if not isinstance(val, list):
                errors.append(f"{path.name}: '{field}' must be a list, got {val!r}")
        elif not isinstance(val, str) or val == "":
            errors.append(f"{path.name}: '{field}' must be a non-empty string, got {val!r}")

    if errors:
        return errors, warnings

    # repo_url well-formed
    m = REPO_URL_RE.match(data["repo_url"])
    if not m:
        errors.append(
            f"{path.name}: repo_url must be https://github.com/<owner>/<repo>, got {data['repo_url']!r}"
        )
    elif m.group(1).lower() != data["owner"].lower():
        errors.append(
            f"{path.name}: owner '{data['owner']}' does not match repo_url owner '{m.group(1)}'"
        )

    # date
    if not DATE_RE.match(data["last_verified"]):
        errors.append(f"{path.name}: last_verified must be YYYY-MM-DD, got {data['last_verified']!r}")
    else:
        try:
            lv = _dt.date.fromisoformat(data["last_verified"])
            age = (today - lv).days
            if age > STALE_DAYS and data["status"] == "verified":
                warnings.append(
                    f"{path.name}: STALE ({age}d > {STALE_DAYS}d) — effective status is 'unverified'; "
                    "re-verify to restore"
                )
        except ValueError:
            errors.append(f"{path.name}: last_verified is not a valid date: {data['last_verified']!r}")

    # threat coverage
    for t in data["threat_coverage"]:
        if t not in ALLOWED_THREATS:
            errors.append(f"{path.name}: threat_coverage value '{t}' not in {sorted(ALLOWED_THREATS)}")
    if not data["threat_coverage"]:
        errors.append(f"{path.name}: threat_coverage must not be empty")

    # status
    if data["status"] not in ALLOWED_STATUS:
        errors.append(f"{path.name}: status must be one of {sorted(ALLOWED_STATUS)}, got {data['status']!r}")

    # risk note
    if _is_instruction_like(data["risk_note"]):
        errors.append(f"{path.name}: risk_note contains instruction-like content (rejected)")

    # url resolution (optional)
    if check_url and m:
        try:
            req = urllib.request.Request(data["repo_url"], method="GET",
                                         headers={"User-Agent": "local-ai-safety-standard/validator"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                code = resp.getcode()
            if code not in (200, 301, 302):
                errors.append(f"{path.name}: repo_url returned HTTP {code}")
        except Exception as exc:  # noqa: BLE001 - a URL we cannot reach is a failure, not a pass
            errors.append(f"{path.name}: repo_url did not resolve ({exc})")

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=None, help="harnesses/ directory (default: <repo>/harnesses)")
    ap.add_argument("--check-url", action="store_true", help="resolve each repo_url over HTTP")
    args = ap.parse_args(argv)

    here = Path(__file__).resolve().parent
    harness_dir = Path(args.dir) if args.dir else here.parent / "harnesses"
    if not harness_dir.is_dir():
        print(f"error: harnesses dir not found: {harness_dir}", file=sys.stderr)
        return 1

    today = _dt.date.today()
    entries = sorted(p for p in harness_dir.glob("*.yaml") if p.name != "_template.yaml")
    if not entries:
        print(f"error: no entries found in {harness_dir}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for path in entries:
        errs, warns = validate_entry(path, today, args.check_url)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    for w in all_warnings:
        print(f"  [warn] {w}")
    for e in all_errors:
        print(f"  [FAIL] {e}")

    print(f"\n{len(entries)} entries checked ({len(all_errors)} errors, {len(all_warnings)} warnings)")
    if all_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
