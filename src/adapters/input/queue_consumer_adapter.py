import asyncio
import json
import logging
from typing import Callable

from src.infrastructure.queue.queue_consumer import QueueConsumer
from src.application.services.ml_processor_service import MLProcessorService
from src.infrastructure.queue.rabbitmq_connection import RabbitMQConnection
from config.settings import settings

logger = logging.getLogger(__name__)

class QueueConsumerAdapter:

    def __init__(self):
        self.consumer = QueueConsumer()
        self.processor = MLProcessorService()
        self.running = False

    async def start(self) -> None:
        try:
            await self.consumer.connect()
            self.running = True
            logger.info("Adaptador de consumer iniciado")
            await self._consume_messages()
        except Exception as e:
            logger.error(f"Error iniciando consumer adapter: {str(e)}")
            raise

    async def stop(self) -> None:
        try:
            self.running = False
            await self.consumer.disconnect()
            logger.info("Adaptador de consumer detenido")
        except Exception as e:
            logger.error(f"Error deteniendo consumer adapter: {str(e)}")

    async def _consume_messages(self) -> None:
        channel = await RabbitMQConnection.get_channel()

        queue_forecast = await channel.get_queue(settings.QUEUE_NAME_FORECAST)
        queue_cluster = await channel.get_queue(settings.QUEUE_NAME_CLUSTER)

        await asyncio.gather(
            self._consume_queue(queue_forecast, "forecast"),
            self._consume_queue(queue_cluster, "cluster")
        )

    async def _consume_queue(self, queue, queue_type: str) -> None:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        body = json.loads(message.body.decode())
                        await self._process_message(body, queue_type)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decodificando mensaje: {str(e)}")
                        await message.nack(requeue=False)
                    except Exception as e:
                        logger.error(f"Error procesando mensaje: {str(e)}")
                        await message.nack(requeue=True)

    async def _process_message(self, body: dict, queue_type: str) -> None:
        ranch_id = body.get("ranch_id")
        animal_id = body.get("animal_id")
        task_id = body.get("task_id")

        if not all([ranch_id, animal_id, task_id]):
            logger.warning(f"Mensaje incompleto en {queue_type}: {body}")
            return

        if queue_type == "forecast":
            result = await self.processor.process_forecasting_task(
                ranch_id,
                animal_id,
                task_id
            )
        elif queue_type == "cluster":
            result = await self.processor.process_clustering_task(
                ranch_id,
                animal_id,
                task_id
            )
        else:
            logger.warning(f"Tipo de cola desconocida: {queue_type}")
            return

        status = result.get("status", "unknown")
        error = result.get("error")

        await self.processor.update_queue_status(
            task_id,
            status.upper(),
            error
        )

        logger.info(f"Mensaje procesado: {task_id} - {status}")