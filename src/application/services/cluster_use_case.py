import logging
from uuid import UUID
from datetime import date
import numpy as np

from src.domain.services.ml_clustering_model import MLClusteringModel
from src.infrastructure.persistence.animal_repository_impl import AnimalRepositoryImpl
from src.infrastructure.persistence.event_repository_impl import EventRepositoryImpl
from src.infrastructure.persistence.prediction_repository_impl import PredictionRepositoryImpl
from src.application.mappers.prediction_mapper import PredictionMapper
from src.application.dto.cluster_result_dto import ClusterResultDTO
from datetime import datetime

logger = logging.getLogger(__name__)

class ClusterUseCase:

    def __init__(self):
        self.animal_repo = AnimalRepositoryImpl()
        self.event_repo = EventRepositoryImpl()
        self.prediction_repo = PredictionRepositoryImpl()

    async def execute(self, ranch_id: UUID, animal_id: UUID) -> ClusterResultDTO:
        try:
            animal = await self.animal_repo.find_by_id(animal_id)
            if not animal:
                raise ValueError(f"Animal {animal_id} no encontrado")

            weight_events = await self.event_repo.find_weight_events(animal_id, days_back=90)
            
            if not weight_events or len(weight_events) < 2:
                cluster_label = "PENDING"
                confidence = 0.0
                explanation = "Datos insuficientes de pesajes para clustering"
                severity = "warning"
            else:
                all_animals = await self.animal_repo.find_active_by_ranch(ranch_id)
                
                lote_features = []
                lote_gdps = []
                
                for other_animal in all_animals:
                    other_weight_events = await self.event_repo.find_weight_events(
                        other_animal.id,
                        days_back=90
                    )
                    
                    if other_weight_events and len(other_weight_events) >= 2:
                        age_days = (date.today() - other_animal.birth_date).days if other_animal.birth_date else 365
                        features = MLClusteringModel.prepare_features(other_weight_events, age_days)
                        
                        if features is not None:
                            lote_features.append(features[0])
                            
                            sorted_events = sorted(other_weight_events, key=lambda x: x[0])
                            weights = np.array([float(e[1]) for e in sorted_events])
                            dates = np.array([e[0] for e in sorted_events])
                            gdp = MLClusteringModel._calculate_gdp(weights, dates)
                            lote_gdps.append(gdp)

                if not lote_features or len(lote_features) < 3:
                    cluster_label = "PENDING"
                    confidence = 0.5
                    explanation = "Lote insuficiente para clustering (< 3 animales)"
                    severity = "warning"
                else:
                    lote_features_array = np.array(lote_features)
                    
                    kmeans_model, scaler, silhouette = MLClusteringModel.train_clustering_model(
                        lote_features_array,
                        n_clusters=3
                    )

                    age_days = (date.today() - animal.birth_date).days if animal.birth_date else 365
                    animal_features = MLClusteringModel.prepare_features(weight_events, age_days)

                    cluster_num, confidence = MLClusteringModel.predict_cluster(
                        animal_features,
                        kmeans_model,
                        scaler
                    )

                    cluster_characteristics = {
                        "gdps": lote_gdps,
                        "all_gdps": lote_gdps
                    }

                    cluster_label, explanation = MLClusteringModel.map_cluster_to_label(
                        cluster_num,
                        cluster_characteristics
                    )

                    breeding_events = await self.event_repo.find_breeding_events(animal_id, days_back=365)
                    birth_events = await self.event_repo.find_birth_events(animal_id, days_back=365)

                    if animal.last_birth_date:
                        days_open = (date.today() - animal.last_birth_date).days
                    else:
                        days_open = 0

                    if len(birth_events) >= 2:
                        calving_interval = (birth_events[0][0] - birth_events[1][0]).days
                    else:
                        calving_interval = 0

                    repro_label, repro_conf, repro_explanation = MLClusteringModel.analyze_reproductive_status(
                        days_open,
                        calving_interval,
                        len(breeding_events)
                    )

                    if repro_label == "REPRO_PROBLEMA":
                        cluster_label = repro_label
                        confidence = repro_conf
                        explanation = repro_explanation

                    severity = "warning" if "REZAGA" in cluster_label or "PROBLEMA" in cluster_label else "info"

            await self.animal_repo.update_cluster_label(animal_id, cluster_label)

            prediction = PredictionMapper.to_prediction(
                ranch_id=ranch_id,
                animal_id=animal_id,
                prediction_type="cluster_assignment",
                prediction_date=date.today(),
                confidence_score=confidence,
                explanation=explanation,
                severity=severity
            )
            await self.prediction_repo.save(prediction)

            return ClusterResultDTO(
                animal_id=animal_id,
                ranch_id=ranch_id,
                cluster_label=cluster_label,
                confidence_score=confidence,
                explanation=explanation,
                severity=severity,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error en ClusterUseCase: {str(e)}")
            raise