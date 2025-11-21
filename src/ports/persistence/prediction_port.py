from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.prediction import Prediction

class PredictionRepository(ABC):
    @abstractmethod
    async def save(self, prediction: Prediction) -> bool:
        pass

    @abstractmethod
    async def save_batch(self, predictions: list) -> bool:
        pass