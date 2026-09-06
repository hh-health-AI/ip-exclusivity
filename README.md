# ip-exclusivity

Patent cliff, biosimilar and generic entry.

| Skill | Moves | Sub-sector | Ease/Impact |
|---|---|---|---|
| `orange-book-loe` | LOE date and terminal-value cliff in DCF/rNPV | #biopharma | 4 / 5 |
| `biosimilar-erosion` | Biologic revenue-erosion slope | #biopharma | 4 / 4 |
| `ptab-ipr-monitor` | Binary IP catalyst; probability-weighted LOE | #biopharma #medtech | 2 / 4 |

**Agent:** `loe-watcher` — monthly Orange Book and Purple Book deltas; PTAB institution
and final-written-decision alerts.

**Data:** FDA Orange Book (monthly Electronic Orange Book zip: products, patent,
exclusivity files) · Purple Book (monthly CSV; database content from May 2020) ·
USPTO Open Data Portal PTAB API (`USPTO_API_KEY` required) · company 10-K legal
proceedings for settlement dates, which are the binding constraint in practice.

## Standard of evidence

Built to **institutional investor standards: rigorous and auditable.** 
In short: every finding carries a source, a retrieval
date and the vintage of the underlying data; confidence is gated by vintage rather
than conviction; scripts fail loudly on empty result sets so silence is never read as
a negative finding; known limitations travel in-line with the number; and evidence
stays separated from view, because this engine issues no recommendations.

## Setup

Open-data endpoints rate-limit unidentified and shared User-Agents, and SEC EDGAR
blocks them outright, so your contact string is required rather than defaulted:

```bash
export HH_CONTACT="Your Name (you@example.com)"
```

## Author

HH-health-ai

## Disclaimers

Not affiliated with, endorsed by, or connected to CMS, HHS, the FDA, the SEC, the
USPTO, the CDC, the EMA or any other government agency. All data is retrieved from
public endpoints subject to those agencies' own terms.

Nothing here is investment advice, and no output should be read as a recommendation to
buy or sell any security. These engines produce evidence for a human analyst to weigh.

Optional MCP servers are independent third-party projects under their own licenses.
Review them before use.

## License

MIT — see [LICENSE](LICENSE).

## Purple Book family lookup

Brand/BLA searches resolve the reference product before looking across the full
export for linked biosimilars. BLA matching is exact. Repeated export headers select
the final full-database section; licensed counts use distinct BLAs, not presentations.

Explicit reference BLA linkage takes precedence over exact reference proper name.
Missing classification/linkage makes `biosimilar_count_licensed` null;
`matched_biosimilar_bla_count` reports only positively linked BLAs. This avoids
certifying a zero from an incomplete linkage. Unknown export schemas fail explicitly.
Use the archive's publication date when citing results; the script's run date does
not establish source vintage. Licensed still does not mean launched.

## Regression tests

Run offline with Python 3.10 or newer (standard library only):

```bash
python3 -m unittest discover -s tests -v
```

Tests use synthetic fixtures and mocked APIs; they do not certify live endpoint
availability or current regulatory facts. GitHub Actions runs the same tests on PRs.
