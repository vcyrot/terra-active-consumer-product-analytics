"""Generate Terra Active synthetic customer acquisition records."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from config import GenerationConfig
from customer_acquisition_parameters import (
    ACQUISITION_CHANNELS,
    ACQUISITION_DEVICES,
    ACQUISITION_DEVICE_WEIGHTS,
    AGE_CHANNEL_ADJUSTMENTS,
    AGE_DEVICE_ADJUSTMENTS,
    BASE_CHANNEL_WEIGHTS,
    CAMPAIGN_DRIVEN_CHANNELS,
    FIRST_TOUCH_SAME_AS_ACQUISITION_PROBABILITY,
    MOBILE_PLATFORM_WEIGHTS,
    PERSONA_CHANNEL_ADJUSTMENTS,
    TABLET_PLATFORM_WEIGHTS,
)

def normalise_weights(
    weights: np.ndarray,
) -> np.ndarray:
    """Normalise positive weights so they sum to one."""

    total = weights.sum()

    if total <= 0:
        raise ValueError(
            "Probability weights must sum to a positive value."
        )

    return weights / total

def get_channel_probabilities(
    persona: str,
    age_band: str,
) -> np.ndarray:
    """Return acquisition probabilities conditional on persona and age."""

    weights = BASE_CHANNEL_WEIGHTS.astype(
        float
    ).copy()

    channel_index = {
        channel: index
        for index, channel
        in enumerate(ACQUISITION_CHANNELS)
    }

    persona_adjustments = (
        PERSONA_CHANNEL_ADJUSTMENTS.get(
            persona,
            {},
        )
    )

    for (
        channel,
        multiplier,
    ) in persona_adjustments.items():

        weights[
            channel_index[channel]
        ] *= multiplier

    age_adjustments = (
        AGE_CHANNEL_ADJUSTMENTS.get(
            age_band,
            {},
        )
    )

    for (
        channel,
        multiplier,
    ) in age_adjustments.items():

        weights[
            channel_index[channel]
        ] *= multiplier

    return normalise_weights(
        weights
    )
    
def get_device_probabilities(
    age_band: str,
) -> np.ndarray:
    """Return device probabilities conditional on age."""

    weights = (
        ACQUISITION_DEVICE_WEIGHTS
        .astype(float)
        .copy()
    )

    device_index = {
        device: index
        for index, device
        in enumerate(ACQUISITION_DEVICES)
    }

    adjustments = (
        AGE_DEVICE_ADJUSTMENTS.get(
            age_band,
            {},
        )
    )

    for (
        device,
        multiplier,
    ) in adjustments.items():

        weights[
            device_index[device]
        ] *= multiplier

    return normalise_weights(
        weights
    )
    
def generate_platform(
    rng: np.random.Generator,
    device: str,
) -> str:
    """Generate a valid platform conditional on acquisition device."""

    if device == "Desktop":
        return "Website"

    if device == "Mobile":
        platforms = list(
            MOBILE_PLATFORM_WEIGHTS.keys()
        )

        probabilities = list(
            MOBILE_PLATFORM_WEIGHTS.values()
        )

        return str(
            rng.choice(
                platforms,
                p=probabilities,
            )
        )

    if device == "Tablet":
        platforms = list(
            TABLET_PLATFORM_WEIGHTS.keys()
        )

        probabilities = list(
            TABLET_PLATFORM_WEIGHTS.values()
        )

        return str(
            rng.choice(
                platforms,
                p=probabilities,
            )
        )

    raise ValueError(
        f"Unknown acquisition device: {device}"
    )
    
def generate_first_touch_channel(
    rng: np.random.Generator,
    acquisition_channel: str,
) -> str:
    """Generate the customer's first known marketing touchpoint."""

    if (
        rng.random()
        < FIRST_TOUCH_SAME_AS_ACQUISITION_PROBABILITY
    ):
        return acquisition_channel

    alternative_channels = [
        channel
        for channel in ACQUISITION_CHANNELS
        if channel != acquisition_channel
    ]

    return str(
        rng.choice(
            alternative_channels
        )
    )
    
def find_matching_campaign(
    rng: np.random.Generator,
    campaigns: pd.DataFrame,
    acquisition_channel: str,
    acquisition_date: pd.Timestamp,
    customer_persona: str,
) -> str | None:
    """
    Return a campaign active on the acquisition date and compatible
    with the acquisition channel.
    """

    if (
        acquisition_channel
        not in CAMPAIGN_DRIVEN_CHANNELS
    ):
        return None

    eligible = campaigns[
        (
            campaigns["channel"]
            == acquisition_channel
        )
        & (
            campaigns["campaign_type"]
            == "Acquisition"
        )
        & (
            campaigns["start_date"]
            <= acquisition_date
        )
        & (
            campaigns["end_date"]
            >= acquisition_date
        )
    ].copy()

    if eligible.empty:
        return None

    targeted = eligible[
        eligible["target_segment"].isin(
            [
                "All Customers",
                customer_persona,
            ]
        )
    ]

    if not targeted.empty:
        eligible = targeted

    return str(
        rng.choice(
            eligible["campaign_id"].to_numpy()
        )
    )
    
    
def generate_customer_acquisition(
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
    config: GenerationConfig,
    ) -> pd.DataFrame:
    """Generate one acquisition record for every Terra Active customer."""

    rng = np.random.default_rng(
        config.random_seed + 4
    )

    campaigns = campaigns.copy()

    campaigns["start_date"] = pd.to_datetime(
        campaigns["start_date"]
    )

    campaigns["end_date"] = pd.to_datetime(
        campaigns["end_date"]
    )

    customers = customers.copy()

    customers["signup_date"] = pd.to_datetime(
        customers["signup_date"]
    )

    records: list[
        dict[str, object]
    ] = []

    for customer in customers.itertuples(
        index=False
    ):

        channel_probabilities = (
            get_channel_probabilities(
                customer.customer_persona,
                customer.age_band,
            )
        )

        acquisition_channel = str(
            rng.choice(
                ACQUISITION_CHANNELS,
                p=channel_probabilities,
            )
        )

        device_probabilities = (
            get_device_probabilities(
                customer.age_band
            )
        )

        acquisition_device = str(
            rng.choice(
                ACQUISITION_DEVICES,
                p=device_probabilities,
            )
        )

        acquisition_platform = (
            generate_platform(
                rng,
                acquisition_device,
            )
        )

        first_touch_channel = (
            generate_first_touch_channel(
                rng,
                acquisition_channel,
            )
        )

        # Initial model:
        # acquisition occurs when account is created.
        acquisition_date = (
            customer.signup_date
        )

        campaign_id = find_matching_campaign(
            rng=rng,
            campaigns=campaigns,
            acquisition_channel=acquisition_channel,
            acquisition_date=acquisition_date,
            customer_persona=(
                customer.customer_persona
            ),
        )

        referral_flag = (
            acquisition_channel
            == "Referral"
        )

        records.append(
            {
                "customer_id": (
                    customer.customer_id
                ),
                "acquisition_date": (
                    acquisition_date
                ),
                "acquisition_channel": (
                    acquisition_channel
                ),
                "campaign_id": (
                    campaign_id
                ),
                "first_touch_channel": (
                    first_touch_channel
                ),
                "last_touch_channel": (
                    acquisition_channel
                ),
                "acquisition_device": (
                    acquisition_device
                ),
                "acquisition_platform": (
                    acquisition_platform
                ),
                "referral_flag": (
                    referral_flag
                ),
            }
        )

    return pd.DataFrame(
        records
    )
    
def validate_customer_acquisition(
    acquisition: pd.DataFrame,
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> None:
    """Validate generated customer acquisition records."""

    required_columns = {
        "customer_id",
        "acquisition_date",
        "acquisition_channel",
        "campaign_id",
        "first_touch_channel",
        "last_touch_channel",
        "acquisition_device",
        "acquisition_platform",
        "referral_flag",
    }

    missing_columns = (
        required_columns
        - set(acquisition.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing acquisition columns: "
            f"{sorted(missing_columns)}"
        )

    if acquisition[
        "customer_id"
    ].duplicated().any():
        raise ValueError(
            "Duplicate customer acquisition "
            "records detected."
        )

    expected_customers = set(
        customers["customer_id"]
    )

    actual_customers = set(
        acquisition["customer_id"]
    )

    if (
        expected_customers
        != actual_customers
    ):
        raise ValueError(
            "Acquisition records do not "
            "match customer population."
        )

    invalid_channels = (
        set(
            acquisition[
                "acquisition_channel"
            ]
        )
        - set(ACQUISITION_CHANNELS)
    )

    if invalid_channels:
        raise ValueError(
            "Invalid acquisition channels: "
            f"{sorted(invalid_channels)}"
        )
    
    date_check = acquisition.merge(
        customers[
            [
                "customer_id",
                "signup_date",
            ]
        ],
        on="customer_id",
        how="left",
        validate="one_to_one",
    )

    date_check["acquisition_date"] = (
        pd.to_datetime(
            date_check[
                "acquisition_date"
            ]
        )
    )

    date_check["signup_date"] = (
        pd.to_datetime(
            date_check[
                "signup_date"
            ]
        )
    )

    if (
        date_check["acquisition_date"]
        > date_check["signup_date"]
    ).any():
        raise ValueError(
            "Acquisition occurs after signup."
        )
        
    if not (
        date_check["acquisition_date"]
        == date_check["signup_date"]
    ).all():
        raise ValueError(
            "Acquisition date must equal "
            "signup date in the initial model."
        )
        
    expected_referral_flag = (
        acquisition[
            "acquisition_channel"
        ]
        == "Referral"
    )

    if not (
        acquisition["referral_flag"]
        == expected_referral_flag
    ).all():
        raise ValueError(
            "Referral flag is inconsistent "
            "with acquisition channel."
        )

    invalid_desktop = acquisition[
        (
            acquisition[
                "acquisition_device"
            ]
            == "Desktop"
        )
        & (
            acquisition[
                "acquisition_platform"
            ]
            != "Website"
        )
    ]

    if not invalid_desktop.empty:
        raise ValueError(
            "Desktop acquisitions must "
            "use Website platform."
        )
        
    valid_campaign_ids = set(
        campaigns["campaign_id"]
    )

    campaign_ids = set(
        acquisition[
            "campaign_id"
        ].dropna()
    )

    invalid_campaigns = (
        campaign_ids
        - valid_campaign_ids
    )

    if invalid_campaigns:
        raise ValueError(
            "Acquisition records reference "
            "unknown campaigns."
        )
        
    linked = acquisition[
        acquisition["campaign_id"].notna()
    ].merge(
        campaigns[
            [
                "campaign_id",
                "channel",
                "campaign_type",
                "start_date",
                "end_date",
            ]
        ],
        on="campaign_id",
        how="left",
        validate="many_to_one",
    )

    linked["acquisition_date"] = (
        pd.to_datetime(
            linked["acquisition_date"]
        )
    )

    linked["start_date"] = (
        pd.to_datetime(
            linked["start_date"]
        )
    )

    linked["end_date"] = (
        pd.to_datetime(
            linked["end_date"]
        )
    )

    if not (
        linked["channel"]
        == linked["acquisition_channel"]
    ).all():
        raise ValueError(
            "Campaign channel does not match "
            "customer acquisition channel."
        )

    if not (
        linked["campaign_type"]
        == "Acquisition"
    ).all():
        raise ValueError(
            "Customer acquisitions reference "
            "non-acquisition campaigns."
        )

    valid_timing = (
        (
            linked["acquisition_date"]
            >= linked["start_date"]
        )
        & (
            linked["acquisition_date"]
            <= linked["end_date"]
        )
    )

    if not valid_timing.all():
        raise ValueError(
            "Acquisition linked to campaign "
            "outside campaign period."
        )
        
def save_customer_acquisition(
    acquisition: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Save customer acquisition records."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "customer_acquisition.csv"
    )

    acquisition.to_csv(
        output_path,
        index=False,
    )

    return output_path