import logging
from src.domain.entities.prediction import Prediction
from src.ports.persistence.prediction_port import PredictionRepository
from src.infrastructure.persistence.postgres_pool import PostgresPool

logger = logging.getLogger(__name__)

class PredictionRepositoryImpl(PredictionRepository):

    async def save(self, prediction: Prediction) -> bool:
        query = """
            INSERT INTO ml_predictions
            (id, ranch_id, animal_id, prediction_type, prediction_date,
             confidence_score, explanation, severity, is_acknowledged, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                explanation = EXCLUDED.explanation,
                severity = EXCLUDED.severity
        """
        try:
            result = await PostgresPool.execute_insert(
                query,
                (
                    str(prediction.id),
                    str(prediction.ranch_id),
                    str(prediction.animal_id),
                    prediction.prediction_type,
                    prediction.prediction_date,
                    prediction.confidence_score,
                    prediction.explanation,
                    prediction.severity,
                    prediction.is_acknowledged,
                    prediction.created_at
                )
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error en save prediction: {str(e)}")
            raise

    async def save_batch(self, predictions: list) -> bool:
        if not predictions:
            return True

        query = """
            INSERT INTO ml_predictions
            (id, ranch_id, animal_id, prediction_type, prediction_date,
             confidence_score, explanation, severity, is_acknowledged, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                explanation = EXCLUDED.explanation,
                severity = EXCLUDED.severity
        """
        try:
            params_list = [
                (
                    str(pred.id),
                    str(pred.ranch_id),
                    str(pred.animal_id),
                    pred.prediction_type,
                    pred.prediction_date,
                    pred.confidence_score,
                    pred.explanation,
                    pred.severity,
                    pred.is_acknowledged,
                    pred.created_at
                )
                for pred in predictions
            ]
            rowcount = await PostgresPool.batch_execute_update(query, params_list)
            return rowcount > 0
        except Exception as e:
            logger.error(f"Error en save_batch predictions: {str(e)}")
            raise