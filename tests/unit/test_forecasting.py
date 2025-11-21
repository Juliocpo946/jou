import pytest
from datetime import date, timedelta
from src.domain.services.forecasting_service import ForecastingService

def test_forecast_sale_date_basic():
    current_weight = 300.0
    gdp = 1.0
    target_weight = 450.0
    current_date = date.today()
    
    predicted_date, confidence = ForecastingService.forecast_sale_date(
        current_weight,
        gdp,
        target_weight,
        current_date
    )
    
    assert predicted_date is not None
    assert predicted_date > current_date
    assert confidence > 0.5

def test_forecast_sale_date_already_at_target():
    current_weight = 450.0
    gdp = 1.0
    target_weight = 450.0
    current_date = date.today()
    
    predicted_date, confidence = ForecastingService.forecast_sale_date(
        current_weight,
        gdp,
        target_weight,
        current_date
    )
    
    assert predicted_date == current_date
    assert confidence == 1.0

def test_forecast_sale_date_zero_gdp():
    current_weight = 300.0
    gdp = 0.0
    target_weight = 450.0
    
    predicted_date, confidence = ForecastingService.forecast_sale_date(
        current_weight,
        gdp,
        target_weight
    )
    
    assert predicted_date is None
    assert confidence == 0.0

def test_forecast_calving_date():
    insemination_date = date.today() - timedelta(days=100)
    gestation_days = 285
    
    calving_date, confidence = ForecastingService.forecast_calving_date(
        insemination_date,
        gestation_days
    )
    
    assert calving_date is not None
    expected_date = insemination_date + timedelta(days=gestation_days)
    assert calving_date == expected_date
    assert confidence == 0.95

def test_forecast_calving_date_none_insemination():
    calving_date, confidence = ForecastingService.forecast_calving_date(
        None,
        285
    )
    
    assert calving_date is None
    assert confidence == 0.0

def test_forecast_dry_off_date():
    calving_date = date.today() + timedelta(days=30)
    days_to_dry = 60
    
    dry_date, confidence = ForecastingService.forecast_dry_off_date(
        calving_date,
        days_to_dry
    )
    
    assert dry_date is not None
    expected_date = calving_date - timedelta(days=days_to_dry)
    assert dry_date == expected_date

def test_forecast_weight_30days():
    current_weight = 300.0
    gdp = 1.5
    
    projected_weight, confidence = ForecastingService.forecast_weight_30days(
        current_weight,
        gdp
    )
    
    expected_weight = current_weight + (gdp * 30)
    assert projected_weight == expected_weight
    assert confidence > 0.5

def test_calculate_days_open():
    last_birth = date.today() - timedelta(days=100)
    days_open = ForecastingService.calculate_days_open(last_birth)
    
    assert days_open == 100

def test_calculate_days_open_none():
    days_open = ForecastingService.calculate_days_open(None)
    assert days_open == 0

def test_calculate_calving_interval():
    previous_birth = date.today() - timedelta(days=400)
    last_birth = date.today() - timedelta(days=100)
    
    interval = ForecastingService.calculate_calving_interval(previous_birth, last_birth)
    assert interval == 300