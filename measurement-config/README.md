# Inspection measurement configuration — design prototypes

Design prototypes for the admin UI that configures the measurement portion of an
Inspectorio inspection workflow. Each file is standalone, self-contained HTML with
no dependencies — open any of them directly in a browser.

**Current version: [`v19.html`](v19.html).** The earlier files are kept as a record of
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
| [`v14.html`](v14.html) | Custom expressions take any number of values bound to letters; three features marked **post-MVP**; one Add button; the page's version log replaced by a structure-and-data-model explainer | Kept `optional` with no case left to justify it; modelled one observed sheet as two steps |
| [`v15.html`](v15.html) | `optional` **removed**; unit may be **none**; the shrinkage and crocking steps merged into one step that reproduces the whole dyelot approval sheet | Removed `optional` and kept sampling out, both contradicted by the shipped product; marked tolerance-around-a-standard post-MVP when Fabric Inspection already ships it |
| [`v16.html`](v16.html) | **Per-step sample size determination restored** (dropped in v10) and the preview draws the declared count; **`required` restored** as a per-value toggle; tolerance-around-a-standard **un-deferred** | Left the destructive test at lot level, which described its scope of meaning rather than its point of capture |
| [`v17.html`](v17.html) | The destructive test moves to **sample level** against the declared one-unit plan; a one-unit fan draws no sub-header | Marked graded bands post-MVP, which the cookware weight step cannot degrade around |
| [`v18.html`](v18.html) | A **hard-goods** case: a cookware weight step (chart of type Weight, ten POMs, ±5/±10 graded bands) plus its reference sample as its own one-unit step; graded bands **un-deferred** | Read a per-group sampling *rate* as a total, so the preview drew counts it could not know |
| **[`v19.html`](v19.html)** | Only `Determined Quantity` states a **total**; `By Item` / `By Size Per Style` / `By Color Per Style` are **rates** and keep the open fan. The cookware plan becomes `By Item: 1` | Current |

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
  not repeats. The 1st/3rd wash readings sit at lot level, so there is no sample fan for a
  repeat fan to multiply. The weight report shows the average, not the raw readings.

A repeat axis bought one real thing: an aggregate that could not go stale when a fourth
reading appeared. That is now `aggregateGapWarning()` — a check on the formula, which
protects every cloned column rather than only those that opted into an axis — plus a
one-click `Duplicate value`. **The cost:** the dyelot sheet's three wash-paired measurements
— length shrinkage, width shrinkage, skewing — need six column definitions where repeats
would have needed three.

A column's **grain** is the set of levels it varies over, derived from where it is
recorded. What keeps mixed grain from becoming ambiguous is an explicit rule on
references:

- **coarser → finer broadcasts.** A lot-level value applies to every sample under it.
- **finer → coarser needs a named aggregate.** Average, lowest, highest or total.

Each of those four is **defined for any number of cells, including none.** That is the bar,
and it is a deliberate exclusion: an aggregate whose meaning depends on exactly one cell
being filled is not an aggregate, it is an unenforceable assumption about data entry. A
config screen must not encode a rule it cannot enforce.

There is also **no first/last.** Positional selection needs an ordered axis, and samples are
a random draw from the lot — "sample 1" carries nothing "sample 3" would not. The one
genuinely ordered thing, a wash sequence, is modelled as separate columns, so a formula
names the column rather than a position.

### Destructive tests are sample-level values under a one-unit plan

Settled in v17. Shrinkage, skewing and colourfastness destroy the swatch, so the plan pulls
**one** unit and every measurement is performed on a swatch cut from it. That sampled unit is
where the value is **recorded**, so that is its level.

The result still *represents* the whole lot — but **scope of meaning and point of capture are
different things**, and these levels are about capture. v13 through v16 conflated them and put
the value at lot level, reasoning from the report: those figures sit on a sheet indexed by
dyelot, one row per lot. That indexing is a *consequence* of the plan being one unit wide, not
an independent fact the configuration has to assert.

**What makes sample level safe is that the plan is declared.** The version that first tried it
had no plan at all: it marked the columns optional so untested rolls stayed blank and reduced
them with an aggregate meaning "whichever single cell happens to be filled" — defined for one
case, undefined for none or several. With the plan stating one unit there is one cell, nothing
is blank, and nothing needs reducing. Pull two and each value needs a named aggregate to give
the lot its figure, which is the ordinary finer-to-coarser rule rather than a special case.

Two consequences worth knowing:

- **The preview is unchanged.** Under a one-unit plan a per-sample column and a lot-level
  column are both a single cell, so v17 draws no sub-header for a fan of one. They are
  indistinguishable in the table because they *are* indistinguishable there. Raise the plan to
  two and the fan appears — which is exactly when the difference starts to mean something.
- **The PRP phrase now parses.** *"Capture per roll, impact to lot"* was read as a cardinality
  claim, retracted as an entry-ergonomics claim, and is in fact neither: it is the sample plan.
  Capture on the pulled roll; the lot's figure follows because the plan is one unit wide.

Mixed grain only occurs in steps without a chart, since a chart step's columns all sit at POM
level. No seeded configuration crosses levels any more; the aggregate rule is kept as a guard
rather than a feature — see open question 10.

One evaluation rule governs every cell of a column.

### Sample size determination is per step

**Restored in v16, after being wrong for six versions.** v1–v9 had it; v10 removed it with the
line *"sampling controls are gone — sample count is derived from lot size upstream and is not
knowable here"*. That was wrong, and the shipped product says so in two places: the
**Measurements** component carries `By Size Per Style: 2` and **Fabric Inspection** carries
`10% Available Quantity`, both on the component itself.

Sampling happens at **two levels**, and conflating them is what caused the error:

| Layer | What it decides | Where it is configured |
|---|---|---|
| `Sample Selection` component | the **pull** — solid grouping, carton pull method, which items the size is calculated for | its own step, shared by every step that depends on it. **Out of scope here.** |
| A step's `Sample size determination` | how many of the available units **this step** measures | on the step. **This screen.** |

Ref: [Workflow Configuration](https://inspectorio.atlassian.net/wiki/spaces/POH/pages/67018459/Workflow+Configuration)
— Sample Selection exists "to provide a sample pull determination for the steps that depend on
it: Carton Check, Packaging, Workmanship, Measurements, Measurement by Defects, Assembly,
Moisture Check", and is auto-added when a dependent component is dragged in.

Three things follow, and they fix defects that had been read as facts about the domain:

- **The step's sample axis now has a declared extent.** A column recorded *once per sample*
  used to name a level whose width was never stated, which is why the preview could only draw
  an anonymous fan.
- **"Never invent a number that isn't knowable" was over-applied.** `Determined Quantity: 3`
  *is* knowable on this screen. The moisture preview now draws exactly three sample cells and
  reproduces the real sheet, instead of two and an ellipsis. A plan that resolves against the
  order's quantity (`% Available Quantity`, an AQL table) or defers to the inspector still
  shows the open fan — those counts really are unknown here.
- **The destructive test stops needing an escape hatch.** One roll per dye lot is now a
  *declared* plan of one unit, not an inference from which cells were left blank.

### `required` is a per-value toggle

**Restored in v16.** v15 removed it on the grounds that no observed case needed it. The case
was in the product all along: Fabric Inspection ships a per-measurement **Required** toggle,
and its own defaults use it — GSM and Cuttable Width required, Bowing and Skewing not. The
polarity here follows the shipped UI (a Required toggle, on by default) rather than v14's
double-negative "optional" checkbox.

What stays refused is the *use* v14 put it to: putting a destructive test on the sample axis,
marking it optional so untested units stay blank, and reducing it with an aggregate meaning
"the one cell that happens to be filled". The PRP-2459 research sketches exactly that. It
fails the totality bar — undefined for none filled and for several, and nothing here can stop
a second one being filled. The difference now is that a step's sample size determination
**declares** the count, so `required` can mean what it means in the product (must be recorded
before the step completes) instead of carrying a sparsity rule it cannot enforce.

### A unit may be none

A judgement is not always on a scale. Colour/shade against a standard swatch is assessed by
eye and resolves to a verdict with no number behind it: unit *none*, evaluation *Inspector
decides*. Before v15 the unit control had no way to say none, so an unset unit rendered as
the first entry in the list and the column silently claimed to be in millimetres.

Three observed columns need this: the dyelot sheet's `COLOR/SHADE`, and — on the roll-indexed
sheet — colour shade and **handfeel**, both per-roll judgements with no scale at all.

This is the boundary of what counts as a value here: shade has no scale but carries its own
judgement of one property, so it is a column. A **remark** (`release 24 hours`) carries no
judgement of anything measured — it is a note about the lot, and faking it as a unitless
value would put free text where the model promises a result. See open question 13.

### One observed sheet is one step

A step renders as one table in the report, so a sheet that is one table is one step. v14 had
the dyelot sheet's shrinkage and crocking as two steps; because this screen configures one
workflow's *ordered* steps, that would have run the crocking test twice in one inspection.
v15's step 5 reproduces the sheet column for column, in the sheet's own order.

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

One feature is marked post-MVP in the prototype — shown working so the design reviews
whole, but out of scope for the first release. **Tolerance around a standard value was on this
list and has been removed from it in v16:** the shipped Fabric Inspection component already
configures asymmetric percentage tolerance (GSM −1/+2, Cuttable Width −5/+5), so a step that
replaces it without this would ship a regression, not a deferral.

| Feature | Without it |
|---|---|
| **Result labels** | A rule resolves to a fixed `Pass` / `Fail`; the admin cannot add, rename or recolour a verdict. |

**Graded bands came off this list in v18.** On a POM-sourced column they cannot degrade at all
— the bands are a percentage of each POM's own standard, and with no single standard on this
screen there are no bounds to fall back to. The cookware weight step is exactly that shape, so
deferring graded bands would not shrink it, it would make it unconfigurable.

That leaves a dependency worth deciding: **a graded rule needs at least three outcomes**, and
with result labels deferred a rule resolves to a fixed `Pass` / `Fail`. So either release one
ships a fixed third label (a `Warning` between the two), or user-defined labels come along with
graded bands. The two cannot be split the way the list currently splits them.

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
8. ~~**Sample count is not configured here.**~~ **Retracted.** A step's sample size
   determination *is* configured on the step in the shipped product (`By Size Per Style: 2` on
   Measurements, `10% Available Quantity` on Fabric Inspection). What is configured elsewhere
   is the **pull** — the `Sample Selection` component. Komar's product table showing 0.5% of
   lot size is a *booking-level* quantity, not the per-step measure count, and reading it as
   the latter is what cost v10 through v15 this field.
9. Colorfastness and shrinkage are **destructive**, so one unit per lot is tested — and the
   figure is reported as a property of the dye lot. ~~Columns can therefore be optional, with
   the rest of the rolls left blank and a lot-level rollup over whichever one carries a
   value.~~ **Retracted:** that reading put a lot-level property on the sample axis. The
   report indexes these by dyelot, one row per lot, with no roll column on the sheet at all.
10. A **dyelot approval sheet** carries, for one dye lot: 1st and 3rd wash shrinkage (length
    and width, limit −5%), 1st and 3rd wash skewing (limit 4%), fabric weight in GSM against
    a standard of 180, colour/shade as a pass/fail judgement, crocking dry (min 4) and wet
    (min 3), plus an overall dyelot verdict, a QC initial and a free-text remark. Both
    observed lots pass at 173 and 174 GSM, which **rules out reading 180 as a minimum** — it
    is a target, and the sheet does not print its tolerance.
11. **Komar's report is two sheets at two levels.** An *Inspection Report* sheet indexed by
    roll (weight, width, length, defects, colour shade, handfeel — per roll) and a *Dyelot
    Testing Report* sheet indexed by dyelot (shrinkage, skewing, crocking — one row per lot).
    Two levels, two sheets, therefore two steps. Colour/shade appears on **both**, which is
    unresolved — see open question 16.
12. **The tests are run on site at every inspection, not read from a lab report.** Komar's QC
    team physically runs the crockmeter and the wash cycle each time; there is no upstream lab
    result to ingest. Each dye lot is a separate dye batch, so a lot that passed at sample
    approval can still fail in bulk. Nothing for this screen to configure — it settles that
    these values are *captured*, not *referenced*.
13. **Crocking is AATCC Test Method 8** (crockmeter), always run dry and wet, graded against
    the **AATCC Gray Scale for Staining**: 5 no transfer · 4 slight · 3 noticeable · 2 heavy ·
    1 very heavy. Komar requires dry ≥ 4 and wet ≥ 3; the observed lot scores exactly 4 and 3
    and passes, so **both limits are inclusive**.
14. **Shrinkage is a signed percentage**, length (warp) and width (weft): negative shrank,
    positive grew. Methods are AATCC TM135 (US, top-loader) or ISO 6330 + ISO 5077 (EU,
    front-loader); skewing belongs to the same test. The research states the *measured* figure
    is the percentage and never says the raw before/after lengths reach the system.
15. **The research asks for the source roll to be reported.** One randomly selected roll per
    dye lot is cut, and "the report shows both the lot result and the source roll number", for
    two stated reasons: tracing a dispute or re-test back to a physical roll, and knowing
    whether a lot result is still valid once a roll is dropped from the shipment. See open
    question 11 — this is now an evidenced requirement, and the design has nowhere to put it.

20. **A client weight specification is a chart.** A cookware set inspected for Lidl has one
    item ID (`HG14443`) and ten measurement points — the set total, then per size an "overall"
    plus its pot and its glass lid weighed separately. Each point carries **its own
    specification and its own tolerance bands** (3515 g for the total, 540 g for the 16 cm pot,
    9999 g for one point that is plainly a placeholder), and the sheet groups them under the
    Style item. Unit, standard and tolerance per point, grouped by style, is the definition of a
    Measurement Chart — so the points are POMs, not columns.
21. **Tolerance bands come in two grades.** The sheet prints −10% / −5% / +5% / +10% per point
    and marks an out-of-tolerance point in blue. Read as bands: within ±5% passes, ±5–10% is
    flagged, beyond ±10% fails. They are percentages of **each POM's own standard**.
22. **Country blocks are separate items, not a sampling stratum.** The product data set carries
    one item per country block, so `CB2` / `CB3` / `CB10` are three item IDs sharing one style.
    The plan is therefore `By Item: 1` — one piece per item — and the sheet's "Country block"
    row names the item each column was measured on, which the inspection already knows. **This
    closes the hard-goods half of open question 11:** the sampled unit's identity is the item.
    The fabric roll is not an item, so that half stays open.
23. **An item can be a set.** `HG14443` is one item comprising three pots and three lids. The
    parts have no identity in the product data, so the only place they appear is the chart —
    which means a POM list for hard goods carries product structure as well as measurement
    points. That is not a defect of the model so much as a fact about the domain: for a pot,
    *where do I put the scale* is *which part*, and the answer is a genuine point of measure.
24. **A reference sample is measured at every point, and is not one of the drawn units.** The
    three pieces read 3585 / 3597 / 3581 g against a paper specification of 3515 g, while the
    reference sample reads 3590 g. Production matches the approved sample; the paper number is
    what is stale. The sheet records the reference uncoloured — recorded for comparison, not
    judged. **It varies by POM but not by sample**, which is a level the model does not have.
25. **A measured value can duplicate a derivable one.** `overall (16 cm)` = 873 g and its parts
    are 554 + 318 = 872; the set total 3585 g against 873 + 1164 + 1543 = 3580. The client
    measures and photographs each rather than deriving any of them, so they are independent
    POMs. Both shapes are expressible; which one is used is the client's choice.

Source for 20–24: sections 2.2 / 2.2.1 of a Lidl hard-goods inspection report (`HG14443`),
with the scale photographs for each measurement point.

16. **The workflow is a list of components, not only measurement steps.** Shipped components
    include `Sample Selection`, `Workmanship`, `Carton Check`, `Packaging`, `Assembly`,
    `Moisture Check`, `Measurements`, `Measurement by Defects`, `Assessment Verification`
    (questionnaires) and `Item Attribute`. Several have prerequisites and are auto-added.
    **The scope of this prototype is the measurement step only** — defects, questionnaires and
    the sample pull each already have their own component.
17. **`Measurements` takes standard *and* tolerance from the POM**; `Measurement by Defects`
    records defects against POMs with no measured value at all. Ref: Workflow Configuration.
18. **Fabric Inspection configures the tolerance here and takes the standard from elsewhere.**
    Its measurement rows (GSM, Cuttable Width with start/mid/end, Roll Length, Bowing, Skewing)
    each carry an `Acceptance Range Classification` of `Tolerance (%)` with a −/+ pair, and no
    standard field. The standard comes from the item's fabric spec. This is a **third**
    provenance combination the prototype does not model — see open question 3.
19. **Fabric Inspection already has a per-measurement `Required` toggle**, and its defaults use
    it: GSM and Cuttable Width required, Bowing and Skewing not.

Sources for 16–19:
[Workflow Configuration](https://inspectorio.atlassian.net/wiki/spaces/POH/pages/67018459/Workflow+Configuration)
and screenshots of the live Sample Selection, Fabric Inspection and Measurements components.

Sources for 7–15: the `09 Moisture Check` sheet (the `09` is its tab position in the client's
workbook — the prototype's step is named `Moisture Check`, after the shipped component),
`Description / quantity of product` and dyelot
approval sheets of a garment/fabric inspection report, and
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
- **Never encode a rule this screen cannot enforce.** An aggregate meaning "whichever single
  cell happens to be filled" is an assumption about data entry dressed as a formula — and
  asking whether it should *stop* the inspector filling a second one is how you notice the
  category error. Every combining rule must be total: defined for none, one, or many.
- **A patch that only makes sense for one case is evidence the level is wrong.** That
  aggregate existed to hold a mis-levelled value together. Fixing the level deleted the
  aggregate, an optional flag and four columns at once. When a rule needs an escape hatch,
  suspect the thing it is escaping from.
- **A capability with no case left is a liability, not neutral.** `optional` cost every
  aggregate and every formula an absent-cell semantics, and the pattern that might have
  replaced it needs a *condition*, not a flag — so keeping the flag would have made the real
  feature harder to add. "Remove capability that rests on an invented example" extends to
  capability whose one real example has since been re-levelled away.
- **Distinguish where a value is CAPTURED from what it MEANS.** A destructive test is measured
  on one pulled unit and speaks for the whole lot. Both are true; only the first is a level.
  Reading the report's indexing as the level put the value a rung too high for three versions,
  and the tell was that the model kept needing an extra mechanism — a rollup, a one-cell
  aggregate, a provenance field — to say something the sample plan already said.
- **A rate is not a total.** "1 per item" is one number on the screen and an unknown number of
  units in the inspection. Treating the two as the same put invented counts in the preview for
  three versions — the same error as inventing a sample count, wearing the costume of a fix for
  it.
- **A missing field can look like a wrong model.** Nothing about the destructive test could be
  stated honestly until the step declared how many units it measures. Six versions of argument
  about levels, aggregates and optionality were all downstream of one deleted control.
- **Distinguish where a value is TYPED from what it is OF.** "Capture per roll, impact to
  lot" describes entry ergonomics in another screen. Reading it as cardinality put a
  lot-level property on the sample axis and cost three follow-on mechanisms.

## Open questions

Ranked by how much each would change the design:

1. **Does the inspector record absolute measurements, or the variation from standard?**
   Narrowed further, still not closed. For shrinkage the answer is now *variation*: the
   research calls it "measured as a percentage" in two directions, with a sign convention
   (negative shrank, positive grew), and never mentions the raw before/after lengths reaching
   the system. Both shapes are expressible today — step 2 captures before/after per POM and
   derives the percentage, step 5 records the percentage directly — so nothing is blocked. The
   open part is whether the *general* answer differs by measurement type.
2. **Can a chart step draw from more than one chart type?** Multi-select today;
   expressible but possibly not meaningful.
3. **Where does `standard` live — and can it come from the item's spec?** On the evaluation
   rule today, typed on this screen. The shipped product has **three** combinations, and the
   prototype models only the first two: (a) standard *and* tolerance from the POM
   (`Measurements`); (b) both typed here; (c) **tolerance typed here, standard from the item's
   fabric spec** — which is how Fabric Inspection's GSM `−1/+2` works, with no standard field
   on the config screen at all. Step 5 types `180` for fabric weight, which is probably wrong
   for that reason. This is the highest-value open question in the list now: it is a missing
   axis, not a missing field.
4. **Are result labels workflow-level or org-level?** Workflow-level today.
5. **Confirm `setType` values** — is `Temperature` real? Does any chart type carry
   percentage tolerance bands? (`Temperature` is currently provisional.)
6. **Is "check" already a taken term in the product?**
7. **Should an ordinal scale be a real value type?** Crocking is graded on the AATCC Gray
   Scale for Staining — 5 no transfer · 4 slight · 3 noticeable · 2 heavy · 1 very heavy —
   where only whole numbers are valid and the rule is "minimum grade 4". The prototype fakes
   it with a `grade (1–5)` unit, which evaluates correctly (dry ≥ 4, wet ≥ 3, both inclusive)
   but loses the level names and the integers-only constraint. The names are now documented,
   so the cost of faking it is concrete: the inspector sees `4`, not `4 — slight transfer`.
8. **Can a formula result ever be POM-bound?** Currently no: adding a formula forces
   `source` to custom. The narrow exception is a unit-preserving aggregate of POM-bound
   readings (measure each POM twice, judge the average against the POM's tolerance).
   Deliberately not offered until someone confirms that pattern is real.
9. **Is a POM-count rule this screen's job?** e.g. "no more than 2 POMs out of tolerance".
   That would be a per-sample value aggregating across POMs, which is the one case that
   would force coarser columns back into chart steps. The assumption is that it is
   step-verdict logic rather than a measured column — worth confirming, because it is the
   only construction that reopens this decision.
10. **Does cross-level aggregation earn its place?** No seeded configuration uses one. It is
    kept as a *guard* rather than a feature: what it prevents is a coarse value silently
    reading a finer one without saying how, which is a real class of bug. A validation earns
    its place by what it forbids, not by what it enables — but the `passthrough` formula that
    exists to carry it now has no example.
11. **Where is the source-unit provenance recorded?** **Upgraded from "confirm it is not
    needed" to a known gap.** The research states outright that the report shows the lot result
    *and* the source roll number, and gives two operational reasons (tracing a dispute or
    re-test to a physical roll; knowing whether a lot result survives a roll being dropped).
    The research's own proposed mechanism is the one this design rejected — put the values on
    the roll axis, mark them optional, and let the filled cell imply the roll — and rejecting
    it leaves the requirement unserved rather than answered. The roll number is an
    *identifier*, not a measurement: it has no unit and no pass/fail rule, so it does not fit
    a value. Either this screen grows a non-measurement field, or the source unit is captured
    by whatever mechanism already records who inspected and when.
    **Largely dissolved by v16.** Restoring the per-step sample size determination gives the
    step a declared sample axis one unit wide, and Fabric Inspection already lets the inspector
    *add rolls under items* — so the sampled roll is a record with an identity at inspection
    time, not something a measurement column has to carry. What remains to confirm is only
    whether the lot figure's report line names that roll automatically.
    **A second domain now needs the same thing.** The cookware sheet labels its three drawn
    pieces `CB2`, `CB3`, `CB10` — country blocks. Roll number and country block are one
    mechanism: *a label on each cell of the sample fan, sourced from the order.* This is no
    longer a fabric quirk, and it is the strongest candidate for the one non-measurement field
    this screen might need.
12. **What is the fabric weight tolerance?** The dyelot sheet prints the standard (180 GSM)
    and no tolerance. Step 5 assumes ±5%, which is the prototype's own invention. Two lots at
    173 and 174 both pass, so the true band is at least ±3.9% — that is all the sheet proves.
    This is also the first *observed* column that depends on the post-MVP
    tolerance-around-a-standard preset; without it the admin types 171 to 189 by hand.
13. **Where does a free-text remark live?** The dyelot sheet's last column is `release
    24 hours` — a note about the lot, carrying no judgement of anything measured. It is
    deliberately not modelled as a unitless value. Confirm it belongs to whatever mechanism
    already carries inspector comments, rather than here.
14. **Where does the step's own verdict live?** The sheet's `OVERALL DYELOT RESULTS` is a
    verdict over the other columns, so it is assumed to be step logic and not an eleventh
    configured column. Same assumption as question 9, arrived at from a different direction —
    if either turns out to be a configured value, both reopen.
15. **Where is the test method recorded?** Crocking is AATCC 8; shrinkage is AATCC TM135 or
    ISO 6330 + 5077. Komar's sheet labels the whole block "KSL Standard" and names no method,
    which the research itself flags as something to confirm with them. There is nowhere on this
    screen to attach a method to a step or a value — and if an auditor or a re-test needs to
    know which procedure produced a number, that is a real omission rather than a nicety.
16. **Is colour/shade judged per roll, per lot, or both?** The research puts colour shade on
    the roll-indexed sheet; the dyelot sheet has its own `COLOR/SHADE` Pass/Fail column. Step 5
    models the lot-level one, which is what that sheet shows. If both are real they are two
    values at two levels in two steps, which the model handles — but confirm it is not one
    value being read twice.
17. **Should there be a level for "once per POM, not per sample"?** Every column in a chart
    step varies by POM *and* sample together. The cookware reference sample varies by POM only:
    one weight per measurement point, on a unit that is not one of the drawn pieces. v18 models
    it as its own chart step under a plan of one, which works and costs nothing (a chart step is
    one value definition however many POMs it has) — but it splits one sheet section into two
    steps. The alternative is a third level, which reopens the "chart steps are per-POM only"
    decision from a direction the invented `Room temperature` example never reached: not a
    *coarser* column in a chart step, but the same POM axis with the sample axis dropped.
18. **Which is the cookware plan — `By Item: 1` or five pieces?** v19 configures `By Item: 1`,
    which is what the report shows happening (three items, one piece each). The sheet's own
    instruction says "take 5 pieces per each measurement point". Resolve before build.
19. **Should the redundancy between measurement points be checked?** `overall (16 cm)` is
    weighed independently at 873 g while its parts weigh 554 + 318 = 872, and the set total is
    weighed at 3585 g while the three overalls sum to 3580. Rounding explains those; a
    transposition would not, and nothing would catch it. The model cannot express it either —
    a formula names *values*, and there is no way to relate one named POM to another.
20. **One quantity, two configurations — is that a problem?** Fabric weight is recorded
    directly on the dyelot sheet (step 5) and derived from a swatch in step 8. Both are
    valid, and which one a client uses is a client choice — the same shape as question 1
    (absolute vs variation) and as `source` being declared rather than inferred.

**Answered along the way:** sampling is per step *and* per workflow — a workflow-level pull
(`Sample Selection`) and a per-step measure count, which is the distinction v10 missed. Whether the screen serves one domain or
several — several: garment, fabric and hard goods, which is why the levels are
domain-neutral. Whether `required` earns its place — **yes**: the shipped
Fabric Inspection component has it per measurement and its defaults use it. Removing it in v15
was an error of evidence, corrected in v16. Whether a destructive test is lot-level or
sample-level — **sample-level**, against the declared plan; see the section above.

## Working note

The in-app browser pane cannot execute scripts from files outside the project
folder. These files are now inside the repo, so they run directly — no copy step
needed.
