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
    ),
]


PRODUCT_PROFILE_WEIGHTS = np.array([
    0.12,  # T-Shirt
    0.08,  # Sports Bra
    0.10,  # Shorts
    0.10,  # Leggings
    0.08,  # Fleece
    0.10,  # Running Jacket
    0.07,  # Waterproof Shell
    0.10,  # Cap
    0.10,  # Socks
    0.07,  # Running Vest
    0.08,  # Backpack
])

assert np.isclose(PRODUCT_PROFILE_WEIGHTS.sum(), 1.0)

COLOUR_FAMILIES = (
    "Black",
    "White",
    "Grey",
    "Navy",
    "Green",
    "Brown",
    "Red",
    "Blue",
    "Beige",
    "Orange",
)

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

def generate_products(
    config: GenerationConfig,
) -> pd.DataFrame:
    """Generate the Terra Active synthetic product catalogue."""

    rng = np.random.default_rng(config.random_seed)

    records: list[dict[str, object]] = []

    available_dates = pd.date_range(
        config.start_date,
        config.end_date,
        freq="D",
    )

    for index in range(config.number_of_products):

        profile_index = rng.choice(
            len(PRODUCT_PROFILES),
            p=PRODUCT_PROFILE_WEIGHTS,
        )

        profile = PRODUCT_PROFILES[profile_index]

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

        launch_date = pd.Timestamp(
            rng.choice(available_dates)
        )

        product_id = f"PROD{index + 1:04d}"

        product_name = (
            f"Terra {profile.subcategory} "
            f"{index + 1:03d}"
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
            "colour_family": rng.choice(
                COLOUR_FAMILIES
            ),
            "collection": rng.choice(
                COLLECTIONS,
                p=[0.35, 0.15, 0.15, 0.20, 0.15],
            ),
            "launch_date": launch_date,
            "list_price": list_price,
            "unit_cost": unit_cost,
            "technical_level": profile.technical_level,
            "waterproof": bool(
                rng.random()
                < profile.waterproof_probability
            ),
            "insulated": bool(
                rng.random()
                < profile.insulated_probability
            ),
            "sustainable_material_pct": round(
                rng.uniform(20, 100),
                1,
            ),
            "active_flag": True,
        }

        records.append(record)

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
        "colour_family",
        "collection",
        "launch_date",
        "list_price",
        "unit_cost",
        "technical_level",
        "waterproof",
        "insulated",
        "sustainable_material_pct",
        "active_flag",
    }

    missing_columns = required_columns.difference(
        df.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing product columns: "
            f"{sorted(missing_columns)}"
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