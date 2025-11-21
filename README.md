Bovara ML Service

Servicio de backend en Python para clustering y forecasting en ganadería.

Arquitectura: Hexagonal + DDD
Base de datos: PostgreSQL (Neon)
Colas: RabbitMQ (CloudAMQP)

Instalación

1. Clonar repositorio y crear venv:
   python -m venv venv
   source venv/bin/activate (Linux/Mac)
   venv\Scripts\activate (Windows)

2. Instalar dependencias:
   pip install -r requirements.txt

3. Configurar variables de entorno:
   cp config/.env.example .env
   Editar .env con tus credenciales

4. Ejecutar servicio:
   python src/main.py

Estructura

src/
  domain/           - Lógica de negocio (entities, repositories, services)
  application/      - Casos de uso (DTOs, mappers, orquestación)
  infrastructure/   - Implementaciones técnicas (BD, queue)
  ports/            - Contratos/interfaces (abstracciones)
  adapters/         - Adaptadores entrada/salida

Desarrollo

Tests unitarios:
  pytest tests/unit/

Tests integración:
  pytest tests/integration/

Linting:
  pylint src/

Variables de Entorno Requeridas

DATABASE_URL
AMQP_URL
QUEUE_NAME_FORECAST
QUEUE_NAME_CLUSTER
WORKER_BATCH_SIZE
WORKER_POLL_INTERVAL
WORKER_MAX_RETRIES