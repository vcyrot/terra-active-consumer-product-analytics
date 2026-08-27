"""Parameters controlling Terra Active synthetic customer generation."""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------
# Customer personas
# ---------------------------------------------------------------------

CUSTOMER_PERSONAS = (
    "Urban Runner",
    "Active Lifestyle",
    "Studio Regular",
    "Outdoor Explorer",
    "Performance Athlete",
)

CUSTOMER_PERSONA_WEIGHTS = np.array([
    0.30,
    0.25,
    0.20,
    0.15,
    0.10,
])

assert np.isclose(
    CUSTOMER_PERSONA_WEIGHTS.sum(),
    1.0,
)


# ---------------------------------------------------------------------
# Age groups
# ---------------------------------------------------------------------

AGE_BANDS = (
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55+",
)

AGE_BAND_WEIGHTS = np.array([
    0.15,
    0.35,
    0.25,
    0.15,
    0.10,
])

assert np.isclose(
    AGE_BAND_WEIGHTS.sum(),
    1.0,
)


# ---------------------------------------------------------------------
# Gender
# ---------------------------------------------------------------------

GENDER_OPTIONS = (
    "Women",
    "Men",
    "Non-Binary / Other",
)

GENDER_WEIGHTS = np.array([
    0.55,
    0.43,
    0.02,
])

assert np.isclose(
    GENDER_WEIGHTS.sum(),
    1.0,
)


# ---------------------------------------------------------------------
# Location distribution
# ---------------------------------------------------------------------

LOCATION_WEIGHTS = {
    "LOC001": 0.16,  # London
    "LOC002": 0.06,  # Manchester
    "LOC003": 0.04,  # Edinburgh
    "LOC004": 0.13,  # Paris
    "LOC005": 0.05,  # Lyon
    "LOC006": 0.03,  # Annecy
    "LOC007": 0.10,  # Berlin
    "LOC008": 0.09,  # Munich
    "LOC009": 0.08,  # Amsterdam
    "LOC010": 0.02,  # Rotterdam
    "LOC011": 0.07,  # Barcelona
    "LOC012": 0.06,  # Madrid
    "LOC013": 0.07,  # Milan
    "LOC014": 0.04,  # Zurich
}

assert np.isclose(
    sum(LOCATION_WEIGHTS.values()),
    1.0,
)


# ---------------------------------------------------------------------
# Persona-specific sport preferences
# ---------------------------------------------------------------------

SPORT_PREFERENCES = {
    "Urban Runner": {
        "Running": 0.70,
        "Gym": 0.12,
        "Pilates": 0.05,
        "Hiking": 0.05,
        "Trail": 0.05,
        "Multi-Sport": 0.03,
    },
    "Active Lifestyle": {
        "Running": 0.20,
        "Gym": 0.25,
        "Pilates": 0.15,
        "Hiking": 0.15,
        "Trail": 0.05,
        "Multi-Sport": 0.20,
    },
    "Studio Regular": {
        "Running": 0.08,
        "Gym": 0.32,
        "Pilates": 0.45,
        "Hiking": 0.03,
        "Trail": 0.02,
        "Multi-Sport": 0.10,
    },
    "Outdoor Explorer": {
        "Running": 0.08,
        "Gym": 0.04,
        "Pilates": 0.02,
        "Hiking": 0.48,
        "Trail": 0.30,
        "Multi-Sport": 0.08,
    },
    "Performance Athlete": {
        "Running": 0.40,
        "Gym": 0.15,
        "Pilates": 0.03,
        "Hiking": 0.05,
        "Trail": 0.27,
        "Multi-Sport": 0.10,
    },
}

for persona, weights in SPORT_PREFERENCES.items():
    assert np.isclose(
        sum(weights.values()),
        1.0,
    ), f"Sport weights for {persona} must sum to 1."
    
SIGNUP_YEAR_WEIGHTS = {
    2023: 0.25,
    2024: 0.33,
    2025: 0.42,
}

assert np.isclose(
    sum(SIGNUP_YEAR_WEIGHTS.values()),
    1.0,
)