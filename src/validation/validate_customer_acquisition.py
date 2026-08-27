"""Analytical validation for Terra Active customer acquisition data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_customer_acquisition(
    path: Path,
) -> pd.DataFrame:
    """Load generated customer acquisition records."""

    if not path.exists():
        raise FileNotFoundError(
            f"Customer acquisition dataset not found: {path}"
        )

    return pd.read_csv(
        path,
        parse_dates=["acquisition_date"],
    )


def load_customers(
    path: Path,
) -> pd.DataFrame:
    """Load generated customer population."""

    if not path.exists():
        raise FileNotFoundError(
            f"Customer dataset not found: {path}"
        )

    return pd.read_csv(
        path,
        parse_dates=["signup_date"],
    )


def load_campaigns(
    path: Path,
) -> pd.DataFrame:
    """Load generated marketing campaigns."""

    if not path.exists():
        raise FileNotFoundError(
            f"Campaign dataset not found: {path}"
        )

    return pd.read_csv(
        path,
        parse_dates=[
            "start_date",
            "end_date",
        ],
    )


def add_customer_context(
    acquisition: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Attach customer attributes to acquisition records."""

    return acquisition.merge(
        customers[
            [
                "customer_id",
                "signup_date",
                "age_band",
                "gender",
                "customer_persona",
                "preferred_sport",
                "location_id",
            ]
        ],
        on="customer_id",
        how="left",
        validate="one_to_one",
    )


def acquisition_channel_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition volume by channel."""

    summary = (
        df["acquisition_channel"]
        .value_counts()
        .rename_axis("acquisition_channel")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def channel_by_persona(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition channels within each persona."""

    summary = (
        df.groupby(
            [
                "customer_persona",
                "acquisition_channel",
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


def channel_by_age(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition channels within each age band."""

    summary = (
        df.groupby(
            [
                "age_band",
                "acquisition_channel",
            ]
        )
        .size()
        .reset_index(name="customer_count")
    )

    age_totals = (
        summary.groupby(
            "age_band"
        )["customer_count"]
        .transform("sum")
    )

    summary["age_band_share_pct"] = (
        summary["customer_count"]
        / age_totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "age_band",
            "customer_count",
        ],
        ascending=[True, False],
    )


def device_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition devices."""

    summary = (
        df["acquisition_device"]
        .value_counts()
        .rename_axis("acquisition_device")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def device_by_age(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition device mix by age band."""

    summary = (
        df.groupby(
            [
                "age_band",
                "acquisition_device",
            ]
        )
        .size()
        .reset_index(name="customer_count")
    )

    totals = (
        summary.groupby(
            "age_band"
        )["customer_count"]
        .transform("sum")
    )

    summary["age_band_share_pct"] = (
        summary["customer_count"]
        / totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "age_band",
            "customer_count",
        ],
        ascending=[True, False],
    )


def platform_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition platforms."""

    summary = (
        df["acquisition_platform"]
        .value_counts()
        .rename_axis("acquisition_platform")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def device_platform_matrix(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Show valid device-platform combinations."""

    return pd.crosstab(
        df["acquisition_device"],
        df["acquisition_platform"],
    ).reset_index()


def first_last_touch_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Measure first-touch vs last-touch alignment."""

    result = df.copy()

    result["same_first_last_touch"] = (
        result["first_touch_channel"]
        == result["last_touch_channel"]
    )

    summary = (
        result["same_first_last_touch"]
        .value_counts()
        .rename_axis("same_first_last_touch")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(result)
        * 100
    ).round(1)

    return summary


def first_touch_channel_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise first-touch channel distribution."""

    summary = (
        df["first_touch_channel"]
        .value_counts()
        .rename_axis("first_touch_channel")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def referral_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise referral acquisition."""

    summary = (
        df["referral_flag"]
        .value_counts()
        .rename_axis("referral_flag")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def campaign_coverage_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Measure overall campaign-link coverage."""

    result = df.copy()

    result["campaign_linked"] = (
        result["campaign_id"].notna()
    )

    summary = (
        result["campaign_linked"]
        .value_counts()
        .rename_axis("campaign_linked")
        .reset_index(name="customer_count")
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(result)
        * 100
    ).round(1)

    return summary


def campaign_coverage_by_channel(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Measure campaign-link coverage by acquisition channel."""

    result = df.copy()

    result["campaign_linked"] = (
        result["campaign_id"].notna()
    )

    summary = (
        result.groupby(
            "acquisition_channel"
        )
        .agg(
            customer_count=(
                "customer_id",
                "count",
            ),
            linked_customers=(
                "campaign_linked",
                "sum",
            ),
        )
        .reset_index()
    )

    summary["campaign_coverage_pct"] = (
        summary["linked_customers"]
        / summary["customer_count"]
        * 100
    ).round(1)

    return summary.sort_values(
        "campaign_coverage_pct",
        ascending=False,
    )


def campaign_linked_customers(
    df: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquired customers linked to each campaign."""

    linked = df[
        df["campaign_id"].notna()
    ].copy()

    if linked.empty:
        return pd.DataFrame(
            columns=[
                "campaign_id",
                "campaign_name",
                "channel",
                "start_date",
                "end_date",
                "acquired_customers",
            ]
        )

    summary = (
        linked.groupby("campaign_id")
        .size()
        .reset_index(
            name="acquired_customers"
        )
    )

    summary = summary.merge(
        campaigns[
            [
                "campaign_id",
                "campaign_name",
                "channel",
                "start_date",
                "end_date",
            ]
        ],
        on="campaign_id",
        how="left",
        validate="one_to_one",
    )

    return summary[
        [
            "campaign_id",
            "campaign_name",
            "channel",
            "start_date",
            "end_date",
            "acquired_customers",
        ]
    ].sort_values(
        "acquired_customers",
        ascending=False,
    )


def unused_acquisition_campaigns(
    df: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Identify acquisition campaigns linked to zero customers."""

    acquisition_campaigns = campaigns[
        campaigns["campaign_type"]
        == "Acquisition"
    ].copy()

    used_campaign_ids = set(
        df["campaign_id"].dropna()
    )

    unused = acquisition_campaigns[
        ~acquisition_campaigns[
            "campaign_id"
        ].isin(used_campaign_ids)
    ]

    return unused[
        [
            "campaign_id",
            "campaign_name",
            "channel",
            "start_date",
            "end_date",
            "target_segment",
        ]
    ].sort_values(
        "start_date"
    )


def campaign_coverage_by_year(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Measure campaign-link coverage by acquisition year."""

    result = df.copy()

    result["acquisition_year"] = (
        result["acquisition_date"].dt.year
    )

    result["campaign_linked"] = (
        result["campaign_id"].notna()
    )

    summary = (
        result.groupby(
            "acquisition_year"
        )
        .agg(
            customers=(
                "customer_id",
                "count",
            ),
            linked_customers=(
                "campaign_linked",
                "sum",
            ),
        )
        .reset_index()
    )

    summary["campaign_coverage_pct"] = (
        summary["linked_customers"]
        / summary["customers"]
        * 100
    ).round(1)

    return summary


def main() -> None:
    """Run analytical validation of customer acquisition."""

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    acquisition_path = (
        project_root
        / "data"
        / "raw"
        / "customer_acquisition.csv"
    )

    customers_path = (
        project_root
        / "data"
        / "raw"
        / "customers.csv"
    )

    campaigns_path = (
        project_root
        / "data"
        / "raw"
        / "campaigns.csv"
    )

    acquisition = load_customer_acquisition(
        acquisition_path
    )

    customers = load_customers(
        customers_path
    )

    campaigns = load_campaigns(
        campaigns_path
    )

    acquisition = add_customer_context(
        acquisition,
        customers,
    )

    print("\nACQUISITION CHANNEL DISTRIBUTION")
    print(
        acquisition_channel_summary(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nACQUISITION CHANNEL BY PERSONA")
    print(
        channel_by_persona(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nACQUISITION CHANNEL BY AGE")
    print(
        channel_by_age(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nDEVICE DISTRIBUTION")
    print(
        device_summary(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nDEVICE BY AGE")
    print(
        device_by_age(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nPLATFORM DISTRIBUTION")
    print(
        platform_summary(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nDEVICE × PLATFORM")
    print(
        device_platform_matrix(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nFIRST TOUCH VS LAST TOUCH")
    print(
        first_last_touch_summary(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nFIRST TOUCH CHANNEL")
    print(
        first_touch_channel_summary(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nREFERRAL SUMMARY")
    print(
        referral_summary(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nOVERALL CAMPAIGN COVERAGE")
    print(
        campaign_coverage_summary(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nCAMPAIGN COVERAGE BY CHANNEL")
    print(
        campaign_coverage_by_channel(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nCAMPAIGN COVERAGE BY YEAR")
    print(
        campaign_coverage_by_year(
            acquisition
        )
        .to_string(index=False)
    )

    print("\nCUSTOMERS LINKED TO CAMPAIGNS")
    print(
        campaign_linked_customers(
            acquisition,
            campaigns,
        )
        .head(30)
        .to_string(index=False)
    )

    unused = unused_acquisition_campaigns(
        acquisition,
        campaigns,
    )

    print("\nUNUSED ACQUISITION CAMPAIGNS")
    print(
        f"Unused acquisition campaigns: "
        f"{len(unused):,}"
    )

    if not unused.empty:
        print(
            unused.to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()