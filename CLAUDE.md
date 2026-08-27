# ip-exclusivity — standing instructions

**Layers covered:** Competitive + Regulatory + Valuation.
**Connector:** none declared. The Orange Book is reached through the openFDA connector
anchored in `fda-safety-signals`; USPTO PTAB needs a free api.uspto.gov key in
`USPTO_API_KEY`. Do not re-declare openFDA here.

## What this engine is for

Producing the single number that dominates large-cap pharma valuation more than any
other: **the date the cash flow stops**. Everything else in this plugin exists to
qualify that date with a probability and an erosion shape.

## How to think about an LOE date

An LOE date is not a fact you look up. It is the *latest binding constraint* among:

1. **Patents** listed in the Orange Book — composition of matter, method of use,
   formulation, device/delivery — each with its own expiry, extensions and
   vulnerability. Method-of-use patents are frequently designed around via skinny
   labelling and should be discounted, not counted.
2. **Regulatory exclusivities** — NCE (5 years, 4 with a Paragraph IV), ODE (7 years),
   paediatric (6 months, applied on top of both patents and exclusivity), and for
   biologics the BPCIA's 12 years from first licensure.
3. **Settlements** — the actual entry date is usually a negotiated one, disclosed in
   10-K legal proceedings or in the settlement itself, and it typically sits years
   before nominal patent expiry. **The settlement date beats the patent date.** A model
   built off patent expiry alone will be systematically wrong and late.
4. **Litigation and PTAB outcomes** — a successful IPR removes a patent from the stack
   entirely.

The output of `orange-book-loe` is therefore a *distribution*: an earliest plausible
entry, a base case, and a nominal expiry, with the probability mass explained.

## Erosion is a second, separate question

A date without a curve is half an answer. Small-molecule oral solids erode brutally
(often 80–90% of volume in the first year with multiple ANDA filers, driven by
automatic substitution at the pharmacy). Biologics erode slowly and partially, because
substitution requires interchangeability designation and payer channel work. Injectables
and device-drug combinations sit in between. `biosimilar-erosion` owns the curve.

## Chaining

your view layer → model-valuation (terminal value and the patent-cliff bridge,
prompt MOD-04) · `rx-utilization` → sdud-trx-proxy (to observe erosion as it happens
rather than assume it) · `global-access` (ex-US exclusivity differs and expires on its
own calendar) · a catalyst engine (a lifecycle-management readout that extends the
franchise).

## Anchored prompt-library IDs

MOD-04 (Patent Cliff and LOE Bridge) · SUB-PHA-05 (Biosimilar Erosion Curve).
## Connector

**Declares nothing, by design.** Orange Book and Purple Book arrive through the `fda`
server that `fda-safety-signals` anchors. Install both plugins together and the
session is shared.

**Do not let the MCP set an LOE date.** `fda-mcp` serves *locally cached* Orange Book
and Purple Book snapshots. Patent listings, use codes and exclusivity grants change on
a monthly cycle, and a stale snapshot moves an LOE date silently — the failure mode
here is a confident wrong answer, not a visible error. `orange_book_loe.py` and
`purple_book.py` parse the live archive and remain authoritative. Every LOE date in a
brief carries the archive's own publication date, not the date you ran the query.

The MCP is for orientation: what is the molecule, which patents are listed at all.
The date arithmetic goes through the scripts.

USPTO and PTAB have no MCP server. `ptab_search.py` is the only path and the USPTO has
moved these endpoints more than once — run `--discover` first when it starts failing.

## Standard of evidence

This engine is built to **institutional investor standards: rigorous and auditable.**
That is a claim about specific mechanisms, and the full list is in
`references/auditability.md`. The load-bearing ones:

- Every finding carries a source, a retrieval date and the **vintage of the underlying
  data** — a different and usually much earlier date.
- Confidence is gated by vintage, not by conviction.
- Scripts fail loudly on empty result sets. Silence is never a negative finding.
- Known limitations travel with the number, in-line, not in a footnote.
- Evidence and view stay separated. This engine does not issue recommendations.

## Desk conventions (all engines)

- **One connector, one plugin — for plugin-level servers only.** A self-hosted
  stdio server is declared in exactly one plugin's `.mcp.json`; co-installed
  plugins share every server session-wide, so a second declaration buys a
  duplicate process, not extra capability. **Account-level hosted connectors are
  different**: CMS Coverage, PopHIVE, ClinicalTrials.gov, PubMed, ChEMBL,
  bioRxiv and Scholar Gateway are connected once in the directory and are visible
  to every plugin. Plugins reference those; they never declare or own them.
  Full map in `references/mcp-setup.md`.
- **MCP for the analyst, scripts for the watcher.** Both paths ship in every
  plugin and they are not redundant. Interactive query refinement goes through
  the server; unattended scheduled evidence goes through the script, because a
  watcher has to be deterministic and re-runnable against the same vintage.
  Where the two disagree, the script wins for anything entering a brief — you
  cannot cite the internals of a third-party server.
- **Engines produce evidence, not views.** An engine skill ends at the brief. The
  your view layer is the only place a position
  is argued. Do not write a recommendation into an engine output.
- **Open data only.** Every input here is free and public. If an analysis needs
  IQVIA, Symphony, Definitive, EvaluatePharma or Citeline, say so and stop — do
  not silently substitute a proxy for the paid panel and present it as equivalent.
- **Cite the vintage every time.** See `references/evidence-brief.md`.
- **Chain, don't duplicate.** These eight engines cross-reference each other by
  name. Anything outside them — valuation models, single-name research, the
  portfolio view layer — is chained into, never reimplemented here. An engine
  that starts doing valuation has stopped being an engine.
- **Scripts are stdlib-only Python 3.** No pip installs. Every script takes
  `--help`, prints JSON or CSV to stdout, and fails loudly on an empty result set
  rather than returning silence that reads like a negative finding.
