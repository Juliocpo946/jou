import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import logging
from typing import List, Tuple, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MLClusteringModel:

    @staticmethod
    def prepare_features(weight_events: List[Tuple], animal_age_days: int = None) -> np.ndarray:
        if not weight_events or len(weight_events) < 2:
            return None

        sorted_events = sorted(weight_events, key=lambda x: x[0])
        weights = np.array([float(event[1]) for event in sorted_events])
        dates = np.array([event[0] for event in sorted_events])

        gdp = MLClusteringModel._calculate_gdp(weights, dates)
        
        current_weight = weights[-1]
        weight_trend = weights[-1] - weights[-2] if len(weights) >= 2 else 0
        weight_variance = np.std(weights) if len(weights) > 1 else 0
        weight_median = np.median(weights)
        
        features = [
            gdp,
            current_weight,
            weight_trend,
            weight_variance,
            weight_median,
            float(animal_age_days) if animal_age_days else 365
        ]

        return np.array(features).reshape(1, -1)

    @staticmethod
    def _calculate_gdp(weights: np.ndarray, dates: np.ndarray) -> float:
        if len(weights) < 2:
            return 0.0

        days_diff = (dates[-1] - dates[0]).days
        if days_diff == 0:
            return 0.0

        weight_diff = weights[-1] - weights[0]
        gdp = weight_diff / days_diff
        return max(gdp, 0.0)

    @staticmethod
    def train_clustering_model(lote_animals_features: np.ndarray, n_clusters: int = 3) -> Tuple:
        if lote_animals_features is None or len(lote_animals_features) < 3:
            return None, None, None

        try:
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(lote_animals_features)

            kmeans = KMeans(
                n_clusters=min(n_clusters, len(lote_animals_features)),
                random_state=42,
                n_init=10,
                max_iter=300
            )
            kmeans.fit(features_scaled)

            silhouette_avg = silhouette_score(features_scaled, kmeans.labels_)
            
            logger.info(f"Clustering entrenado: {n_clusters} clusters, silhouette: {silhouette_avg:.3f}")

            return kmeans, scaler, silhouette_avg
        except Exception as e:
            logger.error(f"Error entrenando clustering: {str(e)}")
            return None, None, None

    @staticmethod
    def predict_cluster(
        animal_features: np.ndarray,
        kmeans_model,
        scaler
    ) -> Tuple[int, float]:
        if kmeans_model is None or scaler is None or animal_features is None:
            return None, 0.0

        try:
            features_scaled = scaler.transform(animal_features)
            cluster_label = kmeans_model.predict(features_scaled)[0]
            
            distances = np.linalg.norm(
                features_scaled - kmeans_model.cluster_centers_[cluster_label]
            )
            confidence = 1.0 / (1.0 + distances)

            return cluster_label, min(confidence, 1.0)
        except Exception as e:
            logger.error(f"Error prediciendo cluster: {str(e)}")
            return None, 0.0

    @staticmethod
    def map_cluster_to_label(cluster_num: int, cluster_characteristics: Dict) -> Tuple[str, str]:
        if cluster_num is None:
            return "PENDING", "Datos insuficientes"

        gdps = cluster_characteristics.get("gdps", [])
        if not gdps:
            return "PENDING", "Sin datos de GDP"

        cluster_gdp = np.mean(gdps)
        all_gdps = cluster_characteristics.get("all_gdps", [])
        
        if all_gdps:
            p75 = np.percentile(all_gdps, 75)
            p25 = np.percentile(all_gdps, 25)
        else:
            p75 = 0.8
            p25 = 0.4

        if cluster_gdp >= p75:
            return "PRODUCTIVO_A", f"Cluster élite con GDP {cluster_gdp:.2f} kg/día"
        elif cluster_gdp >= p25:
            return "PRODUCTIVO_B", f"Cluster normal con GDP {cluster_gdp:.2f} kg/día"
        else:
            return "PRODUCTIVO_C", f"Cluster rezaga con GDP {cluster_gdp:.2f} kg/día"

    @staticmethod
    def analyze_reproductive_status(
        days_open: int,
        calving_interval: int,
        service_count: int
    ) -> Tuple[str, float, str]:
        features = [days_open, calving_interval, service_count]
        
        if days_open > 150:
            confidence = 0.85
            return "REPRO_PROBLEMA", confidence, f"Días abiertos: {days_open} - ciclo irregular"
        
        if calving_interval > 450:
            confidence = 0.80
            return "REPRO_PROBLEMA", confidence, f"Intervalo: {calving_interval} - prolongado"
        
        if 350 <= calving_interval <= 400 and days_open <= 100:
            confidence = 0.95
            return "REPRO_OPTIMO", confidence, f"Intervalo óptimo: {calving_interval} días"
        
        confidence = 0.70
        return "REPRO_NORMAL", confidence, "Estatus reproductivo aceptable"