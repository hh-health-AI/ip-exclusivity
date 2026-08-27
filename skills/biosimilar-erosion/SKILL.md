---
name: biosimilar-erosion
description: >
  This skill should be used when the user asks about "biosimilar erosion", "Purple
  Book", "biologic exclusivity", "interchangeability", "how fast will [biologic]
  erode", "erosion curve", or needs the post-LOE revenue slope for a biologic.
  Anchors prompt-library ID SUB-PHA-05.
metadata:
  version: "0.1.0"
  layer: "Competitive"
---

# Biosimilar erosion curve

Turn a biologic's exclusivity position and competitive set into a dated erosion curve
that a revenue model can consume.

## Workflow

1. **Establish the reference product's position** from the Purple Book
   (`scripts/purple_book.py`): BLA number, first licensure date, reference-product
   exclusivity expiry, and any listed biosimilars with their licensure dates and
   interchangeability status.
2. **Count and qualify the entrants.** Not all approvals launch. Check for: launch
   announcements, settlement-driven launch dates, manufacturing capacity, and whether
   the entrant is a large player with contracting muscle or a small one that will
   discount without winning share.
3. **Determine the substitution mechanism**, which drives everything:
   - *Interchangeable, pharmacy-dispensed* → fastest erosion.
   - *Not interchangeable, physician-administered, buy-and-bill* → slowest; erosion
     depends on ASP dynamics and the physician's reimbursement spread, not on the pharmacy.
   - *Payer-forced switching* → step-shaped erosion at formulary dates (1 January is the
     usual step), not a smooth curve.
4. **Model price and volume separately.** Biosimilar competition is initially price-led:
   the reference product often holds volume while conceding net price through rebates.
   A model that assumes volume loss will misread the first two years and then be
   surprised by the cliff when contracts finally flip.
5. **Build the curve.** Quarterly, from the entry date, with the shape justified by the
   substitution mechanism and by two named analogue molecules with similar mechanics.
   Analogues do more work here than theory.
6. **Watch the defence.** Reference-product sponsors deploy: authorised biosimilars,
   next-generation formulations (higher-concentration, subcutaneous, longer-acting),
   device improvements, and aggressive contracting that trades price for volume
   retention. Each changes the curve; name which ones are in play.
7. **Instrument the curve.** Once entry happens, replace assumption with observation
   via `rx-utilization` → sdud-trx-proxy and Medicare Part B/D spending dashboards.
   A curve that is not being checked against data quarterly is a guess with a chart.
8. Emit the brief.

## Not-automatic

A biosimilar approval does not license an erosion assumption. Approval without launch,
without interchangeability, or without contracting capacity produces very little
erosion, and several approved biosimilars have never meaningfully launched.

Reference: `references/erosion-analogues.md`. Contract: `../../references/evidence-brief.md`.
