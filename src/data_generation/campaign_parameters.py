"""Parameters controlling Terra Active synthetic marketing campaigns."""

"""
Acquisition campaigns are intentionally intermittent rather than continuously active. 
Customers may therefore have a campaign-driven acquisition channel without a specific campaign_id, 
reflecting incomplete or unavailable campaign-level attribution.
"""


from __future__ import annotations

import numpy as np


CAMPAIGN_TYPES = (
    "Acquisition",
    "Product Launch",
    "Event Promotion",
    "Retention",
)

CAMPAIGN_TYPE_WEIGHTS = np.array([
    0.50,  # Acquisition
    0.20,  # Product Launch
    0.15,  # Event Promotion
    0.15,  # Retention
])

assert np.isclose(
    CAMPAIGN_TYPE_WEIGHTS.sum(),
    1.0,
)


TARGET_SEGMENTS = (
    "All Customers",
    "Urban Runner",
    "Active Lifestyle",
    "Studio Regular",
    "Outdoor Explorer",
    "Performance Athlete",
)


TARGET_SEGMENT_WEIGHTS = np.array([
    0.40,  # All Customers
    0.15,  # Urban Runner
    0.13,  # Active Lifestyle
    0.12,  # Studio Regular
    0.10,  # Outdoor Explorer
    0.10,  # Performance Athlete
])

assert np.isclose(
    TARGET_SEGMENT_WEIGHTS.sum(),
    1.0,
)


CAMPAIGN_CHANNELS_BY_TYPE = {
    "Acquisition": (
        "Paid Search",
        "Paid Social",
        "Influencer",
        "Community Event",
    ),
    "Product Launch": (
        "Paid Social",
        "Organic Social",
        "Influencer",
        "Email",
    ),
    "Event Promotion": (
        "Paid Social",
        "Organic Social",
        "Email",
        "Community Event",
    ),
    "Retention": (
        "Email",
        "Organic Social",
        "Community Event",
    ),
}


CAMPAIGN_CHANNEL_WEIGHTS_BY_TYPE = {
    "Acquisition": np.array([
        0.30,  # Paid Search
        0.40,  # Paid Social
        0.15,  # Influencer
        0.15,  # Community Event
    ]),
    "Product Launch": np.array([
        0.35,  # Paid Social
        0.25,  # Organic Social
        0.20,  # Influencer
        0.20,  # Email
    ]),
    "Event Promotion": np.array([
        0.30,  # Paid Social
        0.25,  # Organic Social
        0.20,  # Email
        0.25,  # Community Event
    ]),
    "Retention": np.array([
        0.55,  # Email
        0.25,  # Organic Social
        0.20,  # Community Event
    ]),
}

for campaign_type, weights in (
    CAMPAIGN_CHANNEL_WEIGHTS_BY_TYPE.items()
):
    assert np.isclose(
        weights.sum(),
        1.0,
    ), (
        f"Channel weights for {campaign_type} "
        "must sum to 1."
    )


CAMPAIGN_YEAR_WEIGHTS = {
    2023: 0.25,
    2024: 0.33,
    2025: 0.42,
}

assert np.isclose(
    sum(CAMPAIGN_YEAR_WEIGHTS.values()),
    1.0,
)


CAMPAIGN_DURATION_RANGES = {
    "Acquisition": (14, 45),
    "Product Launch": (10, 35),
    "Event Promotion": (7, 28),
    "Retention": (10, 40),
}


CAMPAIGN_SPEND_RANGES = {
    "Paid Search": (15_000, 90_000),
    "Paid Social": (20_000, 120_000),
    "Influencer": (8_000, 60_000),
    "Organic Social": (3_000, 20_000),
    "Email": (2_000, 15_000),
    "Community Event": (5_000, 35_000),
}


CAMPAIGN_IMPRESSION_RANGES = {
    "Paid Search": (100_000, 1_500_000),
    "Paid Social": (250_000, 3_000_000),
    "Influencer": (75_000, 1_200_000),
    "Organic Social": (50_000, 800_000),
    "Email": (20_000, 400_000),
    "Community Event": (10_000, 150_000),
}


CAMPAIGN_CTR_RANGES = {
    "Paid Search": (0.015, 0.060),
    "Paid Social": (0.008, 0.035),
    "Influencer": (0.010, 0.045),
    "Organic Social": (0.008, 0.030),
    "Email": (0.020, 0.080),
    "Community Event": (0.015, 0.050),
}