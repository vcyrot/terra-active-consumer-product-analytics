"""Generate Terra Active reference locations."""

from __future__ import annotations
from pathlib import Path

import pandas as pd


LOCATIONS = [
    {
        "location_id": "LOC001",
        "city": "London",
        "country": "United Kingdom",
        "country_code": "GB",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "region": "Northern Europe",
        "market_size": "Large",
        "event_hub": True,
    },
    {
        "location_id": "LOC002",
        "city": "Manchester",
        "country": "United Kingdom",
        "country_code": "GB",
        "latitude": 53.4808,
        "longitude": -2.2426,
        "region": "Northern Europe",
        "market_size": "Medium",
        "event_hub": True,
    },
    {
        "location_id": "LOC003",
        "city": "Edinburgh",
        "country": "United Kingdom",
        "country_code": "GB",
        "latitude": 55.9533,
        "longitude": -3.1883,
        "region": "Northern Europe",
        "market_size": "Medium",
        "event_hub": True,
    },
    {
        "location_id": "LOC004",
        "city": "Paris",
        "country": "France",
        "country_code": "FR",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "region": "Western Europe",
        "market_size": "Large",
        "event_hub": True,
    },
    {
        "location_id": "LOC005",
        "city": "Lyon",
        "country": "France",
        "country_code": "FR",
        "latitude": 45.7640,
        "longitude": 4.8357,
        "region": "Western Europe",
        "market_size": "Medium",
        "event_hub": True,
    },
    {
        "location_id": "LOC006",
        "city": "Annecy",
        "country": "France",
        "country_code": "FR",
        "latitude": 45.8992,
        "longitude": 6.1294,
        "region": "Western Europe",
        "market_size": "Small",
        "event_hub": True,
    },
    {
        "location_id": "LOC007",
        "city": "Berlin",
        "country": "Germany",
        "country_code": "DE",
        "latitude": 52.5200,
        "longitude": 13.4050,
        "region": "Central Europe",
        "market_size": "Large",
        "event_hub": True,
    },
    {
        "location_id": "LOC008",
        "city": "Munich",
        "country": "Germany",
        "country_code": "DE",
        "latitude": 48.1351,
        "longitude": 11.5820,
        "region": "Central Europe",
        "market_size": "Large",
        "event_hub": True,
    },
    {
        "location_id": "LOC009",
        "city": "Amsterdam",
        "country": "Netherlands",
        "country_code": "NL",
        "latitude": 52.3676,
        "longitude": 4.9041,
        "region": "Western Europe",
        "market_size": "Medium",
        "event_hub": True,
    },
    {
        "location_id": "LOC010",
        "city": "Rotterdam",
        "country": "Netherlands",
        "country_code": "NL",
        "latitude": 51.9244,
        "longitude": 4.4777,
        "region": "Western Europe",
        "market_size": "Small",
        "event_hub": False,
    },
    {
        "location_id": "LOC011",
        "city": "Barcelona",
        "country": "Spain",
        "country_code": "ES",
        "latitude": 41.3874,
        "longitude": 2.1686,
        "region": "Southern Europe",
        "market_size": "Medium",
        "event_hub": True,
    },
    {
        "location_id": "LOC012",
        "city": "Madrid",
        "country": "Spain",
        "country_code": "ES",
        "latitude": 40.4168,
        "longitude": -3.7038,
        "region": "Southern Europe",
        "market_size": "Medium",
        "event_hub": True,
    },
    {
        "location_id": "LOC013",
        "city": "Milan",
        "country": "Italy",
        "country_code": "IT",
        "latitude": 45.4642,
        "longitude": 9.1900,
        "region": "Southern Europe",
        "market_size": "Medium",
        "event_hub": True,
    },
    {
        "location_id": "LOC014",
        "city": "Zurich",
        "country": "Switzerland",
        "country_code": "CH",
        "latitude": 47.3769,
        "longitude": 8.5417,
        "region": "Central Europe",
        "market_size": "Small",
        "event_hub": True,
    },
]


def generate_locations() -> pd.DataFrame:
    """Return the Terra Active location reference table."""

    locations = pd.DataFrame(LOCATIONS)

    return locations

def validate_locations(df: pd.DataFrame) -> None:
    """Validate the generated location reference table."""

    required_columns = {
        "location_id",
        "city",
        "country",
        "country_code",
        "latitude",
        "longitude",
        "region",
        "market_size",
        "event_hub",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing location columns: {sorted(missing_columns)}"
        )

    if df["location_id"].duplicated().any():
        raise ValueError("Duplicate location IDs detected.")

    if df[["city", "country"]].duplicated().any():
        raise ValueError(
            "Duplicate city-country combinations detected."
        )

    if not df["latitude"].between(-90, 90).all():
        raise ValueError("Invalid latitude detected.")

    if not df["longitude"].between(-180, 180).all():
        raise ValueError("Invalid longitude detected.")

    allowed_market_sizes = {
        "Large",
        "Medium",
        "Small",
    }

    invalid_market_sizes = (
        set(df["market_size"])
        - allowed_market_sizes
    )

    if invalid_market_sizes:
        raise ValueError(
            f"Invalid market sizes: {sorted(invalid_market_sizes)}"
        )
        

def save_locations(
    df: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Save the location reference table as CSV."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_dir / "locations.csv"

    df.to_csv(
        output_path,
        index=False,
    )

    return output_path