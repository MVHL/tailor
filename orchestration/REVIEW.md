# Retrospective — orchestration MVP (2026-08-02)

A critical self-review after the MVP was built and validated end-to-end. Graded as Role B
(adversarial): the goal is to find where the *system* leaks, not to bless it. Findings are
ranked; the top three are already fixed in this pass.

## Is it ready?
Yes for **piloting on non-sensitive repos**. Not yet for **unattended runs on repos with
secrets** (see F1) or for **trusting the auto-generated quality scores** without a human
glance (F2/F4). The loop mechanics (frame→plan→delegate→review→record, red→green, merge,
audit trail) are proven.

## Findings

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| F1 | **High** | `--dangerously-skip-permissions` disables *all* agy permission checks, not just file scope. A headless agy run could touch paths outside the worktree or hit the network. | **Fixed (documented)** — prominent safety note in `CLAUDE.md`; `--sandbox` opt-in; adapter header warns. *Residual:* true confinement (sandbox-by-default that still runs tests) is unverified — needs testing. |
| F2 | **High** | Review wasn't truly independent — the same context framed, delegated, and reviewed, so "adversarial Role B" was just a label and could rationalize its own spec. | **Fixed** — `ag-delegate`/`ag-review` now spawn a fresh subagent for the judgment pass, given only diff+spec+TP. |
| F3 | Med | `ag-init` re-run could duplicate the protocol block / clobber live records. | **Fixed** — marker-based idempotency; skips existing scaffold files. |
| F4 | Med | Quality **scores are self-assigned** by the same LLM → optimistic bias. | Partially addressed — objective metrics (iterations, tokens, tests pass/fail) are mechanical; AC grades now come from the independent subagent. *Residual:* no schema validation of the `metrics`/frontmatter → a malformed RECORD breaks the dashboard. Add a validator in Phase 2. |
| F5 | Med | `ag-frame` leans on `jira-problem-framing`, which may attempt Jira writes; MVP is local-only. | Open — ensure ag-frame uses it in a local/tagging-only mode; don't call Jira in MVP. |
| F6 | Med | Real-world **test-framework detection** is naive ("one command runs the plan"); fragile for complex build/test setups. | Open — planner explores, but needs hardening on real repos. |
| F7 | Low | `agy` JSON schema could drift across versions; empty `conversation_id` would make resume silently no-op. | Open — adapter extracts defensively; add an explicit warn when resume id is empty. |
| F8 | Low | `ag-run` vs `ag` overlap; mild confusion. | Accepted — documented distinction (`/ag` = smart/resume; `/ag-run` = linear). Consolidate later if unused. |
| F9 | Low | Red state isn't checked for the *right* failure reason (could be an import error, not a missing feature). | Open — cheap to add a sanity check in `ag-test-plan`. |
| F10 | Low | Portability: `$ORCH_HOME` is machine-local, not a plugin. | Deferred to Phase 3 (packaging). |

## Highest-leverage next steps (recommend, in order)
1. **Phase 2 dashboard** — turns the `metrics` we now emit into the overview/triage board;
   also the natural home for a frontmatter **validator** (closes F4 residual).
2. **Harden `ag-frame` for local-only + real grilling** (F5) and **test-framework detection**
   (F6) — these are what a real (non-toy) task will hit first.
3. **Verify a sandbox profile that still runs tests** (F1 residual) before any unattended use.

## What's proven (don't re-litigate)
Adapter ↔ agy (v1.1.9) round-trip incl. structured JSON; worktree isolation; red→green;
no-test-cheating check; Conductor-owned merge; full committed audit trail with the
mandatory assumptions/problems/bugs/issues closing section; per-step metrics schema.
