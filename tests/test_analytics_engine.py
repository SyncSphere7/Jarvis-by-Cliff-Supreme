"""
Tests for Supreme Analytics Engine
"""

import pytest
import asyncio
import pandas as pd
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from core.supreme.engines.analytics_engine import (
    SupremeAnalyticsEngine, AnalyticsModel, AnalyticsResult, RealTimeMetric,
    AnalyticsType, ModelType
)
from core.supreme.base_supreme_engine import SupremeRequest


class TestSupremeAnalyticsEngine:
    
    @pytest.fixture
    def mock_config(self):
        return Mock(auto_scaling=True, max_concurrent_operations=10)
    
    @pytest.fixture
    def analytics_engine(self, mock_config):
        return SupremeAnalyticsEngine("test_analytics", mock_config)
    
    @pytest.fixture
    def sample_data(self):
        return [
            {"value": 10, "category": "A", "timestamp": "2024-01-01T00:00:00"},
            {"value": 15, "category": "B", "timestamp": "2024-01-01T01:00:00"},
            {"value": 12, "category": "A", "timestamp": "2024-01-01T02:00:00"},
            {"value": 18, "category": "B", "timestamp": "2024-01-01T03:00:00"},
            {"value": 14, "category": "A", "timestamp": "2024-01-01T04:00:00"}
        ]
    
    @pytest.mark.asyncio
    async def test_initialization(self, analytics_engine):
        """Test analytics engine initialization"""
        with patch.object(analytics_engine, '_load_analytics_data', new_callable=AsyncMock), \
             patch.object(analytics_engine, '_run_real_time_processor', new_callable=AsyncMock), \
             patch.object(analytics_engine, '_initialize_builtin_models', new_callable=AsyncMock):
            
            result = await analytics_engine._initialize_engine()
            assert result is True
            assert len(analytics_engine.analytics_functions) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_data_success(self, analytics_engine, sample_data):
        """Test successful data analysis"""
        with patch.object(analytics_engine, '_descriptive_analysis', new_callable=AsyncMock) as mock_desc:
            mock_desc.return_value = {
                "count": 5,
                "mean": 13.8,
                "std": 3.27,
                "min": 10,
                "max": 18
            }
            
            with patch.object(analytics_engine, '_extract_insights_from_analysis', new_callable=AsyncMock) as mock_insights:
                mock_insights.return_value = ["Data shows normal distribution", "Average value is 13.8"]
                
                parameters = {
                    "data": sample_data,
                    "analysis_type": "descriptive"
                }
                
                result = await analytics_engine._analyze_data(parameters)
                
                assert result["operation"] == "analyze_data"
                assert result["analysis_type"] == "descriptive"
                assert "results" in result
                assert "insights" in result
                assert len(result["insights"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_predictive_model_success(self, analytics_engine):
        """Test successful model creation"""
        with patch.object(analytics_engine, '_initialize_model', new_callable=AsyncMock) as mock_init:
            mock_init.return_value = {"initialized": True}
            
            with patch.object(analytics_engine, '_save_analytics_data', new_callable=AsyncMock):
                parameters = {
                    "model_name": "Test Model",
                    "model_type": "linear_regression",
                    "config": {"learning_rate": 0.01}
                }
                
                result = await analytics_engine._create_predictive_model(parameters)
                
                assert result["operation"] == "create_model"
                assert result["model_name"] == "Test Model"
                assert result["model_type"] == "linear_regression"
                assert result["initialized"] is True
                assert len(analytics_engine.analytics_models) == 1
    
    @pytest.mark.asyncio
    async def test_train_model_success(self, analytics_engine):
        """Test successful model training"""
        # Create a model first
        model = AnalyticsModel(
            model_id="test_model",
            model_name="Test Model",
            model_type=ModelType.LINEAR_REGRESSION,
            model_config={}
        )
        analytics_engine.analytics_models["test_model"] = model
        
        with patch.object(analytics_engine, '_load_data_from_source', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = pd.DataFrame([
                {"feature1": 1, "feature2": 2, "target": 10},
                {"feature1": 2, "feature2": 3, "target": 15},
                {"feature1": 3, "feature2": 4, "target": 20}
            ])
            
            with patch.object(analytics_engine, '_perform_model_training', new_callable=AsyncMock) as mock_train:
                mock_train.return_value = {
                    "model_state": {"trained": True},
                    "metrics": {"mse": 0.5, "r2": 0.95},
                    "training_time": 2.5
                }
                
                with patch.object(analytics_engine, '_save_analytics_data', new_callable=AsyncMock):
                    parameters = {
                        "model_id": "test_model",
                        "training_data": "data.csv",
                        "target_column": "target",
                        "feature_columns": ["feature1", "feature2"]
                    }
                    
                    result = await analytics_engine._train_model(parameters)
                    
                    assert result["operation"] == "train_model"
                    assert result["model_id"] == "test_model"
                    assert result["training_samples"] == 3
                    assert result["performance_metrics"]["mse"] == 0.5
    
    @pytest.mark.asyncio
    async def test_make_prediction_success(self, analytics_engine):
        """Test successful prediction"""
        # Create and add a trained model
        model = AnalyticsModel(
            model_id="test_model",
            model_name="Test Model",
            model_type=ModelType.LINEAR_REGRESSION,
            model_config={},
            model_state={"trained": True}
        )
        analytics_engine.analytics_models["test_model"] = model
        
        with patch.object(analytics_engine, '_perform_prediction', new_callable=AsyncMock) as mock_predict:
            mock_predict.return_value = {
                "predictions": [25.5, 30.2],
                "confidence_scores": [0.85, 0.92],
                "prediction_time": 0.1
            }
            
            parameters = {
                "model_id": "test_model",
                "input_data": [
                    {"feature1": 4, "feature2": 5},
                    {"feature1": 5, "feature2": 6}
                ]
            }
            
            result = await analytics_engine._make_prediction(parameters)
            
            assert result["operation"] == "predict"
            assert result["model_id"] == "test_model"
            assert len(result["predictions"]) == 2
            assert result["predictions"][0] == 25.5
            assert len(result["confidence_scores"]) == 2
    
    @pytest.mark.asyncio
    async def test_process_real_time_data(self, analytics_engine):
        """Test real-time data processing"""
        with patch.object(analytics_engine, '_process_single_data_point', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {"processed": True, "value": 15.0}
            
            with patch.object(analytics_engine, '_check_alert_conditions', new_callable=AsyncMock) as mock_alert:
                mock_alert.return_value = None
                
                with patch.object(analytics_engine, '_calculate_streaming_statistics', new_callable=AsyncMock) as mock_stats:
                    mock_stats.return_value = {
                        "count": 3,
                        "average": 15.0,
                        "min": 10.0,
                        "max": 20.0
                    }
                    
                    parameters = {
                        "stream_id": "test_stream",
                        "data_points": [
                            {"value": 10.0, "tags": {"source": "sensor1"}},
                            {"value": 15.0, "tags": {"source": "sensor2"}},
                            {"value": 20.0, "tags": {"source": "sensor3"}}
                        ]
                    }
                    
                    result = await analytics_engine._process_real_time_data(parameters)
                    
                    assert result["operation"] == "process_realtime"
                    assert result["stream_id"] == "test_stream"
                    assert result["processed_points"] == 3
                    assert result["alerts_triggered"] == 0
                    assert "stream_statistics" in result
    
    @pytest.mark.asyncio
    async def test_generate_insights(self, analytics_engine):
        """Test insight generation"""
        with patch.object(analytics_engine, '_load_data_from_source', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = pd.DataFrame([
                {"value": 10, "category": "A"},
                {"value": 15, "category": "B"},
                {"value": 12, "category": "A"}
            ])
            
            with patch.object(analytics_engine, '_descriptive_analysis', new_callable=AsyncMock) as mock_desc:
                mock_desc.return_value = {"mean": 12.33, "std": 2.52}
                
                with patch.object(analytics_engine, '_generate_trend_insights', new_callable=AsyncMock) as mock_trends:
                    mock_trends.return_value = ["Upward trend detected in category B"]
                    
                    with patch.object(analytics_engine, '_generate_anomaly_insights', new_callable=AsyncMock) as mock_anomalies:
                        mock_anomalies.return_value = ["No significant anomalies detected"]
                        
                        with patch.object(analytics_engine, '_rank_insights', new_callable=AsyncMock) as mock_rank:
                            mock_rank.return_value = [
                                {"insight": "Upward trend detected in category B", "importance": 0.8},
                                {"insight": "No significant anomalies detected", "importance": 0.6}
                            ]
                            
                            parameters = {
                                "data_source": "test_data",
                                "insight_types": ["trends", "anomalies"]
                            }
                            
                            result = await analytics_engine._generate_insights(parameters)
                            
                            assert result["operation"] == "generate_insights"
                            assert result["total_insights"] == 2
                            assert len(result["insights"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_visualization(self, analytics_engine):
        """Test visualization creation"""
        with patch.object(analytics_engine, '_load_data_from_source', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = pd.DataFrame([
                {"x": 1, "y": 10},
                {"x": 2, "y": 15},
                {"x": 3, "y": 12}
            ])
            
            with patch.object(analytics_engine, '_auto_select_chart_type', new_callable=AsyncMock) as mock_chart:
                mock_chart.return_value = "line"
                
                with patch.object(analytics_engine, '_generate_visualization_config', new_callable=AsyncMock) as mock_config:
                    mock_config.return_value = {"type": "line", "x_axis": "x", "y_axis": "y"}
                    
                    with patch.object(analytics_engine, '_prepare_visualization_data', new_callable=AsyncMock) as mock_data:
                        mock_data.return_value = [{"x": 1, "y": 10}, {"x": 2, "y": 15}, {"x": 3, "y": 12}]
                        
                        parameters = {
                            "data_source": "test_data",
                            "chart_type": "auto",
                            "title": "Test Chart"
                        }
                        
                        result = await analytics_engine._create_visualization(parameters)
                        
                        assert result["operation"] == "create_visualization"
                        assert result["chart_type"] == "line"
                        assert result["visualization"]["title"] == "Test Chart"
    
    @pytest.mark.asyncio
    async def test_monitor_real_time_metrics(self, analytics_engine):
        """Test real-time metrics monitoring"""
        # Add some mock metrics
        from collections import deque
        analytics_engine.real_time_metrics["test_stream"] = deque([
            RealTimeMetric("m1", "test_stream", 10.0, datetime.now()),
            RealTimeMetric("m2", "test_stream", 15.0, datetime.now()),
            RealTimeMetric("m3", "test_stream", 12.0, datetime.now())
        ])
        
        with patch.object(analytics_engine, '_get_recent_alerts', new_callable=AsyncMock) as mock_alerts:
            mock_alerts.return_value = []
            
            parameters = {
                "stream_id": "test_stream",
                "time_range": "1h",
                "include_alerts": True
            }
            
            result = await analytics_engine._monitor_real_time_metrics(parameters)
            
            assert result["operation"] == "monitor_metrics"
            assert result["total_streams"] == 1
            assert result["total_metrics"] == 3
            assert "test_stream" in result["streams"]
    
    @pytest.mark.asyncio
    async def test_get_analytics_status_overall(self, analytics_engine):
        """Test getting overall analytics status"""
        # Add some mock data
        model = AnalyticsModel(
            model_id="test_model",
            model_name="Test Model",
            model_type=ModelType.LINEAR_REGRESSION,
            model_config={},
            model_state={"trained": True}
        )
        analytics_engine.analytics_models["test_model"] = model
        
        parameters = {}
        result = await analytics_engine._get_analytics_status(parameters)
        
        assert result["operation"] == "analytics_status"
        assert result["total_models"] == 1
        assert result["trained_models"] == 1
        assert "models" in result
        assert "test_model" in result["models"]
    
    @pytest.mark.asyncio
    async def test_get_analytics_status_specific_model(self, analytics_engine):
        """Test getting status for specific model"""
        model = AnalyticsModel(
            model_id="test_model",
            model_name="Test Model",
            model_type=ModelType.LINEAR_REGRESSION,
            model_config={},
            model_state={"trained": True}
        )
        analytics_engine.analytics_models["test_model"] = model
        
        parameters = {"model_id": "test_model"}
        result = await analytics_engine._get_analytics_status(parameters)
        
        assert result["operation"] == "analytics_status"
        assert result["model_id"] == "test_model"
        assert result["model_name"] == "Test Model"
        assert result["is_trained"] is True
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, analytics_engine):
        """Test getting supported operations"""
        operations = await analytics_engine.get_supported_operations()
        
        expected = [
            "analyze_data", "create_model", "train_model", "predict", "process_realtime",
            "generate_insights", "create_visualization", "monitor_metrics"
        ]
        
        for operation in expected:
            assert operation in operations
    
    @pytest.mark.asyncio
    async def test_execute_operation_routing(self, analytics_engine):
        """Test operation routing"""
        # Test analyze operation
        with patch.object(analytics_engine, '_analyze_data', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = {"analysis": "complete"}
            
            request = SupremeRequest(
                request_id="test_req",
                operation="analyze_data",
                parameters={"data": []}
            )
            
            result = await analytics_engine._execute_operation(request)
            assert result["analysis"] == "complete"
            mock_analyze.assert_called_once()
        
        # Test create model operation
        with patch.object(analytics_engine, '_create_predictive_model', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {"model_id": "test"}
            
            request = SupremeRequest(
                request_id="test_req",
                operation="create_model",
                parameters={"model_name": "test"}
            )
            
            result = await analytics_engine._execute_operation(request)
            assert result["model_id"] == "test"
            mock_create.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])