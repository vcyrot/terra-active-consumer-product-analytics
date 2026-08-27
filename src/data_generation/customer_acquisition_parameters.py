"""Parameters controlling Terra Active customer acquisition generation."""

from __future__ import annotations

import numpy as np


ACQUISITION_CHANNELS = (
    "Organic Search",
    "Paid Search",
    "Paid Social",
    "Organic Social",
    "Referral",
    "Influencer",
    "Community Event",
    "Direct",
)


BASE_CHANNEL_WEIGHTS = np.array([
    0.22,  # Organic Search
    0.12,  # Paid Search
    0.20,  # Paid Social
    0.10,  # Organic Social
    0.09,  # Referral
    0.07,  # Influencer
    0.05,  # Community Event
    0.15,  # Direct
])

assert np.isclose(
    BASE_CHANNEL_WEIGHTS.sum(),
    1.0,
)

ACQUISITION_DEVICES = (
    "Mobile",
    "Desktop",
    "Tablet",
)

ACQUISITION_DEVICE_WEIGHTS = np.array([
    0.70,
    0.27,
    0.03,
])

assert np.isclose(
    ACQUISITION_DEVICE_WEIGHTS.sum(),
    1.0,
)

PERSONA_CHANNEL_ADJUSTMENTS = {
    "Urban Runner": {
        "Paid Social": 1.15,
        "Organic Social": 1.10,
        "Community Event": 1.10,
    },
    "Active Lifestyle": {
        "Paid Social": 1.10,
        "Influencer": 1.05,
    },
    "Studio Regular": {
        "Organic Social": 1.20,
        "Influencer": 1.20,
        "Paid Social": 1.10,
    },
    "Outdoor Explorer": {
        "Organic Search": 1.20,
        "Referral": 1.10,
        "Community Event": 1.10,
    },
    "Performance Athlete": {
        "Referral": 1.20,
        "Community Event": 1.25,
        "Organic Search": 1.10,
    },
}

AGE_CHANNEL_ADJUSTMENTS = {
    "18-24": {
        "Paid Social": 1.25,
        "Influencer": 1.20,
        "Organic Social": 1.15,
        "Direct": 0.85,
    },
    "25-34": {
        "Paid Social": 1.10,
        "Organic Social": 1.05,
    },
    "35-44": {
        "Organic Search": 1.10,
        "Paid Search": 1.05,
    },
    "45-54": {
        "Organic Search": 1.15,
        "Direct": 1.10,
        "Influencer": 0.80,
    },
    "55+": {
        "Organic Search": 1.20,
        "Direct": 1.20,
        "Influencer": 0.65,
        "Paid Social": 0.80,
    },
}

MOBILE_PLATFORM_WEIGHTS = {
    "Website": 0.55,
    "iOS": 0.28,
    "Android": 0.17,
}

TABLET_PLATFORM_WEIGHTS = {
    "Website": 0.70,
    "iOS": 0.20,
    "Android": 0.10,
}

# ---------------------------------------------------------------------
# Campaign-linked acquisition channels
# ---------------------------------------------------------------------

CAMPAIGN_DRIVEN_CHANNELS = {
    "Paid Search",
    "Paid Social",
    "Influencer",
    "Community Event",
}


# ---------------------------------------------------------------------
# First-touch behaviour
# ---------------------------------------------------------------------

FIRST_TOUCH_SAME_AS_ACQUISITION_PROBABILITY = 0.65


# ---------------------------------------------------------------------
# Device adjustments by age
# ---------------------------------------------------------------------

AGE_DEVICE_ADJUSTMENTS = {
    "18-24": {
        "Mobile": 1.15,
        "Desktop": 0.75,
    },
    "25-34": {
        "Mobile": 1.10,
        "Desktop": 0.85,
    },
    "35-44": {
        "Mobile": 1.00,
        "Desktop": 1.00,
    },
    "45-54": {
        "Mobile": 0.90,
        "Desktop": 1.20,
    },
    "55+": {
        "Mobile": 0.80,
        "Desktop": 1.35,
    },
}
