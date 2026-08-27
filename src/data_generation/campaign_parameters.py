"""Parameters controlling Terra Active synthetic marketing campaigns."""

from __future__ import annotations

import numpy as np


CAMPAIGN_CHANNELS = (
    "Paid Search",
    "Paid Social",
    "Influencer",
    "Organic Social",
    "Email",
    "Community Event",
)

CAMPAIGN_TYPES = (
    "Acquisition",
    "Product Launch",
    "Event Promotion",
    "Retention",
)

TARGET_SEGMENTS = (
    "All Customers",
    "Urban Runner",
    "Active Lifestyle",
    "Studio Regular",
    "Outdoor Explorer",
    "Performance Athlete",
)

CAMPAIGN_TYPE_WEIGHTS = np.array([
    0.45,  # Acquisition
    0.25,  # Product Launch
    0.15,  # Event Promotion
    0.15,  # Retention
])

assert np.isclose(
    CAMPAIGN_TYPE_WEIGHTS.sum(),
    1.0,
)