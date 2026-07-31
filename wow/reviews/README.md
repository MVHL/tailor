# Ticket Execution Reviews

Health assessments of individual Jira tickets across their full artifact lifecycle
(Problem · Requirements · Non-Goals · Acceptance Criteria · Test Plan · Impl Plan · Merge
Request), produced by the `ticket-execution-review` skill. Each `.html` file is a
self-contained, light-theme dashboard — open it directly in a browser.

Each dashboard scores its three sections (**Framing / Planning / Building**) as the mean of the
section's *assessable* checks — good = 100%, exists-but-flagged = 50%, overdue = 0%; checks that
are N/A for a Story or "not fetched" are excluded (a section with nothing assessable shows
"n/a"). Scores reflect **artifact & traceability health only**, not code correctness.

Grading follows the org's own rubric in [`../playbook.html`](../playbook.html) §2–3,
[`../lifecycle-drivers.html`](../lifecycle-drivers.html), and
[`../lifecycle-stages.html`](../lifecycle-stages.html) — not invented heuristics. Findings are
advisory; no ticket was edited.

Section scores below are **Framing / Planning / Building**.

| Ticket | Type | Status | Scores (F / P / B) | One-line verdict |
|---|---|---|---|---|
| [ID2-35914](ID2-35914-review.html) — Add new tabs under CPSC Product Registry | Story | Closed / Done | 69% / 0% / n/a | Delivered & closed, but low traceability: the User Story is about credential storage while all ACs restructure UI tabs (copy-paste mismatch); orphan ACs; Impl Plan for the tab work absent. |
| [ID2-35915](ID2-35915-review.html) — Token Validation | Story | Closed / Done | 100% / n/a / 100% | Delivered, well-framed, well-evidenced: User Story aligns with ACs, 3 GitLab MRs linked, PRD + Epic linked, verified on PRE. Remaining gaps are tag hygiene. |
| [ID2-36257](ID2-36257-review.html) — [BE-1] Add submitted_by + meta to CpscImportLog | Story (BE) | In Code Review | 95% / 100% / n/a | In-flight & well-authored: real file-level Impl Plan, sharp ACs (incl. AC4 edge case). Flags: AC5 is a DoD gate not an AC; parent Epic un-framed (In Ideation); an open question unresolved. |

## Common threads across all three

- **No explicit `P/R/T#/IM#` tags on any ticket.** ACs are labeled (`AC1:` …) but Requirements
  and Impl Plans had to be inferred from prose (shown with a yellow "verify — unlabeled"
  border). Running `jira-problem-framing` on each would lift future reviews to high confidence.
- **Test Plans not fetched** — this org keeps formal test cases in a separate **AIO Tests** app
  panel not exposed by the Jira API. All three show informal testing evidence in comments.
- **MR metadata degraded honestly** — layer-1 links were surfaced only for ID2-35915 (3 MRs);
  approvals/review-comment counts need a GitLab token (absent), so those sub-fields read "not
  fetched," never a faked verdict.

_Generated 2026-07-20 from live Jira data._
