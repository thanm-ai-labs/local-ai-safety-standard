# Contributing

Thanks for helping keep the directory honest. This guide covers the bar we hold
entries to and how to submit one.

## Ground rules

- **Verified, not asserted.** Every entry must be checked against its **live**
  repository before it is listed: the URL must resolve to the claimed repo, and
  the license and last activity must be read from the repo — not remembered or
  guessed. An entry that cannot be verified is not listed.
- **No code, ever.** We do not bundle, build, or execute any listed project. The
  directory is metadata and links only. Do not add build steps, vendored code, or
  install scripts.
- **A risk note is mandatory.** Every entry carries a one-line, plain-language
  note about what the tool does and the caution a reader should take. A link-back
  is never an endorsement.
- **No secrets, no internal paths.** Never commit a LAN address, a personal path,
  a username, a token, or an internal reference. The publish scrub rejects these.
- **Staleness is automatic.** An entry older than 90 days drops to *unverified*
  on its own. Re-verify it (bump `last_verified`) to restore it.

## How to add a harness

1. Copy `harnesses/_template.yaml` to `harnesses/<slug>.yaml`.
2. Fill every required field. Read `license` and the last commit **from the live
   repo**. Set `status: unverified` until the checks pass.
3. Run the validator:
   ```bash
   python tools/validate_harnesses.py
   ```
   It checks the schema, that the URL resolves, that `risk_note` is present, and
   that no entry carries instruction-like content. It also reports any entry that
   has gone stale.
4. Open a pull request with the entry **and** the verification evidence (the URL
   you checked, the license you read, the date).

A maintainer reviews the PR. For any entry that claims to be a *security* tool,
the entry gets an extra look — "is this what it claims to be?" — before it is
marked verified.

## The entry schema

Required fields (the validator enforces these):

| Field | Meaning |
|---|---|
| `name` | Display name |
| `repo_url` | `https://github.com/<owner>/<repo>` — must resolve |
| `owner` | GitHub org/user |
| `license` | Read from the live repo |
| `language` | Primary language |
| `last_verified` | ISO date the entry was checked |
| `verified_by` | Who checked it |
| `threat_coverage` | List: `injection`, `exfil`, `destructive`, `supply-chain`, `mcp`, `other` |
| `local_first` | `true` if it runs fully offline |
| `risk_note` | One line, plain language, non-empty |
| `status` | `verified` or `unverified` |

There are deliberately **no free-text fields** beyond `risk_note`. The directory
is structured data, not prose.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
