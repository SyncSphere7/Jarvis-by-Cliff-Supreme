"""
Tests for Supreme Deployment System
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

from core.supreme.supreme_deployment import (
    SupremeDeploymentManager,
    ConfigurationManager,
    EngineInitializer,
    DeploymentStage,
    DeploymentStatus,
    EngineStatus,
    EngineDeploymentInfo
)


class TestConfigurationManager:
    """Test ConfigurationManager functionality"""
    
    @pytest.fixture
    def config_manager(self):
        return ConfigurationManager()
    
    def test_config_manager_initialization(self, config_manager):
        """Test ConfigurationManager initialization"""
        assert config_manager.config_path.name == "config"
        assert isinstance(config_manager.configurations, dict)
    
    def test_get_default_configuration_development(self, config_manager):
        """Test default configuration for development environment"""
        config = config_manager._get_default_configuration("development")
        
        assert isinstance(config, dict)
        assert "supreme_engines" in config
        assert "orchestration" in config
        assert "security" in config
        assert "monitoring" in config
        
        # Check development-specific settings
        assert config["orchestration"]["max_concurrent_requests"] == 100
        assert config["security"]["encryption_enabled"] is False
        assert config["security"]["authentication_required"] is False
    
    def test_get_default_configuration_production(self, config_manager):
        """Test default configuration for production environment"""
        config = config_manager._get_default_configuration("production")
        
        # Check production-specific settings
        assert config["orchestration"]["max_concurrent_requests"] == 1000
        assert config["security"]["encryption_enabled"] is True
        assert config["security"]["authentication_required"] is True
    
    def test_load_configuration_default(self, config_manager):
        """Test loading configuration when file doesn't exist"""
        with patch.object(config_manager.config_path, 'exists', return_value=False):
            config = config_manager.load_configuration("development")
            
            assert isinstance(config, dict)
            assert "supreme_engines" in config
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "config"}')
    def test_load_configuration_from_file(self, mock_file, config_manager):
        """Test loading configuration from file"""
        with patch.object(config_manager.config_path, 'exists', return_value=True):
            with patch('json.load', return_value={"test": "config"}):
                config = config_manager.load_configuration("test")
                
                assert config == {"test": "config"}


class TestEngineInitializer:
    """Test EngineInitializer functionality"""
    
    @pytest.fixture
    def engine_initializer(self):
        return EngineInitializer()
    
    @pytest.fixture
    def sample_engine_configs(self):
        return {
            "reasoning": {"enabled": True, "priority": 10},
            "analytics": {"enabled": True, "priority": 9},
            "system_control": {"enabled": True, "priority": 8},
            "learning": {"enabled": False, "priority": 7}  # Disabled
        }
    
    def test_engine_initializer_initialization(self, engine_initializer):
        """Test EngineInitializer initialization"""
        assert isinstance(engine_initializer.engine_registry, dict)
        assert isinstance(engine_initializer.engine_dependencies, dict)
        assert len(engine_initializer.engine_registry) == 0
    
    def test_calculate_initialization_order(self, engine_initializer):
        """Test engine initialization order calculation"""
        engine_names = ["analytics", "reasoning", "learning"]
        order = engine_initializer._calculate_initialization_order(engine_names)
        
        # Reasoning should come before analytics (dependency)
        reasoning_index = order.index("reasoning")
        analytics_index = order.index("analytics")
        assert reasoning_index < analytics_index
        
        # Learning should come after analytics (dependency)
        learning_index = order.index("learning")
        assert analytics_index < learning_index
    
    @pytest.mark.asyncio
    async def test_initialize_single_engine_success(self, engine_initializer):
        """Test successful single engine initialization"""
        config = {"enabled": True, "priority": 10}
        
        engine_info = await engine_initializer._initialize_single_engine("reasoning", config)
        
        assert isinstance(engine_info, EngineDeploymentInfo)
        assert engine_info.engine_name == "reasoning"
        assert engine_info.status == EngineStatus.READY
        assert engine_info.initialization_time is not None
        assert engine_info.initialization_time > 0
        assert engine_info.error_message is None
    
    @pytest.mark.asyncio
    async def test_initialize_engines(self, engine_initializer, sample_engine_configs):
        """Test initializing multiple engines"""
        engines = await engine_initializer.initialize_engines(sample_engine_configs)
        
        assert isinstance(engines, dict)
        # Should only initialize enabled engines
        assert len(engines) == 3  # reasoning, analytics, system_control (learning is disabled)
        
        # Check that all initialized engines are ready
        for engine_name, engine_info in engines.items():
            assert engine_info.status == EngineStatus.READY
            assert engine_info.initialization_time is not None
    
    @pytest.mark.asyncio
    async def test_initialize_engines_with_dependencies(self, engine_initializer):
        """Test engine initialization respects dependencies"""
        configs = {
            "reasoning": {"enabled": True},
            "analytics": {"enabled": True}  # Depends on reasoning
        }
        
        engines = await engine_initializer.initialize_engines(configs)
        
        # Both should be initialized successfully
        assert "reasoning" in engines
        assert "analytics" in engines
        assert engines["reasoning"].status == EngineStatus.READY
        assert engines["analytics"].status == EngineStatus.READY


class TestSupremeDeploymentManager:
    """Test SupremeDeploymentManager functionality"""
    
    @pytest.fixture
    def deployment_manager(self):
        return SupremeDeploymentManager()
    
    def test_deployment_manager_initialization(self, deployment_manager):
        """Test SupremeDeploymentManager initialization"""
        assert isinstance(deployment_manager.config_manager, ConfigurationManager)
        assert isinstance(deployment_manager.engine_initializer, EngineInitializer)
        assert isinstance(deployment_manager.deployment_history, list)
        assert len(deployment_manager.deployment_history) == 0
    
    @pytest.mark.asyncio
    async def test_deploy_supreme_system_success(self, deployment_manager):
        """Test successful supreme system deployment"""
        result = await deployment_manager.deploy_supreme_system("development", "1.0.0")
        
        assert isinstance(result, dict)
        assert "deployment_id" in result
        assert result["environment"] == "development"
        assert result["version"] == "1.0.0"
        assert result["status"] == DeploymentStatus.COMPLETED.value
        assert result["stage"] == DeploymentStage.READY.value
        assert "engines_deployed" in result
        assert "deployment_time" in result
        assert result["deployment_time"] > 0
        
        # Check that engines were deployed
        engines_deployed = result["engines_deployed"]
        assert len(engines_deployed) > 0
        
        # Check deployment history
        assert len(deployment_manager.deployment_history) == 1
        assert deployment_manager.deployment_history[0] == result
    
    @pytest.mark.asyncio
    async def test_validate_deployment(self, deployment_manager):
        """Test deployment validation"""
        # Create mock engine deployment info
        engines = {
            "reasoning": EngineDeploymentInfo(
                engine_name="reasoning",
                status=EngineStatus.READY,
                initialization_time=1.0
            ),
            "analytics": EngineDeploymentInfo(
                engine_name="analytics",
                status=EngineStatus.ERROR,
                error_message="Test error"
            )
        }
        
        config = {
            "security": {"encryption_enabled": True},
            "monitoring": {"metrics_enabled": True}
        }
        
        validation_results = await deployment_manager._validate_deployment(engines, config)
        
        assert isinstance(validation_results, dict)
        assert "overall_status" in validation_results
        assert "engine_validation" in validation_results
        assert "configuration_validation" in validation_results
        
        # Should have errors due to failed analytics engine
        assert len(validation_results["errors"]) > 0
        assert validation_results["overall_status"] == "failed"
        
        # Check engine validation
        assert "reasoning" in validation_results["engine_validation"]
        assert "analytics" in validation_results["engine_validation"]
        assert validation_results["engine_validation"]["reasoning"]["passed"] is True
        assert validation_results["engine_validation"]["analytics"]["passed"] is False
    
    @pytest.mark.asyncio
    async def test_activate_system(self, deployment_manager):
        """Test system activation"""
        engines = {
            "reasoning": EngineDeploymentInfo(
                engine_name="reasoning",
                status=EngineStatus.READY
            ),
            "analytics": EngineDeploymentInfo(
                engine_name="analytics",
                status=EngineStatus.READY
            )
        }
        
        await deployment_manager._activate_system(engines)
        
        # All ready engines should now be active
        for engine_info in engines.values():
            assert engine_info.status == EngineStatus.ACTIVE
    
    def test_get_deployment_status(self, deployment_manager):
        """Test getting deployment status"""
        # Add mock deployment to history
        mock_deployment = {
            "deployment_id": "test_deployment",
            "status": "completed"
        }
        deployment_manager.deployment_history.append(mock_deployment)
        
        # Test existing deployment
        status = deployment_manager.get_deployment_status("test_deployment")
        assert status == mock_deployment
        
        # Test non-existent deployment
        status = deployment_manager.get_deployment_status("non_existent")
        assert status is None
    
    def test_get_deployment_history(self, deployment_manager):
        """Test getting deployment history"""
        # Add mock deployments
        for i in range(5):
            deployment_manager.deployment_history.append({
                "deployment_id": f"deployment_{i}",
                "status": "completed"
            })
        
        # Test with limit
        history = deployment_manager.get_deployment_history(limit=3)
        assert len(history) == 3
        assert history == deployment_manager.deployment_history[-3:]
        
        # Test without limit
        history = deployment_manager.get_deployment_history(limit=0)
        assert len(history) == 5
        assert history == deployment_manager.deployment_history
    
    @pytest.mark.asyncio
    async def test_health_check_healthy_system(self, deployment_manager):
        """Test health check for healthy system"""
        # Add mock engines to registry
        deployment_manager.engine_initializer.engine_registry = {
            "reasoning": EngineDeploymentInfo(
                engine_name="reasoning",
                status=EngineStatus.ACTIVE
            ),
            "analytics": EngineDeploymentInfo(
                engine_name="analytics",
                status=EngineStatus.READY
            )
        }
        
        health = await deployment_manager.health_check()
        
        assert isinstance(health, dict)
        assert health["overall_health"] == "healthy"
        assert health["total_engines"] == 2
        assert health["healthy_engines"] == 2
        assert "engine_health" in health
        assert "timestamp" in health
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy_system(self, deployment_manager):
        """Test health check for unhealthy system"""
        # Add mock engines with one in error state
        deployment_manager.engine_initializer.engine_registry = {
            "reasoning": EngineDeploymentInfo(
                engine_name="reasoning",
                status=EngineStatus.ACTIVE
            ),
            "analytics": EngineDeploymentInfo(
                engine_name="analytics",
                status=EngineStatus.ERROR,
                error_message="Test error"
            )
        }
        
        health = await deployment_manager.health_check()
        
        assert health["overall_health"] == "unhealthy"
        assert health["total_engines"] == 2
        assert health["healthy_engines"] == 1


if __name__ == "__main__":
    pytest.main([__file__])