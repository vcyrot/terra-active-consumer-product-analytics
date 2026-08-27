"""Generate Terra Active synthetic customer population."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from config import GenerationConfig
from customer_parameters import (
    AGE_BANDS,
    AGE_BAND_WEIGHTS,
    CUSTOMER_PERSONAS,
    CUSTOMER_PERSONA_WEIGHTS,
    GENDER_OPTIONS,
    GENDER_WEIGHTS,
    LOCATION_WEIGHTS,
    SIGNUP_YEAR_WEIGHTS,
    SPORT_PREFERENCES,
)

def generate_signup_dates(
    rng: np.random.Generator,
    config: GenerationConfig,
) -> pd.Series:
    """Generate customer signup dates with year-over-year growth."""

    years = np.array(
        list(SIGNUP_YEAR_WEIGHTS.keys())
    )

    year_probabilities = np.array(
        list(SIGNUP_YEAR_WEIGHTS.values())
    )

    selected_years = rng.choice(
        years,
        size=config.number_of_customers,
        p=year_probabilities,
    )

    signup_dates: list[pd.Timestamp] = []

    for year in selected_years:

        year_start = max(
            config.start_date,
            pd.Timestamp(f"{year}-01-01"),
        )

        year_end = min(
            config.end_date,
            pd.Timestamp(f"{year}-12-31"),
        )

        eligible_dates = pd.date_range(
            year_start,
            year_end,
            freq="D",
        )

        signup_dates.append(
            pd.Timestamp(
                rng.choice(eligible_dates)
            )
        )

    return pd.Series(signup_dates)

def generate_preferred_sport(
    rng: np.random.Generator,
    persona: str,
) -> str:
    """Generate a preferred sport conditional on customer persona."""

    preferences = SPORT_PREFERENCES[
        persona
    ]

    sports = list(
        preferences.keys()
    )

    probabilities = list(
        preferences.values()
    )

    return str(
        rng.choice(
            sports,
            p=probabilities,
        )
    )
    
def generate_customers(
    locations: pd.DataFrame,
    config: GenerationConfig,
) -> pd.DataFrame:
    """Generate the Terra Active synthetic customer population."""

    rng = np.random.default_rng(
        config.random_seed + 2
    )

    location_ids = list(
        LOCATION_WEIGHTS.keys()
    )

    location_probabilities = np.array(
        list(
            LOCATION_WEIGHTS.values()
        )
    )

    # Make sure every configured location actually exists.
    unknown_locations = (
        set(location_ids)
        - set(locations["location_id"])
    )

    if unknown_locations:
        raise ValueError(
            "Customer configuration references "
            "unknown locations: "
            f"{sorted(unknown_locations)}"
        )

    customer_ids = [
        f"CUST{index + 1:06d}"
        for index in range(
            config.number_of_customers
        )
    ]

    personas = rng.choice(
        CUSTOMER_PERSONAS,
        size=config.number_of_customers,
        p=CUSTOMER_PERSONA_WEIGHTS,
    )

    signup_dates = generate_signup_dates(
        rng,
        config,
    )

    location_assignments = rng.choice(
        location_ids,
        size=config.number_of_customers,
        p=location_probabilities,
    )

    age_bands = rng.choice(
        AGE_BANDS,
        size=config.number_of_customers,
        p=AGE_BAND_WEIGHTS,
    )

    genders = rng.choice(
        GENDER_OPTIONS,
        size=config.number_of_customers,
        p=GENDER_WEIGHTS,
    )

    preferred_sports = [
        generate_preferred_sport(
            rng,
            persona,
        )
        for persona in personas
    ]

    marketing_consent = (
        rng.random(
            config.number_of_customers
        )
        < 0.72
    )

    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "signup_date": signup_dates,
        "location_id": location_assignments,
        "age_band": age_bands,
        "gender": genders,
        "customer_persona": personas,
        "preferred_sport": preferred_sports,
        "marketing_consent": marketing_consent,
    })

    return customers

def validate_customers(
    customers: pd.DataFrame,
    locations: pd.DataFrame,
    config: GenerationConfig,
) -> None:
    """Validate generated Terra Active customers."""

    required_columns = {
        "customer_id",
        "signup_date",
        "location_id",
        "age_band",
        "gender",
        "customer_persona",
        "preferred_sport",
        "marketing_consent",
    }

    missing_columns = (
        required_columns
        - set(customers.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing customer columns: "
            f"{sorted(missing_columns)}"
        )

    if len(customers) != config.number_of_customers:
        raise ValueError(
            f"Expected {config.number_of_customers:,} customers, "
            f"found {len(customers):,}."
        )

    if customers[
        "customer_id"
    ].duplicated().any():
        raise ValueError(
            "Duplicate customer IDs detected."
        )

    invalid_locations = (
        set(customers["location_id"])
        - set(locations["location_id"])
    )

    if invalid_locations:
        raise ValueError(
            "Customers reference unknown locations."
        )

    if not customers[
        "signup_date"
    ].between(
        config.start_date,
        config.end_date,
    ).all():
        raise ValueError(
            "Customer signup date outside simulation period."
        )

    if not customers[
        "customer_persona"
    ].isin(
        CUSTOMER_PERSONAS
    ).all():
        raise ValueError(
            "Unknown customer persona detected."
        )

    if customers.isna().any().any():
        raise ValueError(
            "Unexpected missing values detected "
            "in customer master."
        )
        
def save_customers(
    customers: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Save generated customer population."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "customers.csv"
    )

    customers.to_csv(
        output_path,
        index=False,
    )

    return output_path

