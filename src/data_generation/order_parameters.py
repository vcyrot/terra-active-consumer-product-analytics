"""Parameters controlling Terra Active synthetic customer orders."""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Customer purchase lifecycle
# ---------------------------------------------------------------------------

PURCHASE_PROBABILITY_BY_PERSONA = {
    "Urban Runner": 0.72,
    "Active Lifestyle": 0.62,
    "Studio Regular": 0.67,
    "Outdoor Explorer": 0.58,
    "Performance Athlete": 0.70,
}


FIRST_PURCHASE_DELAY_BUCKETS = (
    (0, 7),
    (8, 30),
    (31, 90),
    (91, 180),
    (181, 365),
)

FIRST_PURCHASE_DELAY_WEIGHTS = np.array(
    [
        0.30,
        0.30,
        0.20,
        0.12,
        0.08,
    ]
)

assert np.isclose(
    FIRST_PURCHASE_DELAY_WEIGHTS.sum(),
    1.0,
)


REPEAT_PURCHASE_PROBABILITY_BY_PERSONA = {
    "Urban Runner": 0.70,
    "Active Lifestyle": 0.55,
    "Studio Regular": 0.65,
    "Outdoor Explorer": 0.50,
    "Performance Athlete": 0.62,
}


REPEAT_PURCHASE_DELAY_BUCKETS = (
    (14, 45),
    (46, 90),
    (91, 180),
    (181, 365),
)

REPEAT_PURCHASE_DELAY_WEIGHTS = np.array(
    [
        0.30,
        0.35,
        0.25,
        0.10,
    ]
)

assert np.isclose(
    REPEAT_PURCHASE_DELAY_WEIGHTS.sum(),
    1.0,
)


# ---------------------------------------------------------------------------
# Order device and sales-channel behaviour
# ---------------------------------------------------------------------------

ORDER_DEVICE_WEIGHTS = {
    "Mobile": 0.68,
    "Desktop": 0.29,
    "Tablet": 0.03,
}


ORDER_DEVICE_MULTIPLIERS_BY_AGE = {
    "18-24": {
        "Mobile": 1.15,
        "Desktop": 0.75,
        "Tablet": 1.00,
    },
    "25-34": {
        "Mobile": 1.08,
        "Desktop": 0.85,
        "Tablet": 1.00,
    },
    "35-44": {
        "Mobile": 1.00,
        "Desktop": 1.00,
        "Tablet": 1.00,
    },
    "45-54": {
        "Mobile": 0.88,
        "Desktop": 1.20,
        "Tablet": 1.00,
    },
    "55+": {
        "Mobile": 0.78,
        "Desktop": 1.35,
        "Tablet": 1.00,
    },
}


ACQUISITION_DEVICE_PERSISTENCE_PROBABILITY = 0.60


ORDER_PLATFORM_WEIGHTS_BY_DEVICE = {
    "Desktop": {
        "Website": 1.00,
    },
    "Mobile": {
        "Website": 0.50,
        "iOS": 0.31,
        "Android": 0.19,
    },
    "Tablet": {
        "Website": 0.68,
        "iOS": 0.21,
        "Android": 0.11,
    },
}


ACQUISITION_PLATFORM_PERSISTENCE_PROBABILITY = 0.60


# ---------------------------------------------------------------------------
# Shipping geography behaviour
# ---------------------------------------------------------------------------

HOME_CITY_SHIPPING_PROBABILITY = 0.90

SAME_COUNTRY_OTHER_CITY_PROBABILITY = 0.10

OTHER_COUNTRY_SHIPPING_PROBABILITY = 0.00


assert np.isclose(
    HOME_CITY_SHIPPING_PROBABILITY
    + SAME_COUNTRY_OTHER_CITY_PROBABILITY
    + OTHER_COUNTRY_SHIPPING_PROBABILITY,
    1.0,
)


# ---------------------------------------------------------------------------
# Transaction currency
# ---------------------------------------------------------------------------

CURRENCY_BY_COUNTRY = {
    "United Kingdom": "GBP",
    "France": "EUR",
    "Germany": "EUR",
    "Spain": "EUR",
    "Netherlands": "EUR",
    "Italy": "EUR",
    "Switzerland": "CHF",
}


# ---------------------------------------------------------------------------
# Order status
# ---------------------------------------------------------------------------

# Completed:
#   Order was successfully fulfilled and was not fully refunded.
#
# Cancelled:
#   Order was created but cancelled before fulfilment.
#
# Refunded:
#   Order was fulfilled but ultimately fully refunded.
#
# Partial item-level returns will be represented later in the returns table.

ORDER_STATUS_WEIGHTS = {
    "Completed": 0.955,
    "Cancelled": 0.020,
    "Refunded": 0.025,
}


assert np.isclose(
    sum(ORDER_STATUS_WEIGHTS.values()),
    1.0,
)

# ---------------------------------------------------------------------------
# Promotion behaviour
# ---------------------------------------------------------------------------

PROMOTION_CODE_WEIGHTS = {
    None: 0.84,
    "WELCOME10": 0.05,
    "CLUB15": 0.04,
    "SEASON20": 0.04,
    "EVENT10": 0.02,
    "FREESHIP": 0.01,
}

assert np.isclose(
    sum(PROMOTION_CODE_WEIGHTS.values()),
    1.0,
)

# ---------------------------------------------------------------------------
# Order campaign attribution
# ---------------------------------------------------------------------------

# Probability that an order receives direct campaign attribution when at
# least one eligible campaign is active. Attribution is intentionally
# incomplete because real-world order-level marketing attribution is often
# unavailable or ambiguous.
ORDER_CAMPAIGN_ATTRIBUTION_PROBABILITY = 0.18

# If the customer's first order occurs while their acquisition campaign is
# still active, preserve that acquisition-to-order attribution more often
# than selecting another active campaign.
FIRST_ORDER_ACQUISITION_CAMPAIGN_PERSISTENCE_PROBABILITY = 0.60

# Relative selection weights when several eligible campaigns are active.
ORDER_CAMPAIGN_CHANNEL_WEIGHTS = {
    "Paid Social": 1.00,
    "Paid Search": 1.15,
    "Influencer": 0.80,
    "Community Event": 0.65,
    "Email": 0.75,
    "Organic Social": 0.55,
}