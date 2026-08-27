"""Analytical validation for Terra Active marketing campaigns."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


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


def add_campaign_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate useful campaign-level validation metrics."""

    result = df.copy()

    result["duration_days"] = (
        result["end_date"]
        - result["start_date"]
    ).dt.days + 1

    result["ctr_pct"] = (
        result["clicks"]
        / result["impressions"]
        * 100
    ).round(2)

    result["cost_per_click"] = (
        result["campaign_spend"]
        / result["clicks"]
    ).round(2)

    result["spend_per_1k_impressions"] = (
        result["campaign_spend"]
        / result["impressions"]
        * 1000
    ).round(2)

    return result


def campaign_type_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaign distribution by type."""

    summary = (
        df["campaign_type"]
        .value_counts()
        .rename_axis("campaign_type")
        .reset_index(name="campaign_count")
    )

    summary["campaign_share_pct"] = (
        summary["campaign_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def channel_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaigns by marketing channel."""

    summary = (
        df.groupby("channel")
        .agg(
            campaign_count=(
                "campaign_id",
                "count",
            ),
            total_spend=(
                "campaign_spend",
                "sum",
            ),
            avg_spend=(
                "campaign_spend",
                "mean",
            ),
            total_impressions=(
                "impressions",
                "sum",
            ),
            avg_impressions=(
                "impressions",
                "mean",
            ),
            total_clicks=(
                "clicks",
                "sum",
            ),
            avg_ctr_pct=(
                "ctr_pct",
                "mean",
            ),
            avg_cost_per_click=(
                "cost_per_click",
                "mean",
            ),
            avg_spend_per_1k_impressions=(
                "spend_per_1k_impressions",
                "mean",
            ),
        )
        .reset_index()
    )

    numeric_columns = [
        "total_spend",
        "avg_spend",
        "avg_impressions",
        "avg_ctr_pct",
        "avg_cost_per_click",
        "avg_spend_per_1k_impressions",
    ]

    summary[numeric_columns] = (
        summary[numeric_columns].round(2)
    )

    return summary.sort_values(
        "total_spend",
        ascending=False,
    )


def spend_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaign spend by campaign type."""

    summary = (
        df.groupby("campaign_type")
        .agg(
            campaign_count=(
                "campaign_id",
                "count",
            ),
            total_spend=(
                "campaign_spend",
                "sum",
            ),
            avg_spend=(
                "campaign_spend",
                "mean",
            ),
            min_spend=(
                "campaign_spend",
                "min",
            ),
            max_spend=(
                "campaign_spend",
                "max",
            ),
        )
        .reset_index()
    )

    numeric_columns = [
        "total_spend",
        "avg_spend",
        "min_spend",
        "max_spend",
    ]

    summary[numeric_columns] = (
        summary[numeric_columns].round(2)
    )

    return summary


def duration_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaign durations."""

    return (
        df.groupby("campaign_type")
        .agg(
            campaign_count=(
                "campaign_id",
                "count",
            ),
            avg_duration_days=(
                "duration_days",
                "mean",
            ),
            min_duration_days=(
                "duration_days",
                "min",
            ),
            max_duration_days=(
                "duration_days",
                "max",
            ),
        )
        .reset_index()
        .round(
            {
                "avg_duration_days": 1,
            }
        )
    )


def target_segment_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaign targeting."""

    summary = (
        df["target_segment"]
        .value_counts()
        .rename_axis("target_segment")
        .reset_index(name="campaign_count")
    )

    summary["campaign_share_pct"] = (
        summary["campaign_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def campaigns_by_year(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaigns by start year."""

    result = df.copy()

    result["campaign_year"] = (
        result["start_date"].dt.year
    )

    summary = (
        result.groupby("campaign_year")
        .agg(
            campaigns_started=(
                "campaign_id",
                "count",
            ),
            total_spend=(
                "campaign_spend",
                "sum",
            ),
        )
        .reset_index()
    )

    summary["campaign_share_pct"] = (
        summary["campaigns_started"]
        / len(result)
        * 100
    ).round(1)

    summary["total_spend"] = (
        summary["total_spend"]
        .round(2)
    )

    return summary


def campaign_type_by_year(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Show campaign-type mix by year."""

    result = df.copy()

    result["campaign_year"] = (
        result["start_date"].dt.year
    )

    return pd.crosstab(
        result["campaign_year"],
        result["campaign_type"],
    ).reset_index()


def channel_type_matrix(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Show campaign types generated across channels."""

    return pd.crosstab(
        df["channel"],
        df["campaign_type"],
    ).reset_index()


def ctr_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise click-through-rate behaviour by channel."""

    return (
        df.groupby("channel")
        .agg(
            avg_ctr_pct=(
                "ctr_pct",
                "mean",
            ),
            min_ctr_pct=(
                "ctr_pct",
                "min",
            ),
            max_ctr_pct=(
                "ctr_pct",
                "max",
            ),
        )
        .reset_index()
        .round(2)
    )


def efficiency_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaign efficiency metrics by channel."""

    return (
        df.groupby("channel")
        .agg(
            avg_cost_per_click=(
                "cost_per_click",
                "mean",
            ),
            min_cost_per_click=(
                "cost_per_click",
                "min",
            ),
            max_cost_per_click=(
                "cost_per_click",
                "max",
            ),
            avg_spend_per_1k_impressions=(
                "spend_per_1k_impressions",
                "mean",
            ),
        )
        .reset_index()
        .round(2)
    )


def acquisition_campaign_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition campaigns by channel."""

    acquisition = df[
        df["campaign_type"]
        == "Acquisition"
    ]

    summary = (
        acquisition["channel"]
        .value_counts()
        .rename_axis("channel")
        .reset_index(
            name="acquisition_campaigns"
        )
    )

    if acquisition.empty:
        summary["share_pct"] = 0.0
        return summary

    summary["share_pct"] = (
        summary["acquisition_campaigns"]
        / len(acquisition)
        * 100
    ).round(1)

    return summary


def acquisition_campaigns_by_year(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition campaigns by year."""

    acquisition = df[
        df["campaign_type"]
        == "Acquisition"
    ].copy()

    acquisition["campaign_year"] = (
        acquisition["start_date"].dt.year
    )

    return (
        acquisition.groupby(
            "campaign_year"
        )
        .agg(
            acquisition_campaigns=(
                "campaign_id",
                "count",
            ),
            total_acquisition_spend=(
                "campaign_spend",
                "sum",
            ),
        )
        .reset_index()
        .round(
            {
                "total_acquisition_spend": 2,
            }
        )
    )


def suspicious_campaigns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Identify campaigns with clearly suspicious metrics."""

    return df[
        (df["campaign_spend"] <= 0)
        | (df["impressions"] <= 0)
        | (df["clicks"] <= 0)
        | (df["ctr_pct"] <= 0)
        | (df["cost_per_click"] <= 0)
        | (
            df["spend_per_1k_impressions"]
            <= 0
        )
    ][
        [
            "campaign_id",
            "channel",
            "campaign_type",
            "campaign_spend",
            "impressions",
            "clicks",
            "ctr_pct",
            "cost_per_click",
            "spend_per_1k_impressions",
        ]
    ]


def main() -> None:
    """Run analytical validation of marketing campaigns."""

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    campaigns_path = (
        project_root
        / "data"
        / "raw"
        / "campaigns.csv"
    )

    campaigns = load_campaigns(
        campaigns_path
    )

    campaigns = add_campaign_metrics(
        campaigns
    )

    print("\nCAMPAIGN TYPE DISTRIBUTION")
    print(
        campaign_type_summary(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nCHANNEL SUMMARY")
    print(
        channel_summary(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nSPEND BY CAMPAIGN TYPE")
    print(
        spend_summary(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nCAMPAIGN DURATIONS")
    print(
        duration_summary(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nTARGET SEGMENTS")
    print(
        target_segment_summary(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nCAMPAIGNS BY YEAR")
    print(
        campaigns_by_year(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nCAMPAIGN TYPE BY YEAR")
    print(
        campaign_type_by_year(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nCHANNEL × CAMPAIGN TYPE")
    print(
        channel_type_matrix(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nCTR BY CHANNEL")
    print(
        ctr_summary(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nCAMPAIGN EFFICIENCY BY CHANNEL")
    print(
        efficiency_summary(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nACQUISITION CAMPAIGNS BY CHANNEL")
    print(
        acquisition_campaign_summary(
            campaigns
        )
        .to_string(index=False)
    )

    print("\nACQUISITION CAMPAIGNS BY YEAR")
    print(
        acquisition_campaigns_by_year(
            campaigns
        )
        .to_string(index=False)
    )

    suspicious = suspicious_campaigns(
        campaigns
    )

    print("\nSUSPICIOUS CAMPAIGNS")
    print(
        f"Suspicious campaigns: "
        f"{len(suspicious):,}"
    )

    if not suspicious.empty:
        print(
            suspicious.to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()