from __future__ import annotations

import csv
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
START_YEAR = 2000
END_YEAR = 2024
COUNTRY = "IDN"


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def read_env_file(path: Path | None = None) -> dict[str, str]:
    env_path = path or PROJECT_ROOT / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def fetch_json(url: str, timeout: int = 60) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "indonesia-inequality-data-ingestion/0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_csv_value(row.get(field, "")) for field in fieldnames})


def format_csv_value(value: Any) -> Any:
    if isinstance(value, float):
        return f"{value:.10f}".rstrip("0").rstrip(".")
    return value


def year_rows() -> dict[int, dict[str, Any]]:
    return {year: {"year": year} for year in range(START_YEAR, END_YEAR + 1)}


def clean_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_world_bank_indicators(indicators: dict[str, str], raw_name: str) -> dict[str, dict[int, float | None]]:
    ensure_dirs()
    result: dict[str, dict[int, float | None]] = {}

    for column, indicator in indicators.items():
        query = urllib.parse.urlencode(
            {
                "format": "json",
                "date": f"{START_YEAR}:{END_YEAR}",
                "per_page": 1000,
            }
        )
        url = f"https://api.worldbank.org/v2/country/{COUNTRY}/indicator/{indicator}?{query}"
        payload = fetch_json(url)
        save_json(payload, RAW_DIR / f"{raw_name}_{indicator}.json")

        values: dict[int, float | None] = {}
        observations = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        for item in observations:
            year_text = item.get("date")
            if not year_text:
                continue
            year = int(year_text)
            if START_YEAR <= year <= END_YEAR:
                values[year] = clean_number(item.get("value"))
        result[column] = values

    return result


def merge_indicator_rows(
    indicators: dict[str, str],
    raw_name: str,
    output_name: str,
    fieldnames: list[str],
    source: str = "World Bank API",
    derived: dict[str, tuple[str, ...]] | None = None,
) -> None:
    data = fetch_world_bank_indicators(indicators, raw_name)
    rows_by_year = year_rows()

    for column, values in data.items():
        for year, value in values.items():
            rows_by_year[year][column] = value

    if derived:
        for target, parts in derived.items():
            for year, row in rows_by_year.items():
                vals = [row.get(part) for part in parts]
                if all(value is not None and value != "" for value in vals):
                    row[target] = sum(float(value) for value in vals)

    for row in rows_by_year.values():
        row["source"] = source

    rows = [rows_by_year[year] for year in sorted(rows_by_year)]
    write_csv(PROCESSED_DIR / output_name, rows, fieldnames)


def fetch_bps_json(path_parts: list[str], raw_name: str) -> Any | None:
    env = read_env_file()
    api_key = os.environ.get("BPS_API_KEY") or env.get("BPS_API_KEY")
    if not api_key:
        return None

    base = "https://webapi.bps.go.id/v1/api"
    url = "/".join([base, *[part.strip("/") for part in path_parts], "key", urllib.parse.quote(api_key)])
    try:
        payload = fetch_json(url)
    except urllib.error.HTTPError as exc:
        save_json(
            {
                "error": "BPS API request failed",
                "status": exc.code,
                "reason": exc.reason,
                "url_without_key": url.rsplit("/key/", 1)[0] + "/key/***",
            },
            RAW_DIR / f"{raw_name}_error.json",
        )
        return None

    save_json(payload, RAW_DIR / f"{raw_name}.json")
    return payload
