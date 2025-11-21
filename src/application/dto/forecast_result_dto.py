from dataclasses import dataclass
from uuid import UUID
from datetime import date, datetime
from typing import Optional

@dataclass
class ForecastResultDTO:
    animal_id: UUID
    ranch_id: UUID
    predicted_sale_date: Optional[date]
    expected_calving_date: Optional[date]
    suggested_dry_date: Optional[date]
    next_likely_heat_date: Optional[date]
    projected_weight_30d: Optional[float]
    confidence_score: float
    explanation: str
    severity: str
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            "animal_id": str(self.animal_id),
            "ranch_id": str(self.ranch_id),
            "predicted_sale_date": self.predicted_sale_date.isoformat() if self.predicted_sale_date else None,
            "expected_calving_date": self.expected_calving_date.isoformat() if self.expected_calving_date else None,
            "suggested_dry_date": self.suggested_dry_date.isoformat() if self.suggested_dry_date else None,
            "next_likely_heat_date": self.next_likely_heat_date.isoformat() if self.next_likely_heat_date else None,
            "projected_weight_30d": self.projected_weight_30d,
            "confidence_score": self.confidence_score,
            "explanation": self.explanation,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat()
        }