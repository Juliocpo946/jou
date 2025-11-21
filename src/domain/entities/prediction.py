from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

@dataclass
class Prediction:
    id: UUID
    ranch_id: UUID
    animal_id: UUID
    prediction_type: str
    prediction_date: Optional[date]
    confidence_score: float
    explanation: str
    severity: str
    is_acknowledged: bool
    created_at: datetime

    @staticmethod
    def create_forecast_prediction(
        ranch_id: UUID,
        animal_id: UUID,
        prediction_type: str,
        prediction_date: Optional[date],
        confidence_score: float,
        explanation: str,
        severity: str = "info"
    ) -> "Prediction":
        return Prediction(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            ranch_id=ranch_id,
            animal_id=animal_id,
            prediction_type=prediction_type,
            prediction_date=prediction_date,
            confidence_score=confidence_score,
            explanation=explanation,
            severity=severity,
            is_acknowledged=False,
            created_at=datetime.now()
        )