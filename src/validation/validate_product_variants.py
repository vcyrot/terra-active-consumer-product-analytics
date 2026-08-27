"""Analytical validation for Terra Active product variants."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_product_variants(
    path: Path,
) -> pd.DataFrame:
    """Load the generated product variant catalogue."""

    if not path.exists():
        raise FileNotFoundError(
            f"Product variants not found: {path}"
        )

    return pd.read_csv(path)


def load_products(
    path: Path,
) -> pd.DataFrame:
    """Load the parent product-style catalogue."""

    if not path.exists():
        raise FileNotFoundError(
            f"Product catalogue not found: {path}"
        )

    return pd.read_csv(path)


def add_variant_context(
    variants: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Attach parent product attributes to each SKU."""

    result = variants.merge(
        products[
            [
                "product_id",
                "category",
                "subcategory",
                "gender_positioning",
                "collection",
                "technical_level",
            ]
        ],
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    return result


def sku_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise SKU counts by product subcategory."""

    summary = (
        df.groupby(
            ["category", "subcategory"]
        )
        .agg(
            product_styles=(
                "product_id",
                "nunique",
            ),
            sku_count=(
                "sku_id",
                "count",
            ),
        )
        .reset_index()
    )

    summary["avg_skus_per_style"] = (
        summary["sku_count"]
        / summary["product_styles"]
    ).round(1)

    return summary.sort_values(
        "sku_count",
        ascending=False,
    )


def colour_count_per_style(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise the number of colours available per product style."""

    by_style = (
        df.groupby(
            [
                "product_id",
                "category",
                "subcategory",
            ]
        )["colour_family"]
        .nunique()
        .reset_index(
            name="colour_count"
        )
    )

    summary = (
        by_style.groupby(
            ["category", "subcategory"]
        )
        .agg(
            product_styles=(
                "product_id",
                "count",
            ),
            avg_colours_per_style=(
                "colour_count",
                "mean",
            ),
            min_colours_per_style=(
                "colour_count",
                "min",
            ),
            max_colours_per_style=(
                "colour_count",
                "max",
            ),
        )
        .reset_index()
    )

    summary[
        "avg_colours_per_style"
    ] = (
        summary[
            "avg_colours_per_style"
        ].round(2)
    )

    return summary.sort_values(
        "avg_colours_per_style",
        ascending=False,
    )


def colour_distribution(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise overall SKU colour distribution."""

    summary = (
        df["colour_family"]
        .value_counts()
        .rename_axis("colour_family")
        .reset_index(name="sku_count")
    )

    summary["sku_share_pct"] = (
        summary["sku_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def colour_distribution_by_subcategory(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise colour distribution within each subcategory."""

    summary = (
        df.groupby(
            [
                "subcategory",
                "colour_family",
            ]
        )
        .size()
        .reset_index(
            name="sku_count"
        )
    )

    totals = (
        summary.groupby(
            "subcategory"
        )["sku_count"]
        .transform("sum")
    )

    summary["subcategory_share_pct"] = (
        summary["sku_count"]
        / totals
        * 100
    ).round(1)

    return summary.sort_values(
        [
            "subcategory",
            "sku_count",
        ],
        ascending=[True, False],
    )


def size_distribution(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise SKU distribution by size."""

    summary = (
        df["size"]
        .value_counts()
        .rename_axis("size")
        .reset_index(name="sku_count")
    )

    summary["sku_share_pct"] = (
        summary["sku_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def size_distribution_by_subcategory(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise size distribution within each subcategory."""

    summary = (
        df.groupby(
            [
                "subcategory",
                "size",
            ]
        )
        .size()
        .reset_index(
            name="sku_count"
        )
    )

    return summary.sort_values(
        [
            "subcategory",
            "size",
        ]
    )


def neutral_vs_accent_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Compare neutral and accent colour representation."""

    neutral_colours = {
        "Black",
        "Navy",
        "Grey",
        "White",
        "Beige",
        "Brown",
    }

    result = df.copy()

    result["colour_group"] = (
        result["colour_family"]
        .apply(
            lambda colour: (
                "Neutral"
                if colour in neutral_colours
                else "Accent"
            )
        )
    )

    summary = (
        result["colour_group"]
        .value_counts()
        .rename_axis("colour_group")
        .reset_index(name="sku_count")
    )

    summary["sku_share_pct"] = (
        summary["sku_count"]
        / len(result)
        * 100
    ).round(1)

    return summary


def style_completeness_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Check whether all colours within a style share the same size run.

    This helps detect incomplete colour-size combinations created by the
    generator.
    """

    colour_size_counts = (
        df.groupby(
            [
                "product_id",
                "colour_family",
            ]
        )["size"]
        .nunique()
        .reset_index(
            name="size_count"
        )
    )

    style_summary = (
        colour_size_counts.groupby(
            "product_id"
        )["size_count"]
        .agg(
            min_size_count="min",
            max_size_count="max",
        )
        .reset_index()
    )

    style_summary[
        "consistent_size_run"
    ] = (
        style_summary["min_size_count"]
        == style_summary["max_size_count"]
    )

    return style_summary


def active_variant_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise active and inactive SKU counts."""

    summary = (
        df["active_flag"]
        .value_counts(dropna=False)
        .rename_axis("active_flag")
        .reset_index(name="sku_count")
    )

    summary["sku_share_pct"] = (
        summary["sku_count"]
        / len(df)
        * 100
    ).round(1)

    return summary


def main() -> None:
    """Run analytical validation of the product variant catalogue."""

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    variants_path = (
        project_root
        / "data"
        / "raw"
        / "product_variants.csv"
    )

    products_path = (
        project_root
        / "data"
        / "raw"
        / "products.csv"
    )

    variants = load_product_variants(
        variants_path
    )

    products = load_products(
        products_path
    )

    variants = add_variant_context(
        variants,
        products,
    )

    print("\nSKU SUMMARY")
    print(
        sku_summary(variants)
        .to_string(index=False)
    )

    print("\nCOLOURS PER STYLE")
    print(
        colour_count_per_style(variants)
        .to_string(index=False)
    )

    print("\nOVERALL COLOUR DISTRIBUTION")
    print(
        colour_distribution(variants)
        .to_string(index=False)
    )

    print("\nCOLOUR DISTRIBUTION BY SUBCATEGORY")
    print(
        colour_distribution_by_subcategory(
            variants
        )
        .to_string(index=False)
    )

    print("\nSIZE DISTRIBUTION")
    print(
        size_distribution(variants)
        .to_string(index=False)
    )

    print("\nSIZE DISTRIBUTION BY SUBCATEGORY")
    print(
        size_distribution_by_subcategory(
            variants
        )
        .to_string(index=False)
    )

    print("\nNEUTRAL VS ACCENT COLOURS")
    print(
        neutral_vs_accent_summary(
            variants
        )
        .to_string(index=False)
    )

    print("\nACTIVE VARIANTS")
    print(
        active_variant_summary(
            variants
        )
        .to_string(index=False)
    )

    completeness = (
        style_completeness_summary(
            variants
        )
    )

    inconsistent_styles = (
        completeness[
            ~completeness[
                "consistent_size_run"
            ]
        ]
    )

    print("\nSTYLE SIZE-RUN CONSISTENCY")

    print(
        f"Styles checked: "
        f"{len(completeness):,}"
    )

    print(
        f"Inconsistent styles: "
        f"{len(inconsistent_styles):,}"
    )

    if not inconsistent_styles.empty:
        print(
            inconsistent_styles
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()