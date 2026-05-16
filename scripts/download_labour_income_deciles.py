from __future__ import annotations

import csv
import gzip
import io
import urllib.error
import urllib.request

from common import START_YEAR, END_YEAR, PROCESSED_DIR, RAW_DIR, write_csv


ILOSTAT_LABOUR_INCOME_DISTRIBUTION_URL = (
    "https://rplumber.ilo.org/data/indicator/"
    "?channel=ilostat&format=.csv.gz&id=LAP_2LID_QTL_RT&type=code"
)

RAW_FILENAME = "ilostat_labour_income_distribution_LAP_2LID_QTL_RT.csv.gz"

DECILE_LABELS = {
    "DCL_DECILE_01": "0 - 10%",
    "DCL_DECILE_02": "11 - 20%",
    "DCL_DECILE_03": "21 - 30%",
    "DCL_DECILE_04": "31 - 40%",
    "DCL_DECILE_05": "41 - 50%",
    "DCL_DECILE_06": "51 - 60%",
    "DCL_DECILE_07": "61 - 70%",
    "DCL_DECILE_08": "71 - 80%",
    "DCL_DECILE_09": "81 - 90%",
    "DCL_DECILE_10": "91 - 100%",
}

FIELDS = [
    "year",
    "decile",
    "labour_income_share_pct",
    "avg_wage",
    "estimated_avg_monthly_labour_income",
    "source",
]


def fetch_labour_income_distribution() -> bytes:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / RAW_FILENAME
    request = urllib.request.Request(
        ILOSTAT_LABOUR_INCOME_DISTRIBUTION_URL,
        headers={"User-Agent": "indonesia-inequality-data-ingestion/0.1"},
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read()
    except urllib.error.URLError:
        if raw_path.exists():
            return raw_path.read_bytes()
        raise

    raw_path.write_bytes(payload)
    return payload


def read_average_wages() -> dict[int, float]:
    path = PROCESSED_DIR / "labor_indonesia.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return {
            int(row["year"]): float(row["avg_wage"])
            for row in rows
            if row.get("avg_wage")
        }


def build_rows(payload: bytes, avg_wage_by_year: dict[int, float]) -> list[dict[str, object]]:
    text = gzip.decompress(payload).decode("utf-8-sig")
    rows = csv.DictReader(io.StringIO(text))

    result: list[dict[str, object]] = []
    for row in rows:
        if row.get("ref_area") != "IDN":
            continue

        decile = DECILE_LABELS.get(row.get("classif1", ""))
        if decile is None or not row.get("obs_value"):
            continue

        year = int(row["time"])
        avg_wage = avg_wage_by_year.get(year)
        if not START_YEAR <= year <= END_YEAR or avg_wage is None:
            continue

        labour_income_share_pct = float(row["obs_value"])
        result.append(
            {
                "year": year,
                "decile": decile,
                "labour_income_share_pct": labour_income_share_pct,
                "avg_wage": avg_wage,
                "estimated_avg_monthly_labour_income": avg_wage * labour_income_share_pct / 10,
                "source": (
                    "ILOSTAT LAP_2LID_QTL_RT labour income distribution by decile; "
                    "ILOSTAT EAR_EMTA_SEX_NB_A aggregate average monthly earnings used to index decile labour income"
                ),
            }
        )

    return sorted(result, key=lambda item: (int(item["year"]), str(item["decile"])))


if __name__ == "__main__":
    payload = fetch_labour_income_distribution()
    avg_wage_by_year = read_average_wages()
    rows = build_rows(payload, avg_wage_by_year)
    write_csv(PROCESSED_DIR / "labour_income_deciles_indonesia.csv", rows, FIELDS)
