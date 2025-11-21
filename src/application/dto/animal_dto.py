from dataclasses import dataclass
from uuid import UUID
from datetime import date, datetime
from typing import Optional

@dataclass
class AnimalDTO:
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
    is_active: bool