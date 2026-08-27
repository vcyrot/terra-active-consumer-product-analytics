"""Run the Terra Active synthetic data generation pipeline."""

from config import GenerationConfig
from generate_locations import (
    generate_locations,
    save_locations,
    validate_locations,
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


if __name__ == "__main__":
    main()