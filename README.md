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
