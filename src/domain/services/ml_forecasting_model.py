import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_absolute_error
import logging
from typing import List, Tuple, Optional
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

class MLForecastingModel:

    @staticmethod
    def prepare_weight_series(weight_events: List[Tuple]) -> Tuple[np.ndarray, np.ndarray]:
        if not weight_events or len(weight_events) < 2:
            return None, None

        sorted_events = sorted(weight_events, key=lambda x: x[0])
        
        dates = np.array([event[0] for event in sorted_events])
        weights = np.array([float(event[1]) for event in sorted_events])

        days_from_first = np.array([(d - dates[0]).days for d in dates])

        return days_from_first, weights

    @staticmethod
    def train_weight_regression(
        days_from_first: np.ndarray,
        weights: np.ndarray,
        polynomial_degree: int = 2
    ) -> Tuple:
        if days_from_first is None or weights is None or len(days_from_first) < 3:
            return None, None, None

        try:
            X = days_from_first.reshape(-1, 1)
            
            if polynomial_degree > 1:
                poly = PolynomialFeatures(degree=polynomial_degree)
                X_poly = poly.fit_transform(X)
                model = LinearRegression()
                model.fit(X_poly, weights)
            else:
                model = LinearRegression()
                model.fit(X, weights)

            y_pred = model.predict(X_poly if polynomial_degree > 1 else X)
            r2 = r2_score(weights, y_pred)
            mae = mean_absolute_error(weights, y_pred)

            logger.info(f"Modelo de peso entrenado: R2={r2:.3f}, MAE={mae:.2f}")

            return model, poly if polynomial_degree > 1 else None, r2
        except Exception as e:
            logger.error(f"Error entrenando regresión de peso: {str(e)}")
            return None, None, None

    @staticmethod
    def predict_sale_date(
        current_weight: float,
        target_weight: float,
        model,
        poly_features=None,
        days_from_first: np.ndarray = None,
        current_date: date = None,
        model_r2: float = 0.7
    ) -> Tuple[Optional[date], float]:
        if current_date is None:
            current_date = date.today()

        if current_weight >= target_weight:
            return current_date, 0.95

        if model is None or days_from_first is None:
            return None, 0.0

        try:
            max_days = 730
            for days_ahead in range(1, max_days):
                X_test = np.array([[days_from_first[-1] + days_ahead]])
                
                if poly_features is not None:
                    X_test_transformed = poly_features.transform(X_test)
                    predicted_weight = model.predict(X_test_transformed)[0]
                else:
                    predicted_weight = model.predict(X_test)[0]

                if predicted_weight >= target_weight:
                    confidence = min(model_r2, 0.95)
                    predicted_date = current_date + timedelta(days=days_ahead)
                    return predicted_date, confidence

            return None, 0.3
        except Exception as e:
            logger.error(f"Error prediciendo fecha de venta: {str(e)}")
            return None, 0.0

    @staticmethod
    def predict_weight_30days(
        model,
        poly_features=None,
        days_from_first: np.ndarray = None,
        model_r2: float = 0.7
    ) -> Tuple[float, float]:
        if model is None or days_from_first is None:
            return None, 0.0

        try:
            X_test = np.array([[days_from_first[-1] + 30]])
            
            if poly_features is not None:
                X_test_transformed = poly_features.transform(X_test)
                predicted_weight = model.predict(X_test_transformed)[0]
            else:
                predicted_weight = model.predict(X_test)[0]

            confidence = min(model_r2, 0.90)
            return float(predicted_weight), confidence
        except Exception as e:
            logger.error(f"Error prediciendo peso 30d: {str(e)}")
            return None, 0.0

    @staticmethod
    def predict_breeding_window(
        last_heat_date: Optional[date],
        estrus_cycle_days: int = 21,
        conception_probability: float = 0.65,
        current_date: date = None
    ) -> Tuple[Optional[date], float]:
        if last_heat_date is None or current_date is None:
            current_date = date.today()

        if last_heat_date is None:
            next_heat = current_date + timedelta(days=estrus_cycle_days)
            return next_heat, conception_probability

        days_since_heat = (current_date - last_heat_date).days
        
        if days_since_heat < 0:
            next_heat = last_heat_date
        else:
            cycles_passed = days_since_heat / estrus_cycle_days
            next_cycle = int(np.ceil(cycles_passed))
            next_heat = last_heat_date + timedelta(days=next_cycle * estrus_cycle_days)

        return next_heat, conception_probability

    @staticmethod
    def estimate_conception_success(
        age_days: int,
        health_score: int,
        days_open: int,
        service_count: int
    ) -> float:
        features = np.array([age_days, health_score, days_open, service_count]).reshape(1, -1)
        
        success_rate = 0.80
        
        if age_days < 600 or age_days > 2500:
            success_rate -= 0.15
        
        if health_score < 70:
            success_rate -= 0.20
        
        if days_open > 150:
            success_rate -= 0.25
        
        if service_count > 3:
            success_rate -= (0.10 * (service_count - 3))

        return max(success_rate, 0.1)

    @staticmethod
    def forecast_calving_window(
        last_insemination_date: Optional[date],
        gestation_days: int = 285,
        conception_confidence: float = 0.65,
        current_date: date = None
    ) -> Tuple[Optional[date], float]:
        if last_insemination_date is None or current_date is None:
            current_date = date.today()

        if last_insemination_date is None:
            return None, 0.0

        expected_calving = last_insemination_date + timedelta(days=gestation_days)
        
        if expected_calving < current_date:
            return None, 0.0

        confidence = min(conception_confidence * 0.95, 0.95)
        return expected_calving, confidence

    @staticmethod
    def ensemble_weight_prediction(
        weight_events: List[Tuple],
        target_weight: float,
        current_date: date = None
    ) -> Tuple[Optional[date], float]:
        if current_date is None:
            current_date = date.today()

        if not weight_events or len(weight_events) < 2:
            return None, 0.0

        try:
            days_arr, weights_arr = MLForecastingModel.prepare_weight_series(weight_events)
            
            if days_arr is None:
                return None, 0.0

            linear_model, _, r2_linear = MLForecastingModel.train_weight_regression(
                days_arr, weights_arr, polynomial_degree=1
            )
            poly_model, poly_features, r2_poly = MLForecastingModel.train_weight_regression(
                days_arr, weights_arr, polynomial_degree=2
            )

            linear_date, linear_conf = MLForecastingModel.predict_sale_date(
                weights_arr[-1], target_weight, linear_model, None, days_arr, current_date, r2_linear
            ) if linear_model else (None, 0.0)

            poly_date, poly_conf = MLForecastingModel.predict_sale_date(
                weights_arr[-1], target_weight, poly_model, poly_features, days_arr, current_date, r2_poly
            ) if poly_model else (None, 0.0)

            if linear_conf > poly_conf and linear_date:
                return linear_date, (linear_conf + poly_conf) / 2
            elif poly_date:
                return poly_date, (linear_conf + poly_conf) / 2
            else:
                return None, 0.0

        except Exception as e:
            logger.error(f"Error en ensemble prediction: {str(e)}")
            return None, 0.0