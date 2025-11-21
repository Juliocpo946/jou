from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class Ranch:
    id: UUID
    account_id: UUID
    name: str
    location: str

@dataclass(frozen=True)
class RanchReproSettings:
    id: UUID
    ranch_id: UUID
    avg_gestation_days: int
    estrus_cycle_days: int
    voluntary_waiting_period: int
    days_to_dry_off: int
    gdp_factor_dry_season: float
    gdp_factor_rainy_season: float

@dataclass(frozen=True)
class ProductionGoals:
    id: UUID
    ranch_id: UUID
    target_sale_weight_kg: float
    max_ranch_capacity_kg: float