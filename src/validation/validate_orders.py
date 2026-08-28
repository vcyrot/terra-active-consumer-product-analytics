"""Analytical validation for Terra Active customer order histories."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_data(
    orders_path: Path,
    customers_path: Path,
    acquisition_path: Path,
    locations_path: Path,
    campaigns_path: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Load generated orders and supporting datasets."""

    if not orders_path.exists():
        raise FileNotFoundError(
            f"Orders dataset not found: {orders_path}"
        )

    if not customers_path.exists():
        raise FileNotFoundError(
            f"Customers dataset not found: {customers_path}"
        )

    if not acquisition_path.exists():
        raise FileNotFoundError(
            f"Customer acquisition dataset not found: "
            f"{acquisition_path}"
        )

    if not locations_path.exists():
        raise FileNotFoundError(
            f"Locations dataset not found: {locations_path}"
        )
        
    if not campaigns_path.exists():
        raise FileNotFoundError(
            f"Campaign dataset not found: "
            f"{campaigns_path}"
        )

    orders = pd.read_csv(
        orders_path,
        parse_dates=["order_timestamp"],
    )

    customers = pd.read_csv(
        customers_path,
        parse_dates=["signup_date"],
    )

    acquisition = pd.read_csv(
        acquisition_path,
        parse_dates=["acquisition_date"],
    )

    locations = pd.read_csv(
        locations_path
    )
    
    campaigns = pd.read_csv(
        campaigns_path,
        parse_dates=[
            "start_date",
            "end_date",
        ],
    )

    return (
        orders,
        customers,
        acquisition,
        locations,
        campaigns,
    )


def customer_order_summary(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Create customer-level order metrics."""

    order_summary = (
        orders.groupby("customer_id")
        .agg(
            order_count=("order_id", "count"),
            first_order_timestamp=(
                "order_timestamp",
                "min",
            ),
            last_order_timestamp=(
                "order_timestamp",
                "max",
            ),
        )
        .reset_index()
    )

    result = customers[
        [
            "customer_id",
            "customer_persona",
            "signup_date",
        ]
    ].merge(
        order_summary,
        on="customer_id",
        how="left",
        validate="one_to_one",
    )

    result["order_count"] = (
        result["order_count"]
        .fillna(0)
        .astype(int)
    )

    result["purchaser"] = (
        result["order_count"] > 0
    )

    result["repeat_customer"] = (
        result["order_count"] > 1
    )

    result["days_to_first_purchase"] = (
        result["first_order_timestamp"]
        - result["signup_date"]
    ).dt.days

    return result


def purchaser_summary(
    customer_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise purchasers vs non-purchasers."""

    summary = (
        customer_summary["purchaser"]
        .value_counts()
        .rename_axis("purchaser")
        .reset_index(
            name="customer_count"
        )
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(customer_summary)
        * 100
    ).round(1)

    return summary


def customer_type_summary(
    customer_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Group customers by total order frequency."""

    result = customer_summary.copy()

    result["customer_type"] = pd.cut(
        result["order_count"],
        bins=[
            -1,
            0,
            1,
            2,
            4,
            float("inf"),
        ],
        labels=[
            "Non-purchaser",
            "One-time",
            "2 orders",
            "3-4 orders",
            "5+ orders",
        ],
    )

    summary = (
        result["customer_type"]
        .value_counts(sort=False)
        .rename_axis("customer_type")
        .reset_index(
            name="customer_count"
        )
    )

    summary["population_share_pct"] = (
        summary["customer_count"]
        / len(result)
        * 100
    ).round(1)

    return summary


def orders_per_purchaser_summary(
    customer_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise order frequency among purchasers."""

    purchasers = customer_summary[
        customer_summary["purchaser"]
    ]

    return pd.DataFrame(
        {
            "metric": [
                "Purchasing customers",
                "Average orders",
                "Median orders",
                "Maximum orders",
            ],
            "value": [
                len(purchasers),
                round(
                    purchasers[
                        "order_count"
                    ].mean(),
                    2,
                ),
                round(
                    purchasers[
                        "order_count"
                    ].median(),
                    2,
                ),
                purchasers[
                    "order_count"
                ].max(),
            ],
        }
    )


def purchase_behaviour_by_persona(
    customer_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise purchase behaviour by persona."""

    summary = (
        customer_summary.groupby(
            "customer_persona"
        )
        .agg(
            customers=(
                "customer_id",
                "count",
            ),
            purchasers=(
                "purchaser",
                "sum",
            ),
            repeat_customers=(
                "repeat_customer",
                "sum",
            ),
            avg_orders_per_customer=(
                "order_count",
                "mean",
            ),
        )
        .reset_index()
    )

    summary["purchase_rate_pct"] = (
        summary["purchasers"]
        / summary["customers"]
        * 100
    ).round(1)

    summary[
        "repeat_rate_among_purchasers_pct"
    ] = (
        summary["repeat_customers"]
        / summary["purchasers"]
        * 100
    ).round(1)

    summary[
        "avg_orders_per_customer"
    ] = (
        summary[
            "avg_orders_per_customer"
        ].round(2)
    )

    return summary[
        [
            "customer_persona",
            "customers",
            "purchasers",
            "purchase_rate_pct",
            "repeat_customers",
            "repeat_rate_among_purchasers_pct",
            "avg_orders_per_customer",
        ]
    ]


def first_purchase_delay_summary(
    customer_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise time from signup to first purchase."""

    purchasers = customer_summary[
        customer_summary["purchaser"]
    ]

    delay = purchasers[
        "days_to_first_purchase"
    ]

    return pd.DataFrame(
        {
            "metric": [
                "Average days",
                "Median days",
                "25th percentile",
                "75th percentile",
                "90th percentile",
                "Maximum days",
            ],
            "value": [
                round(
                    delay.mean(),
                    1,
                ),
                round(
                    delay.median(),
                    1,
                ),
                round(
                    delay.quantile(0.25),
                    1,
                ),
                round(
                    delay.quantile(0.75),
                    1,
                ),
                round(
                    delay.quantile(0.90),
                    1,
                ),
                int(
                    delay.max()
                ),
            ],
        }
    )


def first_purchase_delay_buckets(
    customer_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Group first purchases into timing buckets."""

    purchasers = customer_summary[
        customer_summary["purchaser"]
    ].copy()

    purchasers[
        "delay_bucket"
    ] = pd.cut(
        purchasers[
            "days_to_first_purchase"
        ],
        bins=[
            -1,
            7,
            30,
            90,
            180,
            float("inf"),
        ],
        labels=[
            "0-7 days",
            "8-30 days",
            "31-90 days",
            "91-180 days",
            "181+ days",
        ],
    )

    summary = (
        purchasers[
            "delay_bucket"
        ]
        .value_counts(
            sort=False
        )
        .rename_axis(
            "delay_bucket"
        )
        .reset_index(
            name="customers"
        )
    )

    summary["share_pct"] = (
        summary["customers"]
        / len(purchasers)
        * 100
    ).round(1)

    return summary


def second_purchase_summary(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise time from first to second purchase."""

    ranked = orders.sort_values(
        [
            "customer_id",
            "order_timestamp",
            "order_id",
        ]
    ).copy()

    ranked["order_number"] = (
        ranked.groupby(
            "customer_id"
        ).cumcount()
        + 1
    )

    first_orders = ranked[
        ranked["order_number"] == 1
    ][
        [
            "customer_id",
            "order_timestamp",
        ]
    ].rename(
        columns={
            "order_timestamp":
                "first_order_timestamp"
        }
    )

    second_orders = ranked[
        ranked["order_number"] == 2
    ][
        [
            "customer_id",
            "order_timestamp",
        ]
    ].rename(
        columns={
            "order_timestamp":
                "second_order_timestamp"
        }
    )

    repeat = first_orders.merge(
        second_orders,
        on="customer_id",
        how="inner",
        validate="one_to_one",
    )

    repeat[
        "days_to_second_purchase"
    ] = (
        repeat[
            "second_order_timestamp"
        ]
        - repeat[
            "first_order_timestamp"
        ]
    ).dt.days

    delay = repeat[
        "days_to_second_purchase"
    ]

    return pd.DataFrame(
        {
            "metric": [
                "Repeat customers",
                "Average days",
                "Median days",
                "25th percentile",
                "75th percentile",
                "90th percentile",
            ],
            "value": [
                len(repeat),
                round(
                    delay.mean(),
                    1,
                ),
                round(
                    delay.median(),
                    1,
                ),
                round(
                    delay.quantile(0.25),
                    1,
                ),
                round(
                    delay.quantile(0.75),
                    1,
                ),
                round(
                    delay.quantile(0.90),
                    1,
                ),
            ],
        }
    )


def orders_by_year(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise orders by year."""

    result = orders.copy()

    result["order_year"] = (
        result[
            "order_timestamp"
        ].dt.year
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
            purchasing_customers=(
                "customer_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    summary["order_share_pct"] = (
        summary["orders"]
        / len(result)
        * 100
    ).round(1)

    return summary


def orders_by_month(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise orders by calendar month."""

    result = orders.copy()

    result["month"] = (
        result[
            "order_timestamp"
        ].dt.month
    )

    summary = (
        result.groupby(
            "month"
        )
        .agg(
            orders=(
                "order_id",
                "count",
            )
        )
        .reset_index()
    )

    summary["order_share_pct"] = (
        summary["orders"]
        / len(result)
        * 100
    ).round(1)

    return summary


def signup_cohort_summary(
    customer_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise behaviour by signup cohort."""

    result = customer_summary.copy()

    result["signup_year"] = (
        result[
            "signup_date"
        ].dt.year
    )

    summary = (
        result.groupby(
            "signup_year"
        )
        .agg(
            customers=(
                "customer_id",
                "count",
            ),
            purchasers=(
                "purchaser",
                "sum",
            ),
            repeat_customers=(
                "repeat_customer",
                "sum",
            ),
            avg_orders_per_customer=(
                "order_count",
                "mean",
            ),
        )
        .reset_index()
    )

    summary["purchase_rate_pct"] = (
        summary["purchasers"]
        / summary["customers"]
        * 100
    ).round(1)

    summary[
        "repeat_rate_among_purchasers_pct"
    ] = (
        summary["repeat_customers"]
        / summary["purchasers"]
        * 100
    ).round(1)

    summary[
        "avg_orders_per_customer"
    ] = (
        summary[
            "avg_orders_per_customer"
        ].round(2)
    )

    return summary


def device_distribution(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise order device distribution."""

    summary = (
        orders["device"]
        .value_counts()
        .rename_axis("device")
        .reset_index(
            name="orders"
        )
    )

    summary["share_pct"] = (
        summary["orders"]
        / len(orders)
        * 100
    ).round(1)

    return summary


def sales_channel_distribution(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise sales-channel distribution."""

    summary = (
        orders[
            "sales_channel"
        ]
        .value_counts()
        .rename_axis(
            "sales_channel"
        )
        .reset_index(
            name="orders"
        )
    )

    summary["share_pct"] = (
        summary["orders"]
        / len(orders)
        * 100
    ).round(1)

    return summary


def device_channel_distribution(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise device and sales-channel combinations."""

    summary = (
        orders.groupby(
            [
                "device",
                "sales_channel",
            ]
        )
        .size()
        .reset_index(
            name="orders"
        )
    )

    summary["share_pct"] = (
        summary["orders"]
        / len(orders)
        * 100
    ).round(1)

    return summary.sort_values(
        "orders",
        ascending=False,
    )


def acquisition_order_persistence(
    orders: pd.DataFrame,
    acquisition: pd.DataFrame,
) -> pd.DataFrame:
    """Compare acquisition device/platform with order behaviour."""

    comparison = orders.merge(
        acquisition[
            [
                "customer_id",
                "acquisition_device",
                "acquisition_platform",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    comparison["same_device"] = (
        comparison["device"]
        == comparison[
            "acquisition_device"
        ]
    )

    comparison["same_platform"] = (
        comparison[
            "sales_channel"
        ]
        == comparison[
            "acquisition_platform"
        ]
    )

    return pd.DataFrame(
        {
            "metric": [
                "Same acquisition device",
                "Same acquisition platform",
            ],
            "share_pct": [
                round(
                    comparison[
                        "same_device"
                    ].mean()
                    * 100,
                    1,
                ),
                round(
                    comparison[
                        "same_platform"
                    ].mean()
                    * 100,
                    1,
                ),
            ],
        }
    )


def acquisition_device_transition(
    orders: pd.DataFrame,
    acquisition: pd.DataFrame,
) -> pd.DataFrame:
    """Show acquisition-device to order-device transitions."""

    comparison = orders.merge(
        acquisition[
            [
                "customer_id",
                "acquisition_device",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    summary = (
        comparison.groupby(
            [
                "acquisition_device",
                "device",
            ]
        )
        .size()
        .reset_index(
            name="orders"
        )
    )

    totals = (
        summary.groupby(
            "acquisition_device"
        )["orders"]
        .transform("sum")
    )

    summary[
        "share_within_acquisition_device_pct"
    ] = (
        summary["orders"]
        / totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "acquisition_device",
            "orders",
        ],
        ascending=[
            True,
            False,
        ],
    )


def acquisition_platform_transition(
    orders: pd.DataFrame,
    acquisition: pd.DataFrame,
) -> pd.DataFrame:
    """Show acquisition-platform to sales-channel transitions."""

    comparison = orders.merge(
        acquisition[
            [
                "customer_id",
                "acquisition_platform",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    summary = (
        comparison.groupby(
            [
                "acquisition_platform",
                "sales_channel",
            ]
        )
        .size()
        .reset_index(
            name="orders"
        )
    )

    totals = (
        summary.groupby(
            "acquisition_platform"
        )["orders"]
        .transform("sum")
    )

    summary[
        "share_within_acquisition_platform_pct"
    ] = (
        summary["orders"]
        / totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "acquisition_platform",
            "orders",
        ],
        ascending=[
            True,
            False,
        ],
    )


def prepare_order_geography(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    locations: pd.DataFrame,
) -> pd.DataFrame:
    """Attach home and shipping geography to orders."""

    home_locations = (
        locations[
            [
                "location_id",
                "city",
                "country",
            ]
        ]
        .rename(
            columns={
                "location_id":
                    "home_location_id",
                "city":
                    "home_city",
                "country":
                    "home_country",
            }
        )
    )

    shipping_locations = (
        locations[
            [
                "location_id",
                "city",
                "country",
            ]
        ]
        .rename(
            columns={
                "location_id":
                    "shipping_location_id",
                "city":
                    "shipping_city",
                "country":
                    "shipping_country",
            }
        )
    )

    result = orders.merge(
        customers[
            [
                "customer_id",
                "location_id",
            ]
        ].rename(
            columns={
                "location_id":
                    "home_location_id"
            }
        ),
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    result = result.merge(
        home_locations,
        on="home_location_id",
        how="left",
        validate="many_to_one",
    )

    result = result.merge(
        shipping_locations,
        on="shipping_location_id",
        how="left",
        validate="many_to_one",
    )

    result["same_home_location"] = (
        result[
            "home_location_id"
        ]
        == result[
            "shipping_location_id"
        ]
    )

    result["same_country"] = (
        result[
            "home_country"
        ]
        == result[
            "shipping_country"
        ]
    )

    return result


def shipping_location_summary(
    order_geography: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise home vs alternative shipping locations."""

    home_orders = (
        order_geography[
            "same_home_location"
        ].sum()
    )

    alternative_orders = (
        (
            ~order_geography[
                "same_home_location"
            ]
        ).sum()
    )

    total = len(
        order_geography
    )

    return pd.DataFrame(
        {
            "shipping_type": [
                "Home location",
                "Alternative location",
            ],
            "orders": [
                home_orders,
                alternative_orders,
            ],
            "share_pct": [
                round(
                    home_orders
                    / total
                    * 100,
                    1,
                ),
                round(
                    alternative_orders
                    / total
                    * 100,
                    1,
                ),
            ],
        }
    )


def shipping_country_consistency(
    order_geography: pd.DataFrame,
) -> pd.DataFrame:
    """Check whether orders remain within home country."""

    summary = (
        order_geography[
            "same_country"
        ]
        .value_counts()
        .rename_axis(
            "same_country"
        )
        .reset_index(
            name="orders"
        )
    )

    summary["share_pct"] = (
        summary["orders"]
        / len(order_geography)
        * 100
    ).round(1)

    return summary


def orders_by_shipping_location(
    order_geography: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise orders by shipping location."""

    summary = (
        order_geography.groupby(
            [
                "shipping_location_id",
                "shipping_city",
                "shipping_country",
            ]
        )
        .agg(
            orders=(
                "order_id",
                "count",
            ),
            customers=(
                "customer_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    summary["order_share_pct"] = (
        summary["orders"]
        / len(order_geography)
        * 100
    ).round(1)

    return summary.sort_values(
        "orders",
        ascending=False,
    )


def currency_distribution(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise transaction currencies."""

    summary = (
        orders["currency"]
        .value_counts()
        .rename_axis(
            "currency"
        )
        .reset_index(
            name="orders"
        )
    )

    summary["share_pct"] = (
        summary["orders"]
        / len(orders)
        * 100
    ).round(1)

    return summary


def currency_consistency(
    orders: pd.DataFrame,
    locations: pd.DataFrame,
) -> pd.DataFrame:
    """Check whether currency matches shipping country."""

    currency_by_country = {
        "United Kingdom": "GBP",
        "France": "EUR",
        "Germany": "EUR",
        "Spain": "EUR",
        "Netherlands": "EUR",
        "Italy": "EUR",
        "Switzerland": "CHF",
    }

    shipping_locations = (
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
                "country":
                    "shipping_country",
            }
        )
    )

    result = orders.merge(
        shipping_locations,
        on="shipping_location_id",
        how="left",
        validate="many_to_one",
    )

    result[
        "expected_currency"
    ] = (
        result[
            "shipping_country"
        ].map(
            currency_by_country
        )
    )

    result[
        "currency_match"
    ] = (
        result["currency"]
        == result[
            "expected_currency"
        ]
    )

    summary = (
        result[
            "currency_match"
        ]
        .value_counts()
        .rename_axis(
            "currency_match"
        )
        .reset_index(
            name="orders"
        )
    )

    summary["share_pct"] = (
        summary["orders"]
        / len(result)
        * 100
    ).round(1)

    return summary


def order_status_distribution(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise overall order status distribution."""

    summary = (
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

    summary["share_pct"] = (
        summary["orders"]
        / len(orders)
        * 100
    ).round(1)

    return summary


def order_status_by_year(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise order status distribution by year."""

    result = orders.copy()

    result["order_year"] = (
        result[
            "order_timestamp"
        ].dt.year
    )

    summary = (
        result.groupby(
            [
                "order_year",
                "order_status",
            ]
        )
        .size()
        .reset_index(
            name="orders"
        )
    )

    year_totals = (
        summary.groupby(
            "order_year"
        )["orders"]
        .transform("sum")
    )

    summary[
        "share_within_year_pct"
    ] = (
        summary["orders"]
        / year_totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "order_year",
            "order_status",
        ]
    )


def order_status_by_persona(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise order status distribution by customer persona."""

    result = orders.merge(
        customers[
            [
                "customer_id",
                "customer_persona",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    summary = (
        result.groupby(
            [
                "customer_persona",
                "order_status",
            ]
        )
        .size()
        .reset_index(
            name="orders"
        )
    )

    persona_totals = (
        summary.groupby(
            "customer_persona"
        )["orders"]
        .transform("sum")
    )

    summary[
        "share_within_persona_pct"
    ] = (
        summary["orders"]
        / persona_totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "customer_persona",
            "order_status",
        ]
    )


def rank_customer_orders(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Assign chronological order number within each customer."""

    result = (
        orders.sort_values(
            [
                "customer_id",
                "order_timestamp",
                "order_id",
            ]
        )
        .copy()
    )

    result[
        "order_number"
    ] = (
        result.groupby(
            "customer_id"
        ).cumcount()
        + 1
    )

    result[
        "order_type"
    ] = (
        result[
            "order_number"
        ]
        .eq(1)
        .map(
            {
                True: "First order",
                False: "Repeat order",
            }
        )
    )

    return result


def promotion_code_distribution(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise overall promotion-code usage."""

    result = orders.copy()

    result[
        "promotion_label"
    ] = (
        result[
            "promotion_code"
        ].fillna(
            "No promotion"
        )
    )

    summary = (
        result[
            "promotion_label"
        ]
        .value_counts()
        .rename_axis(
            "promotion_code"
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
        / len(result)
        * 100
    ).round(1)

    return summary


def promotion_by_order_type(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise promotion usage for first vs repeat orders."""

    ranked = rank_customer_orders(
        orders
    )

    eligible = ranked[
        ranked[
            "order_status"
        ]
        != "Cancelled"
    ].copy()

    eligible[
        "promotion_label"
    ] = (
        eligible[
            "promotion_code"
        ].fillna(
            "No promotion"
        )
    )

    summary = (
        eligible.groupby(
            [
                "order_type",
                "promotion_label",
            ],
            observed=False,
        )
        .size()
        .reset_index(
            name="orders"
        )
    )

    order_type_totals = (
        summary.groupby(
            "order_type"
        )["orders"]
        .transform("sum")
    )

    summary[
        "share_within_order_type_pct"
    ] = (
        summary[
            "orders"
        ]
        / order_type_totals
        * 100
    ).round(1)

    return (
        summary.rename(
            columns={
                "promotion_label":
                    "promotion_code"
            }
        )
        .sort_values(
            [
                "order_type",
                "orders",
            ],
            ascending=[
                True,
                False,
            ],
        )
    )


def promotion_by_year(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise promotion usage by order year."""

    result = orders[
        orders[
            "order_status"
        ]
        != "Cancelled"
    ].copy()

    result[
        "order_year"
    ] = (
        result[
            "order_timestamp"
        ].dt.year
    )

    result[
        "promotion_label"
    ] = (
        result[
            "promotion_code"
        ].fillna(
            "No promotion"
        )
    )

    summary = (
        result.groupby(
            [
                "order_year",
                "promotion_label",
            ]
        )
        .size()
        .reset_index(
            name="orders"
        )
    )

    year_totals = (
        summary.groupby(
            "order_year"
        )["orders"]
        .transform("sum")
    )

    summary[
        "share_within_year_pct"
    ] = (
        summary[
            "orders"
        ]
        / year_totals
        * 100
    ).round(1)

    return (
        summary.rename(
            columns={
                "promotion_label":
                    "promotion_code"
            }
        )
        .sort_values(
            [
                "order_year",
                "orders",
            ],
            ascending=[
                True,
                False,
            ],
        )
    )


def promotion_by_persona(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise promotion usage by customer persona."""

    result = orders.merge(
        customers[
            [
                "customer_id",
                "customer_persona",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    result = result[
        result[
            "order_status"
        ]
        != "Cancelled"
    ].copy()

    result[
        "promotion_label"
    ] = (
        result[
            "promotion_code"
        ].fillna(
            "No promotion"
        )
    )

    summary = (
        result.groupby(
            [
                "customer_persona",
                "promotion_label",
            ]
        )
        .size()
        .reset_index(
            name="orders"
        )
    )

    persona_totals = (
        summary.groupby(
            "customer_persona"
        )["orders"]
        .transform("sum")
    )

    summary[
        "share_within_persona_pct"
    ] = (
        summary[
            "orders"
        ]
        / persona_totals
        * 100
    ).round(1)

    return (
        summary.rename(
            columns={
                "promotion_label":
                    "promotion_code"
            }
        )
        .sort_values(
            [
                "customer_persona",
                "orders",
            ],
            ascending=[
                True,
                False,
            ],
        )
    )


def promotion_rule_checks(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Check core promotion business rules."""

    ranked = rank_customer_orders(
        orders
    )

    welcome_on_repeat_orders = (
        (
            ranked[
                "promotion_code"
            ]
            == "WELCOME10"
        )
        & (
            ranked[
                "order_number"
            ]
            > 1
        )
    ).sum()

    cancelled_with_promotion = (
        (
            ranked[
                "order_status"
            ]
            == "Cancelled"
        )
        & ranked[
            "promotion_code"
        ].notna()
    ).sum()

    valid_promotion_codes = {
        "WELCOME10",
        "CLUB15",
        "SEASON20",
        "EVENT10",
        "FREESHIP",
    }

    invalid_promotion_codes = (
        ranked[
            "promotion_code"
        ].notna()
        & ~ranked[
            "promotion_code"
        ].isin(
            valid_promotion_codes
        )
    ).sum()

    return pd.DataFrame(
        {
            "check": [
                "WELCOME10 on repeat orders",
                "Cancelled orders with promotion",
                "Invalid promotion codes",
            ],
            "violations": [
                int(
                    welcome_on_repeat_orders
                ),
                int(
                    cancelled_with_promotion
                ),
                int(
                    invalid_promotion_codes
                ),
            ],
        }
    )

def prepare_campaign_validation(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Attach customer and campaign attributes to attributed orders."""

    attributed = orders[
        orders["campaign_id"].notna()
    ].copy()

    attributed = attributed.merge(
        customers[
            [
                "customer_id",
                "customer_persona",
                "marketing_consent",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

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

    attributed = attributed.merge(
        campaign_details,
        on="campaign_id",
        how="left",
        validate="many_to_one",
    )

    attributed["order_date"] = (
        attributed[
            "order_timestamp"
        ].dt.normalize()
    )

    attributed["campaign_start_date"] = (
        attributed[
            "start_date"
        ].dt.normalize()
    )

    attributed["campaign_end_date"] = (
        attributed[
            "end_date"
        ].dt.normalize()
    )

    return attributed


def campaign_attribution_summary(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise overall order-level campaign attribution."""

    result = orders.copy()

    result["campaign_linked"] = (
        result["campaign_id"].notna()
    )

    summary = (
        result["campaign_linked"]
        .value_counts()
        .rename_axis(
            "campaign_linked"
        )
        .reset_index(
            name="orders"
        )
    )

    summary["share_pct"] = (
        summary["orders"]
        / len(result)
        * 100
    ).round(1)

    return summary


def campaign_attribution_by_year(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise order-level campaign attribution by year."""

    result = orders.copy()

    result["order_year"] = (
        result[
            "order_timestamp"
        ].dt.year
    )

    result["campaign_linked"] = (
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
        summary["linked_orders"]
        / summary["orders"]
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

    summary["share_pct"] = (
        summary["orders"]
        / len(attributed)
        * 100
    ).round(1)

    return summary


def campaign_attribution_by_order_type(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Compare campaign attribution for first and repeat orders."""

    ranked = rank_customer_orders(
        orders
    )

    ranked["campaign_linked"] = (
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
        summary["linked_orders"]
        / summary["orders"]
        * 100
    ).round(1)

    return summary


def acquisition_campaign_eligibility(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    acquisition: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """
    Measure acquisition-campaign persistence among first orders
    for which that acquisition campaign is still eligible.
    """

    ranked = rank_customer_orders(
        orders
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

    first_orders = first_orders.merge(
        acquisition_campaigns,
        on="customer_id",
        how="left",
        validate="one_to_one",
    )

    first_orders = first_orders.merge(
        customers[
            [
                "customer_id",
                "customer_persona",
                "marketing_consent",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    acquisition_campaign_details = (
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
                "campaign_id":
                    "acquisition_campaign_id",
                "channel":
                    "acquisition_campaign_channel",
                "start_date":
                    "acquisition_campaign_start_date",
                "end_date":
                    "acquisition_campaign_end_date",
                "target_segment":
                    "acquisition_campaign_target_segment",
            }
        )
    )

    first_orders = first_orders.merge(
        acquisition_campaign_details,
        on="acquisition_campaign_id",
        how="left",
        validate="many_to_one",
    )

    with_acquisition_campaign = (
        first_orders[
            first_orders[
                "acquisition_campaign_id"
            ].notna()
        ]
        .copy()
    )

    with_acquisition_campaign[
        "order_date"
    ] = (
        with_acquisition_campaign[
            "order_timestamp"
        ].dt.normalize()
    )

    with_acquisition_campaign[
        "campaign_start_date"
    ] = (
        with_acquisition_campaign[
            "acquisition_campaign_start_date"
        ].dt.normalize()
    )

    with_acquisition_campaign[
        "campaign_end_date"
    ] = (
        with_acquisition_campaign[
            "acquisition_campaign_end_date"
        ].dt.normalize()
    )

    active_on_order_date = (
        (
            with_acquisition_campaign[
                "order_date"
            ]
            >= with_acquisition_campaign[
                "campaign_start_date"
            ]
        )
        & (
            with_acquisition_campaign[
                "order_date"
            ]
            <= with_acquisition_campaign[
                "campaign_end_date"
            ]
        )
    )

    segment_match = (
        with_acquisition_campaign[
            "customer_persona"
        ]
        == with_acquisition_campaign[
            "acquisition_campaign_target_segment"
        ]
    )

    consent_eligible = (
        (
            with_acquisition_campaign[
                "acquisition_campaign_channel"
            ]
            != "Email"
        )
        | (
            with_acquisition_campaign[
                "marketing_consent"
            ].astype(bool)
        )
    )

    with_acquisition_campaign[
        "acquisition_campaign_eligible"
    ] = (
        active_on_order_date
        & segment_match
        & consent_eligible
    )

    eligible = (
        with_acquisition_campaign[
            with_acquisition_campaign[
                "acquisition_campaign_eligible"
            ]
        ]
        .copy()
    )

    eligible[
        "same_campaign"
    ] = (
        eligible[
            "campaign_id"
        ]
        == eligible[
            "acquisition_campaign_id"
        ]
    )

    total_first_orders = len(
        first_orders
    )

    first_orders_with_acquisition_campaign = len(
        with_acquisition_campaign
    )

    eligible_first_orders = len(
        eligible
    )

    same_campaign_orders = int(
        eligible[
            "same_campaign"
        ].sum()
    )

    if eligible_first_orders > 0:
        conditional_persistence_pct = round(
            same_campaign_orders
            / eligible_first_orders
            * 100,
            1,
        )
    else:
        conditional_persistence_pct = 0.0

    return pd.DataFrame(
        {
            "metric": [
                "Total first orders",
                "First orders with acquisition campaign",
                "Acquisition campaign still eligible",
                "Same campaign among eligible first orders",
                "Conditional persistence pct",
            ],
            "value": [
                total_first_orders,
                first_orders_with_acquisition_campaign,
                eligible_first_orders,
                same_campaign_orders,
                conditional_persistence_pct,
            ],
        }
    )


def campaign_rule_checks(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Check core order-level campaign attribution rules."""

    valid_campaign_ids = set(
        campaigns[
            "campaign_id"
        ]
    )

    unknown_campaign_ids = (
        orders[
            "campaign_id"
        ].notna()
        & ~orders[
            "campaign_id"
        ].isin(
            valid_campaign_ids
        )
    ).sum()

    attributed = (
        prepare_campaign_validation(
            orders=orders,
            customers=customers,
            campaigns=campaigns,
        )
    )

    outside_campaign_window = (
        (
            attributed[
                "order_date"
            ]
            < attributed[
                "campaign_start_date"
            ]
        )
        | (
            attributed[
                "order_date"
            ]
            > attributed[
                "campaign_end_date"
            ]
        )
    ).sum()

    target_segment_mismatch = (
        attributed[
            "customer_persona"
        ]
        != attributed[
            "campaign_target_segment"
        ]
    ).sum()

    email_without_consent = (
        (
            attributed[
                "campaign_channel"
            ]
            == "Email"
        )
        & (
            ~attributed[
                "marketing_consent"
            ].astype(bool)
        )
    ).sum()

    return pd.DataFrame(
        {
            "check": [
                "Unknown campaign IDs",
                "Orders outside campaign window",
                "Target-segment mismatches",
                "Email attribution without consent",
            ],
            "violations": [
                int(
                    unknown_campaign_ids
                ),
                int(
                    outside_campaign_window
                ),
                int(
                    target_segment_mismatch
                ),
                int(
                    email_without_consent
                ),
            ],
        }
    )


def campaign_coverage_summary(
    orders: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise how many campaigns receive order attribution."""

    attributed_campaigns = (
        orders[
            "campaign_id"
        ]
        .dropna()
        .nunique()
    )

    total_campaigns = (
        campaigns[
            "campaign_id"
        ].nunique()
    )

    unused_campaigns = (
        total_campaigns
        - attributed_campaigns
    )

    return pd.DataFrame(
        {
            "metric": [
                "Total campaigns",
                "Campaigns with attributed orders",
                "Campaigns without attributed orders",
                "Campaign coverage pct",
            ],
            "value": [
                total_campaigns,
                attributed_campaigns,
                unused_campaigns,
                round(
                    attributed_campaigns
                    / total_campaigns
                    * 100,
                    1,
                ),
            ],
        }
    )


def suspicious_orders(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    locations: pd.DataFrame,
) -> pd.DataFrame:
    """Identify invalid order records."""

    validation = orders.merge(
        customers[
            [
                "customer_id",
                "signup_date",
                "location_id",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    valid_location_ids = set(
        locations[
            "location_id"
        ]
    )

    valid_device_channel = (
        (
            (
                validation[
                    "device"
                ]
                == "Desktop"
            )
            & (
                validation[
                    "sales_channel"
                ]
                == "Website"
            )
        )
        | (
            validation[
                "device"
            ].isin(
                [
                    "Mobile",
                    "Tablet",
                ]
            )
            & validation[
                "sales_channel"
            ].isin(
                [
                    "Website",
                    "iOS",
                    "Android",
                ]
            )
        )
    )

    valid_order_statuses = {
        "Completed",
        "Cancelled",
        "Refunded",
    }

    invalid_order_status = (
        validation[
            "order_status"
        ].isna()
        | ~validation[
            "order_status"
        ].isin(
            valid_order_statuses
        )
    )

    valid_promotion_codes = {
        "WELCOME10",
        "CLUB15",
        "SEASON20",
        "EVENT10",
        "FREESHIP",
    }

    invalid_promotion_code = (
        validation[
            "promotion_code"
        ].notna()
        & ~validation[
            "promotion_code"
        ].isin(
            valid_promotion_codes
        )
    )

    cancelled_with_promotion = (
        (
            validation[
                "order_status"
            ]
            == "Cancelled"
        )
        & validation[
            "promotion_code"
        ].notna()
    )

    ranked_orders = (
        validation.sort_values(
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

    invalid_welcome_order_ids = set(
        ranked_orders.loc[
            (
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
                    > 1
                )
            ),
            "order_id",
        ]
    )

    welcome_on_repeat_order = (
        validation[
            "order_id"
        ].isin(
            invalid_welcome_order_ids
        )
    )

    suspicious = validation[
        validation[
            "signup_date"
        ].isna()
        | (
            validation[
                "order_timestamp"
            ]
            < validation[
                "signup_date"
            ]
        )
        | ~valid_device_channel
        | (
            ~validation[
                "shipping_location_id"
            ].isin(
                valid_location_ids
            )
        )
        | invalid_order_status
        | invalid_promotion_code
        | cancelled_with_promotion
        | welcome_on_repeat_order
    ]

    return suspicious[
        [
            "order_id",
            "customer_id",
            "signup_date",
            "order_timestamp",
            "device",
            "sales_channel",
            "currency",
            "location_id",
            "shipping_location_id",
            "order_status",
            "promotion_code",
        ]
    ]


def main() -> None:
    """Run analytical validation."""

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    orders_path = (
        project_root
        / "data"
        / "raw"
        / "orders.csv"
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

    (
        orders,
        customers,
        acquisition,
        locations,
        campaigns,
    ) = load_data(
        orders_path=orders_path,
        customers_path=customers_path,
        acquisition_path=acquisition_path,
        locations_path=locations_path,
        campaigns_path=campaigns_path,
    )

    customer_summary = (
        customer_order_summary(
            orders=orders,
            customers=customers,
        )
    )

    order_geography = (
        prepare_order_geography(
            orders=orders,
            customers=customers,
            locations=locations,
        )
    )

    print(
        "\nDATASET SUMMARY"
    )

    print(
        f"Orders: {len(orders):,}"
    )

    print(
        f"Customers: {len(customers):,}"
    )

    print(
        "Purchasing customers: "
        f"{orders['customer_id'].nunique():,}"
    )

    print(
        "\nPURCHASER DISTRIBUTION"
    )

    print(
        purchaser_summary(
            customer_summary
        ).to_string(
            index=False
        )
    )

    print(
        "\nCUSTOMER PURCHASE FREQUENCY"
    )

    print(
        customer_type_summary(
            customer_summary
        ).to_string(
            index=False
        )
    )

    print(
        "\nORDERS PER PURCHASING CUSTOMER"
    )

    print(
        orders_per_purchaser_summary(
            customer_summary
        ).to_string(
            index=False
        )
    )

    print(
        "\nPURCHASE BEHAVIOUR BY PERSONA"
    )

    print(
        purchase_behaviour_by_persona(
            customer_summary
        ).to_string(
            index=False
        )
    )

    print(
        "\nTIME TO FIRST PURCHASE"
    )

    print(
        first_purchase_delay_summary(
            customer_summary
        ).to_string(
            index=False
        )
    )

    print(
        "\nFIRST PURCHASE DELAY BUCKETS"
    )

    print(
        first_purchase_delay_buckets(
            customer_summary
        ).to_string(
            index=False
        )
    )

    print(
        "\nTIME TO SECOND PURCHASE"
    )

    print(
        second_purchase_summary(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nORDERS BY YEAR"
    )

    print(
        orders_by_year(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nORDERS BY MONTH"
    )

    print(
        orders_by_month(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nSIGNUP COHORT BEHAVIOUR"
    )

    print(
        signup_cohort_summary(
            customer_summary
        ).to_string(
            index=False
        )
    )

    print(
        "\nORDER DEVICE DISTRIBUTION"
    )

    print(
        device_distribution(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nSALES CHANNEL DISTRIBUTION"
    )

    print(
        sales_channel_distribution(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nDEVICE × SALES CHANNEL"
    )

    print(
        device_channel_distribution(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nACQUISITION → ORDER PERSISTENCE"
    )

    print(
        acquisition_order_persistence(
            orders=orders,
            acquisition=acquisition,
        ).to_string(
            index=False
        )
    )

    print(
        "\nACQUISITION DEVICE → ORDER DEVICE"
    )

    print(
        acquisition_device_transition(
            orders=orders,
            acquisition=acquisition,
        ).to_string(
            index=False
        )
    )

    print(
        "\nACQUISITION PLATFORM → ORDER SALES CHANNEL"
    )

    print(
        acquisition_platform_transition(
            orders=orders,
            acquisition=acquisition,
        ).to_string(
            index=False
        )
    )

    print(
        "\nSHIPPING LOCATION TYPE"
    )

    print(
        shipping_location_summary(
            order_geography
        ).to_string(
            index=False
        )
    )

    print(
        "\nHOME COUNTRY → SHIPPING COUNTRY CONSISTENCY"
    )

    print(
        shipping_country_consistency(
            order_geography
        ).to_string(
            index=False
        )
    )

    print(
        "\nORDERS BY SHIPPING LOCATION"
    )

    print(
        orders_by_shipping_location(
            order_geography
        ).to_string(
            index=False
        )
    )

    print(
        "\nCURRENCY DISTRIBUTION"
    )

    print(
        currency_distribution(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nCURRENCY CONSISTENCY"
    )

    print(
        currency_consistency(
            orders=orders,
            locations=locations,
        ).to_string(
            index=False
        )
    )

    print(
        "\nORDER STATUS DISTRIBUTION"
    )

    print(
        order_status_distribution(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nORDER STATUS BY YEAR"
    )

    print(
        order_status_by_year(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nORDER STATUS BY PERSONA"
    )

    print(
        order_status_by_persona(
            orders=orders,
            customers=customers,
        ).to_string(
            index=False
        )
    )

    print(
        "\nPROMOTION CODE DISTRIBUTION"
    )

    print(
        promotion_code_distribution(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nPROMOTION BY ORDER TYPE"
    )

    print(
        promotion_by_order_type(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nPROMOTION BY YEAR"
    )

    print(
        promotion_by_year(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nPROMOTION BY PERSONA"
    )

    print(
        promotion_by_persona(
            orders=orders,
            customers=customers,
        ).to_string(
            index=False
        )
    )

    print(
        "\nPROMOTION RULE CHECKS"
    )

    print(
        promotion_rule_checks(
            orders
        ).to_string(
            index=False
        )
    )
    
    print(
        "\nCAMPAIGN ATTRIBUTION"
    )

    print(
        campaign_attribution_summary(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nCAMPAIGN ATTRIBUTION BY YEAR"
    )

    print(
        campaign_attribution_by_year(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nCAMPAIGN ATTRIBUTION BY CHANNEL"
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
        "\nCAMPAIGN ATTRIBUTION BY ORDER TYPE"
    )

    print(
        campaign_attribution_by_order_type(
            orders
        ).to_string(
            index=False
        )
    )

    print(
        "\nACQUISITION CAMPAIGN ELIGIBILITY"
    )

    print(
        acquisition_campaign_eligibility(
            orders=orders,
            customers=customers,
            acquisition=acquisition,
            campaigns=campaigns,
        ).to_string(
            index=False
        )
    )

    print(
        "\nCAMPAIGN COVERAGE"
    )

    print(
        campaign_coverage_summary(
            orders=orders,
            campaigns=campaigns,
        ).to_string(
            index=False
        )
    )

    print(
        "\nCAMPAIGN RULE CHECKS"
    )

    print(
        campaign_rule_checks(
            orders=orders,
            customers=customers,
            campaigns=campaigns,
        ).to_string(
            index=False
        )
    )

    suspicious = (
        suspicious_orders(
            orders=orders,
            customers=customers,
            locations=locations,
        )
    )

    print(
        "\nSUSPICIOUS ORDERS"
    )

    print(
        f"Suspicious orders: "
        f"{len(suspicious):,}"
    )

    if not suspicious.empty:
        print(
            suspicious.to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()