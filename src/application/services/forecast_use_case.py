import logging
from uuid import UUID
from datetime import date
import numpy as np

from src.domain.services.ml_forecasting_model import MLForecastingModel
from src.infrastructure.persistence.animal_repository_impl import AnimalRepositoryImpl
from src.infrastructure.persistence.event_repository_impl import EventRepositoryImpl
from src.infrastructure.persistence.ranch_repository_impl import RanchRepositoryImpl
from src.infrastructure.persistence.prediction_repository_impl import PredictionRepositoryImpl
from src.application.mappers.prediction_mapper import PredictionMapper
from src.application.dto.forecast_result_dto import ForecastResultDTO
from datetime import datetime

logger = logging.getLogger(__name__)

class ForecastUseCase:

    def __init__(self):
        self.animal_repo = AnimalRepositoryImpl()
        self.event_repo = EventRepositoryImpl()
        self.ranch_repo = RanchRepositoryImpl()
        self.prediction_repo = PredictionRepositoryImpl()

    async def execute(self, ranch_id: UUID, animal_id: UUID) -> ForecastResultDTO:
        try:
            animal = await self.animal_repo.find_by_id(animal_id)
            if not animal:
                raise ValueError(f"Animal {animal_id} no encontrado")

            repro_settings = await self.ranch_repo.get_repro_settings(ranch_id)
            production_goals = await self.ranch_repo.get_production_goals(ranch_id)

            if not repro_settings or not production_goals:
                raise ValueError(f"Configuración faltante para rancho {ranch_id}")

            weight_events = await self.event_repo.find_weight_events(animal_id, days_back=90)
            
            if weight_events:
                current_weight = float(weight_events[0][1])
                
                days_arr, weights_arr = MLForecastingModel.prepare_weight_series(weight_events)
                
                if days_arr is not None and len(days_arr) >= 3:
                    linear_model, _, r2_linear = MLForecastingModel.train_weight_regression(
                        days_arr, weights_arr, polynomial_degree=1
                    )
                    
                    predicted_sale_date, sale_confidence = MLForecastingModel.predict_sale_date(
                        current_weight,
                        production_goals.target_sale_weight_kg,
                        linear_model,
                        None,
                        days_arr,
                        date.today(),
                        r2_linear if r2_linear else 0.7
                    )

                    projected_weight_30d, weight_confidence = MLForecastingModel.predict_weight_30days(
                        linear_model,
                        None,
                        days_arr,
                        r2_linear if r2_linear else 0.7
                    )
                else:
                    predicted_sale_date, sale_confidence = None, 0.3
                    projected_weight_30d, weight_confidence = None, 0.3
            else:
                current_weight = 0.0
                predicted_sale_date, sale_confidence = None, 0.0
                projected_weight_30d, weight_confidence = None, 0.0

            expected_calving_date, calving_confidence = MLForecastingModel.forecast_calving_window(
                animal.last_insemination_date,
                repro_settings.avg_gestation_days,
                0.65,
                date.today()
            )

            if expected_calving_date:
                suggested_dry_date, dry_confidence = MLForecastingModel.forecast_calving_window(
                    animal.last_insemination_date,
                    repro_settings.avg_gestation_days - repro_settings.days_to_dry_off,
                    0.70,
                    date.today()
                )
            else:
                suggested_dry_date, dry_confidence = None, 0.0

            next_likely_heat_date, heat_confidence = MLForecastingModel.predict_breeding_window(
                animal.last_heat_date,
                repro_settings.estrus_cycle_days,
                0.65,
                date.today()
            )

            age_days = (date.today() - animal.birth_date).days if animal.birth_date else 365
            
            breeding_events = await self.event_repo.find_breeding_events(animal_id, days_back=365)
            
            if animal.last_birth_date:
                days_open = (date.today() - animal.last_birth_date).days
            else:
                days_open = 0

            conception_success = MLForecastingModel.estimate_conception_success(
                age_days,
                animal.health_score,
                days_open,
                len(breeding_events)
            )

            overall_confidence = np.mean([
                sale_confidence if sale_confidence else 0.3,
                calving_confidence if calving_confidence else 0.3,
                dry_confidence if dry_confidence else 0.3,
                heat_confidence if heat_confidence else 0.3,
                conception_success
            ])

            explanation = self._generate_explanation(
                predicted_sale_date,
                expected_calving_date,
                current_weight,
                conception_success
            )

            severity = "info" if overall_confidence >= 0.70 else "warning"

            await self.animal_repo.update_forecast_data(
                animal_id,
                predicted_sale_date,
                expected_calving_date,
                suggested_dry_date,
                next_likely_heat_date,
                projected_weight_30d
            )

            prediction = PredictionMapper.to_prediction(
                ranch_id=ranch_id,
                animal_id=animal_id,
                prediction_type="forecast_update",
                prediction_date=date.today(),
                confidence_score=overall_confidence,
                explanation=explanation,
                severity=severity
            )
            await self.prediction_repo.save(prediction)

            return ForecastResultDTO(
                animal_id=animal_id,
                ranch_id=ranch_id,
                predicted_sale_date=predicted_sale_date,
                expected_calving_date=expected_calving_date,
                suggested_dry_date=suggested_dry_date,
                next_likely_heat_date=next_likely_heat_date,
                projected_weight_30d=projected_weight_30d,
                confidence_score=overall_confidence,
                explanation=explanation,
                severity=severity,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error en ForecastUseCase: {str(e)}")
            raise

    def _generate_explanation(
        self,
        predicted_sale_date,
        expected_calving_date,
        current_weight,
        conception_success
    ) -> str:
        parts = []

        if predicted_sale_date:
            parts.append(f"Venta estimada: {predicted_sale_date.isoformat()}")

        if expected_calving_date:
            parts.append(f"Parto esperado: {expected_calving_date.isoformat()}")

        if current_weight > 0:
            parts.append(f"Peso actual: {current_weight:.1f} kg")

        if conception_success > 0:
            parts.append(f"Éxito concepción: {conception_success*100:.0f}%")

        return " | ".join(parts) if parts else "Sin datos suficientes"