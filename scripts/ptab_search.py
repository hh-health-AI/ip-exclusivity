#!/usr/bin/env python3
"""Search USPTO PTAB proceedings (inter partes review and friends).

Requires a free USPTO Open Data Portal key in USPTO_API_KEY.

Usage
-----
    python3 ptab_search.py --patent 9000000
    python3 ptab_search.py --party "Mylan" --limit 50

Proceedings are available from September 2012. Search by PATENT NUMBER, not company
name -- challenges are often filed against a licensor or predecessor entity and a
company-name search misses them.
"""
import argparse, json, os, sys, urllib.error, urllib.parse, urllib.request

from _ua import user_agent

HOST = "https://api.uspto.gov"
PATHS = ["/api/v1/patent/decisions/ptab", "/ptab/v1/proceedings", "/api/v1/ptab/proceedings"]

MILESTONES = {
    "petition_filed": "clock starts",
    "institution_decision": "~6 months after filing; first real information event -- "
                            "institution means a reasonable likelihood at least one "
                            "claim is unpatentable",
    "final_written_decision": "statutorily within 12 months of institution",
    "federal_circuit_appeal": "adds 12-18 months",
}


def call(path, params, key):
    url = f"{HOST}{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-API-KEY": key,
                                               "Accept": "application/json",
                                               **user_agent("ptab-search")})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--patent", help="patent number, digits only")
    ap.add_argument("--party", help="petitioner or patent owner name")
    ap.add_argument("--limit", type=int, default=25)
    a = ap.parse_args()

    key = os.environ.get("USPTO_API_KEY")
    if not key:
        sys.stderr.write("USPTO_API_KEY not set. Register free at the USPTO Open Data "
                         "Portal (developer.uspto.gov) and export the key.\n")
        sys.exit(1)
    if not (a.patent or a.party):
        ap.error("--patent or --party required")

    params = {"limit": str(a.limit)}
    if a.patent:
        params["patentNumber"] = a.patent.replace(",", "")
    if a.party:
        params["partyName"] = a.party

    last_err = None
    for path in PATHS:
        try:
            res = call(path, params, key)
            out = {"endpoint": path, "query": params, "results": res,
                   "milestone_meanings": MILESTONES,
                   "caveats": [
                       "Discretionary denial can end a petition without any view on the "
                       "merits -- that is not a substantive win for the patent owner.",
                       "Institution rates and final-outcome rates are very different "
                       "numbers; institution does not license an invalidity assumption.",
                       "District-court Hatch-Waxman litigation runs in parallel and is "
                       "NOT in PTAB -- use CourtListener/RECAP and the sponsor's legal "
                       "proceedings disclosure for that.",
                       "Verify the assignment chain: assignee, Orange Book applicant and "
                       "ticker names frequently differ.",
                   ]}
            json.dump(out, sys.stdout, indent=2); print(); return
        except urllib.error.HTTPError as e:
            last_err = f"{path} -> HTTP {e.code}"
        except Exception as e:  # noqa: BLE001
            last_err = f"{path} -> {e}"

    sys.stderr.write(f"All candidate PTAB endpoints failed ({last_err}). USPTO has "
                     "reorganised its API paths more than once; check the current "
                     "Open Data Portal docs and update PATHS in this script.\n")
    sys.exit(3)


if __name__ == "__main__":
    main()
