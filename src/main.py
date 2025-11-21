import asyncio
import logging
import sys
import signal

from config.settings import settings
from src.infrastructure.persistence.postgres_pool import PostgresPool
from src.adapters.input.queue_consumer_adapter import QueueConsumerAdapter

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class MLServiceWorker:

    def __init__(self):
        self.consumer_adapter = QueueConsumerAdapter()
        self.running = False

    async def start(self) -> None:
        try:
            logger.info("Iniciando servicio ML de Bovara")
            settings.validate()

            await PostgresPool.initialize()
            logger.info("Base de datos PostgreSQL inicializada")

            await self.consumer_adapter.start()
            self.running = True

            logger.info("Servicio ML en ejecución. Esperando mensajes...")

            await self._wait_for_shutdown()

        except KeyboardInterrupt:
            logger.info("Servicio interrumpido por usuario")
        except Exception as e:
            logger.error(f"Error fatal en servicio: {str(e)}")
            sys.exit(1)
        finally:
            await self.stop()

    async def stop(self) -> None:
        logger.info("Deteniendo servicio ML")
        try:
            await self.consumer_adapter.stop()
        except Exception as e:
            logger.error(f"Error deteniendo consumer: {str(e)}")

        try:
            await PostgresPool.close()
        except Exception as e:
            logger.error(f"Error cerrando BD: {str(e)}")

        self.running = False
        logger.info("Servicio detenido")

    async def _wait_for_shutdown(self) -> None:
        loop = asyncio.get_event_loop()
        shutdown_event = asyncio.Event()

        def signal_handler(sig, frame):
            logger.info(f"Señal {sig} recibida")
            shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        await shutdown_event.wait()

async def main():
    worker = MLServiceWorker()
    await worker.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servicio finalizado")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error no manejado: {str(e)}")
        sys.exit(1)