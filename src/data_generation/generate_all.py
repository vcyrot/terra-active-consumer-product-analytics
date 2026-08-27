"""Run the Terra Active synthetic data generation pipeline."""

from config import GenerationConfig
from generate_locations import (
    generate_locations,
    save_locations,
    validate_locations,
)
from generate_products import (
    generate_products,
    save_products,
    validate_products,
)
from generate_product_variants import (
    generate_product_variants,
    save_product_variants,
    validate_product_variants,
)
from generate_customers import (
    generate_customers,
    save_customers,
    validate_customers,
)


def main() -> None:
    """Generate all Terra Active synthetic datasets."""

    config = GenerationConfig()

    print("Generating Terra Active synthetic data...")
    print()

    # ---------------------------------------------------------
    # Locations
    # ---------------------------------------------------------

    print("Generating locations...")

    locations = generate_locations()

    validate_locations(locations)

    locations_path = save_locations(
        locations,
        config.raw_data_dir,
    )

    print(
        f"✓ Generated {len(locations):,} locations"
    )
    print(
        f"✓ Saved to: {locations_path}"
    )
    
    # ---------------------------------------------------------
    # Products
    # ---------------------------------------------------------

    print()
    print("Generating products...")

    products = generate_products(config)

    validate_products(
        products,
        config,
    )

    products_path = save_products(
        products,
        config.raw_data_dir,
    )

    print(
        f"✓ Generated {len(products):,} products"
    )

    print(
        f"✓ Saved to: {products_path}"
    )
    
    # ---------------------------------------------------------
    # Product variants
    # ---------------------------------------------------------

    print()
    print("Generating product variants...")

    product_variants = (
        generate_product_variants(
            products,
            config,
        )
    )

    validate_product_variants(
        product_variants,
        products,
    )

    variants_path = save_product_variants(
        product_variants,
        config.raw_data_dir,
    )

    print(
        f"✓ Generated "
        f"{len(product_variants):,} product variants"
    )

    print(
        f"✓ Saved to: {variants_path}"
    )
    
        # ---------------------------------------------------------
    # Customers
    # ---------------------------------------------------------

    print()
    print("Generating customers...")

    customers = generate_customers(
        locations,
        config,
    )

    validate_customers(
        customers,
        locations,
        config,
    )

    customers_path = save_customers(
        customers,
        config.raw_data_dir,
    )

    print(
        f"✓ Generated {len(customers):,} customers"
    )

    print(
        f"✓ Saved to: {customers_path}"
    )


if __name__ == "__main__":
    main()