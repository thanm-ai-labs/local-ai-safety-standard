# Reference implementation

The standard in [`../STANDARD.md`](../STANDARD.md) is a model. This directory
points to a **working stack that implements it end to end**, published under this
org and auditable line by line.

The reference stack is the integrated guardrail set that this org runs in
production. It is the only code in this project that we stand behind — the
directory entries in [`../harnesses/`](../harnesses/) are third-party and are
listed for reference, not endorsed.

## The pieces

| Layer (STANDARD.md) | Reference component | Repo |
|---|---|---|
| Layer 0 — guardrails immutable | guardrail manifest + baseline | `thanm-ai-labs/safety-guard` |
| Layer 4 — reversible / mass-deletion gate | git safety gate | `thanm-ai-labs/git-safety` |
| Layer 2 — egress allowlist | LLM endpoint guard | (in the agent-loop reference set) |
| Layer 6 — dual-signal checks | plan critic + scenario runner | (in the agent-loop reference set) |
| Layer 1/3/5 — pinned objectives, tool isolation, capability ledger | the local agent loop | (in the agent-loop reference set) |

> The agent-loop reference set (checkpoint, critic, bounded worker, endpoint
> guard) is published as its own repo under this org. See the org page for the
> current list.

## Why a reference matters

A standard is only as good as the proof that it can be built. The reference stack
shows the layers working together — the immutable guardrail baseline, the egress
allowlist, the dual-signal critic, the reversible-action gate — so a reader can
audit the mechanism, not just read the description.

**Review before use.** Even the reference is code you should read before you run
it. That is the point of publishing it.
