import pytest
import numpy as np
from datetime import datetime, timedelta, date
from src.domain.services.ml_clustering_model import MLClusteringModel

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

def test_prepare_features(sample_weight_events):
    features = MLClusteringModel.prepare_features(sample_weight_events, animal_age_days=500)
    
    assert features is not None
    assert features.shape == (1, 6)

def test_prepare_features_insufficient_data():
    single_event = [(datetime.now().date(), 300.0)]
    features = MLClusteringModel.prepare_features(single_event)
    
    assert features is None

def test_calculate_gdp(sample_weight_events):
    sorted_events = sorted(sample_weight_events, key=lambda x: x[0])
    weights = np.array([float(event[1]) for event in sorted_events])
    dates = np.array([event[0] for event in sorted_events])
    
    gdp = MLClusteringModel._calculate_gdp(weights, dates)
    
    assert gdp > 0
    assert gdp == 2.0

def test_train_clustering_model(sample_weight_events, low_weight_events):
    features_list = []
    
    for events in [sample_weight_events, low_weight_events, sample_weight_events]:
        features = MLClusteringModel.prepare_features(events, 500)
        if features is not None:
            features_list.append(features[0])
    
    features_array = np.array(features_list)
    kmeans, scaler, silhouette = MLClusteringModel.train_clustering_model(features_array, n_clusters=2)
    
    assert kmeans is not None
    assert scaler is not None
    assert silhouette >= -1.0 and silhouette <= 1.0

def test_predict_cluster(sample_weight_events):
    features_list = []
    for i in range(5):
        features = MLClusteringModel.prepare_features(sample_weight_events, 500 + i*100)
        if features is not None:
            features_list.append(features[0])
    
    features_array = np.array(features_list)
    kmeans, scaler, _ = MLClusteringModel.train_clustering_model(features_array, n_clusters=2)
    
    test_features = MLClusteringModel.prepare_features(sample_weight_events, 600)
    cluster_num, confidence = MLClusteringModel.predict_cluster(test_features, kmeans, scaler)
    
    assert cluster_num is not None
    assert 0 <= confidence <= 1.0

def test_analyze_reproductive_status():
    label, conf, exp = MLClusteringModel.analyze_reproductive_status(
        days_open=80,
        calving_interval=380,
        service_count=1
    )
    
    assert label == "REPRO_OPTIMO"
    assert conf == 0.95

def test_analyze_reproductive_status_problema():
    label, conf, exp = MLClusteringModel.analyze_reproductive_status(
        days_open=200,
        calving_interval=500,
        service_count=3
    )
    
    assert label == "REPRO_PROBLEMA"
    assert conf > 0.75