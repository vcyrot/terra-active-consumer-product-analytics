"""Generate Terra Active product colour and size variants."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from config import GenerationConfig


# ---------------------------------------------------------------------
# Size configuration
# ---------------------------------------------------------------------

APPAREL_SIZES = (
    "XS",
    "S",
    "M",
    "L",
    "XL",
)

ACCESSORY_SIZES = {
    "Cap": ("ONE_SIZE",),
    "Running Vest": ("XS/S", "M/L", "XL"),
    "Backpack": ("ONE_SIZE",),
    "Socks": ("S", "M", "L"),
}


def get_sizes(
    category: str,
    subcategory: str,
) -> tuple[str, ...]:
    """Return valid sizes for a product type."""

    if category == "Apparel":
        return APPAREL_SIZES

    return ACCESSORY_SIZES.get(
        subcategory,
        ("ONE_SIZE",),
    )


# ---------------------------------------------------------------------
# Colour configuration
# ---------------------------------------------------------------------

COLOUR_FAMILIES = (
    "Black",
    "Navy",
    "Grey",
    "White",
    "Beige",
    "Green",
    "Brown",
    "Blue",
    "Red",
    "Orange",
)

COLOUR_WEIGHTS = np.array([
    0.22,  # Black
    0.15,  # Navy
    0.13,  # Grey
    0.12,  # White
    0.10,  # Beige
    0.09,  # Green
    0.06,  # Brown
    0.05,  # Blue
    0.04,  # Red
    0.04,  # Orange
])

assert np.isclose(
    COLOUR_WEIGHTS.sum(),
    1.0,
)


# ---------------------------------------------------------------------
# Number of colours per product style
# ---------------------------------------------------------------------

COLOUR_COUNT_OPTIONS = {
    "Apparel": (
        np.array([2, 3, 4, 5]),
        np.array([0.15, 0.40, 0.30, 0.15]),
    ),
    "Accessory": (
        np.array([2, 3, 4]),
        np.array([0.35, 0.45, 0.20]),
    ),
}

for _, probabilities in COLOUR_COUNT_OPTIONS.values():
    assert np.isclose(
        probabilities.sum(),
        1.0,
    )


# ---------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------

def generate_product_variants(
    products: pd.DataFrame,
    config: GenerationConfig,
) -> pd.DataFrame:
    """Generate colour-size SKUs for every Terra Active product style."""

    required_product_columns = {
        "product_id",
        "category",
        "subcategory",
    }

    missing_columns = (
        required_product_columns
        - set(products.columns)
    )

    if missing_columns:
        raise ValueError(
            "Products table is missing columns required "
            "for variant generation: "
            f"{sorted(missing_columns)}"
        )

    rng = np.random.default_rng(
        config.random_seed + 1
    )

    records: list[dict[str, object]] = []

    sku_number = 1

    for _, product in products.iterrows():

        category = product["category"]
        subcategory = product["subcategory"]

        if category not in COLOUR_COUNT_OPTIONS:
            raise ValueError(
                f"Unknown product category: {category}"
            )

        colour_options, colour_probabilities = (
            COLOUR_COUNT_OPTIONS[category]
        )

        number_of_colours = int(
            rng.choice(
                colour_options,
                p=colour_probabilities,
            )
        )

        selected_colours = rng.choice(
            COLOUR_FAMILIES,
            size=number_of_colours,
            replace=False,
            p=COLOUR_WEIGHTS,
        )

        sizes = get_sizes(
            category,
            subcategory,
        )

        for colour in selected_colours:
            for size in sizes:

                sku_id = (
                    f"SKU{sku_number:06d}"
                )

                record = {
                    "sku_id": sku_id,
                    "product_id": product[
                        "product_id"
                    ],
                    "colour_family": str(
                        colour
                    ),
                    "size": size,
                    "active_flag": True,
                }

                records.append(record)

                sku_number += 1

    return pd.DataFrame(records)


# ---------------------------------------------------------------------
# Structural validation
# ---------------------------------------------------------------------

def validate_product_variants(
    variants: pd.DataFrame,
    products: pd.DataFrame,
) -> None:
    """Validate generated product variants."""

    required_columns = {
        "sku_id",
        "product_id",
        "colour_family",
        "size",
        "active_flag",
    }

    missing_columns = (
        required_columns
        - set(variants.columns)
    )

    if missing_columns:
        raise ValueError(
            "Product variants are missing required columns: "
            f"{sorted(missing_columns)}"
        )

    # ---------------------------------------------------------
    # Primary key
    # ---------------------------------------------------------

    if variants["sku_id"].duplicated().any():
        raise ValueError(
            "Duplicate SKU IDs detected."
        )

    # ---------------------------------------------------------
    # Foreign key
    # ---------------------------------------------------------

    invalid_products = (
        set(variants["product_id"])
        - set(products["product_id"])
    )

    if invalid_products:
        raise ValueError(
            "Product variants reference unknown products."
        )

    # ---------------------------------------------------------
    # Unique style-colour-size combinations
    # ---------------------------------------------------------

    duplicate_variants = variants.duplicated(
        subset=[
            "product_id",
            "colour_family",
            "size",
        ]
    )

    if duplicate_variants.any():
        raise ValueError(
            "Duplicate product-colour-size "
            "combinations detected."
        )

    # ---------------------------------------------------------
    # Every style must have at least one SKU
    # ---------------------------------------------------------

    missing_products = (
        set(products["product_id"])
        - set(variants["product_id"])
    )

    if missing_products:
        raise ValueError(
            "Some products have no sellable variants."
        )

    # ---------------------------------------------------------
    # Colour validation
    # ---------------------------------------------------------

    invalid_colours = (
        set(variants["colour_family"])
        - set(COLOUR_FAMILIES)
    )

    if invalid_colours:
        raise ValueError(
            "Unknown colours detected: "
            f"{sorted(invalid_colours)}"
        )

    # ---------------------------------------------------------
    # Size validation
    # ---------------------------------------------------------

    product_attributes = products[
        [
            "product_id",
            "category",
            "subcategory",
        ]
    ]

    validation = variants.merge(
        product_attributes,
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    invalid_size_rows = []

    for _, row in validation.iterrows():

        expected_sizes = get_sizes(
            row["category"],
            row["subcategory"],
        )

        if row["size"] not in expected_sizes:
            invalid_size_rows.append(
                row["sku_id"]
            )

    if invalid_size_rows:
        raise ValueError(
            "Invalid product sizes detected for SKUs: "
            f"{invalid_size_rows[:10]}"
        )

    # ---------------------------------------------------------
    # Active flag
    # ---------------------------------------------------------

    if not variants[
        "active_flag"
    ].isin([True, False]).all():
        raise ValueError(
            "Invalid active_flag values detected."
        )


# ---------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------

def save_product_variants(
    df: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Save generated product variants."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "product_variants.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    return output_path