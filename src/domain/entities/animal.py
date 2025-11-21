from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

@dataclass(frozen=True)
class Animal:
    id: UUID
    ranch_id: UUID
    visual_tag: str
    electronic_tag: Optional[str]
    name: Optional[str]
    sex: str
    birth_date: Optional[date]
    breed: Optional[str]
    productive_status: Optional[str]
    reproductive_status: Optional[str]
    health_score: int
    last_heat_date: Optional[date]
    last_birth_date: Optional[date]
    last_insemination_date: Optional[date]
    current_cluster_label: str
    predicted_sale_date: Optional[date]
    expected_calving_date: Optional[date]
    suggested_dry_date: Optional[date]
    next_likely_heat_date: Optional[date]
    projected_weight_30d: Optional[float]
    is_active: bool
    server_updated_at: datetime

    def is_valid_for_clustering(self) -> bool:
        return self.is_active and self.birth_date is not None

    def is_valid_for_forecasting(self) -> bool:
        return self.is_active