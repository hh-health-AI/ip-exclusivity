#!/usr/bin/env python3
"""Parse the FDA Purple Book CSV export into a reference-product / biosimilar view.

Stdlib only. Download the monthly Purple Book database extract (CSV) from
purplebooksearch.fda.gov and pass the local path.

Usage
-----
    python3 purple_book.py --csv purplebook.csv --product HUMIRA
    python3 purple_book.py --csv purplebook.csv --bla 125057 --json

Content in the database begins from May 2020; older licensure history may be absent.
"""
import argparse, csv, datetime, json, sys


def norm(row):
    lower = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
    def g(*keys):
        for k in keys:
            if k in lower and lower[k]:
                return lower[k]
        return ""
    return {
        "proprietary_name": g("proprietary name", "proprietary_name"),
        "proper_name": g("proper name", "proper_name", "nonproprietary name"),
        "bla_number": g("bla number", "bla_number", "application number"),
        "bla_type": g("bla type", "bla_type"),
        "applicant": g("applicant", "company"),
        "licensure_date": g("approval date", "licensure date", "bla approval date"),
        "ref_product_exclusivity_expiry": g("ref product exclusivity expiry date",
                                            "reference product exclusivity expiry date",
                                            "exclusivity expiry date"),
        "interchangeable_exclusivity_expiry": g("interchangeable exclusivity expiry date"),
        "marketing_status": g("marketing status"),
        "ref_product_proper_name": g("ref product proper name", "reference product proper name"),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--product", help="proprietary or proper name substring")
    ap.add_argument("--bla", help="BLA number")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    with open(a.csv, newline="", encoding="utf-8-sig", errors="replace") as f:
        # Purple Book exports carry preamble lines before the header row.
        lines = f.readlines()
    start = 0
    for i, ln in enumerate(lines[:25]):
        if "BLA" in ln.upper() and "NAME" in ln.upper():
            start = i
            break
    rows = [norm(r) for r in csv.DictReader(lines[start:])]

    def match(r):
        if a.bla:
            return a.bla.lstrip("0") in (r["bla_number"] or "").lstrip("0")
        q = (a.product or "").upper()
        return q and (q in r["proprietary_name"].upper() or q in r["proper_name"].upper())

    hits = [r for r in rows if match(r)]
    if not hits:
        sys.stderr.write("No matching rows. Try the proper (nonproprietary) name -- "
                         "biosimilars carry a four-letter suffix, e.g. adalimumab-atto.\n")
        sys.exit(2)

    originators = [r for r in hits if (r["bla_type"] or "").strip() in ("351(a)", "351a", "")]
    biosims = [r for r in hits if (r["bla_type"] or "").strip() in ("351(k)", "351k")]

    out = {
        "retrieved": datetime.date.today().isoformat(),
        "query": {"product": a.product, "bla": a.bla},
        "reference_products": originators,
        "biosimilars_licensed": biosims,
        "biosimilar_count_licensed": len(biosims),
        "reading": [
            "Licensed is not launched. Check for launch announcements, settlement-driven "
            "launch dates and manufacturing capacity before assuming any erosion.",
            "Interchangeability drives pharmacy-level substitution. Without it, erosion "
            "is payer- and provider-led and much slower.",
            "Physician-administered buy-and-bill products erode via ASP dynamics, not "
            "pharmacy substitution -- model price and volume separately.",
        ],
    }
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
