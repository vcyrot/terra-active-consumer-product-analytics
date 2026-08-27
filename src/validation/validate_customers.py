"""Analytical validation for the Terra Active customer population."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_customers(
    path: Path,
) -> pd.DataFrame:
    """Load the generated customer population."""

    if not path.exists():
        raise FileNotFoundError(
            f"Customer dataset not found: {path}"
        )

    return pd.read_csv(
        path,
        parse_dates=["signup_date"],
    )


def load_locations(
    path: Path,
) -> pd.DataFrame:
    """Load Terra Active reference locations."""

    if not path.exists():
        raise FileNotFoundError(
            f"Location dataset not found: {path}"
        )

    return pd.read_csv(path)


def add_location_context(
    customers: pd.DataFrame,
    locations: pd.DataFrame,
) -> pd.DataFrame:
    """Attach city and country information to each customer."""

    return customers.merge(
        locations[
            [
                "location_id",
                "city",
                "country",
                "market_size",
                "region",
            ]
        ],
        on="location_id",
        how="left",
        validate="many_to_one",
    )


def customer_count_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Return a one-row summary of the customer population."""

    return pd.DataFrame(
        {
            "customer_count": [
                df["customer_id"].nunique()
            ],
            "first_signup_date": [
                df["signup_date"].min()
            ],
            "latest_signup_date": [
                df["signup_date"].max()
            ],
            "marketing_consent_rate_pct": [
                round(
                    df["marketing_consent"].mean()
                    * 100,
                    1,
                )
            ],
        }
    )


def persona_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise customer persona distribution."""

    summary = (
        df["customer_persona"]
        .value_counts()
        .rename_axis("customer_persona")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def age_band_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise customer age-band distribution."""

    summary = (
        df["age_band"]
        .value_counts()
        .rename_axis("age_band")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def gender_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise customer gender distribution."""

    summary = (
        df["gender"]
        .value_counts()
        .rename_axis("gender")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def location_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise customer distribution by city."""

    summary = (
        df.groupby(
            [
                "location_id",
                "city",
                "country",
                "market_size",
            ]
        )
        .size()
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary.sort_values(
        "customer_count",
        ascending=False,
    )


def country_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise customer population by country."""

    summary = (
        df.groupby("country")
        .size()
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary.sort_values(
        "customer_count",
        ascending=False,
    )


def signup_year_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise customer acquisition volume by signup year."""

    result = df.copy()

    result["signup_year"] = (
        result["signup_date"].dt.year
    )

    summary = (
        result.groupby("signup_year")
        .size()
        .reset_index(name="customers_signed_up")
    )

    summary["population_share_pct"] = (
        summary["customers_signed_up"]
        / len(result)
        * 100
    ).round(1)

    return summary


def signup_month_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise customer signups by calendar month."""

    result = df.copy()

    result["signup_month"] = (
        result["signup_date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        result.groupby("signup_month")
        .size()
        .reset_index(name="customers_signed_up")
    )


def sport_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise overall preferred-sport distribution."""

    summary = (
        df["preferred_sport"]
        .value_counts()
        .rename_axis("preferred_sport")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def persona_sport_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise preferred sport within each customer persona."""

    summary = (
        df.groupby(
            [
                "customer_persona",
                "preferred_sport",
            ]
        )
        .size()
        .reset_index(name="customer_count")
    )

    persona_totals = (
        summary.groupby(
            "customer_persona"
        )["customer_count"]
        .transform("sum")
    )

    summary["persona_share_pct"] = (
        summary["customer_count"]
        / persona_totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "customer_persona",
            "customer_count",
        ],
        ascending=[True, False],
    )


def persona_location_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise customer personas across Terra Active markets."""

    summary = (
        df.groupby(
            [
                "city",
                "customer_persona",
            ]
        )
        .size()
        .reset_index(name="customer_count")
    )

    city_totals = (
        summary.groupby(
            "city"
        )["customer_count"]
        .transform("sum")
    )

    summary["city_share_pct"] = (
        summary["customer_count"]
        / city_totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "city",
            "customer_count",
        ],
        ascending=[True, False],
    )


def marketing_consent_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise marketing consent by customer persona."""

    summary = (
        df.groupby("customer_persona")
        .agg(
            customer_count=(
                "customer_id",
                "count",
            ),
            marketing_consent_rate=(
                "marketing_consent",
                "mean",
            ),
        )
        .reset_index()
    )

    summary[
        "marketing_consent_rate_pct"
    ] = (
        summary["marketing_consent_rate"]
        * 100
    ).round(1)

    return summary.drop(
        columns=["marketing_consent_rate"]
    )


def main() -> None:
    """Run analytical validation of the customer population."""

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    customers_path = (
        project_root
        / "data"
        / "raw"
        / "customers.csv"
    )

    locations_path = (
        project_root
        / "data"
        / "raw"
        / "locations.csv"
    )

    customers = load_customers(
        customers_path
    )

    locations = load_locations(
        locations_path
    )

    customers = add_location_context(
        customers,
        locations,
    )

    print("\nCUSTOMER POPULATION SUMMARY")
    print(
        customer_count_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nPERSONA DISTRIBUTION")
    print(
        persona_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nAGE-BAND DISTRIBUTION")
    print(
        age_band_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nGENDER DISTRIBUTION")
    print(
        gender_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nCUSTOMERS BY CITY")
    print(
        location_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nCUSTOMERS BY COUNTRY")
    print(
        country_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nSIGNUPS BY YEAR")
    print(
        signup_year_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nPREFERRED SPORT")
    print(
        sport_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nPREFERRED SPORT BY PERSONA")
    print(
        persona_sport_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nMARKETING CONSENT BY PERSONA")
    print(
        marketing_consent_summary(
            customers
        )
        .to_string(index=False)
    )

    print("\nPERSONA MIX BY CITY")
    print(
        persona_location_summary(
            customers
        )
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()