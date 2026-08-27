"""Generate Terra Active synthetic marketing campaigns."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from campaign_parameters import (
    CAMPAIGN_CHANNELS,
    CAMPAIGN_TYPES,
    CAMPAIGN_TYPE_WEIGHTS,
    TARGET_SEGMENTS,
)
from config import GenerationConfig

def generate_campaigns(
    config: GenerationConfig,
) -> pd.DataFrame:
    """Generate Terra Active synthetic marketing campaigns."""

    rng = np.random.default_rng(
        config.random_seed + 3
    )

    records: list[dict[str, object]] = []

    available_dates = pd.date_range(
        config.start_date,
        config.end_date,
        freq="D",
    )

    for index in range(
        config.number_of_campaigns
    ):

        campaign_type = rng.choice(
            CAMPAIGN_TYPES,
            p=CAMPAIGN_TYPE_WEIGHTS,
        )

        channel = rng.choice(
            CAMPAIGN_CHANNELS
        )

        start_date = pd.Timestamp(
            rng.choice(available_dates)
        )

        duration_days = int(
            rng.integers(
                7,
                46,
            )
        )

        end_date = min(
            start_date
            + pd.Timedelta(
                days=duration_days
            ),
            config.end_date,
        )

        target_segment = rng.choice(
            TARGET_SEGMENTS
        )

        campaign_spend = round(
            rng.uniform(
                5_000,
                80_000,
            ),
            2,
        )

        impressions = int(
            rng.integers(
                50_000,
                2_000_000,
            )
        )

        click_through_rate = rng.uniform(
            0.005,
            0.045,
        )

        clicks = int(
            impressions
            * click_through_rate
        )

        campaign_id = (
            f"CAMP{index + 1:04d}"
        )

        campaign_name = (
            f"Terra {campaign_type} "
            f"{index + 1:03d}"
        )

        records.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "channel": channel,
                "campaign_type": campaign_type,
                "start_date": start_date,
                "end_date": end_date,
                "target_segment": target_segment,
                "campaign_spend": campaign_spend,
                "impressions": impressions,
                "clicks": clicks,
            }
        )

    return pd.DataFrame(records)

def validate_campaigns(
    campaigns: pd.DataFrame,
    config: GenerationConfig,
) -> None:
    """Validate generated Terra Active campaigns."""

    required_columns = {
        "campaign_id",
        "campaign_name",
        "channel",
        "campaign_type",
        "start_date",
        "end_date",
        "target_segment",
        "campaign_spend",
        "impressions",
        "clicks",
    }

    missing_columns = (
        required_columns
        - set(campaigns.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing campaign columns: "
            f"{sorted(missing_columns)}"
        )

    if len(campaigns) != (
        config.number_of_campaigns
    ):
        raise ValueError(
            "Unexpected number of campaigns."
        )

    if campaigns[
        "campaign_id"
    ].duplicated().any():
        raise ValueError(
            "Duplicate campaign IDs detected."
        )

    if (
        campaigns["end_date"]
        < campaigns["start_date"]
    ).any():
        raise ValueError(
            "Campaign end date precedes start date."
        )

    if (
        campaigns["campaign_spend"]
        < 0
    ).any():
        raise ValueError(
            "Negative campaign spend detected."
        )

    if (
        campaigns["clicks"]
        > campaigns["impressions"]
    ).any():
        raise ValueError(
            "Campaign clicks exceed impressions."
        )
        
def save_campaigns(
    campaigns: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Save generated campaign data."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "campaigns.csv"
    )

    campaigns.to_csv(
        output_path,
        index=False,
    )

    return output_path

