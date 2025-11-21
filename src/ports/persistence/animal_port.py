from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List

from src.domain.entities.animal import Animal

class AnimalRepository(ABC):
    @abstractmethod
    async def find_by_id(self, animal_id: UUID) -> Optional[Animal]:
        pass

    @abstractmethod
    async def find_by_ranch(self, ranch_id: UUID) -> List[Animal]:
        pass

    @abstractmethod
    async def find_active_by_ranch(self, ranch_id: UUID) -> List[Animal]:
        pass

    @abstractmethod
    async def update_cluster_label(self, animal_id: UUID, label: str) -> bool:
        pass

    @abstractmethod
    async def update_forecast_data(
        self,
        animal_id: UUID,
        predicted_sale_date: Optional[object],
        expected_calving_date: Optional[object],
        suggested_dry_date: Optional[object],
        next_likely_heat_date: Optional[object],
        projected_weight_30d: Optional[float]
    ) -> bool:
        pass