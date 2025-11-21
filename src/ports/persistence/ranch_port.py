from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from src.domain.entities.ranch import Ranch, RanchReproSettings, ProductionGoals

class RanchRepository(ABC):
    @abstractmethod
    async def find_by_id(self, ranch_id: UUID) -> Optional[Ranch]:
        pass

    @abstractmethod
    async def get_repro_settings(self, ranch_id: UUID) -> Optional[RanchReproSettings]:
        pass

    @abstractmethod
    async def get_production_goals(self, ranch_id: UUID) -> Optional[ProductionGoals]:
        pass