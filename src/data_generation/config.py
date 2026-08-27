"""Central configuration for Terra Active synthetic data generation."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class GenerationConfig:
    """Configuration controlling the Terra Active synthetic environment."""

    # Reproducibility
    random_seed: int = 42

    # Simulation period
    start_date: pd.Timestamp = pd.Timestamp("2023-01-01")
    end_date: pd.Timestamp = pd.Timestamp("2025-12-31")

    # Dataset scale
    number_of_customers: int = 100_000
    number_of_products: int = 200
    number_of_campaigns: int = 75

    # Repository paths
    project_root: Path = Path(__file__).resolve().parents[2]

    @property
    def raw_data_dir(self) -> Path:
        return self.project_root / "data" / "raw"

    @property
    def external_data_dir(self) -> Path:
        return self.project_root / "data" / "external"

    @property
    def processed_data_dir(self) -> Path:
        return self.project_root / "data" / "processed"