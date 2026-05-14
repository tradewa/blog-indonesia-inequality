from __future__ import annotations

from common import fetch_bps_json


SEARCH_TERMS = [
    "inflasi",
    "indeks harga konsumen",
    "beras",
    "upah",
    "gini",
    "kemiskinan",
]


def print_matches(payload: object, term: str) -> None:
    text = str(payload).lower()
    if term.lower() not in text:
        print(f"{term}: no obvious match in first BPS dynamic-table page")
        return
    print(f"{term}: possible match found in raw payload; inspect data/raw/bps_dynamic_tables_page1.json")


if __name__ == "__main__":
    payload = fetch_bps_json(
        ["list", "model", "dynamictable", "lang", "ind", "domain", "0000", "page", "1"],
        "bps_dynamic_tables_page1",
    )
    if payload is None:
        print("BPS API request did not return data. See data/raw/bps_dynamic_tables_page1_error.json.")
    else:
        for search_term in SEARCH_TERMS:
            print_matches(payload, search_term)
