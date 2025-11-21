from abc import ABC, abstractmethod
from typing import Callable, Any

class QueueConsumerPort(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def start_consuming(self, callback: Callable[[Any], None]) -> None:
        pass

    @abstractmethod
    async def acknowledge_message(self, message_id: str) -> None:
        pass

    @abstractmethod
    async def reject_message(self, message_id: str, requeue: bool = True) -> None:
        pass