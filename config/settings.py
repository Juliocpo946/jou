import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))

    AMQP_URL: str = os.getenv("AMQP_URL", "")
    AMQP_HOST: str = os.getenv("AMQP_HOST", "")
    AMQP_PORT: int = int(os.getenv("AMQP_PORT", "5671"))
    AMQP_USER: str = os.getenv("AMQP_USER", "")
    AMQP_PASSWORD: str = os.getenv("AMQP_PASSWORD", "")
    AMQP_VHOST: str = os.getenv("AMQP_VHOST", "")

    QUEUE_NAME_FORECAST: str = os.getenv("QUEUE_NAME_FORECAST", "bovara.forecast")
    QUEUE_NAME_CLUSTER: str = os.getenv("QUEUE_NAME_CLUSTER", "bovara.cluster")
    QUEUE_DEAD_LETTER: str = os.getenv("QUEUE_DEAD_LETTER", "bovara.dlq")

    WORKER_BATCH_SIZE: int = int(os.getenv("WORKER_BATCH_SIZE", "50"))
    WORKER_POLL_INTERVAL: int = int(os.getenv("WORKER_POLL_INTERVAL", "10"))
    WORKER_MAX_RETRIES: int = int(os.getenv("WORKER_MAX_RETRIES", "3"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @classmethod
    def validate(cls):
        required_fields = [
            "DATABASE_URL",
            "AMQP_URL",
        ]
        for field in required_fields:
            if not getattr(cls, field):
                raise ValueError(f"Falta variable de entorno requerida: {field}")

settings = Settings()