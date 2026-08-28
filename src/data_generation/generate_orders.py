"""Generate synthetic Terra Active customer order histories."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from order_parameters import (
    ACQUISITION_DEVICE_PERSISTENCE_PROBABILITY,
    ACQUISITION_PLATFORM_PERSISTENCE_PROBABILITY,
    CURRENCY_BY_COUNTRY,
    FIRST_ORDER_ACQUISITION_CAMPAIGN_PERSISTENCE_PROBABILITY,
    FIRST_PURCHASE_DELAY_BUCKETS,
    FIRST_PURCHASE_DELAY_WEIGHTS,
    HOME_CITY_SHIPPING_PROBABILITY,
    ORDER_CAMPAIGN_ATTRIBUTION_PROBABILITY,
    ORDER_CAMPAIGN_CHANNEL_WEIGHTS,
    ORDER_DEVICE_MULTIPLIERS_BY_AGE,
    ORDER_DEVICE_WEIGHTS,
    ORDER_PLATFORM_WEIGHTS_BY_DEVICE,
    ORDER_STATUS_WEIGHTS,
    OTHER_COUNTRY_SHIPPING_PROBABILITY,
    PROMOTION_CODE_WEIGHTS,
    PURCHASE_PROBABILITY_BY_PERSONA,
    REPEAT_PURCHASE_DELAY_BUCKETS,
    REPEAT_PURCHASE_DELAY_WEIGHTS,
    REPEAT_PURCHASE_PROBABILITY_BY_PERSONA,
    SAME_COUNTRY_OTHER_CITY_PROBABILITY,
)


SIMULATION_END_DATE = pd.Timestamp(
    "2025-12-31 23:59:59"
)


def load_customers(
    path: Path,
) -> pd.DataFrame:
    """Load generated Terra Active customers."""

    if not path.exists():
        raise FileNotFoundError(
            f"Customer dataset not found: {path}"
        )

    return pd.read_csv(
        path,
        parse_dates=[
            "signup_date",
        ],
    )


def load_customer_acquisition(
    path: Path,
) -> pd.DataFrame:
    """Load customer acquisition attributes."""

    if not path.exists():
        raise FileNotFoundError(
            f"Customer acquisition dataset not found: "
            f"{path}"
        )

    return pd.read_csv(
        path,
        parse_dates=[
            "acquisition_date",
        ],
    )


def load_locations(
    path: Path,
) -> pd.DataFrame:
    """Load Terra Active geographic locations."""

    if not path.exists():
        raise FileNotFoundError(
            f"Locations dataset not found: {path}"
        )

    locations = pd.read_csv(
        path
    )

    required_columns = {
        "location_id",
        "city",
        "country",
    }

    missing_columns = (
        required_columns.difference(
            locations.columns
        )
    )

    if missing_columns:
        raise ValueError(
            "Locations dataset missing columns: "
            f"{sorted(missing_columns)}"
        )

    if (
        locations[
            "location_id"
        ]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Duplicate location IDs detected."
        )

    return locations


def load_campaigns(
    path: Path,
) -> pd.DataFrame:
    """Load Terra Active marketing campaigns."""

    if not path.exists():
        raise FileNotFoundError(
            f"Campaign dataset not found: {path}"
        )

    campaigns = pd.read_csv(
        path,
        parse_dates=[
            "start_date",
            "end_date",
        ],
    )

    required_columns = {
        "campaign_id",
        "channel",
        "start_date",
        "end_date",
        "target_segment",
    }

    missing_columns = (
        required_columns.difference(
            campaigns.columns
        )
    )

    if missing_columns:
        raise ValueError(
            "Campaign dataset missing columns: "
            f"{sorted(missing_columns)}"
        )

    if (
        campaigns[
            "campaign_id"
        ]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Duplicate campaign IDs detected."
        )

    invalid_dates = (
        campaigns[
            "end_date"
        ]
        < campaigns[
            "start_date"
        ]
    )

    if invalid_dates.any():
        raise ValueError(
            "Campaign end date detected "
            "before start date."
        )

    return campaigns


def prepare_customers(
    customers: pd.DataFrame,
    acquisition: pd.DataFrame,
    locations: pd.DataFrame,
) -> pd.DataFrame:
    """Attach acquisition and home-location attributes."""

    acquisition_columns = (
        acquisition[
            [
                "customer_id",
                "acquisition_device",
                "acquisition_platform",
                "campaign_id",
            ]
        ]
        .rename(
            columns={
                "campaign_id":
                    "acquisition_campaign_id",
            }
        )
    )

    result = customers.merge(
        acquisition_columns,
        on="customer_id",
        how="left",
        validate="one_to_one",
    )

    home_locations = (
        locations[
            [
                "location_id",
                "country",
            ]
        ]
        .rename(
            columns={
                "country":
                    "home_country",
            }
        )
    )

    result = result.merge(
        home_locations,
        on="location_id",
        how="left",
        validate="many_to_one",
    )

    missing_acquisition = (
        result[
            [
                "acquisition_device",
                "acquisition_platform",
            ]
        ]
        .isna()
        .any(axis=1)
    )

    if missing_acquisition.any():
        raise ValueError(
            "Customers missing acquisition "
            "device/platform information."
        )

    if (
        result[
            "home_country"
        ]
        .isna()
        .any()
    ):
        raise ValueError(
            "Customers reference unknown "
            "home locations."
        )

    return result


def sample_delay(
    rng: np.random.Generator,
    buckets: tuple[
        tuple[int, int],
        ...
    ],
    weights: np.ndarray,
) -> int:
    """Sample a number of days from weighted delay buckets."""

    bucket_index = rng.choice(
        len(buckets),
        p=weights,
    )

    (
        minimum_days,
        maximum_days,
    ) = buckets[
        bucket_index
    ]

    return int(
        rng.integers(
            minimum_days,
            maximum_days + 1,
        )
    )


def sample_order_timestamp(
    rng: np.random.Generator,
    base_date: pd.Timestamp,
    delay_days: int,
) -> pd.Timestamp:
    """Create an order timestamp after a base date."""

    order_date = (
        base_date
        + pd.Timedelta(
            days=delay_days
        )
    )

    hour = int(
        rng.integers(
            8,
            23,
        )
    )

    minute = int(
        rng.integers(
            0,
            60,
        )
    )

    second = int(
        rng.integers(
            0,
            60,
        )
    )

    return (
        order_date.normalize()
        + pd.Timedelta(
            hours=hour,
            minutes=minute,
            seconds=second,
        )
    )


def generate_customer_orders(
    customer: pd.Series,
    rng: np.random.Generator,
) -> list[pd.Timestamp]:
    """Generate the order history for one customer."""

    persona = customer[
        "customer_persona"
    ]

    signup_date = customer[
        "signup_date"
    ]

    purchase_probability = (
        PURCHASE_PROBABILITY_BY_PERSONA[
            persona
        ]
    )

    if (
        rng.random()
        >= purchase_probability
    ):
        return []

    first_delay = sample_delay(
        rng=rng,
        buckets=(
            FIRST_PURCHASE_DELAY_BUCKETS
        ),
        weights=(
            FIRST_PURCHASE_DELAY_WEIGHTS
        ),
    )

    first_order = (
        sample_order_timestamp(
            rng=rng,
            base_date=signup_date,
            delay_days=first_delay,
        )
    )

    if (
        first_order
        > SIMULATION_END_DATE
    ):
        return []

    order_timestamps = [
        first_order
    ]

    current_order = first_order

    repeat_probability = (
        REPEAT_PURCHASE_PROBABILITY_BY_PERSONA[
            persona
        ]
    )

    while (
        rng.random()
        < repeat_probability
    ):
        repeat_delay = sample_delay(
            rng=rng,
            buckets=(
                REPEAT_PURCHASE_DELAY_BUCKETS
            ),
            weights=(
                REPEAT_PURCHASE_DELAY_WEIGHTS
            ),
        )

        next_order = (
            sample_order_timestamp(
                rng=rng,
                base_date=current_order,
                delay_days=repeat_delay,
            )
        )

        if (
            next_order
            > SIMULATION_END_DATE
        ):
            break

        order_timestamps.append(
            next_order
        )

        current_order = next_order

    return order_timestamps


def normalise_weights(
    weights: np.ndarray,
) -> np.ndarray:
    """Normalise probability weights."""

    total = weights.sum()

    if total <= 0:
        raise ValueError(
            "Probability weights must "
            "sum to more than zero."
        )

    return (
        weights
        / total
    )


def sample_order_device(
    customer: pd.Series,
    rng: np.random.Generator,
) -> str:
    """Sample the device used for an order."""

    acquisition_device = (
        customer[
            "acquisition_device"
        ]
    )

    if (
        rng.random()
        < ACQUISITION_DEVICE_PERSISTENCE_PROBABILITY
    ):
        return str(
            acquisition_device
        )

    devices = list(
        ORDER_DEVICE_WEIGHTS.keys()
    )

    base_weights = np.array(
        [
            ORDER_DEVICE_WEIGHTS[
                device
            ]
            for device
            in devices
        ],
        dtype=float,
    )

    age_band = customer[
        "age_band"
    ]

    age_multipliers = (
        ORDER_DEVICE_MULTIPLIERS_BY_AGE[
            age_band
        ]
    )

    adjusted_weights = np.array(
        [
            base_weight
            * age_multipliers[
                device
            ]
            for (
                device,
                base_weight,
            )
            in zip(
                devices,
                base_weights,
            )
        ],
        dtype=float,
    )

    adjusted_weights = (
        normalise_weights(
            adjusted_weights
        )
    )

    return str(
        rng.choice(
            devices,
            p=adjusted_weights,
        )
    )


def platform_is_valid_for_device(
    platform: str,
    device: str,
) -> bool:
    """Check whether platform/device combination is valid."""

    return (
        platform
        in ORDER_PLATFORM_WEIGHTS_BY_DEVICE[
            device
        ]
    )


def sample_sales_channel(
    customer: pd.Series,
    device: str,
    rng: np.random.Generator,
) -> str:
    """Sample Website, iOS or Android sales channel."""

    acquisition_platform = (
        customer[
            "acquisition_platform"
        ]
    )

    can_reuse_platform = (
        platform_is_valid_for_device(
            platform=(
                acquisition_platform
            ),
            device=device,
        )
    )

    if (
        can_reuse_platform
        and (
            rng.random()
            < ACQUISITION_PLATFORM_PERSISTENCE_PROBABILITY
        )
    ):
        return str(
            acquisition_platform
        )

    platform_weights = (
        ORDER_PLATFORM_WEIGHTS_BY_DEVICE[
            device
        ]
    )

    platforms = list(
        platform_weights.keys()
    )

    weights = np.array(
        [
            platform_weights[
                platform
            ]
            for platform
            in platforms
        ],
        dtype=float,
    )

    weights = normalise_weights(
        weights
    )

    return str(
        rng.choice(
            platforms,
            p=weights,
        )
    )


def sample_shipping_location_id(
    customer: pd.Series,
    locations: pd.DataFrame,
    rng: np.random.Generator,
) -> str:
    """Sample the shipping location for an order."""

    home_location_id = (
        customer[
            "location_id"
        ]
    )

    home_country = (
        customer[
            "home_country"
        ]
    )

    shipping_type = rng.choice(
        [
            "home_location",
            "same_country",
            "other_country",
        ],
        p=[
            HOME_CITY_SHIPPING_PROBABILITY,
            SAME_COUNTRY_OTHER_CITY_PROBABILITY,
            OTHER_COUNTRY_SHIPPING_PROBABILITY,
        ],
    )

    if (
        shipping_type
        == "home_location"
    ):
        return str(
            home_location_id
        )

    if (
        shipping_type
        == "same_country"
    ):
        candidates = locations[
            (
                locations[
                    "country"
                ]
                == home_country
            )
            & (
                locations[
                    "location_id"
                ]
                != home_location_id
            )
        ]

        if candidates.empty:
            return str(
                home_location_id
            )

        return str(
            rng.choice(
                candidates[
                    "location_id"
                ].to_numpy()
            )
        )

    candidates = locations[
        locations[
            "country"
        ]
        != home_country
    ]

    if candidates.empty:
        return str(
            home_location_id
        )

    return str(
        rng.choice(
            candidates[
                "location_id"
            ].to_numpy()
        )
    )


def currency_for_location(
    shipping_location_id: str,
    locations_by_id: pd.DataFrame,
) -> str:
    """Return transaction currency for a shipping location."""

    country = (
        locations_by_id.at[
            shipping_location_id,
            "country",
        ]
    )

    try:
        return (
            CURRENCY_BY_COUNTRY[
                country
            ]
        )

    except KeyError as exc:
        raise ValueError(
            f"No currency configured "
            f"for country: {country}"
        ) from exc


def sample_order_status(
    rng: np.random.Generator,
) -> str:
    """Sample the eventual status of an order."""

    statuses = list(
        ORDER_STATUS_WEIGHTS.keys()
    )

    weights = np.array(
        [
            ORDER_STATUS_WEIGHTS[
                status
            ]
            for status
            in statuses
        ],
        dtype=float,
    )

    weights = normalise_weights(
        weights
    )

    return str(
        rng.choice(
            statuses,
            p=weights,
        )
    )


def sample_promotion_code(
    order_status: str,
    is_first_order: bool,
    rng: np.random.Generator,
) -> str | None:
    """Sample the promotion code used on an order."""

    if (
        order_status
        == "Cancelled"
    ):
        return None

    promotion_weights = (
        PROMOTION_CODE_WEIGHTS.copy()
    )

    # WELCOME10 is intentionally restricted to the
    # customer's first order.
    #
    # On repeat orders, its probability is transferred
    # to the no-promotion bucket rather than distributed
    # across the other promotions.
    if not is_first_order:
        welcome_weight = (
            promotion_weights.pop(
                "WELCOME10"
            )
        )

        promotion_weights[
            None
        ] += welcome_weight

    promotion_codes = list(
        promotion_weights.keys()
    )

    weights = np.array(
        [
            promotion_weights[
                promotion_code
            ]
            for promotion_code
            in promotion_codes
        ],
        dtype=float,
    )

    weights = normalise_weights(
        weights
    )

    promotion_code = rng.choice(
        promotion_codes,
        p=weights,
    )

    if promotion_code is None:
        return None

    return str(
        promotion_code
    )


def eligible_campaigns_for_order(
    customer: pd.Series,
    order_timestamp: pd.Timestamp,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Return campaigns eligible for an order."""

    order_date = (
        order_timestamp.normalize()
    )

    eligible = campaigns[
        (
            campaigns[
                "start_date"
            ].dt.normalize()
            <= order_date
        )
        & (
            campaigns[
                "end_date"
            ].dt.normalize()
            >= order_date
        )
        & (
            campaigns[
                "target_segment"
            ]
            == customer[
                "customer_persona"
            ]
        )
    ].copy()

    # Customers without marketing consent should not
    # receive direct attribution to email campaigns.
    if not bool(
        customer[
            "marketing_consent"
        ]
    ):
        eligible = eligible[
            eligible[
                "channel"
            ]
            != "Email"
        ]

    return eligible


def sample_campaign_id(
    customer: pd.Series,
    order_timestamp: pd.Timestamp,
    is_first_order: bool,
    campaigns: pd.DataFrame,
    rng: np.random.Generator,
) -> str | None:
    """Sample direct marketing campaign attribution for an order."""

    eligible = (
        eligible_campaigns_for_order(
            customer=customer,
            order_timestamp=(
                order_timestamp
            ),
            campaigns=campaigns,
        )
    )

    if eligible.empty:
        return None

    acquisition_campaign_id = (
        customer[
            "acquisition_campaign_id"
        ]
    )

    eligible_campaign_ids = set(
        eligible[
            "campaign_id"
        ]
    )

    acquisition_campaign_eligible = (
        is_first_order
        and pd.notna(
            acquisition_campaign_id
        )
        and (
            acquisition_campaign_id
            in eligible_campaign_ids
        )
    )

    # If a customer's acquisition campaign is still active
    # when their first order occurs, preserve the attribution
    # more often than assigning another active campaign.
    if (
        acquisition_campaign_eligible
        and (
            rng.random()
            < FIRST_ORDER_ACQUISITION_CAMPAIGN_PERSISTENCE_PROBABILITY
        )
    ):
        return str(
            acquisition_campaign_id
        )

    # Attribution remains intentionally incomplete.
    if (
        rng.random()
        >= ORDER_CAMPAIGN_ATTRIBUTION_PROBABILITY
    ):
        return None

    weights = (
        eligible[
            "channel"
        ]
        .map(
            ORDER_CAMPAIGN_CHANNEL_WEIGHTS
        )
        .fillna(
            1.0
        )
        .to_numpy(
            dtype=float
        )
    )

    weights = normalise_weights(
        weights
    )

    return str(
        rng.choice(
            eligible[
                "campaign_id"
            ].to_numpy(),
            p=weights,
        )
    )


def generate_orders(
    customers: pd.DataFrame,
    locations: pd.DataFrame,
    campaigns: pd.DataFrame,
    seed: int,
) -> pd.DataFrame:
    """Generate order histories for all customers."""

    # Separate RNG streams keep previously validated
    # behavioural layers stable as new order-level
    # attributes are introduced.
    lifecycle_rng = (
        np.random.default_rng(
            seed
        )
    )

    channel_rng = (
        np.random.default_rng(
            seed + 1
        )
    )

    geography_rng = (
        np.random.default_rng(
            seed + 2
        )
    )

    status_rng = (
        np.random.default_rng(
            seed + 3
        )
    )

    promotion_rng = (
        np.random.default_rng(
            seed + 4
        )
    )

    campaign_rng = (
        np.random.default_rng(
            seed + 5
        )
    )

    locations_by_id = (
        locations.set_index(
            "location_id"
        )
    )

    records: list[
        dict[str, object]
    ] = []

    order_number = 1

    for (
        _,
        customer,
    ) in customers.iterrows():

        order_timestamps = (
            generate_customer_orders(
                customer=customer,
                rng=lifecycle_rng,
            )
        )

        for (
            order_index,
            order_timestamp,
        ) in enumerate(
            order_timestamps
        ):
            is_first_order = (
                order_index
                == 0
            )

            device = (
                sample_order_device(
                    customer=customer,
                    rng=channel_rng,
                )
            )

            sales_channel = (
                sample_sales_channel(
                    customer=customer,
                    device=device,
                    rng=channel_rng,
                )
            )

            shipping_location_id = (
                sample_shipping_location_id(
                    customer=customer,
                    locations=locations,
                    rng=geography_rng,
                )
            )

            currency = (
                currency_for_location(
                    shipping_location_id=(
                        shipping_location_id
                    ),
                    locations_by_id=(
                        locations_by_id
                    ),
                )
            )

            order_status = (
                sample_order_status(
                    rng=status_rng,
                )
            )

            promotion_code = (
                sample_promotion_code(
                    order_status=(
                        order_status
                    ),
                    is_first_order=(
                        is_first_order
                    ),
                    rng=promotion_rng,
                )
            )

            campaign_id = (
                sample_campaign_id(
                    customer=customer,
                    order_timestamp=(
                        order_timestamp
                    ),
                    is_first_order=(
                        is_first_order
                    ),
                    campaigns=campaigns,
                    rng=campaign_rng,
                )
            )

            records.append(
                {
                    "order_id": (
                        f"ORD{order_number:07d}"
                    ),
                    "customer_id": (
                        customer[
                            "customer_id"
                        ]
                    ),
                    "order_timestamp": (
                        order_timestamp
                    ),
                    "sales_channel": (
                        sales_channel
                    ),
                    "device": (
                        device
                    ),
                    "currency": (
                        currency
                    ),
                    "shipping_location_id": (
                        shipping_location_id
                    ),
                    "order_status": (
                        order_status
                    ),
                    "promotion_code": (
                        promotion_code
                    ),
                    "campaign_id": (
                        campaign_id
                    ),
                }
            )

            order_number += 1

    return pd.DataFrame(
        records,
        columns=[
            "order_id",
            "customer_id",
            "order_timestamp",
            "sales_channel",
            "device",
            "currency",
            "shipping_location_id",
            "order_status",
            "promotion_code",
            "campaign_id",
        ],
    )


def validate_orders(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    locations: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> None:
    """Run technical validation on generated orders."""

    if (
        orders[
            "order_id"
        ]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Duplicate order IDs detected."
        )

    valid_customer_ids = set(
        customers[
            "customer_id"
        ]
    )

    unknown_customers = (
        ~orders[
            "customer_id"
        ].isin(
            valid_customer_ids
        )
    )

    if unknown_customers.any():
        raise ValueError(
            "Orders reference "
            "unknown customers."
        )

    validation = orders.merge(
        customers[
            [
                "customer_id",
                "signup_date",
                "customer_persona",
                "marketing_consent",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    before_signup = (
        validation[
            "order_timestamp"
        ]
        < validation[
            "signup_date"
        ]
    )

    if before_signup.any():
        raise ValueError(
            "Orders detected before "
            "customer signup."
        )

    after_simulation = (
        validation[
            "order_timestamp"
        ]
        > SIMULATION_END_DATE
    )

    if after_simulation.any():
        raise ValueError(
            "Orders detected after "
            "simulation end."
        )

    valid_platforms = {
        "Website",
        "iOS",
        "Android",
    }

    invalid_platforms = (
        ~orders[
            "sales_channel"
        ].isin(
            valid_platforms
        )
    )

    if invalid_platforms.any():
        raise ValueError(
            "Invalid sales channels detected."
        )

    valid_devices = {
        "Desktop",
        "Mobile",
        "Tablet",
    }

    invalid_devices = (
        ~orders[
            "device"
        ].isin(
            valid_devices
        )
    )

    if invalid_devices.any():
        raise ValueError(
            "Invalid order devices detected."
        )

    invalid_desktop_platform = (
        (
            orders[
                "device"
            ]
            == "Desktop"
        )
        & (
            orders[
                "sales_channel"
            ]
            != "Website"
        )
    )

    if (
        invalid_desktop_platform
        .any()
    ):
        raise ValueError(
            "Desktop orders must "
            "use Website."
        )

    valid_location_ids = set(
        locations[
            "location_id"
        ]
    )

    invalid_shipping_locations = (
        ~orders[
            "shipping_location_id"
        ].isin(
            valid_location_ids
        )
    )

    if (
        invalid_shipping_locations
        .any()
    ):
        raise ValueError(
            "Orders reference unknown "
            "shipping locations."
        )

    location_country = (
        locations[
            [
                "location_id",
                "country",
            ]
        ]
        .rename(
            columns={
                "location_id":
                    "shipping_location_id",
            }
        )
    )

    currency_validation = (
        orders[
            [
                "order_id",
                "shipping_location_id",
                "currency",
            ]
        ]
        .merge(
            location_country,
            on="shipping_location_id",
            how="left",
            validate="many_to_one",
        )
    )

    currency_validation[
        "expected_currency"
    ] = (
        currency_validation[
            "country"
        ].map(
            CURRENCY_BY_COUNTRY
        )
    )

    invalid_currency = (
        currency_validation[
            "expected_currency"
        ].isna()
        | (
            currency_validation[
                "currency"
            ]
            != currency_validation[
                "expected_currency"
            ]
        )
    )

    if invalid_currency.any():
        raise ValueError(
            "Currency does not match "
            "shipping location."
        )

    valid_order_statuses = set(
        ORDER_STATUS_WEIGHTS.keys()
    )

    invalid_statuses = (
        ~orders[
            "order_status"
        ].isin(
            valid_order_statuses
        )
    )

    if invalid_statuses.any():
        raise ValueError(
            "Invalid order statuses detected."
        )

    if (
        orders[
            "order_status"
        ]
        .isna()
        .any()
    ):
        raise ValueError(
            "Missing order statuses detected."
        )

    valid_promotion_codes = {
        promotion_code
        for promotion_code
        in PROMOTION_CODE_WEIGHTS.keys()
        if promotion_code
        is not None
    }

    invalid_promotions = (
        orders[
            "promotion_code"
        ].notna()
        & ~orders[
            "promotion_code"
        ].isin(
            valid_promotion_codes
        )
    )

    if invalid_promotions.any():
        raise ValueError(
            "Invalid promotion codes detected."
        )

    cancelled_with_promotion = (
        (
            orders[
                "order_status"
            ]
            == "Cancelled"
        )
        & orders[
            "promotion_code"
        ].notna()
    )

    if (
        cancelled_with_promotion
        .any()
    ):
        raise ValueError(
            "Cancelled orders must not "
            "have promotion codes."
        )

    ranked_orders = (
        orders.sort_values(
            [
                "customer_id",
                "order_timestamp",
                "order_id",
            ]
        )
        .copy()
    )

    ranked_orders[
        "order_number"
    ] = (
        ranked_orders.groupby(
            "customer_id"
        ).cumcount()
        + 1
    )

    invalid_welcome_orders = (
        (
            ranked_orders[
                "promotion_code"
            ]
            == "WELCOME10"
        )
        & (
            ranked_orders[
                "order_number"
            ]
            != 1
        )
    )

    if (
        invalid_welcome_orders
        .any()
    ):
        raise ValueError(
            "WELCOME10 detected on "
            "non-first orders."
        )

    # ------------------------------------------------------------------
    # Campaign validation
    # ------------------------------------------------------------------

    valid_campaign_ids = set(
        campaigns[
            "campaign_id"
        ]
    )

    invalid_campaign_ids = (
        orders[
            "campaign_id"
        ].notna()
        & ~orders[
            "campaign_id"
        ].isin(
            valid_campaign_ids
        )
    )

    if invalid_campaign_ids.any():
        raise ValueError(
            "Orders reference unknown "
            "campaign IDs."
        )

    attributed_orders = (
        validation[
            validation[
                "campaign_id"
            ].notna()
        ]
        .copy()
    )

    if not attributed_orders.empty:

        campaign_details = (
            campaigns[
                [
                    "campaign_id",
                    "channel",
                    "start_date",
                    "end_date",
                    "target_segment",
                ]
            ]
            .rename(
                columns={
                    "channel":
                        "campaign_channel",
                    "target_segment":
                        "campaign_target_segment",
                }
            )
        )

        attributed_orders = (
            attributed_orders.merge(
                campaign_details,
                on="campaign_id",
                how="left",
                validate="many_to_one",
            )
        )

        attributed_orders[
            "order_date"
        ] = (
            attributed_orders[
                "order_timestamp"
            ].dt.normalize()
        )

        attributed_orders[
            "campaign_start_date"
        ] = (
            attributed_orders[
                "start_date"
            ].dt.normalize()
        )

        attributed_orders[
            "campaign_end_date"
        ] = (
            attributed_orders[
                "end_date"
            ].dt.normalize()
        )

        outside_campaign_window = (
            (
                attributed_orders[
                    "order_date"
                ]
                < attributed_orders[
                    "campaign_start_date"
                ]
            )
            | (
                attributed_orders[
                    "order_date"
                ]
                > attributed_orders[
                    "campaign_end_date"
                ]
            )
        )

        if (
            outside_campaign_window
            .any()
        ):
            raise ValueError(
                "Attributed orders detected "
                "outside campaign windows."
            )

        target_segment_mismatch = (
            attributed_orders[
                "customer_persona"
            ]
            != attributed_orders[
                "campaign_target_segment"
            ]
        )

        if (
            target_segment_mismatch
            .any()
        ):
            raise ValueError(
                "Campaign target-segment "
                "mismatch detected."
            )

        email_without_consent = (
            (
                attributed_orders[
                    "campaign_channel"
                ]
                == "Email"
            )
            & (
                ~attributed_orders[
                    "marketing_consent"
                ].astype(bool)
            )
        )

        if (
            email_without_consent
            .any()
        ):
            raise ValueError(
                "Email campaign attribution "
                "detected without marketing consent."
            )


def campaign_attribution_summary(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise overall campaign attribution."""

    linked = (
        orders[
            "campaign_id"
        ].notna()
    )

    summary = pd.DataFrame(
        {
            "campaign_linked": [
                False,
                True,
            ],
            "orders": [
                int(
                    (~linked).sum()
                ),
                int(
                    linked.sum()
                ),
            ],
        }
    )

    summary[
        "share_pct"
    ] = (
        summary[
            "orders"
        ]
        / len(orders)
        * 100
    ).round(1)

    return summary


def campaign_attribution_by_year(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaign attribution by year."""

    result = orders.copy()

    result[
        "order_year"
    ] = (
        result[
            "order_timestamp"
        ].dt.year
    )

    result[
        "campaign_linked"
    ] = (
        result[
            "campaign_id"
        ].notna()
    )

    summary = (
        result.groupby(
            "order_year"
        )
        .agg(
            orders=(
                "order_id",
                "count",
            ),
            linked_orders=(
                "campaign_linked",
                "sum",
            ),
        )
        .reset_index()
    )

    summary[
        "campaign_attribution_pct"
    ] = (
        summary[
            "linked_orders"
        ]
        / summary[
            "orders"
        ]
        * 100
    ).round(1)

    return summary


def campaign_attribution_by_channel(
    orders: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise attributed orders by campaign channel."""

    attributed = orders[
        orders[
            "campaign_id"
        ].notna()
    ].copy()

    if attributed.empty:
        return pd.DataFrame(
            columns=[
                "channel",
                "orders",
                "share_pct",
            ]
        )

    attributed = attributed.merge(
        campaigns[
            [
                "campaign_id",
                "channel",
            ]
        ],
        on="campaign_id",
        how="left",
        validate="many_to_one",
    )

    summary = (
        attributed[
            "channel"
        ]
        .value_counts()
        .rename_axis(
            "channel"
        )
        .reset_index(
            name="orders"
        )
    )

    summary[
        "share_pct"
    ] = (
        summary[
            "orders"
        ]
        / len(attributed)
        * 100
    ).round(1)

    return summary


def campaign_attribution_by_order_type(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise campaign attribution for first vs repeat orders."""

    ranked = (
        orders.sort_values(
            [
                "customer_id",
                "order_timestamp",
                "order_id",
            ]
        )
        .copy()
    )

    ranked[
        "order_number"
    ] = (
        ranked.groupby(
            "customer_id"
        ).cumcount()
        + 1
    )

    ranked[
        "order_type"
    ] = np.where(
        ranked[
            "order_number"
        ]
        == 1,
        "First order",
        "Repeat order",
    )

    ranked[
        "campaign_linked"
    ] = (
        ranked[
            "campaign_id"
        ].notna()
    )

    summary = (
        ranked.groupby(
            "order_type"
        )
        .agg(
            orders=(
                "order_id",
                "count",
            ),
            linked_orders=(
                "campaign_linked",
                "sum",
            ),
        )
        .reset_index()
    )

    summary[
        "campaign_attribution_pct"
    ] = (
        summary[
            "linked_orders"
        ]
        / summary[
            "orders"
        ]
        * 100
    ).round(1)

    return summary


def acquisition_campaign_persistence_summary(
    orders: pd.DataFrame,
    acquisition: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise acquisition campaign persistence into first orders."""

    ranked = (
        orders.sort_values(
            [
                "customer_id",
                "order_timestamp",
                "order_id",
            ]
        )
        .copy()
    )

    ranked[
        "order_number"
    ] = (
        ranked.groupby(
            "customer_id"
        ).cumcount()
        + 1
    )

    first_orders = ranked[
        ranked[
            "order_number"
        ]
        == 1
    ].copy()

    acquisition_campaigns = (
        acquisition[
            [
                "customer_id",
                "campaign_id",
            ]
        ]
        .rename(
            columns={
                "campaign_id":
                    "acquisition_campaign_id",
            }
        )
    )

    first_orders = (
        first_orders.merge(
            acquisition_campaigns,
            on="customer_id",
            how="left",
            validate="one_to_one",
        )
    )

    with_acquisition_campaign = (
        first_orders[
            first_orders[
                "acquisition_campaign_id"
            ].notna()
        ]
        .copy()
    )

    if (
        with_acquisition_campaign.empty
    ):
        return pd.DataFrame(
            {
                "metric": [
                    "First-order customers "
                    "with acquisition campaign",
                    "Same acquisition campaign "
                    "on first order",
                ],
                "value": [
                    0,
                    0,
                ],
            }
        )

    same_campaign = (
        with_acquisition_campaign[
            "campaign_id"
        ]
        == with_acquisition_campaign[
            "acquisition_campaign_id"
        ]
    )

    return pd.DataFrame(
        {
            "metric": [
                "First-order customers "
                "with acquisition campaign",
                "Same acquisition campaign "
                "on first order",
                "Persistence share pct",
            ],
            "value": [
                len(
                    with_acquisition_campaign
                ),
                int(
                    same_campaign.sum()
                ),
                round(
                    same_campaign.mean()
                    * 100,
                    1,
                ),
            ],
        }
    )


def main() -> None:
    """Generate and save Terra Active orders."""

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    customers_path = (
        project_root
        / "data"
        / "raw"
        / "customers.csv"
    )

    acquisition_path = (
        project_root
        / "data"
        / "raw"
        / "customer_acquisition.csv"
    )

    locations_path = (
        project_root
        / "data"
        / "raw"
        / "locations.csv"
    )

    campaigns_path = (
        project_root
        / "data"
        / "raw"
        / "campaigns.csv"
    )

    output_path = (
        project_root
        / "data"
        / "raw"
        / "orders.csv"
    )

    customers = load_customers(
        customers_path
    )

    acquisition = (
        load_customer_acquisition(
            acquisition_path
        )
    )

    locations = load_locations(
        locations_path
    )

    campaigns = load_campaigns(
        campaigns_path
    )

    customers = prepare_customers(
        customers=customers,
        acquisition=acquisition,
        locations=locations,
    )

    orders = generate_orders(
        customers=customers,
        locations=locations,
        campaigns=campaigns,
        seed=42,
    )

    validate_orders(
        orders=orders,
        customers=customers,
        locations=locations,
        campaigns=campaigns,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    orders.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Generated {len(orders):,} "
        f"orders for "
        f"{orders['customer_id'].nunique():,} "
        f"customers."
    )

    print(
        "\nOrder status distribution:"
    )

    status_summary = (
        orders[
            "order_status"
        ]
        .value_counts()
        .rename_axis(
            "order_status"
        )
        .reset_index(
            name="orders"
        )
    )

    status_summary[
        "share_pct"
    ] = (
        status_summary[
            "orders"
        ]
        / len(orders)
        * 100
    ).round(1)

    print(
        status_summary.to_string(
            index=False
        )
    )

    print(
        "\nOverall promotion code distribution:"
    )

    promotion_summary = (
        orders[
            "promotion_code"
        ]
        .fillna(
            "No promotion"
        )
        .value_counts()
        .rename_axis(
            "promotion_code"
        )
        .reset_index(
            name="orders"
        )
    )

    promotion_summary[
        "share_pct"
    ] = (
        promotion_summary[
            "orders"
        ]
        / len(orders)
        * 100
    ).round(1)

    print(
        promotion_summary.to_string(
            index=False
        )
    )

    ranked_orders = (
        orders.sort_values(
            [
                "customer_id",
                "order_timestamp",
                "order_id",
            ]
        )
        .copy()
    )

    ranked_orders[
        "order_number"
    ] = (
        ranked_orders.groupby(
            "customer_id"
        ).cumcount()
        + 1
    )

    first_orders = (
        ranked_orders[
            ranked_orders[
                "order_number"
            ]
            == 1
        ]
    )

    repeat_orders = (
        ranked_orders[
            ranked_orders[
                "order_number"
            ]
            > 1
        ]
    )

    non_cancelled_first_orders = (
        first_orders[
            first_orders[
                "order_status"
            ]
            != "Cancelled"
        ]
    )

    non_cancelled_repeat_orders = (
        repeat_orders[
            repeat_orders[
                "order_status"
            ]
            != "Cancelled"
        ]
    )

    print(
        "\nPromotion code distribution "
        "among non-cancelled first orders:"
    )

    first_promotion_summary = (
        non_cancelled_first_orders[
            "promotion_code"
        ]
        .fillna(
            "No promotion"
        )
        .value_counts()
        .rename_axis(
            "promotion_code"
        )
        .reset_index(
            name="orders"
        )
    )

    first_promotion_summary[
        "share_pct"
    ] = (
        first_promotion_summary[
            "orders"
        ]
        / len(
            non_cancelled_first_orders
        )
        * 100
    ).round(1)

    print(
        first_promotion_summary.to_string(
            index=False
        )
    )

    print(
        "\nPromotion code distribution "
        "among non-cancelled repeat orders:"
    )

    repeat_promotion_summary = (
        non_cancelled_repeat_orders[
            "promotion_code"
        ]
        .fillna(
            "No promotion"
        )
        .value_counts()
        .rename_axis(
            "promotion_code"
        )
        .reset_index(
            name="orders"
        )
    )

    repeat_promotion_summary[
        "share_pct"
    ] = (
        repeat_promotion_summary[
            "orders"
        ]
        / len(
            non_cancelled_repeat_orders
        )
        * 100
    ).round(1)

    print(
        repeat_promotion_summary.to_string(
            index=False
        )
    )

    welcome_on_repeat_orders = (
        (
            repeat_orders[
                "promotion_code"
            ]
            == "WELCOME10"
        )
        .sum()
    )

    cancelled_with_promotion = (
        (
            orders[
                "order_status"
            ]
            == "Cancelled"
        )
        & orders[
            "promotion_code"
        ].notna()
    ).sum()

    print(
        "\nPromotion rule checks:"
    )

    print(
        "WELCOME10 on repeat orders: "
        f"{welcome_on_repeat_orders:,}"
    )

    print(
        "Cancelled orders with promotion: "
        f"{cancelled_with_promotion:,}"
    )

    print(
        "\nOverall campaign attribution:"
    )

    print(
        campaign_attribution_summary(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nCampaign attribution by year:"
    )

    print(
        campaign_attribution_by_year(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nCampaign attribution by channel:"
    )

    print(
        campaign_attribution_by_channel(
            orders=orders,
            campaigns=campaigns,
        ).to_string(
            index=False
        )
    )

    print(
        "\nCampaign attribution by order type:"
    )

    print(
        campaign_attribution_by_order_type(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nAcquisition campaign "
        "to first-order persistence:"
    )

    print(
        acquisition_campaign_persistence_summary(
            orders=orders,
            acquisition=acquisition,
        ).to_string(
            index=False
        )
    )

    print(
        f"\nSaved orders to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()