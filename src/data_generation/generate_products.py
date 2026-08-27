"""Generate Terra Active synthetic product catalogue."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from config import GenerationConfig

@dataclass(frozen=True)
class ProductProfile:
    """Business rules associated with a Terra Active product type."""
    category: str
    subcategory: str
    min_price: float
    max_price: float
    min_cost_ratio: float
    max_cost_ratio: float
    technical_level: str
    waterproof_probability: float
    insulated_probability: float
    sport_options: tuple[str, ...]
    min_sustainable_pct: float
    max_sustainable_pct: float
    

PRODUCT_PROFILES = [
    ProductProfile(
        category="Apparel",
        subcategory="T-Shirt",
        min_price=40,
        max_price=80,
        min_cost_ratio=0.25,
        max_cost_ratio=0.40,
        technical_level="Lifestyle",
        waterproof_probability=0.00,
        insulated_probability=0.00,
        sport_options=("Running", "Gym", "Lifestyle", "Multi-Sport"),
        min_sustainable_pct=80,
        max_sustainable_pct=100,
    ),
    ProductProfile(
        category="Apparel",
        subcategory="Sports Bra",
        min_price=50,
        max_price=90,
        min_cost_ratio=0.25,
        max_cost_ratio=0.40,
        technical_level="Performance",
        waterproof_probability=0.00,
        insulated_probability=0.00,
        sport_options=("Gym", "Pilates", "Running"),
        min_sustainable_pct=50,
        max_sustainable_pct=90,
    ),
    ProductProfile(
        category="Apparel",
        subcategory="Shorts",
        min_price=60,
        max_price=110,
        min_cost_ratio=0.25,
        max_cost_ratio=0.40,
        technical_level="Performance",
        waterproof_probability=0.05,
        insulated_probability=0.00,
        sport_options=("Running", "Gym", "Trail"),
        min_sustainable_pct=50,
        max_sustainable_pct=90,
    ),
    ProductProfile(
        category="Apparel",
        subcategory="Leggings",
        min_price=80,
        max_price=140,
        min_cost_ratio=0.25,
        max_cost_ratio=0.40,
        technical_level="Performance",
        waterproof_probability=0.00,
        insulated_probability=0.05,
        sport_options=("Pilates", "Gym", "Running"),
        min_sustainable_pct=50,
        max_sustainable_pct=90,
    ),
    ProductProfile(
        category="Apparel",
        subcategory="Fleece",
        min_price=120,
        max_price=220,
        min_cost_ratio=0.30,
        max_cost_ratio=0.45,
        technical_level="Technical",
        waterproof_probability=0.05,
        insulated_probability=0.80,
        sport_options=("Hiking", "Trail", "Lifestyle"),
        min_sustainable_pct=30,
        max_sustainable_pct=70,
    ),
    ProductProfile(
        category="Apparel",
        subcategory="Running Jacket",
        min_price=150,
        max_price=300,
        min_cost_ratio=0.30,
        max_cost_ratio=0.45,
        technical_level="Technical",
        waterproof_probability=0.65,
        insulated_probability=0.25,
        sport_options=("Running", "Trail"),
        min_sustainable_pct=30,
        max_sustainable_pct=80,
    ),
    ProductProfile(
        category="Apparel",
        subcategory="Waterproof Shell",
        min_price=220,
        max_price=450,
        min_cost_ratio=0.35,
        max_cost_ratio=0.50,
        technical_level="Technical",
        waterproof_probability=0.95,
        insulated_probability=0.15,
        sport_options=("Hiking", "Trail", "Outdoor"),
        min_sustainable_pct=30,
        max_sustainable_pct=70,
    ),
    ProductProfile(
        category="Accessory",
        subcategory="Cap",
        min_price=25,
        max_price=50,
        min_cost_ratio=0.20,
        max_cost_ratio=0.35,
        technical_level="Lifestyle",
        waterproof_probability=0.05,
        insulated_probability=0.00,
        sport_options=("Running", "Lifestyle", "Multi-Sport"),
        min_sustainable_pct=60,
        max_sustainable_pct=100,
    ),
    ProductProfile(
        category="Accessory",
        subcategory="Socks",
        min_price=15,
        max_price=30,
        min_cost_ratio=0.20,
        max_cost_ratio=0.35,
        technical_level="Performance",
        waterproof_probability=0.00,
        insulated_probability=0.10,
        sport_options=("Running", "Hiking", "Gym"),
        min_sustainable_pct=80,
        max_sustainable_pct=100,
    ),
    ProductProfile(
        category="Accessory",
        subcategory="Running Vest",
        min_price=90,
        max_price=180,
        min_cost_ratio=0.30,
        max_cost_ratio=0.45,
        technical_level="Technical",
        waterproof_probability=0.30,
        insulated_probability=0.00,
        sport_options=("Running", "Trail"),
        min_sustainable_pct=30,
        max_sustainable_pct=80,
    ),
    ProductProfile(
        category="Accessory",
        subcategory="Backpack",
        min_price=100,
        max_price=250,
        min_cost_ratio=0.30,
        max_cost_ratio=0.45,
        technical_level="Technical",
        waterproof_probability=0.50,
        insulated_probability=0.00,
        sport_options=("Hiking", "Outdoor", "Lifestyle"),
        min_sustainable_pct=35,
        max_sustainable_pct=75,
    ),
]


PRODUCT_ASSORTMENT = {
    "T-Shirt": 28,
    "Sports Bra": 18,
    "Shorts": 24,
    "Leggings": 26,
    "Fleece": 16,
    "Running Jacket": 24,
    "Waterproof Shell": 14,
    "Cap": 10,
    "Socks": 18,
    "Running Vest": 12,
    "Backpack": 10,
}

GENDER_POSITIONING = (
    "Women",
    "Men",
    "Unisex",
)

COLLECTIONS = (
    "Core",
    "Spring",
    "Summer",
    "Autumn",
    "Winter",
)
COLLECTION_WEIGHTS = np.array([
    0.35,  # Core
    0.15,  # Spring
    0.15,  # Summer
    0.20,  # Autumn
    0.15,  # Winter
])

assert np.isclose(COLLECTION_WEIGHTS.sum(), 1.0)

COLLECTION_LAUNCH_MONTHS = {
    "Spring": (2, 3),
    "Summer": (4, 5, 6),
    "Autumn": (8, 9),
    "Winter": (10, 11),
}

def generate_launch_date(
    rng: np.random.Generator,
    collection: str,
    config: GenerationConfig,
) -> pd.Timestamp:
    """Generate a launch date consistent with the collection."""

    available_dates = pd.date_range(
        config.start_date,
        config.end_date,
        freq="D",
    )

    if collection == "Core":
        eligible_dates = available_dates
    else:
        eligible_months = COLLECTION_LAUNCH_MONTHS[
            collection
        ]

        eligible_dates = available_dates[
            available_dates.month.isin(
                eligible_months
            )
        ]

    return pd.Timestamp(
        rng.choice(eligible_dates)
    )

def generate_products(
    config: GenerationConfig,
) -> pd.DataFrame:
    """Generate the Terra Active synthetic product-style catalogue."""

    rng = np.random.default_rng(
        config.random_seed
    )

    if (
        sum(PRODUCT_ASSORTMENT.values())
        != config.number_of_products
    ):
        raise ValueError(
            "PRODUCT_ASSORTMENT must sum to "
            f"{config.number_of_products} products."
        )

    profile_lookup = {
        profile.subcategory: profile
        for profile in PRODUCT_PROFILES
    }
    
    missing_profiles = (
        set(PRODUCT_ASSORTMENT)
        - set(profile_lookup)
    )

    if missing_profiles:
        raise ValueError(
            "Missing ProductProfile definitions for: "
            f"{sorted(missing_profiles)}"
        )

    records: list[dict[str, object]] = []

    product_number = 1

    for (
        subcategory,
        product_count,
    ) in PRODUCT_ASSORTMENT.items():

        profile = profile_lookup[
            subcategory
        ]

        for _ in range(product_count):

            list_price = round(
                rng.uniform(
                    profile.min_price,
                    profile.max_price,
                ),
                2,
            )

            cost_ratio = rng.uniform(
                profile.min_cost_ratio,
                profile.max_cost_ratio,
            )

            unit_cost = round(
                list_price * cost_ratio,
                2,
            )

            collection = rng.choice(
                COLLECTIONS,
                p=COLLECTION_WEIGHTS,
            )

            launch_date = generate_launch_date(
                rng,
                collection,
                config,
            )

            product_id = (
                f"PROD{product_number:04d}"
            )

            product_name = (
                f"Terra "
                f"{profile.subcategory} "
                f"{product_number:03d}"
            )

            record = {
                "product_id": product_id,
                "product_name": product_name,
                "category": profile.category,
                "subcategory": profile.subcategory,
                "sport_positioning": rng.choice(
                    profile.sport_options
                ),
                "gender_positioning": rng.choice(
                    GENDER_POSITIONING,
                    p=[0.40, 0.30, 0.30],
                ),
                "collection": collection,
                "launch_date": launch_date,
                "list_price": list_price,
                "unit_cost": unit_cost,
                "technical_level": (
                    profile.technical_level
                ),
                "waterproof": bool(
                    rng.random()
                    < profile.waterproof_probability
                ),
                "insulated": bool(
                    rng.random()
                    < profile.insulated_probability
                ),
                "sustainable_material_pct": round(
                    rng.uniform(
                        profile.min_sustainable_pct,
                        profile.max_sustainable_pct,
                    ),
                    1,
                ),
            }

            records.append(record)

            product_number += 1

    return pd.DataFrame(records)

def validate_products(
    df: pd.DataFrame,
    config: GenerationConfig,
) -> None:
    """Validate generated Terra Active products."""

    required_columns = {
        "product_id",
        "product_name",
        "category",
        "subcategory",
        "sport_positioning",
        "gender_positioning",
        "collection",
        "launch_date",
        "list_price",
        "unit_cost",
        "technical_level",
        "waterproof",
        "insulated",
        "sustainable_material_pct",
    }

    missing_columns = required_columns.difference(
        df.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing product columns: "
            f"{sorted(missing_columns)}"
        )
        
    expected_count = sum(PRODUCT_ASSORTMENT.values())

    if len(df) != expected_count:
        raise ValueError(
            f"Expected {expected_count} products, "
            f"found {len(df)}."
        )

    actual_assortment = (
        df["subcategory"]
        .value_counts()
        .to_dict()
    )

    if actual_assortment != PRODUCT_ASSORTMENT:
        raise ValueError(
            "Generated assortment does not match "
            "PRODUCT_ASSORTMENT."
        )

    if not df["collection"].isin(
        COLLECTIONS
    ).all():
        raise ValueError(
            "Unknown product collection detected."
        )

    if not df["gender_positioning"].isin(
        GENDER_POSITIONING
    ).all():
        raise ValueError(
            "Unknown gender positioning detected."
        )
    
    for collection, months in (
        COLLECTION_LAUNCH_MONTHS.items()
    ):
        collection_rows = df[
            df["collection"] == collection
        ]

        if not collection_rows[
            "launch_date"
        ].dt.month.isin(months).all():
            raise ValueError(
                f"{collection} products found outside "
                f"their launch window."
            )

    if df["product_id"].duplicated().any():
        raise ValueError(
            "Duplicate product IDs detected."
        )

    if (df["list_price"] <= 0).any():
        raise ValueError(
            "Invalid product prices detected."
        )

    if (df["unit_cost"] <= 0).any():
        raise ValueError(
            "Invalid product costs detected."
        )

    if (
        df["unit_cost"] >= df["list_price"]
    ).any():
        raise ValueError(
            "Product cost must be below list price."
        )

    if not df[
        "sustainable_material_pct"
    ].between(0, 100).all():
        raise ValueError(
            "Invalid sustainable material percentages."
        )

    if not df["launch_date"].between(
        config.start_date,
        config.end_date,
    ).all():
        raise ValueError(
            "Product launch dates outside simulation period."
        )
        
def save_products(
    df: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Save generated product catalogue."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_dir / "products.csv"

    df.to_csv(
        output_path,
        index=False,
    )

    return output_path