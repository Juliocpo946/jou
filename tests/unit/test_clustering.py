import pytest
from datetime import datetime, timedelta
from src.domain.services.clustering_service import ClusteringService
from src.domain.value_objects.cluster_label import ClusterLabel

@pytest.fixture
def sample_weight_events():
    today = datetime.now().date()
    return [
        (today - timedelta(days=30), 300.0),
        (today - timedelta(days=20), 320.0),
        (today - timedelta(days=10), 340.0),
        (today, 360.0),
    ]

@pytest.fixture
def low_weight_events():
    today = datetime.now().date()
    return [
        (today - timedelta(days=30), 300.0),
        (today - timedelta(days=20), 310.0),
        (today - timedelta(days=10), 315.0),
        (today, 318.0),
    ]

def test_calculate_gdp_normal(sample_weight_events):
    gdp = ClusteringService.calculate_gdp(sample_weight_events)
    assert gdp > 0
    assert gdp == 2.0

def test_calculate_gdp_low(low_weight_events):
    gdp = ClusteringService.calculate_gdp(low_weight_events)
    assert gdp > 0
    assert gdp < 1.0

def test_calculate_gdp_insufficient_data():
    single_event = [(datetime.now().date(), 300.0)]
    gdp = ClusteringService.calculate_gdp(single_event)
    assert gdp == 0.0

def test_calculate_lote_percentiles():
    gdps = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
    percentiles = ClusteringService.calculate_lote_percentiles(gdps)
    
    assert "p25" in percentiles
    assert "p50" in percentiles
    assert "p75" in percentiles
    assert percentiles["p25"] < percentiles["p50"] < percentiles["p75"]

def test_calculate_lote_percentiles_empty():
    percentiles = ClusteringService.calculate_lote_percentiles([])
    assert percentiles["p25"] == 0.4
    assert percentiles["p50"] == 0.6
    assert percentiles["p75"] == 0.8