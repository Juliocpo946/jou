from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass
class ForecastTaskMessage:
    ranch_id: str
    animal_id: str
    task_id: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict) -> "ForecastTaskMessage":
        return cls(
            ranch_id=data.get("ranch_id"),
            animal_id=data.get("animal_id"),
            task_id=data.get("task_id"),
            timestamp=data.get("timestamp")
        )

    def to_dict(self) -> dict:
        return {
            "ranch_id": self.ranch_id,
            "animal_id": self.animal_id,
            "task_id": self.task_id,
            "timestamp": self.timestamp
        }

@dataclass
class ClusterTaskMessage:
    ranch_id: str
    animal_id: str
    task_id: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict) -> "ClusterTaskMessage":
        return cls(
            ranch_id=data.get("ranch_id"),
            animal_id=data.get("animal_id"),
            task_id=data.get("task_id"),
            timestamp=data.get("timestamp")
        )

    def to_dict(self) -> dict:
        return {
            "ranch_id": self.ranch_id,
            "animal_id": self.animal_id,
            "task_id": self.task_id,
            "timestamp": self.timestamp
        }

@dataclass
class ResultMessage:
    animal_id: str
    ranch_id: str
    result_type: str
    result_data: dict
    timestamp: str
    status: str

    def to_dict(self) -> dict:
        return {
            "animal_id": self.animal_id,
            "ranch_id": self.ranch_id,
            "result_type": self.result_type,
            "result_data": self.result_data,
            "timestamp": self.timestamp,
            "status": self.status
        }