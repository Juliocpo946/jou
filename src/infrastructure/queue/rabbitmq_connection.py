import aio_pika
from aio_pika import Connection, Channel, Queue, Exchange
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class RabbitMQConnection:
    _connection: Connection = None
    _channel: Channel = None

    @classmethod
    async def initialize(cls) -> None:
        if cls._connection is not None:
            return

        try:
            cls._connection = await aio_pika.connect_robust(
                settings.AMQP_URL,
                timeout=10
            )
            cls._channel = await cls._connection.channel()
            logger.info("Conexión RabbitMQ establecida correctamente")
        except Exception as e:
            logger.error(f"Error conectando a RabbitMQ: {str(e)}")
            raise

    @classmethod
    async def close(cls) -> None:
        if cls._connection is not None:
            await cls._connection.close()
            cls._connection = None
            cls._channel = None
            logger.info("Conexión RabbitMQ cerrada")

    @classmethod
    async def get_channel(cls) -> Channel:
        if cls._channel is None:
            raise RuntimeError("Canal RabbitMQ no inicializado")
        return cls._channel

    @classmethod
    async def declare_queue(cls, queue_name: str, durable: bool = True) -> Queue:
        channel = await cls.get_channel()
        queue = await channel.declare_queue(queue_name, durable=durable)
        return queue

    @classmethod
    async def declare_exchange(
        cls,
        exchange_name: str,
        exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.DIRECT,
        durable: bool = True
    ) -> Exchange:
        channel = await cls.get_channel()
        exchange = await channel.declare_exchange(
            exchange_name,
            exchange_type,
            durable=durable
        )
        return exchange

    @classmethod
    async def get_connection(cls) -> Connection:
        if cls._connection is None:
            raise RuntimeError("Conexión RabbitMQ no inicializada")
        return cls._connection