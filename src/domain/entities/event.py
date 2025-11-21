from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass(frozen=True)
class Event:
    id: UUID
    animal_id: UUID
    ranch_id: UUID
    event_type: str
    event_date: datetime
    notes: Optional[str]
    created_by: Optional[UUID]
    source: str
    server_updated_at: datetime

    def is_weight_event(self) -> bool:
        return self.event_type == "weight"

    def is_breeding_event(self) -> bool:
        return self.event_type == "breeding"

    def is_birth_event(self) -> bool:
        return self.event_type == "birth"

    def is_estrus_event(self) -> bool:
        return self.event_type == "estrus"