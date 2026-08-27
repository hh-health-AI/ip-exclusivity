---
name: orange-book-loe
description: >
  This skill should be used when the user asks about "LOE", "loss of exclusivity",
  "patent cliff", "when does [drug] go generic", "Orange Book", "Paragraph IV",
  "patent expiry", "generic entry date", or needs the exclusivity date that sets the
  terminal value in a pharma model. Anchors prompt-library ID MOD-04.
metadata:
  version: "0.1.0"
  layer: "Competitive"
---

# Orange Book LOE build

Construct the loss-of-exclusivity date for a brand as a distribution with named
constraints, not as a single looked-up number.

## Workflow

1. **Resolve the brand to Orange Book application numbers.** One brand may span several
   NDAs (different strengths, formulations, delivery systems). Run
   `scripts/orange_book_loe.py --brand X` after downloading the current Electronic
   Orange Book zip; the script parses `products.txt`, `patent.txt` and `exclusivity.txt`
   and joins them on appl_no + product_no.
2. **Stack the patents and classify each one.** For every listed patent record:
   - Expiry date, including any patent-term extension already reflected.
   - **Drug substance flag** (composition of matter) — the hard constraint.
   - **Drug product flag** (formulation) — designable-around, medium strength.
   - **Use code** (method of use) — weakest; a generic can carve the indication out
     with a skinny label under §viii and enter for the remaining indications.
   - **Delisting requested** — a signal the sponsor has conceded the patent.
3. **Stack the exclusivities.** NCE, ODE, NPP/NP, paediatric extension. Note that
   paediatric exclusivity attaches on top of both patents and other exclusivities,
   which is why it so often *is* the binding date.
4. **Find the Paragraph IV filings.** FDA publishes the Paragraph IV certification
   list with the date of first filing. First filing starts the clock: a first
   applicant may hold 180-day generic exclusivity, and the date of first filing plus
   the 30-month stay is the earliest structurally plausible entry.
5. **Go and find the settlement.** Search the sponsor's 10-K legal proceedings and
   8-Ks for the molecule name and "settlement", "agreement", "authorised generic",
   "entry date". Settlements routinely set entry years before nominal expiry, and are
   the single largest source of error in models built from the Orange Book alone.
   If no settlement is disclosed, say so explicitly — that is itself information.
6. **Check PTAB.** Run `ptab-ipr-monitor` on the key patents. An instituted IPR on the
   composition-of-matter patent is a material probability shift.
7. **Produce the distribution.** Three dated scenarios with rough probabilities:
   - *Earliest plausible*: Paragraph IV first-filing + 30-month stay, or a disclosed
     settlement date, or a successful IPR outcome.
   - *Base*: the constraint you actually believe binds, with the reason.
   - *Nominal*: latest listed patent plus paediatric, i.e. the number a naive model uses.
8. **Hand to valuation.** State the terminal-value consequence directly: which years
   of cash flow move, and what the DCF is worth under each scenario. your view layer
   → model-valuation owns the model; this skill owns the date and the reason.
9. Emit the brief.

## Traps

- **Authorised generics.** The brand can launch its own generic at entry, retaining
  material profit. A model that zeroes the franchise at LOE overshoots.
- **Non-substitutable formulations.** Devices, depots, and combination products erode
  far more slowly because pharmacy-level substitution does not apply.
- **Ex-US expiry differs.** European SPCs and Japanese exclusivity run on their own
  calendars. `global-access` owns those; do not assume the US date applies globally.
- **Delisting and reverse payments.** Watch FTC actions on pay-for-delay; a challenged
  settlement can be re-opened.

## Not-automatic

An Orange Book patent stack does not license an entry-date conclusion on its own —
without the settlement search and the Paragraph IV list, the date is the nominal
one, which is usually wrong and always too late.

Reference: `references/exclusivity-mechanics.md`. Contract: `../../references/evidence-brief.md`.
