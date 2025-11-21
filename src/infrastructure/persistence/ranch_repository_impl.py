from uuid import UUID
from typing import Optional
import logging

from src.domain.entities.ranch import Ranch, RanchReproSettings, ProductionGoals
from src.ports.persistence.ranch_port import RanchRepository
from src.infrastructure.persistence.postgres_pool import PostgresPool

logger = logging.getLogger(__name__)

class RanchRepositoryImpl(RanchRepository):

    async def find_by_id(self, ranch_id: UUID) -> Optional[Ranch]:
        query = """
            SELECT id, account_id, name, location
            FROM ranches
            WHERE id = %s AND is_deleted = FALSE
        """
        try:
            result = await PostgresPool.execute_one(query, (str(ranch_id),))
            if result:
                return Ranch(
                    id=UUID(result[0]),
                    account_id=UUID(result[1]),
                    name=result[2],
                    location=result[3]
                )
            return None
        except Exception as e:
            logger.error(f"Error en find_by_id: {str(e)}")
            raise

    async def get_repro_settings(self, ranch_id: UUID) -> Optional[RanchReproSettings]:
        query = """
            SELECT id, ranch_id, avg_gestation_days, estrus_cycle_days,
                   voluntary_waiting_period, days_to_dry_off,
                   gdp_factor_dry_season, gdp_factor_rainy_season
            FROM ranch_repro_settings
            WHERE ranch_id = %s AND is_deleted = FALSE
        """
        try:
            result = await PostgresPool.execute_one(query, (str(ranch_id),))
            if result:
                return RanchReproSettings(
                    id=UUID(result[0]),
                    ranch_id=UUID(result[1]),
                    avg_gestation_days=result[2],
                    estrus_cycle_days=result[3],
                    voluntary_waiting_period=result[4],
                    days_to_dry_off=result[5],
                    gdp_factor_dry_season=float(result[6]),
                    gdp_factor_rainy_season=float(result[7])
                )
            return None
        except Exception as e:
            logger.error(f"Error en get_repro_settings: {str(e)}")
            raise

    async def get_production_goals(self, ranch_id: UUID) -> Optional[ProductionGoals]:
        query = """
            SELECT id, ranch_id, target_sale_weight_kg, max_ranch_capacity_kg
            FROM production_goals
            WHERE ranch_id = %s AND is_deleted = FALSE
        """
        try:
            result = await PostgresPool.execute_one(query, (str(ranch_id),))
            if result:
                return ProductionGoals(
                    id=UUID(result[0]),
                    ranch_id=UUID(result[1]),
                    target_sale_weight_kg=float(result[2]),
                    max_ranch_capacity_kg=float(result[3]) if result[3] else None
                )
            return None
        except Exception as e:
            logger.error(f"Error en get_production_goals: {str(e)}")
            raise