#!/usr/bin/env python3
"""Parse the FDA Electronic Orange Book and build a patent/exclusivity stack.

Stdlib only. Works from the monthly EOB zip (products.txt, patent.txt,
exclusivity.txt), which is the authoritative source. Download it from the FDA
Orange Book data files page and pass the local path.

Usage
-----
    python3 orange_book_loe.py --zip EOBZIP.zip --brand ELIQUIS
    python3 orange_book_loe.py --zip EOBZIP.zip --appl-no 202155 --json

The script does NOT know about settlements. Settlements usually set the real entry
date years before nominal expiry, so it prints a mandatory reminder to search the
sponsor's 10-K legal proceedings before reporting an LOE.
"""
import argparse, collections, csv, datetime, io, json, sys, zipfile

PATENT_STRENGTH = {
    "drug_substance": ("composition of matter", "hard constraint"),
    "drug_product": ("formulation", "designable-around; medium strength"),
    "use_code": ("method of use", "weak; carve-out possible via skinny label (sec viii)"),
}


def read_pipe(zf, name):
    for n in zf.namelist():
        if n.lower().endswith(name):
            raw = zf.read(n).decode("utf-8", errors="replace")
            return list(csv.DictReader(io.StringIO(raw), delimiter="~"))
    raise SystemExit(f"{name} not found in zip; members: {zf.namelist()}")


def parse_date(s):
    for fmt in ("%b %d, %Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(s.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", required=True, help="path to the Electronic Orange Book zip")
    ap.add_argument("--brand", help="trade name, case-insensitive substring")
    ap.add_argument("--appl-no", help="application number")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    with zipfile.ZipFile(a.zip) as zf:
        products = read_pipe(zf, "products.txt")
        patents = read_pipe(zf, "patent.txt")
        excl = read_pipe(zf, "exclusivity.txt")

    def match(p):
        if a.appl_no:
            return str(p.get("Appl_No", "")).lstrip("0") == a.appl_no.lstrip("0")
        return a.brand and a.brand.upper() in (p.get("Trade_Name") or "").upper()

    prods = [p for p in products if match(p)]
    if not prods:
        sys.stderr.write("No matching products. Check spelling of the trade name as the "
                         "Orange Book records it, and remember one brand can span "
                         "several application numbers.\n")
        sys.exit(2)

    appls = {str(p.get("Appl_No")) for p in prods}
    pat = [p for p in patents if str(p.get("Appl_No")) in appls]
    exc = [e for e in excl if str(e.get("Appl_No")) in appls]

    pat_rows = []
    for p in pat:
        kind = []
        if (p.get("Drug_Substance_Flag") or "").strip().upper() == "Y":
            kind.append("drug_substance")
        if (p.get("Drug_Product_Flag") or "").strip().upper() == "Y":
            kind.append("drug_product")
        if (p.get("Patent_Use_Code") or "").strip():
            kind.append("use_code")
        pat_rows.append({
            "patent_no": p.get("Patent_No"),
            "appl_no": p.get("Appl_No"),
            "product_no": p.get("Product_No"),
            "expiry": p.get("Patent_Expire_Date_Text"),
            "expiry_parsed": str(parse_date(p.get("Patent_Expire_Date_Text") or "") or ""),
            "use_code": p.get("Patent_Use_Code"),
            "delist_requested": p.get("Delist_Flag"),
            "pediatric_extension_flag": p.get("Pediatric_Extension"),
            "kinds": kind,
            "strength_read": [PATENT_STRENGTH[k][1] for k in kind] or ["unclassified"],
        })

    exc_rows = [{"appl_no": e.get("Appl_No"), "product_no": e.get("Product_No"),
                 "code": e.get("Exclusivity_Code"),
                 "expiry": e.get("Exclusivity_Date"),
                 "expiry_parsed": str(parse_date(e.get("Exclusivity_Date") or "") or "")}
                for e in exc]

    dates = [d for d in [r["expiry_parsed"] for r in pat_rows] +
                       [r["expiry_parsed"] for r in exc_rows] if d]
    nominal = max(dates) if dates else None

    hard = [r for r in pat_rows if "drug_substance" in r["kinds"] and r["expiry_parsed"]]
    hard_max = max((r["expiry_parsed"] for r in hard), default=None)

    out = {
        "query": {"brand": a.brand, "appl_no": a.appl_no},
        "retrieved": datetime.date.today().isoformat(),
        "applications": sorted(appls),
        "products": [{"trade_name": p.get("Trade_Name"), "appl_no": p.get("Appl_No"),
                      "product_no": p.get("Product_No"), "strength": p.get("Strength"),
                      "df_route": p.get("DF;Route"), "applicant": p.get("Applicant_Full_Name"),
                      "approval_date": p.get("Approval_Date"),
                      "rld": p.get("RLD"), "te_code": p.get("TE_Code")} for p in prods],
        "patents": sorted(pat_rows, key=lambda r: r["expiry_parsed"] or ""),
        "exclusivities": sorted(exc_rows, key=lambda r: r["expiry_parsed"] or ""),
        "nominal_loe": nominal,
        "latest_composition_of_matter_expiry": hard_max,
        "MANDATORY_NEXT_STEPS": [
            "NOMINAL IS NOT THE ANSWER. Search the sponsor's 10-K legal proceedings and "
            "8-Ks for a settlement/entry date on this molecule -- settlements routinely "
            "set entry years earlier and beat the patent date.",
            "Check the FDA Paragraph IV certification list for the date of first filing; "
            "first filing + 30-month stay is the earliest structurally plausible entry.",
            "Run ptab-ipr-monitor on the composition-of-matter patents above.",
            "Discount method-of-use patents: a skinny label under sec viii can carve the "
            "indication out and let a generic enter for the rest.",
            "Paediatric exclusivity adds 6 months on top of BOTH patents and "
            "exclusivities and is frequently the binding constraint.",
        ],
    }
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
