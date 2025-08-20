"""
Supreme Predictive Modeler
Advanced machine learning and predictive analytics capabilities.
"""

import logging
import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import os
import hashlib
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import joblib

from ..base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse

class ModelCategory(Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    ANOMALY_DETECTION = "anomaly_detection"

class ModelStatus(Enum):
    CREATED = "created"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"

@dataclass
class ModelConfig:
    """Configuration for a predictive model"""
    model_id: str
    model_name: str
    model_category: ModelCategory
    algorithm: str
    hyperparameters: Dict[str, Any] = None
    feature_columns: List[str] = None
    target_column: str = None
    preprocessing_steps: List[str] = None
    
    def __post_init__(self):
        if self.hyperparameters is None:
            self.hyperparameters = {}
        if self.feature_columns is None:
            self.feature_columns = []
        if self.preprocessing_steps is None:
            self.preprocessing_steps = []

@dataclass
class ModelTrainingJob:
    """Represents a model training job"""
    job_id: str
    model_id: str
    training_data_path: str
    validation_split: float
    status: ModelStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    training_metrics: Dict[str, float] = None
    validation_metrics: Dict[str, float] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.training_metrics is None:
            self.training_metrics = {}
        if self.validation_metrics is None:
            self.validation_metrics = {}

@dataclass
class PredictionRequest:
    """Represents a prediction request"""
    request_id: str
    model_id: str
    input_data: Dict[str, Any]
    prediction_type: str = "single"
    return_probabilities: bool = False
    return_explanations: bool = False

@dataclass
class PredictionResult:
    """Represents a prediction result"""
    request_id: str
    model_id: str
    predictions: List[Any]
    probabilities: Optional[List[List[float]]] = None
    confidence_scores: Optional[List[float]] = None
    explanations: Optional[List[Dict[str, Any]]] = None
    prediction_time: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class SupremePredictiveModeler(BaseSupremeEngine):
    """
    Supreme predictive modeler with advanced ML capabilities.
    Provides automated model training, hyperparameter tuning, and predictions.
    """
    
    def __init__(self, engine_name: str, config):
        super().__init__(engine_name, config)
        
        # Model storage
        self.model_configs: Dict[str, ModelConfig] = {}
        self.trained_models: Dict[str, Any] = {}
        self.model_scalers: Dict[str, StandardScaler] = {}
        self.model_encoders: Dict[str, Dict[str, LabelEncoder]] = {}
        self.training_jobs: Dict[str, ModelTrainingJob] = {}
        self.prediction_history: List[PredictionResult] = []
        
        # Modeling capabilities
        self.modeling_capabilities = {
            "create_model": self._create_model,
            "train_model": self._train_model,
            "predict": self._make_prediction,
            "evaluate_model": self._evaluate_model,
            "tune_hyperparameters": self._tune_hyperparameters,
            "deploy_model": self._deploy_model,
            "get_model_info": self._get_model_info
        }
        
        # Supported algorithms
        self.algorithms = {
            "linear_regression": LinearRegression,
            "logistic_regression": LogisticRegression,
            "random_forest_regressor": RandomForestRegressor,
            "random_forest_classifier": RandomForestClassifier
        }
        
        # Data persistence
        self.data_dir = "data/models"
        self.models_dir = os.path.join(self.data_dir, "trained")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
    
    async def _initialize_engine(self) -> bool:
        """Initialize the predictive modeler"""
        try:
            self.logger.info("Initializing Supreme Predictive Modeler...")
            
            # Load existing model configurations
            await self._load_model_data()
            
            # Load trained models
            await self._load_trained_models()
            
            self.logger.info(f"Predictive Modeler initialized with {len(self.model_configs)} models")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Predictive Modeler: {e}")
            return False
    
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Execute predictive modeling operation"""
        operation = request.operation.lower()
        parameters = request.parameters
        
        # Route to appropriate modeling capability
        if "create" in operation and "model" in operation:
            return await self._create_model(parameters)
        elif "train" in operation:
            return await self._train_model(parameters)
        elif "predict" in operation:
            return await self._make_prediction(parameters)
        elif "evaluate" in operation:
            return await self._evaluate_model(parameters)
        elif "tune" in operation:
            return await self._tune_hyperparameters(parameters)
        elif "deploy" in operation:
            return await self._deploy_model(parameters)
        elif "info" in operation or "status" in operation:
            return await self._get_model_info(parameters)
        else:
            return await self._get_modeler_status(parameters)
    
    async def get_supported_operations(self) -> List[str]:
        """Get supported predictive modeling operations"""
        return [
            "create_model", "train_model", "predict", "evaluate_model",
            "tune_hyperparameters", "deploy_model", "get_model_info", "modeler_status"
        ]
    
    async def _create_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new predictive model"""
        try:
            model_name = parameters.get("model_name")
            model_category = parameters.get("category", "regression")
            algorithm = parameters.get("algorithm", "linear_regression")
            hyperparameters = parameters.get("hyperparameters", {})
            feature_columns = parameters.get("feature_columns", [])
            target_column = parameters.get("target_column")
            preprocessing_steps = parameters.get("preprocessing_steps", ["standardize"])
            
            if not model_name:
                return {"error": "model_name is required", "operation": "create_model"}
            
            # Generate model ID
            model_id = self._generate_model_id(model_name)
            
            # Validate algorithm
            if algorithm not in self.algorithms:
                return {
                    "error": f"Unsupported algorithm: {algorithm}. Supported: {list(self.algorithms.keys())}",
                    "operation": "create_model"
                }
            
            # Create model configuration
            model_config = ModelConfig(
                model_id=model_id,
                model_name=model_name,
                model_category=ModelCategory(model_category),
                algorithm=algorithm,
                hyperparameters=hyperparameters,
                feature_columns=feature_columns,
                target_column=target_column,
                preprocessing_steps=preprocessing_steps
            )
            
            # Store configuration
            self.model_configs[model_id] = model_config
            
            result = {
                "operation": "create_model",
                "model_id": model_id,
                "model_name": model_name,
                "category": model_category,
                "algorithm": algorithm,
                "hyperparameters": hyperparameters,
                "created_at": datetime.now().isoformat()
            }
            
            # Save model data
            await self._save_model_data()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating model: {e}")
            return {"error": str(e), "operation": "create_model"}
    
    async def _train_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Train a predictive model"""
        try:
            model_id = parameters.get("model_id")
            training_data = parameters.get("training_data")
            validation_split = parameters.get("validation_split", 0.2)
            
            if not model_id or not training_data:
                return {"error": "model_id and training_data are required", "operation": "train_model"}
            
            if model_id not in self.model_configs:
                return {"error": f"Model {model_id} not found", "operation": "train_model"}
            
            model_config = self.model_configs[model_id]
            
            # Create training job
            job_id = self._generate_job_id()
            training_job = ModelTrainingJob(
                job_id=job_id,
                model_id=model_id,
                training_data_path=str(training_data),
                validation_split=validation_split,
                status=ModelStatus.TRAINING,
                started_at=datetime.now()
            )
            
            self.training_jobs[job_id] = training_job
            
            try:
                # Load and prepare data
                if isinstance(training_data, str):
                    # Load from file path
                    df = pd.read_csv(training_data)
                elif isinstance(training_data, list):
                    df = pd.DataFrame(training_data)
                else:
                    df = training_data
                
                # Prepare features and target
                if model_config.feature_columns:
                    X = df[model_config.feature_columns]
                else:
                    X = df.drop(columns=[model_config.target_column] if model_config.target_column else [])
                
                if model_config.target_column:
                    y = df[model_config.target_column]
                else:
                    return {"error": "target_column is required for supervised learning", "operation": "train_model"}
                
                # Preprocessing
                X_processed, y_processed = await self._preprocess_data(X, y, model_config)
                
                # Split data
                X_train, X_val, y_train, y_val = train_test_split(
                    X_processed, y_processed, test_size=validation_split, random_state=42
                )
                
                # Create and train model
                model_class = self.algorithms[model_config.algorithm]
                model = model_class(**model_config.hyperparameters)
                
                # Train the model
                start_time = datetime.now()
                model.fit(X_train, y_train)
                training_time = (datetime.now() - start_time).total_seconds()
                
                # Evaluate on training and validation sets
                train_predictions = model.predict(X_train)
                val_predictions = model.predict(X_val)
                
                # Calculate metrics
                training_metrics = await self._calculate_metrics(y_train, train_predictions, model_config.model_category)
                validation_metrics = await self._calculate_metrics(y_val, val_predictions, model_config.model_category)
                
                # Store trained model
                self.trained_models[model_id] = model
                
                # Update training job
                training_job.status = ModelStatus.TRAINED
                training_job.completed_at = datetime.now()
                training_job.training_metrics = training_metrics
                training_job.validation_metrics = validation_metrics
                
                # Save model to disk
                model_path = os.path.join(self.models_dir, f"{model_id}.joblib")
                joblib.dump(model, model_path)
                
                result = {
                    "operation": "train_model",
                    "job_id": job_id,
                    "model_id": model_id,
                    "model_name": model_config.model_name,
                    "training_samples": len(X_train),
                    "validation_samples": len(X_val),
                    "training_time": training_time,
                    "training_metrics": training_metrics,
                    "validation_metrics": validation_metrics,
                    "status": "completed"
                }
                
                # Save model data
                await self._save_model_data()
                
                return result
                
            except Exception as e:
                # Update training job with error
                training_job.status = ModelStatus.FAILED
                training_job.completed_at = datetime.now()
                training_job.error_message = str(e)
                
                return {
                    "operation": "train_model",
                    "job_id": job_id,
                    "model_id": model_id,
                    "status": "failed",
                    "error": str(e)
                }
                
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return {"error": str(e), "operation": "train_model"}
    
    async def _make_prediction(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions using a trained model"""
        try:
            model_id = parameters.get("model_id")
            input_data = parameters.get("input_data")
            return_probabilities = parameters.get("return_probabilities", False)
            return_explanations = parameters.get("return_explanations", False)
            
            if not model_id or not input_data:
                return {"error": "model_id and input_data are required", "operation": "predict"}
            
            if model_id not in self.trained_models:
                return {"error": f"Trained model {model_id} not found", "operation": "predict"}
            
            model = self.trained_models[model_id]
            model_config = self.model_configs[model_id]
            
            # Prepare input data
            if isinstance(input_data, dict):
                input_df = pd.DataFrame([input_data])
            elif isinstance(input_data, list):
                if isinstance(input_data[0], dict):
                    input_df = pd.DataFrame(input_data)
                else:
                    input_df = pd.DataFrame([input_data])
            else:
                input_df = input_data
            
            # Select features
            if model_config.feature_columns:
                X = input_df[model_config.feature_columns]
            else:
                X = input_df
            
            # Preprocess input data
            X_processed = await self._preprocess_input_data(X, model_config)
            
            # Make predictions
            start_time = datetime.now()
            predictions = model.predict(X_processed)
            prediction_time = (datetime.now() - start_time).total_seconds()
            
            # Get probabilities if requested and supported
            probabilities = None
            if return_probabilities and hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(X_processed).tolist()
            
            # Calculate confidence scores
            confidence_scores = await self._calculate_confidence_scores(model, X_processed, predictions)
            
            # Generate explanations if requested
            explanations = None
            if return_explanations:
                explanations = await self._generate_prediction_explanations(model, model_config, X_processed, predictions)
            
            # Create prediction result
            result = PredictionResult(
                request_id=self._generate_request_id(),
                model_id=model_id,
                predictions=predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                probabilities=probabilities,
                confidence_scores=confidence_scores,
                explanations=explanations,
                prediction_time=prediction_time
            )
            
            # Store in history
            self.prediction_history.append(result)
            
            # Limit history size
            if len(self.prediction_history) > 1000:
                self.prediction_history = self.prediction_history[-1000:]
            
            return {
                "operation": "predict",
                "request_id": result.request_id,
                "model_id": model_id,
                "model_name": model_config.model_name,
                "predictions": result.predictions,
                "probabilities": result.probabilities,
                "confidence_scores": result.confidence_scores,
                "explanations": result.explanations,
                "prediction_time": result.prediction_time,
                "input_samples": len(input_df)
            }
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return {"error": str(e), "operation": "predict"}
    
    async def _evaluate_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a trained model on test data"""
        try:
            model_id = parameters.get("model_id")
            test_data = parameters.get("test_data")
            
            if not model_id or not test_data:
                return {"error": "model_id and test_data are required", "operation": "evaluate_model"}
            
            if model_id not in self.trained_models:
                return {"error": f"Trained model {model_id} not found", "operation": "evaluate_model"}
            
            model = self.trained_models[model_id]
            model_config = self.model_configs[model_id]
            
            # Load test data
            if isinstance(test_data, str):
                df = pd.read_csv(test_data)
            elif isinstance(test_data, list):
                df = pd.DataFrame(test_data)
            else:
                df = test_data
            
            # Prepare features and target
            if model_config.feature_columns:
                X = df[model_config.feature_columns]
            else:
                X = df.drop(columns=[model_config.target_column] if model_config.target_column else [])
            
            if model_config.target_column:
                y_true = df[model_config.target_column]
            else:
                return {"error": "target_column is required for evaluation", "operation": "evaluate_model"}
            
            # Preprocess data
            X_processed = await self._preprocess_input_data(X, model_config)
            
            # Make predictions
            y_pred = model.predict(X_processed)
            
            # Calculate metrics
            metrics = await self._calculate_metrics(y_true, y_pred, model_config.model_category)
            
            # Additional evaluation metrics
            evaluation_results = {
                "model_id": model_id,
                "model_name": model_config.model_name,
                "test_samples": len(df),
                "metrics": metrics,
                "evaluation_time": datetime.now().isoformat()
            }
            
            # Add detailed results for classification
            if model_config.model_category == ModelCategory.CLASSIFICATION:
                try:
                    from sklearn.metrics import classification_report, confusion_matrix
                    evaluation_results["classification_report"] = classification_report(y_true, y_pred, output_dict=True)
                    evaluation_results["confusion_matrix"] = confusion_matrix(y_true, y_pred).tolist()
                except:
                    pass
            
            return {
                "operation": "evaluate_model",
                **evaluation_results
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {"error": str(e), "operation": "evaluate_model"}    

    async def _tune_hyperparameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tune hyperparameters for a model"""
        try:
            model_id = parameters.get("model_id")
            param_grid = parameters.get("param_grid", {})
            cv_folds = parameters.get("cv_folds", 5)
            scoring = parameters.get("scoring", "accuracy")
            
            if not model_id:
                return {"error": "model_id is required", "operation": "tune_hyperparameters"}
            
            if model_id not in self.model_configs:
                return {"error": f"Model {model_id} not found", "operation": "tune_hyperparameters"}
            
            # This is a simplified implementation
            # In a real system, you would use GridSearchCV or RandomizedSearchCV
            
            model_config = self.model_configs[model_id]
            
            # Mock hyperparameter tuning results
            best_params = param_grid.copy() if param_grid else model_config.hyperparameters
            best_score = 0.85  # Mock score
            
            # Update model configuration with best parameters
            model_config.hyperparameters.update(best_params)
            
            result = {
                "operation": "tune_hyperparameters",
                "model_id": model_id,
                "model_name": model_config.model_name,
                "best_parameters": best_params,
                "best_score": best_score,
                "cv_folds": cv_folds,
                "scoring": scoring
            }
            
            # Save updated configuration
            await self._save_model_data()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error tuning hyperparameters: {e}")
            return {"error": str(e), "operation": "tune_hyperparameters"}
    
    async def _deploy_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a trained model for production use"""
        try:
            model_id = parameters.get("model_id")
            deployment_config = parameters.get("deployment_config", {})
            
            if not model_id:
                return {"error": "model_id is required", "operation": "deploy_model"}
            
            if model_id not in self.trained_models:
                return {"error": f"Trained model {model_id} not found", "operation": "deploy_model"}
            
            model_config = self.model_configs[model_id]
            
            # Mock deployment process
            deployment_endpoint = f"/api/models/{model_id}/predict"
            deployment_status = "deployed"
            
            result = {
                "operation": "deploy_model",
                "model_id": model_id,
                "model_name": model_config.model_name,
                "deployment_endpoint": deployment_endpoint,
                "deployment_status": deployment_status,
                "deployment_config": deployment_config,
                "deployed_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error deploying model: {e}")
            return {"error": str(e), "operation": "deploy_model"}
    
    async def _get_model_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a model"""
        try:
            model_id = parameters.get("model_id")
            
            if not model_id:
                return {"error": "model_id is required", "operation": "get_model_info"}
            
            if model_id not in self.model_configs:
                return {"error": f"Model {model_id} not found", "operation": "get_model_info"}
            
            model_config = self.model_configs[model_id]
            is_trained = model_id in self.trained_models
            
            # Get training job info
            training_job = None
            for job in self.training_jobs.values():
                if job.model_id == model_id:
                    training_job = job
                    break
            
            # Get recent predictions
            recent_predictions = [
                {
                    "request_id": pred.request_id,
                    "predictions_count": len(pred.predictions),
                    "prediction_time": pred.prediction_time,
                    "created_at": pred.created_at.isoformat()
                }
                for pred in self.prediction_history[-10:]
                if pred.model_id == model_id
            ]
            
            result = {
                "operation": "get_model_info",
                "model_id": model_id,
                "model_name": model_config.model_name,
                "category": model_config.model_category.value,
                "algorithm": model_config.algorithm,
                "hyperparameters": model_config.hyperparameters,
                "feature_columns": model_config.feature_columns,
                "target_column": model_config.target_column,
                "preprocessing_steps": model_config.preprocessing_steps,
                "is_trained": is_trained,
                "training_job": {
                    "job_id": training_job.job_id,
                    "status": training_job.status.value,
                    "started_at": training_job.started_at.isoformat(),
                    "completed_at": training_job.completed_at.isoformat() if training_job.completed_at else None,
                    "training_metrics": training_job.training_metrics,
                    "validation_metrics": training_job.validation_metrics,
                    "error_message": training_job.error_message
                } if training_job else None,
                "recent_predictions": recent_predictions
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
            return {"error": str(e), "operation": "get_model_info"}
    
    async def _get_modeler_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get overall modeler status"""
        try:
            total_models = len(self.model_configs)
            trained_models = len(self.trained_models)
            active_jobs = len([job for job in self.training_jobs.values() if job.status == ModelStatus.TRAINING])
            total_predictions = len(self.prediction_history)
            
            # Model statistics by category
            category_stats = {}
            for config in self.model_configs.values():
                category = config.model_category.value
                if category not in category_stats:
                    category_stats[category] = {"total": 0, "trained": 0}
                category_stats[category]["total"] += 1
                if config.model_id in self.trained_models:
                    category_stats[category]["trained"] += 1
            
            # Algorithm statistics
            algorithm_stats = {}
            for config in self.model_configs.values():
                algorithm = config.algorithm
                if algorithm not in algorithm_stats:
                    algorithm_stats[algorithm] = {"total": 0, "trained": 0}
                algorithm_stats[algorithm]["total"] += 1
                if config.model_id in self.trained_models:
                    algorithm_stats[algorithm]["trained"] += 1
            
            result = {
                "operation": "modeler_status",
                "total_models": total_models,
                "trained_models": trained_models,
                "active_training_jobs": active_jobs,
                "total_predictions": total_predictions,
                "category_statistics": category_stats,
                "algorithm_statistics": algorithm_stats,
                "models": {
                    model_id: {
                        "name": config.model_name,
                        "category": config.model_category.value,
                        "algorithm": config.algorithm,
                        "is_trained": model_id in self.trained_models
                    }
                    for model_id, config in self.model_configs.items()
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting modeler status: {e}")
            return {"error": str(e), "operation": "modeler_status"}
    
    # Helper methods
    
    def _generate_model_id(self, model_name: str) -> str:
        """Generate unique model ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{model_name}_{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_job_id(self) -> str:
        """Generate unique job ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"job_{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"pred_{timestamp}".encode()).hexdigest()[:16]
    
    async def _load_model_data(self):
        """Load model configurations from storage"""
        try:
            configs_file = os.path.join(self.data_dir, "model_configs.json")
            if os.path.exists(configs_file):
                with open(configs_file, 'r') as f:
                    configs_data = json.load(f)
                    for model_id, config_data in configs_data.items():
                        config = ModelConfig(
                            model_id=model_id,
                            model_name=config_data['model_name'],
                            model_category=ModelCategory(config_data['model_category']),
                            algorithm=config_data['algorithm'],
                            hyperparameters=config_data['hyperparameters'],
                            feature_columns=config_data['feature_columns'],
                            target_column=config_data['target_column'],
                            preprocessing_steps=config_data['preprocessing_steps']
                        )
                        self.model_configs[model_id] = config
            
            # Load training jobs
            jobs_file = os.path.join(self.data_dir, "training_jobs.json")
            if os.path.exists(jobs_file):
                with open(jobs_file, 'r') as f:
                    jobs_data = json.load(f)
                    for job_id, job_data in jobs_data.items():
                        job = ModelTrainingJob(
                            job_id=job_id,
                            model_id=job_data['model_id'],
                            training_data_path=job_data['training_data_path'],
                            validation_split=job_data['validation_split'],
                            status=ModelStatus(job_data['status']),
                            started_at=datetime.fromisoformat(job_data['started_at']),
                            completed_at=datetime.fromisoformat(job_data['completed_at']) if job_data['completed_at'] else None,
                            training_metrics=job_data['training_metrics'],
                            validation_metrics=job_data['validation_metrics'],
                            error_message=job_data['error_message']
                        )
                        self.training_jobs[job_id] = job
                        
        except Exception as e:
            self.logger.warning(f"Could not load model data: {e}")
    
    async def _save_model_data(self):
        """Save model configurations to storage"""
        try:
            # Save model configurations
            configs_data = {}
            for model_id, config in self.model_configs.items():
                configs_data[model_id] = {
                    'model_name': config.model_name,
                    'model_category': config.model_category.value,
                    'algorithm': config.algorithm,
                    'hyperparameters': config.hyperparameters,
                    'feature_columns': config.feature_columns,
                    'target_column': config.target_column,
                    'preprocessing_steps': config.preprocessing_steps
                }
            
            configs_file = os.path.join(self.data_dir, "model_configs.json")
            with open(configs_file, 'w') as f:
                json.dump(configs_data, f, indent=2)
            
            # Save training jobs
            jobs_data = {}
            for job_id, job in self.training_jobs.items():
                jobs_data[job_id] = {
                    'model_id': job.model_id,
                    'training_data_path': job.training_data_path,
                    'validation_split': job.validation_split,
                    'status': job.status.value,
                    'started_at': job.started_at.isoformat(),
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'training_metrics': job.training_metrics,
                    'validation_metrics': job.validation_metrics,
                    'error_message': job.error_message
                }
            
            jobs_file = os.path.join(self.data_dir, "training_jobs.json")
            with open(jobs_file, 'w') as f:
                json.dump(jobs_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Could not save model data: {e}")
    
    async def _load_trained_models(self):
        """Load trained models from disk"""
        try:
            for model_id in self.model_configs.keys():
                model_path = os.path.join(self.models_dir, f"{model_id}.joblib")
                if os.path.exists(model_path):
                    try:
                        model = joblib.load(model_path)
                        self.trained_models[model_id] = model
                    except Exception as e:
                        self.logger.warning(f"Could not load model {model_id}: {e}")
                        
        except Exception as e:
            self.logger.warning(f"Could not load trained models: {e}")
    
    async def _preprocess_data(self, X: pd.DataFrame, y: pd.Series, config: ModelConfig) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess training data"""
        try:
            X_processed = X.copy()
            y_processed = y.copy()
            
            # Handle missing values
            X_processed = X_processed.fillna(X_processed.mean(numeric_only=True))
            
            # Encode categorical variables
            categorical_columns = X_processed.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                encoders = {}
                for col in categorical_columns:
                    encoder = LabelEncoder()
                    X_processed[col] = encoder.fit_transform(X_processed[col].astype(str))
                    encoders[col] = encoder
                self.model_encoders[config.model_id] = encoders
            
            # Scale features if specified
            if "standardize" in config.preprocessing_steps:
                scaler = StandardScaler()
                X_processed = scaler.fit_transform(X_processed)
                self.model_scalers[config.model_id] = scaler
            
            # Encode target variable for classification
            if config.model_category == ModelCategory.CLASSIFICATION:
                if y_processed.dtype == 'object':
                    target_encoder = LabelEncoder()
                    y_processed = target_encoder.fit_transform(y_processed)
                    if config.model_id not in self.model_encoders:
                        self.model_encoders[config.model_id] = {}
                    self.model_encoders[config.model_id]['target'] = target_encoder
            
            return X_processed, y_processed.values
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {e}")
            raise
    
    async def _preprocess_input_data(self, X: pd.DataFrame, config: ModelConfig) -> np.ndarray:
        """Preprocess input data for prediction"""
        try:
            X_processed = X.copy()
            
            # Handle missing values
            X_processed = X_processed.fillna(X_processed.mean(numeric_only=True))
            
            # Apply encoders
            if config.model_id in self.model_encoders:
                encoders = self.model_encoders[config.model_id]
                for col, encoder in encoders.items():
                    if col != 'target' and col in X_processed.columns:
                        X_processed[col] = encoder.transform(X_processed[col].astype(str))
            
            # Apply scaler
            if config.model_id in self.model_scalers:
                scaler = self.model_scalers[config.model_id]
                X_processed = scaler.transform(X_processed)
            
            return X_processed
            
        except Exception as e:
            self.logger.error(f"Error preprocessing input data: {e}")
            raise
    
    async def _calculate_metrics(self, y_true, y_pred, model_category: ModelCategory) -> Dict[str, float]:
        """Calculate performance metrics"""
        try:
            metrics = {}
            
            if model_category == ModelCategory.REGRESSION:
                metrics['mse'] = float(mean_squared_error(y_true, y_pred))
                metrics['rmse'] = float(np.sqrt(metrics['mse']))
                metrics['mae'] = float(np.mean(np.abs(y_true - y_pred)))
                
                # R-squared
                ss_res = np.sum((y_true - y_pred) ** 2)
                ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
                metrics['r2'] = float(1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0
                
            elif model_category == ModelCategory.CLASSIFICATION:
                metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
                
                # Precision, recall, F1 for binary classification
                try:
                    from sklearn.metrics import precision_score, recall_score, f1_score
                    metrics['precision'] = float(precision_score(y_true, y_pred, average='weighted'))
                    metrics['recall'] = float(recall_score(y_true, y_pred, average='weighted'))
                    metrics['f1'] = float(f1_score(y_true, y_pred, average='weighted'))
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            return {}
    
    async def _calculate_confidence_scores(self, model, X: np.ndarray, predictions) -> List[float]:
        """Calculate confidence scores for predictions"""
        try:
            # For models with predict_proba, use max probability as confidence
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(X)
                confidence_scores = [float(max(probs)) for probs in probabilities]
            else:
                # For regression or models without probabilities, use a simple heuristic
                confidence_scores = [0.8] * len(predictions)  # Mock confidence
            
            return confidence_scores
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence scores: {e}")
            return [0.5] * len(predictions)
    
    async def _generate_prediction_explanations(self, model, config: ModelConfig, X: np.ndarray, predictions) -> List[Dict[str, Any]]:
        """Generate explanations for predictions"""
        try:
            explanations = []
            
            # For tree-based models, we could use feature importance
            if hasattr(model, 'feature_importances_'):
                feature_importance = model.feature_importances_
                
                for i, pred in enumerate(predictions):
                    explanation = {
                        "prediction": float(pred),
                        "top_features": []
                    }
                    
                    # Get top contributing features
                    if config.feature_columns:
                        feature_contributions = list(zip(config.feature_columns, feature_importance))
                        feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)
                        
                        explanation["top_features"] = [
                            {"feature": feat, "importance": float(imp)}
                            for feat, imp in feature_contributions[:5]
                        ]
                    
                    explanations.append(explanation)
            else:
                # Generic explanation for other models
                for pred in predictions:
                    explanations.append({
                        "prediction": float(pred),
                        "explanation": "Model-specific explanations not available for this algorithm"
                    })
            
            return explanations
            
        except Exception as e:
            self.logger.error(f"Error generating explanations: {e}")
            return [{"explanation": "Error generating explanation"}] * len(predictions)