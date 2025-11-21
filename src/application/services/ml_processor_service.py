import logging
from uuid import UUID
from typing import Dict, Any

from src.application.services.cluster_use_case import ClusterUseCase
from src.application.services.forecast_use_case import ForecastUseCase
from src.infrastructure.persistence.postgres_pool import PostgresPool

logger = logging.getLogger(__name__)

class MLProcessorService:

    def __init__(self):
        self.cluster_use_case = ClusterUseCase()
        self.forecast_use_case = ForecastUseCase()

    async def process_clustering_task(
        self,
        ranch_id: str,
        animal_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Procesando clustering - Tarea {task_id}")

            result = await self.cluster_use_case.execute(
                UUID(ranch_id),
                UUID(animal_id)
            )

            logger.info(f"Clustering completado para animal {animal_id}: {result.cluster_label}")

            return {
                "status": "success",
                "task_id": task_id,
                "data": result.to_dict()
            }
        except Exception as e:
            logger.error(f"Error en clustering {task_id}: {str(e)}")
            return {
                "status": "error",
                "task_id": task_id,
                "error": str(e)
            }

    async def process_forecasting_task(
        self,
        ranch_id: str,
        animal_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Procesando forecasting - Tarea {task_id}")

            result = await self.forecast_use_case.execute(
                UUID(ranch_id),
                UUID(animal_id)
            )

            logger.info(f"Forecasting completado para animal {animal_id}")

            return {
                "status": "success",
                "task_id": task_id,
                "data": result.to_dict()
            }
        except Exception as e:
            logger.error(f"Error en forecasting {task_id}: {str(e)}")
            return {
                "status": "error",
                "task_id": task_id,
                "error": str(e)
            }

    async def update_queue_status(
        self,
        task_id: str,
        status: str,
        error_message: str = None
    ) -> None:
        try:
            if error_message:
                query = """
                    UPDATE processing_queue
                    SET status = %s, error_message = %s, processed_at = NOW()
                    WHERE id = %s
                """
                await PostgresPool.execute_update(query, (status, error_message, task_id))
            else:
                query = """
                    UPDATE processing_queue
                    SET status = %s, processed_at = NOW()
                    WHERE id = %s
                """
                await PostgresPool.execute_update(query, (status, task_id))
        except Exception as e:
            logger.error(f"Error actualizando status de queue: {str(e)}")