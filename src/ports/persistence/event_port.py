from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from datetime import datetime, timedelta

from src.domain.entities.event import Event

class EventRepository(ABC):
    @abstractmethod
    async def find_by_animal(self, animal_id: UUID, days_back: int = 90) -> List[Event]:
        pass

    @abstractmethod
    async def find_weight_events(self, animal_id: UUID, days_back: int = 90) -> List[tuple]:
        pass

    @abstractmethod
    async def find_breeding_events(self, animal_id: UUID, days_back: int = 365) -> List[tuple]:
        pass

    @abstractmethod
    async def find_birth_events(self, animal_id: UUID, days_back: int = 365) -> List[tuple]:
        pass

    @abstractmethod
    async def get_last_event_by_type(self, animal_id: UUID, event_type: str) -> Optional[tuple]:
        pass