from typing import List, Tuple
from datetime import datetime, timedelta
import logging
from statistics import mean, stdev

from src.domain.entities.animal import Animal
from src.domain.value_objects.cluster_label import ClusterLabel

logger = logging.getLogger(__name__)

class ClusteringService:

    @staticmethod
    def calculate_gdp(weight_events: List[Tuple]) -> float:
        if len(weight_events) < 2:
            return 0.0

        sorted_events = sorted(weight_events, key=lambda x: x[0])
        weights = [float(event[1]) for event in sorted_events]
        dates = [event[0] for event in sorted_events]

        first_date = dates[0]
        last_date = dates[-1]
        days_diff = (last_date - first_date).days

        if days_diff == 0:
            return 0.0

        weight_diff = weights[-1] - weights[0]
        gdp = weight_diff / days_diff

        return max(gdp, 0.0)

    @staticmethod
    def calculate_cluster_label(
        animal: Animal,
        weight_events: List[Tuple],
        lote_percentiles: dict,
        health_status: int
    ) -> Tuple[str, float, str]:
        if not weight_events or len(weight_events) < 2:
            return ClusterLabel.PENDING, 0.0, "Datos insuficientes para clustering"

        gdp = ClusteringService.calculate_gdp(weight_events)
        
        if gdp >= lote_percentiles.get("p75", 0.8):
            return (
                ClusterLabel.PRODUCTIVO_A,
                0.9,
                f"GDP {gdp:.2f} kg/día por encima del percentil 75"
            )
        elif gdp >= lote_percentiles.get("p25", 0.4):
            return (
                ClusterLabel.PRODUCTIVO_B,
                0.85,
                f"GDP {gdp:.2f} kg/día dentro del rango normal"
            )
        else:
            return (
                ClusterLabel.PRODUCTIVO_C,
                0.8,
                f"GDP {gdp:.2f} kg/día por debajo del percentil 25 - candidato venta sanitaria"
            )

    @staticmethod
    def calculate_lote_percentiles(all_gdps: List[float]) -> dict:
        if not all_gdps:
            return {"p25": 0.4, "p50": 0.6, "p75": 0.8}

        try:
            sorted_gdps = sorted(all_gdps)
            n = len(sorted_gdps)
            
            p25_idx = int(n * 0.25)
            p50_idx = int(n * 0.50)
            p75_idx = int(n * 0.75)

            return {
                "p25": sorted_gdps[p25_idx],
                "p50": sorted_gdps[p50_idx],
                "p75": sorted_gdps[p75_idx]
            }
        except Exception as e:
            logger.error(f"Error calculando percentiles: {str(e)}")
            return {"p25": 0.4, "p50": 0.6, "p75": 0.8}

    @staticmethod
    def evaluate_reproductive_status(
        animal: Animal,
        days_open: int,
        calving_interval: int
    ) -> Tuple[str, float, str]:
        if days_open > 150:
            return (
                ClusterLabel.REPRO_PROBLEMA,
                0.75,
                f"Días abiertos {days_open} - ciclo irregular o anovulatoria"
            )

        if calving_interval > 450:
            return (
                ClusterLabel.REPRO_PROBLEMA,
                0.75,
                f"Intervalo entre partos {calving_interval} días - problema reproductivo"
            )

        if calving_interval >= 350 and calving_interval <= 400:
            return (
                ClusterLabel.REPRO_OPTIMO,
                0.9,
                f"Intervalo entre partos óptimo: {calving_interval} días"
            )

        return (
            ClusterLabel.REPRO_OPTIMO,
            0.85,
            "Estatus reproductivo normal"
        )