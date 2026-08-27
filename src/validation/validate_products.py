"""Analytical validation for the Terra Active product catalogue."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_products(
    path: Path,
) -> pd.DataFrame:
    """Load the generated product-style catalogue."""

    if not path.exists():
        raise FileNotFoundError(
            f"Product catalogue not found: {path}"
        )

    return pd.read_csv(
        path,
        parse_dates=["launch_date"],
    )


def add_commercial_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate product-level commercial metrics."""

    result = df.copy()

    result["gross_margin_value"] = (
        result["list_price"]
        - result["unit_cost"]
    ).round(2)

    result["gross_margin_pct"] = (
        result["gross_margin_value"]
        / result["list_price"]
        * 100
    ).round(1)

    return result


def product_mix(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise catalogue composition by subcategory."""

    summary = (
        df.groupby(
            ["category", "subcategory"]
        )
        .size()
        .reset_index(
            name="product_count"
        )
    )

    summary["catalogue_share_pct"] = (
        summary["product_count"]
        / len(df)
        * 100
    ).round(1)

    return summary.sort_values(
        "product_count",
        ascending=False,
    )


def commercial_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise price and margin characteristics."""

    summary = (
        df.groupby("subcategory")
        .agg(
            product_count=(
                "product_id",
                "count",
            ),
            avg_price=(
                "list_price",
                "mean",
            ),
            min_price=(
                "list_price",
                "min",
            ),
            max_price=(
                "list_price",
                "max",
            ),
            avg_unit_cost=(
                "unit_cost",
                "mean",
            ),
            avg_gross_margin_value=(
                "gross_margin_value",
                "mean",
            ),
            avg_gross_margin_pct=(
                "gross_margin_pct",
                "mean",
            ),
        )
        .reset_index()
    )

    numeric_columns = [
        "avg_price",
        "min_price",
        "max_price",
        "avg_unit_cost",
        "avg_gross_margin_value",
        "avg_gross_margin_pct",
    ]

    summary[numeric_columns] = (
        summary[numeric_columns].round(2)
    )

    return summary.sort_values(
        "avg_price",
        ascending=False,
    )


def technical_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise technical attributes by subcategory."""

    summary = (
        df.groupby("subcategory")
        .agg(
            product_count=(
                "product_id",
                "count",
            ),
            waterproof_rate=(
                "waterproof",
                "mean",
            ),
            insulated_rate=(
                "insulated",
                "mean",
            ),
            avg_sustainable_material_pct=(
                "sustainable_material_pct",
                "mean",
            ),
        )
        .reset_index()
    )

    summary["waterproof_rate"] = (
        summary["waterproof_rate"]
        * 100
    ).round(1)

    summary["insulated_rate"] = (
        summary["insulated_rate"]
        * 100
    ).round(1)

    summary[
        "avg_sustainable_material_pct"
    ] = (
        summary[
            "avg_sustainable_material_pct"
        ].round(1)
    )

    return summary


def sustainability_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise sustainability characteristics."""

    summary = (
        df.groupby("subcategory")
        .agg(
            avg_sustainable_pct=(
                "sustainable_material_pct",
                "mean",
            ),
            min_sustainable_pct=(
                "sustainable_material_pct",
                "min",
            ),
            max_sustainable_pct=(
                "sustainable_material_pct",
                "max",
            ),
        )
        .reset_index()
    )

    numeric_columns = [
        "avg_sustainable_pct",
        "min_sustainable_pct",
        "max_sustainable_pct",
    ]

    summary[numeric_columns] = (
        summary[numeric_columns].round(1)
    )

    return summary.sort_values(
        "avg_sustainable_pct",
        ascending=False,
    )


def collection_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise catalogue composition by collection."""

    summary = (
        df["collection"]
        .value_counts()
        .rename_axis("collection")
        .reset_index(
            name="product_count"
        )
    )

    summary["catalogue_share_pct"] = (
        summary["product_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def launch_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise product launches by year and collection."""

    result = df.copy()

    result["launch_year"] = (
        result["launch_date"].dt.year
    )

    summary = (
        result.groupby(
            ["launch_year", "collection"]
        )
        .size()
        .reset_index(
            name="products_launched"
        )
    )

    return summary.sort_values(
        ["launch_year", "collection"]
    )


def launch_month_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise launch timing by collection and month."""

    result = df.copy()

    result["launch_month"] = (
        result["launch_date"].dt.month
    )

    summary = (
        result.groupby(
            ["collection", "launch_month"]
        )
        .size()
        .reset_index(
            name="products_launched"
        )
    )

    return summary.sort_values(
        ["collection", "launch_month"]
    )


def positioning_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise sport and technical positioning."""

    summary = (
        df.groupby(
            [
                "technical_level",
                "sport_positioning",
            ]
        )
        .size()
        .reset_index(
            name="product_count"
        )
    )

    return summary.sort_values(
        "product_count",
        ascending=False,
    )


def gender_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise gender positioning."""

    summary = (
        df["gender_positioning"]
        .value_counts()
        .rename_axis(
            "gender_positioning"
        )
        .reset_index(
            name="product_count"
        )
    )

    summary["catalogue_share_pct"] = (
        summary["product_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def main() -> None:
    """Run analytical validation of the product catalogue."""

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    product_path = (
        project_root
        / "data"
        / "raw"
        / "products.csv"
    )

    products = load_products(
        product_path
    )

    products = add_commercial_metrics(
        products
    )

    print("\nPRODUCT MIX")
    print(
        product_mix(products)
        .to_string(index=False)
    )

    print("\nCOMMERCIAL SUMMARY")
    print(
        commercial_summary(products)
        .to_string(index=False)
    )

    print("\nTECHNICAL ATTRIBUTES")
    print(
        technical_summary(products)
        .to_string(index=False)
    )

    print("\nSUSTAINABILITY")
    print(
        sustainability_summary(products)
        .to_string(index=False)
    )

    print("\nCOLLECTION MIX")
    print(
        collection_summary(products)
        .to_string(index=False)
    )

    print("\nLAUNCHES BY YEAR AND COLLECTION")
    print(
        launch_summary(products)
        .to_string(index=False)
    )

    print("\nLAUNCH MONTHS")
    print(
        launch_month_summary(products)
        .to_string(index=False)
    )

    print("\nPRODUCT POSITIONING")
    print(
        positioning_summary(products)
        .to_string(index=False)
    )

    print("\nGENDER POSITIONING")
    print(
        gender_summary(products)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()