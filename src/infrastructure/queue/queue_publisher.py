import json
import logging
from typing import Dict, Any

from src.ports.queue.queue_publisher_port import QueuePublisherPort
from src.infrastructure.queue.rabbitmq_connection import RabbitMQConnection
import aio_pika

logger = logging.getLogger(__name__)

class QueuePublisher(QueuePublisherPort):

    async def connect(self) -> None:
        try:
            await RabbitMQConnection.initialize()
            logger.info("Publicador conectado a RabbitMQ")
        except Exception as e:
            logger.error(f"Error conectando publicador: {str(e)}")
            raise

    async def disconnect(self) -> None:
        try:
            await RabbitMQConnection.close()
            logger.info("Publicador desconectado de RabbitMQ")
        except Exception as e:
            logger.error(f"Error desconectando publicador: {str(e)}")
            raise

    async def publish(self, queue_name: str, message: Dict[str, Any]) -> bool:
        try:
            channel = await RabbitMQConnection.get_channel()
            queue = await channel.get_queue(queue_name)
            
            message_body = json.dumps(message).encode()
            amqp_message = aio_pika.Message(
                body=message_body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await queue.put(amqp_message)
            logger.debug(f"Mensaje publicado en {queue_name}")
            return True
        except Exception as e:
            logger.error(f"Error publicando en {queue_name}: {str(e)}")
            return False