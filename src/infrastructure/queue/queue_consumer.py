import json
import logging
from typing import Callable, Any
from aio_pika import IncomingMessage

from src.ports.queue.queue_consumer_port import QueueConsumerPort
from src.infrastructure.queue.rabbitmq_connection import RabbitMQConnection
from config.settings import settings

logger = logging.getLogger(__name__)

class QueueConsumer(QueueConsumerPort):

    def __init__(self):
        self.queue_forecast = None
        self.queue_cluster = None

    async def connect(self) -> None:
        try:
            await RabbitMQConnection.initialize()
            self.queue_forecast = await RabbitMQConnection.declare_queue(
                settings.QUEUE_NAME_FORECAST,
                durable=True
            )
            self.queue_cluster = await RabbitMQConnection.declare_queue(
                settings.QUEUE_NAME_CLUSTER,
                durable=True
            )
            logger.info("Colas declaradas correctamente")
        except Exception as e:
            logger.error(f"Error conectando a colas: {str(e)}")
            raise

    async def disconnect(self) -> None:
        try:
            await RabbitMQConnection.close()
            logger.info("Desconectado de RabbitMQ")
        except Exception as e:
            logger.error(f"Error desconectando: {str(e)}")
            raise

    async def start_consuming(self, callback: Callable[[Any], None]) -> None:
        try:
            async with self.queue_forecast.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            body = json.loads(message.body.decode())
                            await callback({
                                "queue": "forecast",
                                "message": body,
                                "message_id": message.message_id
                            })
                        except json.JSONDecodeError as e:
                            logger.error(f"Error decodificando mensaje: {str(e)}")
                            await message.nack(requeue=False)
        except Exception as e:
            logger.error(f"Error en consumidor forecast: {str(e)}")
            raise

    async def acknowledge_message(self, message_id: str) -> None:
        logger.debug(f"Mensaje reconocido: {message_id}")

    async def reject_message(self, message_id: str, requeue: bool = True) -> None:
        logger.warning(f"Mensaje rechazado: {message_id}, requeue={requeue}")