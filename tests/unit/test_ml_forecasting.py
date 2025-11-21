import pytest
import numpy as np
from datetime import datetime, timedelta, date
from src.domain.services.ml_forecasting_model import MLForecastingModel

@pytest.fixture
def weight_series():
    today = datetime.now().date()
    return [
        (today - timedelta(days=60), 250.0),
        (today - timedelta(days=45), 280.0),
        (today - timedelta(days=30), 310.0),
        (today - timedelta(days=15), 340.0),
        (today, 370.0),
    ]

def test_prepare_weight_series(weight_series):
    days_arr, weights_arr = MLForecastingModel.prepare_weight_series(weight_series)
    
    assert days_arr is not None
    assert weights_arr is not None
    assert len(days_arr) == 5
    assert len(weights_arr) == 5
    assert weights_arr[0] < weights_arr[-1]

def test_prepare_weight_series_insufficient():
    events = [(datetime.now().date(), 300.0)]
    days_arr, weights_arr = MLForecastingModel.prepare_weight_series(events)
    
    assert days_arr is None
    assert weights_arr is None

def test_train_weight_regression(weight_series):
    days_arr, weights_arr = MLForecastingModel.prepare_weight_series(weight_series)
    
    model, poly_features, r2 = MLForecastingModel.train_weight_regression(
        days_arr, weights_arr, polynomial_degree=1
    )
    
    assert model is not None
    assert r2 > 0.5

def test_train_weight_regression_polynomial(weight_series):
    days_arr, weights_arr = MLForecastingModel.prepare_weight_series(weight_series)
    
    model, poly_features, r2 = MLForecastingModel.train_weight_regression(
        days_arr, weights_arr, polynomial_degree=2
    )
    
    assert model is not None
    assert poly_features is not None
    assert r2 > 0.5

def test_predict_sale_date(weight_series):
    days_arr, weights_arr = MLForecastingModel.prepare_weight_series(weight_series)
    
    model, poly_features, r2 = MLForecastingModel.train_weight_regression(
        days_arr, weights_arr, polynomial_degree=1
    )
    
    current_weight = weights_arr[-1]
    target_weight = 450.0
    
    sale_date, confidence = MLForecastingModel.predict_sale_date(
        current_weight,
        target_weight,
        model,
        None,
        days_arr,
        date.today(),
        r2
    )
    
    if sale_date:
        assert sale_date > date.today()
        assert 0.0 <= confidence <= 1.0

def test_predict_weight_30days(weight_series):
    days_arr, weights_arr = MLForecastingModel.prepare_weight_series(weight_series)
    
    model, poly_features, r2 = MLForecastingModel.train_weight_regression(
        days_arr, weights_arr, polynomial_degree=1
    )
    
    weight_30d, confidence = MLForecastingModel.predict_weight_30days(
        model, None, days_arr, r2
    )
    
    if weight_30d:
        assert weight_30d > weights_arr[-1]
        assert 0.0 <= confidence <= 1.0

def test_predict_breeding_window():
    last_heat = date.today() - timedelta(days=10)
    
    next_heat, confidence = MLForecastingModel.predict_breeding_window(
        last_heat,
        estrus_cycle_days=21,
        conception_probability=0.65
    )
    
    assert next_heat is not None
    assert next_heat > date.today()
    assert confidence == 0.65

def test_estimate_conception_success():
    success = MLForecastingModel.estimate_conception_success(
        age_days=1000,
        health_score=80,
        days_open=80,
        service_count=1
    )
    
    assert 0.0 <= success <= 1.0
    assert success > 0.5

def test_forecast_calving_window():
    insem_date = date.today() - timedelta(days=100)
    
    calving_date, confidence = MLForecastingModel.forecast_calving_window(
        insem_date,
        gestation_days=285,
        conception_confidence=0.75
    )
    
    if calving_date:
        expected = insem_date + timedelta(days=285)
        assert calving_date == expected
        assert 0.7 <= confidence <= 0.95

def test_ensemble_weight_prediction(weight_series):
    sale_date, confidence = MLForecastingModel.ensemble_weight_prediction(
        weight_series,
        target_weight=450.0,
        current_date=date.today()
    )
    
    if sale_date:
        assert sale_date >= date.today()
        assert 0.0 <= confidence <= 1.0