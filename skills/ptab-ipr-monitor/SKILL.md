---
name: ptab-ipr-monitor
description: >
  This skill should be used when the user asks about "PTAB", "IPR", "inter partes
  review", "patent challenge", "is the patent being challenged", "invalidation risk",
  or wants to track administrative patent challenges against a franchise's key patents.
metadata:
  version: "0.1.0"
  layer: "Competitive"
---

# PTAB / IPR monitor

Track administrative challenges to the patents that hold up a franchise, and convert
procedural milestones into probability shifts on the LOE date.

## Workflow

1. **Start from the patent stack**, not from the company. Take the patent numbers
   `orange-book-loe` identified as binding and search PTAB for proceedings against each
   (`scripts/ptab_search.py --patent 9,000,000`). Searching by company name misses
   challenges filed against a licensor or a predecessor entity.
2. **Identify the petitioner.** A generic filer signals an entry attempt. A
   competitor-manufacturer or a patent-adverse fund signals something else. Petitioner
   identity changes what a win means commercially.
3. **Track the procedural milestones**, which are the datable catalysts:
   - Petition filed.
   - **Institution decision** — roughly six months after filing. This is the first real
     information event: institution means the Board found a reasonable likelihood that
     at least one claim is unpatentable.
   - **Final written decision** — statutorily within 12 months of institution.
   - Appeal to the Federal Circuit — adds 12–18 months.
   - Note that discretionary denial practice has shifted repeatedly; a petition can be
     denied on discretionary grounds without any view on the merits, which is not a
     win for the patentee on substance.
4. **Score the claims at risk.** Losing a method-of-use claim is usually survivable.
   Losing composition-of-matter is the franchise. Say which claims the petition targets.
5. **Update the LOE distribution.** Move probability mass from *nominal* toward
   *earliest plausible* on institution; move it decisively on a final written decision
   holding claims unpatentable. Re-emit the `orange-book-loe` brief rather than
   reporting the PTAB outcome in isolation.
6. Emit the brief.

## Caveats

USPTO's Open Data Portal API requires a free key (`USPTO_API_KEY`). Proceedings are
available from September 2012 onward. Entity mapping is the practical difficulty:
patent assignee names, Orange Book applicant names and ticker names frequently differ.
Verify the assignment chain before concluding a patent belongs to the covered name.

District-court Hatch-Waxman litigation runs in parallel and is *not* in PTAB; for that,
use the free CourtListener/RECAP docket data and the sponsor's own legal-proceedings
disclosure.

## Not-automatic

An instituted IPR does not license an invalidity assumption — institution rates and
final-outcome rates are very different numbers, and a settlement can end the proceeding
at any point on terms that reveal nothing.

Contract: `../../references/evidence-brief.md`.
