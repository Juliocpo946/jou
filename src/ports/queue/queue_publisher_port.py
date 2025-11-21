from abc import ABC, abstractmethod
from typing import Dict, Any

class QueuePublisherPort(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def publish(self, queue_name: str, message: Dict[str, Any]) -> bool:
        pass