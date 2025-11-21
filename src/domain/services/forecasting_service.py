from typing import List, Tuple, Optional
from datetime import datetime, timedelta, date
import logging

from src.domain.entities.animal import Animal
from src.domain.entities.ranch import RanchReproSettings, ProductionGoals

logger = logging.getLogger(__name__)

class ForecastingService:

    @staticmethod
    def forecast_sale_date(
        current_weight_kg: float,
        gdp_kg_per_day: float,
        target_weight_kg: float,
        current_date: date = None
    ) -> Tuple[Optional[date], float]:
        if current_date is None:
            current_date = date.today()

        if gdp_kg_per_day <= 0:
            return None, 0.0

        if current_weight_kg >= target_weight_kg:
            return current_date, 1.0

        weight_diff = target_weight_kg - current_weight_kg
        days_to_target = int(weight_diff / gdp_kg_per_day)

        if days_to_target < 0:
            days_to_target = 0

        predicted_date = current_date + timedelta(days=days_to_target)
        confidence = min(0.95, 0.7 + (gdp_kg_per_day * 0.1))

        return predicted_date, confidence

    @staticmethod
    def forecast_calving_date(
        last_insemination_date: Optional[date],
        gestation_days: int,
        current_date: date = None
    ) -> Tuple[Optional[date], float]:
        if last_insemination_date is None:
            return None, 0.0

        if current_date is None:
            current_date = date.today()

        expected_calving = last_insemination_date + timedelta(days=gestation_days)
        
        if expected_calving < current_date:
            return None, 0.0

        confidence = 0.95

        return expected_calving, confidence

    @staticmethod
    def forecast_dry_off_date(
        expected_calving_date: Optional[date],
        days_to_dry_off: int,
        current_date: date = None
    ) -> Tuple[Optional[date], float]:
        if expected_calving_date is None:
            return None, 0.0

        if current_date is None:
            current_date = date.today()

        dry_date = expected_calving_date - timedelta(days=days_to_dry_off)

        if dry_date < current_date:
            return current_date, 0.5

        confidence = 0.90

        return dry_date, confidence

    @staticmethod
    def forecast_next_heat_date(
        last_heat_date: Optional[date],
        estrus_cycle_days: int,
        current_date: date = None
    ) -> Tuple[Optional[date], float]:
        if last_heat_date is None:
            return None, 0.0

        if current_date is None:
            current_date = date.today()

        next_heat = last_heat_date + timedelta(days=estrus_cycle_days)

        if next_heat < current_date:
            next_heat = current_date + timedelta(days=estrus_cycle_days)

        confidence = 0.75

        return next_heat, confidence

    @staticmethod
    def forecast_weight_30days(
        current_weight_kg: float,
        gdp_kg_per_day: float
    ) -> Tuple[float, float]:
        projected_weight = current_weight_kg + (gdp_kg_per_day * 30)
        confidence = min(0.85, 0.7 + (gdp_kg_per_day * 0.1))

        return projected_weight, confidence

    @staticmethod
    def calculate_gdp_30days(weight_events: List[Tuple]) -> float:
        if len(weight_events) < 2:
            return 0.5

        sorted_events = sorted(weight_events, key=lambda x: x[0])
        recent_events = sorted_events[-4:] if len(sorted_events) >= 4 else sorted_events

        if len(recent_events) < 2:
            return 0.5

        weights = [float(event[1]) for event in recent_events]
        dates = [event[0] for event in recent_events]

        first_date = dates[0]
        last_date = dates[-1]
        days_diff = (last_date - first_date).days

        if days_diff == 0:
            return 0.5

        weight_diff = weights[-1] - weights[0]
        gdp = weight_diff / days_diff

        return max(gdp, 0.1)

    @staticmethod
    def calculate_days_open(
        last_birth_date: Optional[date],
        current_date: date = None
    ) -> int:
        if last_birth_date is None:
            return 0

        if current_date is None:
            current_date = date.today()

        days = (current_date - last_birth_date).days
        return max(days, 0)

    @staticmethod
    def calculate_calving_interval(
        previous_birth_date: Optional[date],
        last_birth_date: Optional[date]
    ) -> int:
        if previous_birth_date is None or last_birth_date is None:
            return 0

        interval = (last_birth_date - previous_birth_date).days
        return max(interval, 0)