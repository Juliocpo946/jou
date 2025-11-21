from uuid import uuid4
from datetime import datetime
from src.domain.entities.prediction import Prediction

class PredictionMapper:

    @staticmethod
    def to_prediction(
        ranch_id,
        animal_id,
        prediction_type: str,
        prediction_date,
        confidence_score: float,
        explanation: str,
        severity: str = "info"
    ) -> Prediction:
        return Prediction(
            id=uuid4(),
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

    @staticmethod
    def from_dict(data: dict) -> Prediction:
        return Prediction(
            id=uuid4(),
            ranch_id=data.get("ranch_id"),
            animal_id=data.get("animal_id"),
            prediction_type=data.get("prediction_type"),
            prediction_date=data.get("prediction_date"),
            confidence_score=float(data.get("confidence_score", 0.0)),
            explanation=data.get("explanation", ""),
            severity=data.get("severity", "info"),
            is_acknowledged=False,
            created_at=datetime.now()
        )