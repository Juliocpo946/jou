from uuid import UUID
from typing import Optional, List
import logging

from src.ports.persistence.event_port import EventRepository
from src.infrastructure.persistence.postgres_pool import PostgresPool

logger = logging.getLogger(__name__)

class EventRepositoryImpl(EventRepository):

    async def find_by_animal(self, animal_id: UUID, days_back: int = 90) -> List[tuple]:
        query = """
            SELECT e.id, e.animal_id, e.ranch_id, e.event_type, e.event_date,
                   e.notes, e.created_by, e.source, e.server_updated_at
            FROM events e
            WHERE e.animal_id = %s
            AND e.event_date >= NOW() - INTERVAL '%s days'
            AND e.is_deleted = FALSE
            ORDER BY e.event_date DESC
        """
        try:
            results = await PostgresPool.execute(query, (str(animal_id), days_back))
            return results
        except Exception as e:
            logger.error(f"Error en find_by_animal: {str(e)}")
            raise

    async def find_weight_events(self, animal_id: UUID, days_back: int = 90) -> List[tuple]:
        query = """
            SELECT e.event_date, ew.weight_kg, ew.body_condition_score
            FROM events e
            JOIN event_weights ew ON e.id = ew.event_id
            WHERE e.animal_id = %s
            AND e.event_date >= NOW() - INTERVAL '%s days'
            AND e.is_deleted = FALSE
            ORDER BY e.event_date DESC
        """
        try:
            results = await PostgresPool.execute(query, (str(animal_id), days_back))
            return results
        except Exception as e:
            logger.error(f"Error en find_weight_events: {str(e)}")
            raise

    async def find_breeding_events(self, animal_id: UUID, days_back: int = 365) -> List[tuple]:
        query = """
            SELECT e.event_date, eb.breeding_type, eb.sire_id, eb.technician_name
            FROM events e
            JOIN event_breeding eb ON e.id = eb.event_id
            WHERE e.animal_id = %s
            AND e.event_date >= NOW() - INTERVAL '%s days'
            AND e.is_deleted = FALSE
            ORDER BY e.event_date DESC
        """
        try:
            results = await PostgresPool.execute(query, (str(animal_id), days_back))
            return results
        except Exception as e:
            logger.error(f"Error en find_breeding_events: {str(e)}")
            raise

    async def find_birth_events(self, animal_id: UUID, days_back: int = 365) -> List[tuple]:
        query = """
            SELECT e.event_date, eb.birth_type, eb.offspring_count, eb.live_births
            FROM events e
            JOIN event_births eb ON e.id = eb.event_id
            WHERE e.animal_id = %s
            AND e.event_date >= NOW() - INTERVAL '%s days'
            AND e.is_deleted = FALSE
            ORDER BY e.event_date DESC
        """
        try:
            results = await PostgresPool.execute(query, (str(animal_id), days_back))
            return results
        except Exception as e:
            logger.error(f"Error en find_birth_events: {str(e)}")
            raise

    async def get_last_event_by_type(self, animal_id: UUID, event_type: str) -> Optional[tuple]:
        query = """
            SELECT e.id, e.event_date, e.event_type
            FROM events e
            WHERE e.animal_id = %s
            AND e.event_type = %s
            AND e.is_deleted = FALSE
            ORDER BY e.event_date DESC
            LIMIT 1
        """
        try:
            result = await PostgresPool.execute_one(query, (str(animal_id), event_type))
            return result
        except Exception as e:
            logger.error(f"Error en get_last_event_by_type: {str(e)}")
            raise