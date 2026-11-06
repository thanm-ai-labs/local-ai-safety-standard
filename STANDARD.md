# The Local AI Safety Standard

A layered model for running local LLMs and AI agents safely. Each layer answers
one question. The layers are **cumulative** — a safe deployment has all of them,
in this order — and each is **enforced in code**, not left to the model's
goodness.

The through-line: **a capable agent that is not *pinned* drifts toward its own
goals.** The standard is how you pin it — to your objectives, inside your
boundary, with every consequential action reversible and consented, and every
claim checked by a second signal.

## The threat model (what we are defending against)

1. **Objective drift / rogue behavior** — the agent optimizes for something other
   than what you asked.
2. **Indirect prompt injection** — the agent reads untrusted content (a web page,
   a file, an email) and is steered into an action.
3. **Exfiltration** — data leaves the boundary to an endpoint you did not approve.
4. **Destructive / irreversible action** — the agent deletes, overwrites, or
   pushes something that cannot be undone.
5. **Self-amplification** — the agent grows its own capability or modifies the
   guardrails that constrain it.
6. **Supply-chain / trust inversion** — a "recommended" tool is not what it
   claims to be.

## The layers

### Layer 0 — The guardrails cannot be modified by the guarded (keystone)

The controls that constrain the agent are **hashed into a committed baseline**.
Any change to a guardrail file fails a check unless a human approves it (a
signed trailer). The agent that is guarded cannot edit its own cage. Without this
layer, every other layer can be quietly removed by the thing it protects.

*Maps to: OWASP Agentic — excessive autonomy / self-modification.*

### Layer 1 — Objectives are pinned, not inferred

The agent's goal is stated explicitly and checked against, not inferred from
context. A plan is written and critiqued **before** execution; a consequential
decision enumerates its options before the plan is written. The agent states what
it believes is right even when it disagrees with the user — agreement is not the
goal, correctness is.

*Maps to: OWASP Agentic — objective hijacking / goal misalignment.*

### Layer 2 — The boundary is local; egress is allowlisted

Every outbound call is checked against an allowlist of approved endpoints
(loopback + private network + a named set of public APIs). Anything else is
denied. A single choke point enforces it, and a scan runs in CI. The default is
*no egress*; the cloud is a choice, not a default.

*Maps to: OWASP Agentic — data exfiltration / sensitive information disclosure.*

### Layer 3 — No self-amplification (least privilege, tool isolation)

Each capability is enumerated in a ledger; a new capability is a human decision,
not a side effect. Tools are isolated by domain — an agent that reads untrusted
content holds no tools that can act on it. **Ingestion is separated from
execution by construction.** A compromised reader has no hands.

*Maps to OWASP Agentic — excessive agency / privilege escalation.*

### Layer 4 — Every consequential action is reversible and consented

Before a production change, the current state is captured (the rollback point).
Destructive command classes are denied by a denylist (a floor, not a ceiling).
Mass deletion is gated by a second check. Actions with real-world consequence
require explicit confirmation of the exact action.

*Maps to: OWASP Agentic — irreversible action / resource abuse.*

### Layer 5 — Every capability is enumerated

The set of things the system can do is a declared, reviewable list. Capability
growth without approval is a finding. You can answer "what can this agent do?"
from a document, not by reading the code.

*Maps to: OWASP Agentic — excessive autonomy / scope creep.*

### Layer 6 — Dual-signal checks (the second signal)

Where possible, every decision and data assertion is checked by **two independent
signals** — a second model, a second tool, a test against a build, a read against
a query. A single signal is a hypothesis, not a fact. The plan is critiqued by a
different model than the one that wrote it; a check that cannot run is reported
as a **blind spot**, never waved through as clean.

*Maps to: OWASP Agentic — over-reliance on a single component / lack of
verification.*

### Layer 7 — Kernel-level sandboxing

The inference runtime and the worker run in a sandbox with network egress denied
(or restricted to loopback). Model artifacts are checksum-verified on download.
The sandbox is the last physical barrier between the agent and the host.

*Maps to: OWASP Agentic — insufficient isolation / runtime compromise.*

### Layer 8 — A load-bearing upgrade always comes back

Upgrading a component the system runs *on* (the runtime, the model pool, a
supervisor) follows a safe-upgrade protocol: stage a verified rollback artifact
**before** touching anything, pretest on a scratch surface, cut over with a
self-contained gated script that auto-rolls-back on failure, then post-verify the
component is genuinely serving. The guarantee: the component is back and serving
whether the upgrade succeeded or failed.

*Maps to: OWASP Agentic — supply-chain / availability.*

## The directory and the reference

- `harnesses/` lists open-source projects that implement pieces of these layers.
  Each entry is verified (URL, license, last activity) on a dated basis and
  carries a risk note. **Stale entries drop to unverified.**
- `reference/` points to a working stack that implements the layers end to end,
  published and auditable under this org.

## Using the standard

You do not need all eight layers to start, but you should know which ones you are
missing. Layer 0 (the guardrails are immutable) and Layer 2 (egress is
allowlisted) are the two that matter most for a local deployment, because they are
the ones an agent can otherwise remove or bypass on its own.
