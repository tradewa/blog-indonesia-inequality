from __future__ import annotations

from common import fetch_bps_json


RELEVANT_SUBJECTS = {
    3: "Consumer Prices Indices",
    5: "Consumption and Expenditure",
    19: "Labour Wages",
    20: "Wholesale Price Indices",
    23: "Poverty and Inequality",
}

SEARCH_TERMS = [
    "inflasi",
    "inflation",
    "indeks harga konsumen",
    "consumer price index",
    "beras",
    "rice",
    "upah",
    "wage",
    "gini",
    "kemiskinan",
    "poverty",
    "expenditure",
]


def rows_from_payload(payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, dict) or payload.get("status") != "OK":
        return []

    data = payload.get("data")
    if not isinstance(data, list) or len(data) < 2 or not isinstance(data[1], list):
        return []

    return [row for row in data[1] if isinstance(row, dict)]


def row_matches(row: dict[str, object]) -> bool:
    text = " ".join(str(value) for value in row.values()).lower()
    return any(term.lower() in text for term in SEARCH_TERMS)


def print_variable_matches(subject_id: int, subject_name: str) -> None:
    matches: list[dict[str, object]] = []

    for page in range(1, 9):
        payload = fetch_bps_json(
            ["list", "model", "var", "lang", "eng", "domain", "0000", "subject", str(subject_id), "page", str(page)],
            f"bps_var_subject_{subject_id}_page{page}",
        )
        rows = rows_from_payload(payload)
        if not rows:
            break

        matches.extend(row for row in rows if row_matches(row))

    print(f"\nSubject {subject_id}: {subject_name}")
    if not matches:
        print("  no matches in scanned variable pages")
        return

    for row in matches:
        print(f"  var {row.get('var_id')}: {row.get('title')}")


if __name__ == "__main__":
    for subject_id, subject_name in RELEVANT_SUBJECTS.items():
        print_variable_matches(subject_id, subject_name)
