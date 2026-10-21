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
        "ref_product_bla": g("reference product bla number", "ref product bla number"),
    }


def bla_id(value):
    return value.strip().lstrip("0")


def kind(row):
    return row["bla_type"].lower().replace(" ", "").replace("(", "").replace(")", "")


def read_rows(lines):
    # Monthly exports contain an updates section followed by the full database.
    # Restart at a repeated header so changed products are not counted twice.
    header, rows = None, []
    for cells in csv.reader(lines):
        names = {c.strip().lower() for c in cells}
        if names.intersection({"bla number", "bla_number"}) and names.intersection({"proper name", "proper_name"}):
            header, rows = cells, []
        elif header and len(cells) == len(header):
            row = norm(dict(zip(header, cells)))
            if row["bla_number"].isdigit():
                rows.append(row)
    if not header or not rows:
        raise ValueError("No supported Purple Book header/product rows found")
    return rows


def select_family(rows, product=None, bla=None):
    if not (product and product.strip()) and not (bla and bla.strip().isdigit()):
        raise ValueError("Provide a nonempty product name or numeric BLA number")
    hits = [r for r in rows if
            (bla_id(r["bla_number"]) == bla_id(bla) if bla else
             any((product or "").casefold() in r[k].casefold()
                 for k in ("proprietary_name", "proper_name")))]
    if not hits:
        raise ValueError("No matching products; check the name or exact BLA number")
    refs = [r for r in rows if kind(r) == "351a"]
    originators = [r for r in refs if r in hits or any(
        (h["ref_product_bla"] and bla_id(h["ref_product_bla"]) == bla_id(r["bla_number"])) or
        (not h["ref_product_bla"] and h["ref_product_proper_name"] and
         h["ref_product_proper_name"].casefold() == r["proper_name"].casefold())
        for h in hits if kind(h) == "351k")]
    ids = {bla_id(r["bla_number"]) for r in originators}
    names = {r["proper_name"].casefold() for r in originators if r["proper_name"]}
    ambiguous = {name for name in names if len({bla_id(r["bla_number"]) for r in refs
                 if r["proper_name"].casefold() == name}) > 1}
    biosims = [r for r in rows if kind(r) == "351k" and (
        (r["ref_product_bla"] and bla_id(r["ref_product_bla"]) in ids) or
        (not r["ref_product_bla"] and r["ref_product_proper_name"].casefold() in names - ambiguous))]
    # Without explicit reference linkage, do not silently certify a zero count.
    complete = bool(originators) and not ambiguous and all(kind(r) in ("351a", "351k") for r in rows) and all(
        r["ref_product_bla"] or r["ref_product_proper_name"] for r in rows if kind(r) == "351k")
    count = len({bla_id(r["bla_number"]) for r in biosims})
    return {"reference_products": originators, "biosimilars_licensed": biosims,
            "matched_biosimilar_bla_count": count,
            "biosimilar_count_licensed": count if complete else None,
            "linkage_complete": complete,
            "linkage_note": "Explicit reference BLA preferred, otherwise exact reference proper name. "
                            "Counts are distinct BLAs, not strength/presentation rows. "
                            "Missing classification or linkage makes the total unknown."}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", required=True)
    selector = ap.add_mutually_exclusive_group(required=True)
    selector.add_argument("--product", help="proprietary or proper name substring")
    selector.add_argument("--bla", help="exact BLA number")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    with open(a.csv, newline="", encoding="utf-8-sig", errors="replace") as f:
        # Purple Book exports carry preamble lines before the header row.
        lines = f.readlines()
    try:
        family = select_family(read_rows(lines), a.product, a.bla)
    except ValueError as exc:
        ap.exit(2, str(exc) + "\n")

    out = {
        "retrieved": datetime.date.today().isoformat(),
        "query": {"product": a.product, "bla": a.bla},
        **family,
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
