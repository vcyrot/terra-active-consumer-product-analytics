"""Generate Terra Active synthetic marketing campaigns."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from campaign_parameters import (
    CAMPAIGN_CHANNELS_BY_TYPE,
    CAMPAIGN_CHANNEL_WEIGHTS_BY_TYPE,
    CAMPAIGN_CTR_RANGES,
    CAMPAIGN_DURATION_RANGES,
    CAMPAIGN_IMPRESSION_RANGES,
    CAMPAIGN_SPEND_RANGES,
    CAMPAIGN_TYPES,
    CAMPAIGN_TYPE_WEIGHTS,
    CAMPAIGN_YEAR_WEIGHTS,
    TARGET_SEGMENTS,
    TARGET_SEGMENT_WEIGHTS,
)
from config import GenerationConfig

def generate_campaign_start_date(
    rng: np.random.Generator,
    config: GenerationConfig,
) -> pd.Timestamp:
    """Generate a campaign start date consistent with business growth."""

    years = np.array(
        list(CAMPAIGN_YEAR_WEIGHTS.keys())
    )

    year_probabilities = np.array(
        list(CAMPAIGN_YEAR_WEIGHTS.values())
    )

    selected_year = int(
        rng.choice(
            years,
            p=year_probabilities,
        )
    )

    year_start = max(
        config.start_date,
        pd.Timestamp(
            f"{selected_year}-01-01"
        ),
    )

    year_end = min(
        config.end_date,
        pd.Timestamp(
            f"{selected_year}-12-31"
        ),
    )

    eligible_dates = pd.date_range(
        year_start,
        year_end,
        freq="D",
    )

    return pd.Timestamp(
        rng.choice(
            eligible_dates
        )
    )

def generate_campaigns(
    config: GenerationConfig,
) -> pd.DataFrame:
    """Generate Terra Active synthetic marketing campaigns."""

    rng = np.random.default_rng(
        config.random_seed + 3
    )

    records: list[dict[str, object]] = []


    for index in range(
        config.number_of_campaigns
    ):

        campaign_type = rng.choice(
            CAMPAIGN_TYPES,
            p=CAMPAIGN_TYPE_WEIGHTS,
        )

        channels = CAMPAIGN_CHANNELS_BY_TYPE[campaign_type]

        channel_weights = (
            CAMPAIGN_CHANNEL_WEIGHTS_BY_TYPE[
                campaign_type
            ]
        )

        channel = str(
            rng.choice(
                channels,
                p=channel_weights,
            )
        )

        start_date = (
            generate_campaign_start_date(
                rng,
                config,
            )
        )

        min_duration, max_duration = (
            CAMPAIGN_DURATION_RANGES[
                campaign_type
            ]
        )

        duration_days = int(
            rng.integers(
                min_duration,
                max_duration + 1,
            )
        )

        end_date = min(
            start_date
            + pd.Timedelta(
                days=duration_days
            ),
            config.end_date,
        )

        target_segment = str(
            rng.choice(
                TARGET_SEGMENTS,
                p=TARGET_SEGMENT_WEIGHTS,
            )
        )

        min_spend, max_spend = (
            CAMPAIGN_SPEND_RANGES[
                channel
            ]
        )

        campaign_spend = round(
            rng.uniform(
                min_spend,
                max_spend,
            ),
            2,
        )

        min_impressions, max_impressions = (
            CAMPAIGN_IMPRESSION_RANGES[
                channel
            ]
        )

        impressions = int(
            rng.integers(
                min_impressions,
                max_impressions + 1,
            )
        )

        min_ctr, max_ctr = (
            CAMPAIGN_CTR_RANGES[
                channel
            ]
        )

        click_through_rate = rng.uniform(
            min_ctr,
            max_ctr,
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

