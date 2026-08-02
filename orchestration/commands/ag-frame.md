---
description: Frame a raw idea/PRP into a canonical spec (P/R/NG/AC) by grilling until it holds.
argument-hint: "<idea, PRP paste/link, or bug report>"
---

Frame this task: **$ARGUMENTS**

1. Pick a `<task-id>`: a short kebab slug of the ask (e.g. `reject-conflicting-codes`).
   Create `.orchestration/runs/<task-id>/` and `decisions.md` from the template.
2. Invoke the **ag-frame** skill on the input above. Grill the human; log each Q&A as a `DEC`.
3. Write `.orchestration/runs/<task-id>/spec.md` and report the Assessor coverage result.

Stop and ask the human on genuine scope/requirement decisions. Otherwise, when the spec
passes, tell the user it's ready for `/ag-plan <task-id>`.
