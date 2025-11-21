from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass
class ClusterResultDTO:
    animal_id: UUID
    ranch_id: UUID
    cluster_label: str
    confidence_score: float
    explanation: str
    severity: str
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            "animal_id": str(self.animal_id),
            "ranch_id": str(self.ranch_id),
            "cluster_label": self.cluster_label,
            "confidence_score": self.confidence_score,
            "explanation": self.explanation,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat()
        }