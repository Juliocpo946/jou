from uuid import UUID
from typing import Optional, List
from datetime import datetime
import logging

from src.domain.entities.animal import Animal
from src.ports.persistence.animal_port import AnimalRepository
from src.infrastructure.persistence.postgres_pool import PostgresPool
from src.application.mappers.animal_mapper import AnimalMapper

logger = logging.getLogger(__name__)

class AnimalRepositoryImpl(AnimalRepository):
    
    async def find_by_id(self, animal_id: UUID) -> Optional[Animal]:
        query = """
            SELECT id, ranch_id, lot_id, visual_tag, electronic_tag, name,
                   sex, birth_date, breed, productive_status, reproductive_status,
                   health_score, last_heat_date, last_birth_date, last_insemination_date,
                   current_cluster_label, predicted_sale_date, expected_calving_date,
                   suggested_dry_date, next_likely_heat_date, projected_weight_30d,
                   is_active, server_updated_at, is_deleted
            FROM animals
            WHERE id = %s AND is_deleted = FALSE
        """
        try:
            result = await PostgresPool.execute_one(query, (str(animal_id),))
            if result:
                return AnimalMapper.from_db_row(result)
            return None
        except Exception as e:
            logger.error(f"Error en find_by_id: {str(e)}")
            raise

    async def find_by_ranch(self, ranch_id: UUID) -> List[Animal]:
        query = """
            SELECT id, ranch_id, lot_id, visual_tag, electronic_tag, name,
                   sex, birth_date, breed, productive_status, reproductive_status,
                   health_score, last_heat_date, last_birth_date, last_insemination_date,
                   current_cluster_label, predicted_sale_date, expected_calving_date,
                   suggested_dry_date, next_likely_heat_date, projected_weight_30d,
                   is_active, server_updated_at, is_deleted
            FROM animals
            WHERE ranch_id = %s AND is_deleted = FALSE
            ORDER BY visual_tag
        """
        try:
            results = await PostgresPool.execute(query, (str(ranch_id),))
            return [AnimalMapper.from_db_row(row) for row in results]
        except Exception as e:
            logger.error(f"Error en find_by_ranch: {str(e)}")
            raise

    async def find_active_by_ranch(self, ranch_id: UUID) -> List[Animal]:
        query = """
            SELECT id, ranch_id, lot_id, visual_tag, electronic_tag, name,
                   sex, birth_date, breed, productive_status, reproductive_status,
                   health_score, last_heat_date, last_birth_date, last_insemination_date,
                   current_cluster_label, predicted_sale_date, expected_calving_date,
                   suggested_dry_date, next_likely_heat_date, projected_weight_30d,
                   is_active, server_updated_at, is_deleted
            FROM animals
            WHERE ranch_id = %s AND is_active = TRUE AND is_deleted = FALSE
            ORDER BY visual_tag
        """
        try:
            results = await PostgresPool.execute(query, (str(ranch_id),))
            return [AnimalMapper.from_db_row(row) for row in results]
        except Exception as e:
            logger.error(f"Error en find_active_by_ranch: {str(e)}")
            raise

    async def update_cluster_label(self, animal_id: UUID, label: str) -> bool:
        query = """
            UPDATE animals
            SET current_cluster_label = %s,
                server_updated_at = NOW()
            WHERE id = %s AND is_deleted = FALSE
        """
        try:
            rowcount = await PostgresPool.execute_update(query, (label, str(animal_id)))
            return rowcount > 0
        except Exception as e:
            logger.error(f"Error en update_cluster_label: {str(e)}")
            raise

    async def update_forecast_data(
        self,
        animal_id: UUID,
        predicted_sale_date: Optional[object],
        expected_calving_date: Optional[object],
        suggested_dry_date: Optional[object],
        next_likely_heat_date: Optional[object],
        projected_weight_30d: Optional[float]
    ) -> bool:
        query = """
            UPDATE animals
            SET predicted_sale_date = %s,
                expected_calving_date = %s,
                suggested_dry_date = %s,
                next_likely_heat_date = %s,
                projected_weight_30d = %s,
                server_updated_at = NOW()
            WHERE id = %s AND is_deleted = FALSE
        """
        try:
            rowcount = await PostgresPool.execute_update(
                query,
                (
                    predicted_sale_date,
                    expected_calving_date,
                    suggested_dry_date,
                    next_likely_heat_date,
                    projected_weight_30d,
                    str(animal_id)
                )
            )
            return rowcount > 0
        except Exception as e:
            logger.error(f"Error en update_forecast_data: {str(e)}")
            raise