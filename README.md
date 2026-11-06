# Local AI Safety Standard

A practical, layered standard for running **local** LLMs and AI agents safely —
plus a curated, verified directory of the safety harnesses and guardrails that
implement it, and a pointer to a reference implementation you can audit.

This is not another list of tools. It is an answer to one question:

> *If I run my own models on my own hardware, what do I actually need — in what
> order — so that a capable agent stays pinned to my objectives, stays inside my
> boundary, and can never be turned into the thing it is meant to guard?*

## What this is

- **A standard** (`STANDARD.md`) — a layered model of the controls that keep a
  local agent safe, mapped to the OWASP Agentic Top 10. Read it first.
- **A directory** (`harnesses/`) — a curated, categorized set of open-source
  safety harnesses and guardrails. Every entry is **verified against its live
  repository** (URL, license, last activity) on a dated basis, and carries a
  plain-language risk note. Entries that go stale drop to *unverified*
  automatically.
- **A reference implementation** (`reference/`) — a working, integrated guardrail
  stack that implements the standard end to end, published under this org and
  auditable line by line.

## What this is not

- **Not an endorsement.** Listing a project here means we verified its identity
  and metadata on a given date. It does **not** mean we have audited its code,
  and it does **not** mean we recommend you run it without review. **Review any
  harness before you use it, and run it in a sandbox.**
- **Not a forum.** There is no account, no comment, no dynamic input. The only
  way to add or change an entry is a reviewed pull request.
- **Not a vendor.** We do not bundle, build, or execute any listed project's
  code. The directory is metadata and links.

## The values

- **Privacy by default.** Everything runs on your hardware before it ever
  touches the network. Your data stays on your machines.
- **Local-first, one machine.** The reference stack is designed to run on a
  single box with no cloud dependency.
- **Ethical by construction.** The safety rules are enforced by the process —
  gates, checks, and a second signal — not hoped for.
- **Community driven.** Add a harness by opening a pull request with the
  verification evidence. The bar is in `CONTRIBUTING.md`.

## Start here

1. Read [`STANDARD.md`](STANDARD.md) — the layered model.
2. Browse [`harnesses/`](harnesses/) — the verified directory.
3. Look at [`reference/`](reference/) — the working stack that implements it.
4. Want to add a harness? Read [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT — see [`LICENSE`](LICENSE).
