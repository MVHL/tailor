# Inspection measurement configuration — design prototypes

Design prototypes for the admin UI that configures the measurement portion of an
Inspectorio inspection workflow. Each file is standalone, self-contained HTML with
no dependencies — open any of them directly in a browser.

**Current version: [`v14.html`](v14.html).** The earlier files are kept as a record of
what was tried and why it was rejected.

Each file carries its rationale in code comments. Read those rather than
re-deriving the model.

## Version history

| File | Change | Why superseded |
|---|---|---|
| [`v1.html`](v1.html) | Original. Separate "input value" and "calculated value" row types; per-row Specification/Standalone toggle | Two Add buttons for one thing with an optional attribute; calculated rows were forced to carry an evaluation, blocking intermediate plumbing values |
| [`v2.html`](v2.html) | Merged row types into one `+ Add value`; merged Source + type/unit into a "Value from" control | "Value from" was the wrong axis — it implied provenance of the *number* when the control governed the *unit and criteria* |
| [`v3.html`](v3.html) | Split into two independent axes (Specification, Value); POM terminology; ordered workflow steps instead of reusable templates | Presented "formula judged against chart tolerance" as a win — later retracted as meaningless |
| [`v4.html`](v4.html) | Measurement Chart, not POM; no unit at chart level; sidebar became the drag-reorderable inspection order | Kept the chart choice per row, so a chart row and a single value sat in the same list at the same visual weight |
| [`v5.html`](v5.html) | One evaluation structure with presets over it, replacing one structure per rule type | — (this part survives in v9) |
| [`v6.html`](v6.html) | `basis` moved from bound to rule; lower ≤ upper and empty-interval validation; graded bands | Band validation was "must widen", which falsely rejected adjacent bands (0–8 Pass, 8–12 Warning) |
| [`v7.html`](v7.html) | User-defined result labels; standard-presence decides relative vs actual bands; the confusing "absolute" basis removed | Let *some* rows be per-POM and others scalar within one step — the root cause of the meaningless formula-against-chart case |
| [`v8.html`](v8.html) | Moved the chart/custom choice up to the step; a chart step had no rows at all | Broke the shrinkage-per-POM case: measure Before/After wash per POM, derive a shrinkage per POM |
| [`v9.html`](v9.html) | A step has a `scope`; rows are columns, uniform within the step; two Add buttons; per-POM preview table | Forced every column in a step to share one cardinality. Two real reports break that — see v10 |
| [`v10.html`](v10.html) | Cardinality moves to the **column** as a capture level, plus an authored repeat axis; `mc` nullable so `scope` disappears; `source` declared not inferred; broadcast/aggregate rule on formula references | The repeat axis needed a 2D fan the preview could not draw; coarser columns inside a chart step rested on an invented example |
| [`v11.html`](v11.html) · [`v12.html`](v12.html) | Preview rendering: generic `{POM n}` placeholders instead of invented POM names, real form inputs instead of `[ enter ]` badges, uniform summary row | v12 dropped v10's `× per sample` header note, leaving the repeat fan silently mis-stated |
| [`v13.html`](v13.html) | Chart steps are **per-POM only**; the **repeat axis is removed**; `Duplicate value`; aggregate-completeness warning | — (this part survives) |
| **[`v14.html`](v14.html)** | Custom expressions take any number of values bound to letters; three features marked **post-MVP**; one Add button; the page's version log replaced by a structure-and-data-model explainer | Current |

## The model

A **step** is `{name, mc: null | {types:[]}, rows:[]}`. `mc` is *nullable*, not an
empty list — "no chart" and "a chart of any type" are different configurations and
cannot share one representation. Because the chart's presence is what gives the step a
POM level, there is no separate scope flag that could disagree with it.

A **row is a column** of the inspector's table, and it declares where it is
recorded. Three levels, the same shape in every product domain:

| Level | Garment | Fabric | Count knowable on this screen? |
|---|---|---|---|
| Lot | the order line item | the dye lot | no — from the order |
| Sample | the piece drawn | the roll | no — derived from lot size upstream |
| POM | point of measure in a chart | usually absent | no — resolves per chart |

No count is knowable on this screen, so it never shows one: columns say *per sample* and
the number resolves at inspection time.

**Which levels exist is decided by the step.** With a chart, POM is the only one — the
step's table *is* the chart, so every column in it is a column of that table, and the level
is stated rather than offered. Without a chart, lot and sample are both available and a
step may mix them.

**There is no repeat axis.** Measurements repeated within one unit — 1st and 3rd wash,
three weighings — are separate columns, not named repeats on one column. Two reasons:

- **The preview cannot draw it.** Repeats × samples is a two-dimensional set of cells
  inside a single table cell, needing a third header level. A version that tried it
  rendered only one of the two fans, so `Weight` read as three readings *in total* while
  `Average weight` read as per-sample — the opposite of the truth.
- **No observed column carries both fans.** The moisture check's three cells are samples,
  not repeats. Komar's 1st/3rd wash sit on a destructive test where only one roll per lot
  is measured, so the sample fan is 1 and it renders flat. The weight report shows the
  average, not the raw readings.

A repeat axis bought one real thing: an aggregate that could not go stale when a fourth
reading appeared. That is now `aggregateGapWarning()` — a check on the formula, which
protects every cloned column rather than only those that opted into an axis — plus a
one-click `Duplicate value`. **The honest cost:** Komar needs eight column definitions
where repeats would have needed four. That verbosity is left visible in the sample data
rather than trimmed.

A column's **grain** is the set of levels it varies over, derived from where it is
recorded. What keeps mixed grain from becoming ambiguous is an explicit rule on
references:

- **coarser → finer broadcasts.** A lot-level value applies to every sample under it.
- **finer → coarser needs a named aggregate.** Average, lowest, highest, total, or
  *the single recorded value* — the last being Komar's "capture per roll, impact to
  lot", where a destructive test leaves every other roll blank.

Mixed grain only occurs in steps without a chart, since a chart step's columns all sit at
POM level. The aggregate still earns its place there: Komar's rollup from sample to lot is
a level change.

One evaluation rule governs every cell of a column.

`source` (`"pom" | "custom"`) is **declared**, not inferred. Inferring it from
*(step has a chart) && (row has no formula)* forces every hand-entered column in a chart
step to be a POM measurement in the POM's own unit, which is wrong: whether a given
quantity is configured as a POM is a client's choice, not a property of the quantity, so
the same measurement is POM-backed for one customer and hand-defined for another.
`Within POM tolerance` is offered only where it can mean something — a column recorded per
POM, in a step with a chart, not derived.

A **formula** names other values in the same step. A **custom expression** binds as many of
them as it needs to letters `A, B, C…` and refers to them by letter; the expression is
checked against the bindings, so a letter with no value behind it, or a value never
referred to, is caught here rather than at inspection time.

### Post-MVP

Three features are marked post-MVP in the prototype — shown working so the design reviews
whole, but out of scope for the first release:

| Feature | Without it |
|---|---|
| **Result labels** | A rule resolves to a fixed `Pass` / `Fail`; the admin cannot add, rename or recolour a verdict. |
| **Graded bands** | Degrades to a single limit — the middle grade is lost. |
| **Tolerance around a standard value** | Degrades to a range the admin computes by hand (200 g ±5% → 190 to 210). |

Both deferred presets degrade rather than disappear, with one exception: **graded bands on
a POM-sourced column** cannot degrade. Its bands are a percentage of each POM's own
standard, and with no single standard on this screen there are no bounds to compute, so it
can only fall back to plain `Within POM tolerance` — pass or fail, no grade.

## Domain facts (authoritative — from product review)

1. A **Measurement Chart** is a group of POMs, rendered as a table in the inspection,
   grouped by **Style ID**.
   Ref: https://inspectorio.atlassian.net/wiki/spaces/POH/pages/67036774/Measurement+Chart
   (thin page — most sections are TBU as of Jul 2022)
2. Each **POM** carries its own unit, standard value and tolerance bands. The chart
   itself carries none of these.
3. Selecting a chart means measuring **every POM in it, per sample**. The POM list is
   not knowable at config time — so the UI never shows a POM count.
4. A step can measure per-POM **and** derive per-POM values.
5. **Result labels are user-defined** (e.g. `Pass, CRF, CRF-Passed, Warning,
   Hard Fail`), each carrying whether it counts as a pass.
6. This screen configures **one workflow's ordered steps**, not reusable templates.
7. It must serve **garment, fabric and hard goods**. The step name is the admin's;
   only the structure has to be universal. This is why the levels carry
   domain-neutral names — "POM" is kept because *point of measure* already is one.
8. **Sample count is not configured here.** It is derived from lot size upstream
   (Komar's product table: consistently 0.5% of lot size, rounded, across four line
   items), and lot ≠ order quantity. Per-step sampling controls do not belong on this screen.
9. Columns can be **optional**. Colorfastness and shrinkage are destructive, so one
   roll per dye lot is tested and the rest stay blank; the lot result aggregates
   whichever unit carries a value, and the report names that unit.

Sources for 7–9: the `09 Moisture Check` and `Description / quantity of product`
sheets of a garment inspection report, and
[Colorfastness & Shrinkage Measurement Research](https://inspectorio.atlassian.net/wiki/spaces/~7120203600f22dc9534f9b9eefab548be3312a/pages/90505255/Colorfastness+Shrinkage+Measurement+Research)
(client research for [PRP-2459](https://inspectorio.atlassian.net/browse/PRP-2459),
not a spec of this screen).

## Design principles

- **Merge a choice the user has not made yet; split one they have.** Formula-vs-inspector
  is one Add button (you don't know at creation whether you'll need a formula);
  chart-vs-custom is two Add buttons (you do). The asymmetry is deliberate.
- **Toggling an axis never destroys work.** Switching capture level, value source, or
  evaluation preset stashes the other side. Only explicit destructive actions discard.
  This splits in two: a *structural* change (the chart being turned off, a level moving)
  parks a rule and restores it, while an *explicit* source change applies that side's
  default. Conflating them makes a chart toggled off and on overwrite a column deliberately
  left "Not evaluated".
- **Don't remove capability because a case is rare.** But *do* remove capability that
  rests on an invented example. Two were deleted on those grounds — coarser columns inside
  a chart step, and the repeat axis — after checking that no observed report needed either.
  The test is whether a real case exists, not whether one can be imagined.
- **State, don't offer, a decision that never changes.** A chart step's level dropdown had
  one valid option, so it could only ever be set wrong.
- **Presets are authoring intent; the structure is what evaluates.** Store both.
- **Never invent a number that isn't knowable.** No count on this screen is knowable, so
  none is shown.
- **Don't name a concept with a word the domain doesn't use.** "Occasion" was invented
  here and failed on first contact. Renaming it to "repeat" helped; removing it helped
  more. A concept needing a rename is worth re-checking for a concept needing deletion.
- **Show cardinality, don't describe it** — and when the drawing needs a note to be
  correct, distrust the model, not the drawing. The repeat fan was once patched with a
  `× per sample` header note; when the note was later dropped the table began lying. That
  the shape could not be drawn honestly was the real finding.
- **Make the model reproduce a real report before trusting it.** The moisture preview is
  checked against the real sheet: one lot row, three sample cells for moisture, one cell
  each for the two air readings.
- **A validation can replace an axis.** `aggregateGapWarning()` delivers the only
  correctness benefit repeats had, at a fraction of the model cost, and covers cases
  repeats never did.

## Open questions

Ranked by how much each would change the design:

1. **Does the inspector record absolute measurements, or the variation from standard?**
   Narrowed, not closed. The Komar report shows the *reported* shrinkage is a variation
   (`−3.8%`), which supports recording absolutes and deriving the variation as its own
   column — but it never shows whether the raw before/after lengths are captured.
2. **Can a chart step draw from more than one chart type?** Multi-select today;
   expressible but possibly not meaningful.
3. **Where does `standard` live?** On the evaluation rule today; arguably belongs on
   the row beside `unit`.
4. **Are result labels workflow-level or org-level?** Workflow-level today.
5. **Confirm `setType` values** — is `Temperature` real? Does any chart type carry
   percentage tolerance bands? (`Temperature` is currently provisional.)
6. **Is "check" already a taken term in the product?**
7. **Should an ordinal scale be a real value type?** Crocking is graded on the AATCC
   Gray Scale 1–5, where levels have names ("4 = slight transfer"), only whole numbers
   are valid, and the rule is "minimum grade 4". The prototype fakes it with a `grade (1–5)` unit,
   which evaluates correctly but loses the level names and the integers-only constraint.
8. **Can a formula result ever be POM-bound?** Currently no: adding a formula forces
   `source` to custom. The narrow exception is a unit-preserving aggregate of POM-bound
   readings (measure each POM twice, judge the average against the POM's tolerance).
   Deliberately not offered until someone confirms that pattern is real.
9. **Is a POM-count rule this screen's job?** e.g. "no more than 2 POMs out of tolerance".
   That would be a per-sample value aggregating across POMs, which is the one case that
   would force coarser columns back into chart steps. The assumption is that it is
   step-verdict logic rather than a measured column — worth confirming, because it is the
   only construction that reopens this decision.
10. **Are the lot rollups configuration or engine behaviour?** Komar's shrinkage is
    captured per roll and reported per lot. The prototype models the rollup as four explicit lot
    columns to demonstrate the aggregate, but the research describes it as something the
    system does. If it is automatic, those four columns should not exist.

**Answered along the way:** sampling is neither per step nor per workflow — it is per lot,
derived from lot size, and outside this screen. Whether the screen serves one domain or
several — several: garment, fabric and hard goods, which is why the levels are
domain-neutral.

## Working note

The in-app browser pane cannot execute scripts from files outside the project
folder. These files are now inside the repo, so they run directly — no copy step
needed.
