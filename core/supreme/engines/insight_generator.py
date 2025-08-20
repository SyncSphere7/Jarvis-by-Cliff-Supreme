"""
Supreme Insight Generator
Intelligent insight extraction and business intelligence capabilities.
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
import statistics
from collections import Counter

from ..base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse

class InsightType(Enum):
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    PATTERN = "pattern"
    FORECAST = "forecast"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"

class InsightSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Insight:
    """Represents a generated insight"""
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    severity: InsightSeverity
    confidence_score: float
    data_source: str
    affected_metrics: List[str] = None
    recommendations: List[str] = None
    supporting_data: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.affected_metrics is None:
            self.affected_metrics = []
        if self.recommendations is None:
            self.recommendations = []
        if self.supporting_data is None:
            self.supporting_data = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class InsightRule:
    """Defines rules for insight generation"""
    rule_id: str
    rule_name: str
    insight_type: InsightType
    conditions: Dict[str, Any]
    threshold_values: Dict[str, float] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.threshold_values is None:
            self.threshold_values = {}

@dataclass
class BusinessMetric:
    """Represents a business metric for analysis"""
    metric_id: str
    metric_name: str
    metric_type: str  # revenue, cost, efficiency, quality, etc.
    current_value: float
    target_value: Optional[float] = None
    historical_values: List[float] = None
    unit: str = ""
    
    def __post_init__(self):
        if self.historical_values is None:
            self.historical_values = []

class SupremeInsightGenerator(BaseSupremeEngine):
    """
    Supreme insight generator with intelligent analysis capabilities.
    Automatically discovers patterns, trends, and actionable insights from data.
    """
    
    def __init__(self, engine_name: str, config):
        super().__init__(engine_name, config)
        
        # Insight storage
        self.generated_insights: List[Insight] = []
        self.insight_rules: Dict[str, InsightRule] = {}
        self.business_metrics: Dict[str, BusinessMetric] = {}
        
        # Insight capabilities
        self.insight_capabilities = {
            "generate_insights": self._generate_insights,
            "analyze_trends": self._analyze_trends,
            "detect_anomalies": self._detect_anomalies,
            "find_correlations": self._find_correlations,
            "create_recommendations": self._create_recommendations,
            "monitor_metrics": self._monitor_business_metrics,
            "create_alerts": self._create_intelligent_alerts
        }
        
        # Built-in insight rules
        self.builtin_rules = self._initialize_builtin_rules()
        
        # Data persistence
        self.data_dir = "data/insights"
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def _initialize_engine(self) -> bool:
        """Initialize the insight generator"""
        try:
            self.logger.info("Initializing Supreme Insight Generator...")
            
            # Load existing insight data
            await self._load_insight_data()
            
            # Initialize built-in rules
            for rule_id, rule_config in self.builtin_rules.items():
                if rule_id not in self.insight_rules:
                    self.insight_rules[rule_id] = InsightRule(**rule_config)
            
            self.logger.info(f"Insight Generator initialized with {len(self.insight_rules)} rules")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Insight Generator: {e}")
            return False
    
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Execute insight generation operation"""
        operation = request.operation.lower()
        parameters = request.parameters
        
        # Route to appropriate insight capability
        if "generate" in operation and "insight" in operation:
            return await self._generate_insights(parameters)
        elif "trend" in operation:
            return await self._analyze_trends(parameters)
        elif "anomal" in operation:
            return await self._detect_anomalies(parameters)
        elif "correlat" in operation:
            return await self._find_correlations(parameters)
        elif "recommend" in operation:
            return await self._create_recommendations(parameters)
        elif "monitor" in operation:
            return await self._monitor_business_metrics(parameters)
        elif "alert" in operation:
            return await self._create_intelligent_alerts(parameters)
        else:
            return await self._get_insight_status(parameters)
    
    async def get_supported_operations(self) -> List[str]:
        """Get supported insight generation operations"""
        return [
            "generate_insights", "analyze_trends", "detect_anomalies", "find_correlations",
            "create_recommendations", "monitor_metrics", "create_alerts", "insight_status"
        ]
    
    async def _generate_insights(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive insights from data"""
        try:
            data_source = parameters.get("data_source")
            data = parameters.get("data")
            insight_types = parameters.get("insight_types", ["trend", "anomaly", "correlation"])
            min_confidence = parameters.get("min_confidence", 0.7)
            
            if not data and not data_source:
                return {"error": "data or data_source is required", "operation": "generate_insights"}
            
            # Load data if needed
            if data_source and not data:
                data = await self._load_data_from_source(data_source)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            generated_insights = []
            
            # Generate different types of insights
            for insight_type in insight_types:
                if insight_type == "trend":
                    trend_insights = await self._generate_trend_insights(df, data_source or "provided_data")
                    generated_insights.extend(trend_insights)
                
                elif insight_type == "anomaly":
                    anomaly_insights = await self._generate_anomaly_insights(df, data_source or "provided_data")
                    generated_insights.extend(anomaly_insights)
                
                elif insight_type == "correlation":
                    correlation_insights = await self._generate_correlation_insights(df, data_source or "provided_data")
                    generated_insights.extend(correlation_insights)
                
                elif insight_type == "pattern":
                    pattern_insights = await self._generate_pattern_insights(df, data_source or "provided_data")
                    generated_insights.extend(pattern_insights)
                
                elif insight_type == "forecast":
                    forecast_insights = await self._generate_forecast_insights(df, data_source or "provided_data")
                    generated_insights.extend(forecast_insights)
            
            # Filter by confidence score
            filtered_insights = [
                insight for insight in generated_insights
                if insight.confidence_score >= min_confidence
            ]
            
            # Sort by confidence and severity
            filtered_insights.sort(
                key=lambda x: (x.confidence_score, self._severity_weight(x.severity)),
                reverse=True
            )
            
            # Store insights
            self.generated_insights.extend(filtered_insights)
            
            # Limit insights history
            if len(self.generated_insights) > 1000:
                self.generated_insights = self.generated_insights[-1000:]
            
            result = {
                "operation": "generate_insights",
                "data_source": data_source or "provided_data",
                "insight_types": insight_types,
                "total_insights": len(filtered_insights),
                "insights": [
                    {
                        "insight_id": insight.insight_id,
                        "type": insight.insight_type.value,
                        "title": insight.title,
                        "description": insight.description,
                        "severity": insight.severity.value,
                        "confidence_score": insight.confidence_score,
                        "affected_metrics": insight.affected_metrics,
                        "recommendations": insight.recommendations,
                        "created_at": insight.created_at.isoformat()
                    }
                    for insight in filtered_insights[:20]  # Top 20 insights
                ]
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return {"error": str(e), "operation": "generate_insights"}
    
    async def _analyze_trends(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in data"""
        try:
            data_source = parameters.get("data_source")
            data = parameters.get("data")
            time_column = parameters.get("time_column", "timestamp")
            value_columns = parameters.get("value_columns")
            
            if not data and not data_source:
                return {"error": "data or data_source is required", "operation": "analyze_trends"}
            
            # Load data if needed
            if data_source and not data:
                data = await self._load_data_from_source(data_source)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # Ensure time column is datetime
            if time_column in df.columns:
                df[time_column] = pd.to_datetime(df[time_column])
                df = df.sort_values(time_column)
            
            # Analyze trends for each value column
            trend_results = {}
            
            if value_columns:
                columns_to_analyze = value_columns
            else:
                # Auto-detect numeric columns
                columns_to_analyze = df.select_dtypes(include=[np.number]).columns.tolist()
            
            for column in columns_to_analyze:
                if column in df.columns:
                    trend_analysis = await self._analyze_column_trend(df, column, time_column)
                    trend_results[column] = trend_analysis
            
            result = {
                "operation": "analyze_trends",
                "data_source": data_source or "provided_data",
                "analyzed_columns": len(trend_results),
                "trend_analysis": trend_results
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return {"error": str(e), "operation": "analyze_trends"}
    
    async def _detect_anomalies(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in data"""
        try:
            data_source = parameters.get("data_source")
            data = parameters.get("data")
            method = parameters.get("method", "statistical")
            sensitivity = parameters.get("sensitivity", 2.0)
            
            if not data and not data_source:
                return {"error": "data or data_source is required", "operation": "detect_anomalies"}
            
            # Load data if needed
            if data_source and not data:
                data = await self._load_data_from_source(data_source)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # Detect anomalies in numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            anomaly_results = {}
            
            for column in numeric_columns:
                anomalies = await self._detect_column_anomalies(df[column], method, sensitivity)
                if anomalies:
                    anomaly_results[column] = anomalies
            
            result = {
                "operation": "detect_anomalies",
                "data_source": data_source or "provided_data",
                "method": method,
                "sensitivity": sensitivity,
                "columns_analyzed": len(numeric_columns),
                "anomalies_found": sum(len(anomalies) for anomalies in anomaly_results.values()),
                "anomaly_details": anomaly_results
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return {"error": str(e), "operation": "detect_anomalies"}
    
    async def _find_correlations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Find correlations between variables"""
        try:
            data_source = parameters.get("data_source")
            data = parameters.get("data")
            min_correlation = parameters.get("min_correlation", 0.5)
            method = parameters.get("method", "pearson")
            
            if not data and not data_source:
                return {"error": "data or data_source is required", "operation": "find_correlations"}
            
            # Load data if needed
            if data_source and not data:
                data = await self._load_data_from_source(data_source)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # Calculate correlation matrix for numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                return {
                    "operation": "find_correlations",
                    "error": "No numeric columns found for correlation analysis"
                }
            
            correlation_matrix = numeric_df.corr(method=method)
            
            # Find significant correlations
            significant_correlations = []
            
            for i, col1 in enumerate(correlation_matrix.columns):
                for j, col2 in enumerate(correlation_matrix.columns):
                    if i < j:  # Avoid duplicates and self-correlation
                        corr_value = correlation_matrix.loc[col1, col2]
                        if abs(corr_value) >= min_correlation:
                            significant_correlations.append({
                                "variable1": col1,
                                "variable2": col2,
                                "correlation": float(corr_value),
                                "strength": self._correlation_strength(abs(corr_value)),
                                "direction": "positive" if corr_value > 0 else "negative"
                            })
            
            # Sort by correlation strength
            significant_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            
            result = {
                "operation": "find_correlations",
                "data_source": data_source or "provided_data",
                "method": method,
                "min_correlation": min_correlation,
                "variables_analyzed": len(numeric_df.columns),
                "significant_correlations": len(significant_correlations),
                "correlations": significant_correlations,
                "correlation_matrix": correlation_matrix.to_dict()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error finding correlations: {e}")
            return {"error": str(e), "operation": "find_correlations"}
    
    async def _create_recommendations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create actionable recommendations based on insights"""
        try:
            insight_ids = parameters.get("insight_ids", [])
            context = parameters.get("context", {})
            
            if not insight_ids:
                # Use recent insights if none specified
                insight_ids = [insight.insight_id for insight in self.generated_insights[-10:]]
            
            recommendations = []
            
            for insight_id in insight_ids:
                insight = next((i for i in self.generated_insights if i.insight_id == insight_id), None)
                if insight:
                    insight_recommendations = await self._generate_recommendations_for_insight(insight, context)
                    recommendations.extend(insight_recommendations)
            
            # Prioritize recommendations
            prioritized_recommendations = await self._prioritize_recommendations(recommendations)
            
            result = {
                "operation": "create_recommendations",
                "insights_analyzed": len(insight_ids),
                "recommendations_generated": len(prioritized_recommendations),
                "recommendations": prioritized_recommendations
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating recommendations: {e}")
            return {"error": str(e), "operation": "create_recommendations"}
    
    async def _monitor_business_metrics(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor business metrics and generate insights"""
        try:
            metrics = parameters.get("metrics", [])
            time_range = parameters.get("time_range", "30d")
            
            if not metrics:
                return {"error": "metrics are required", "operation": "monitor_metrics"}
            
            monitoring_results = []
            
            for metric_config in metrics:
                metric_id = metric_config.get("metric_id")
                metric_name = metric_config.get("metric_name")
                current_value = metric_config.get("current_value")
                target_value = metric_config.get("target_value")
                historical_values = metric_config.get("historical_values", [])
                
                # Create or update business metric
                business_metric = BusinessMetric(
                    metric_id=metric_id,
                    metric_name=metric_name,
                    metric_type=metric_config.get("metric_type", "general"),
                    current_value=current_value,
                    target_value=target_value,
                    historical_values=historical_values,
                    unit=metric_config.get("unit", "")
                )
                
                self.business_metrics[metric_id] = business_metric
                
                # Analyze metric performance
                metric_analysis = await self._analyze_business_metric(business_metric)
                monitoring_results.append(metric_analysis)
            
            result = {
                "operation": "monitor_metrics",
                "metrics_monitored": len(metrics),
                "time_range": time_range,
                "monitoring_results": monitoring_results
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error monitoring metrics: {e}")
            return {"error": str(e), "operation": "monitor_metrics"}
    
    async def _create_intelligent_alerts(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent alerts based on data patterns"""
        try:
            alert_rules = parameters.get("alert_rules", [])
            data_source = parameters.get("data_source")
            
            if not alert_rules:
                return {"error": "alert_rules are required", "operation": "create_alerts"}
            
            alerts_created = []
            
            for rule in alert_rules:
                alert = await self._evaluate_alert_rule(rule, data_source)
                if alert:
                    alerts_created.append(alert)
            
            result = {
                "operation": "create_alerts",
                "rules_evaluated": len(alert_rules),
                "alerts_created": len(alerts_created),
                "alerts": alerts_created
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating alerts: {e}")
            return {"error": str(e), "operation": "create_alerts"}
    
    async def _get_insight_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive insight status"""
        try:
            total_insights = len(self.generated_insights)
            recent_insights = len([i for i in self.generated_insights if i.created_at > datetime.now() - timedelta(days=7)])
            
            # Insights by type
            insights_by_type = {}
            for insight in self.generated_insights:
                insight_type = insight.insight_type.value
                if insight_type not in insights_by_type:
                    insights_by_type[insight_type] = 0
                insights_by_type[insight_type] += 1
            
            # Insights by severity
            insights_by_severity = {}
            for insight in self.generated_insights:
                severity = insight.severity.value
                if severity not in insights_by_severity:
                    insights_by_severity[severity] = 0
                insights_by_severity[severity] += 1
            
            result = {
                "operation": "insight_status",
                "total_insights": total_insights,
                "recent_insights": recent_insights,
                "active_rules": len(self.insight_rules),
                "monitored_metrics": len(self.business_metrics),
                "insights_by_type": insights_by_type,
                "insights_by_severity": insights_by_severity,
                "recent_insights_details": [
                    {
                        "insight_id": insight.insight_id,
                        "type": insight.insight_type.value,
                        "title": insight.title,
                        "severity": insight.severity.value,
                        "confidence_score": insight.confidence_score,
                        "created_at": insight.created_at.isoformat()
                    }
                    for insight in self.generated_insights[-10:]
                ]
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting insight status: {e}")
            return {"error": str(e), "operation": "insight_status"}    
   
 # Helper methods for insight generation
    
    def _initialize_builtin_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize built-in insight rules"""
        return {
            "trend_detection": {
                "rule_id": "trend_detection",
                "rule_name": "Trend Detection",
                "insight_type": InsightType.TREND,
                "conditions": {"min_data_points": 5, "trend_threshold": 0.1},
                "threshold_values": {"significance": 0.05}
            },
            "anomaly_detection": {
                "rule_id": "anomaly_detection",
                "rule_name": "Statistical Anomaly Detection",
                "insight_type": InsightType.ANOMALY,
                "conditions": {"method": "zscore", "threshold": 2.0},
                "threshold_values": {"confidence": 0.95}
            },
            "correlation_analysis": {
                "rule_id": "correlation_analysis",
                "rule_name": "Correlation Analysis",
                "insight_type": InsightType.CORRELATION,
                "conditions": {"min_correlation": 0.7, "method": "pearson"},
                "threshold_values": {"significance": 0.01}
            }
        }
    
    async def _load_insight_data(self):
        """Load existing insight data"""
        try:
            insights_file = os.path.join(self.data_dir, "insights.json")
            if os.path.exists(insights_file):
                with open(insights_file, 'r') as f:
                    insights_data = json.load(f)
                    for insight_data in insights_data:
                        insight = Insight(
                            insight_id=insight_data['insight_id'],
                            insight_type=InsightType(insight_data['insight_type']),
                            title=insight_data['title'],
                            description=insight_data['description'],
                            severity=InsightSeverity(insight_data['severity']),
                            confidence_score=insight_data['confidence_score'],
                            data_source=insight_data['data_source'],
                            affected_metrics=insight_data['affected_metrics'],
                            recommendations=insight_data['recommendations'],
                            supporting_data=insight_data['supporting_data'],
                            created_at=datetime.fromisoformat(insight_data['created_at'])
                        )
                        self.generated_insights.append(insight)
                        
        except Exception as e:
            self.logger.warning(f"Could not load insight data: {e}")
    
    def _severity_weight(self, severity: InsightSeverity) -> int:
        """Get numeric weight for severity"""
        weights = {
            InsightSeverity.LOW: 1,
            InsightSeverity.MEDIUM: 2,
            InsightSeverity.HIGH: 3,
            InsightSeverity.CRITICAL: 4
        }
        return weights.get(severity, 1)
    
    def _correlation_strength(self, correlation: float) -> str:
        """Determine correlation strength"""
        if correlation >= 0.8:
            return "very_strong"
        elif correlation >= 0.6:
            return "strong"
        elif correlation >= 0.4:
            return "moderate"
        elif correlation >= 0.2:
            return "weak"
        else:
            return "very_weak"
    
    def _generate_insight_id(self) -> str:
        """Generate unique insight ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"insight_{timestamp}".encode()).hexdigest()[:16]
    
    async def _load_data_from_source(self, data_source: str) -> pd.DataFrame:
        """Load data from various sources"""
        # This would implement actual data loading logic
        # For now, return mock data
        return pd.DataFrame([
            {"value": 10, "category": "A", "timestamp": "2024-01-01"},
            {"value": 15, "category": "B", "timestamp": "2024-01-02"},
            {"value": 12, "category": "A", "timestamp": "2024-01-03"}
        ])
    
    async def _generate_trend_insights(self, df: pd.DataFrame, data_source: str) -> List[Insight]:
        """Generate trend-based insights"""
        insights = []
        
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            for column in numeric_columns:
                if len(df[column]) >= 5:  # Minimum data points for trend analysis
                    # Simple trend detection using linear regression
                    x = np.arange(len(df[column]))
                    y = df[column].values
                    
                    # Calculate slope
                    slope = np.polyfit(x, y, 1)[0]
                    
                    if abs(slope) > 0.1:  # Significant trend threshold
                        trend_direction = "increasing" if slope > 0 else "decreasing"
                        
                        insight = Insight(
                            insight_id=self._generate_insight_id(),
                            insight_type=InsightType.TREND,
                            title=f"{trend_direction.title()} trend detected in {column}",
                            description=f"The metric '{column}' shows a {trend_direction} trend with a slope of {slope:.3f}",
                            severity=InsightSeverity.MEDIUM if abs(slope) > 0.5 else InsightSeverity.LOW,
                            confidence_score=min(0.9, abs(slope) * 2),
                            data_source=data_source,
                            affected_metrics=[column],
                            supporting_data={"slope": slope, "trend_direction": trend_direction}
                        )
                        insights.append(insight)
            
        except Exception as e:
            self.logger.error(f"Error generating trend insights: {e}")
        
        return insights
    
    async def _generate_anomaly_insights(self, df: pd.DataFrame, data_source: str) -> List[Insight]:
        """Generate anomaly-based insights"""
        insights = []
        
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            for column in numeric_columns:
                values = df[column].dropna()
                if len(values) >= 10:
                    # Z-score based anomaly detection
                    mean_val = values.mean()
                    std_val = values.std()
                    z_scores = np.abs((values - mean_val) / std_val)
                    
                    anomalies = values[z_scores > 2.0]  # 2 standard deviations
                    
                    if len(anomalies) > 0:
                        insight = Insight(
                            insight_id=self._generate_insight_id(),
                            insight_type=InsightType.ANOMALY,
                            title=f"Anomalies detected in {column}",
                            description=f"Found {len(anomalies)} anomalous values in '{column}' that deviate significantly from the mean",
                            severity=InsightSeverity.HIGH if len(anomalies) > len(values) * 0.1 else InsightSeverity.MEDIUM,
                            confidence_score=0.8,
                            data_source=data_source,
                            affected_metrics=[column],
                            supporting_data={
                                "anomaly_count": len(anomalies),
                                "anomaly_percentage": len(anomalies) / len(values) * 100,
                                "anomaly_values": anomalies.tolist()[:10]  # First 10 anomalies
                            }
                        )
                        insights.append(insight)
            
        except Exception as e:
            self.logger.error(f"Error generating anomaly insights: {e}")
        
        return insights
    
    async def _generate_correlation_insights(self, df: pd.DataFrame, data_source: str) -> List[Insight]:
        """Generate correlation-based insights"""
        insights = []
        
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            
            if len(numeric_df.columns) >= 2:
                correlation_matrix = numeric_df.corr()
                
                # Find strong correlations
                for i, col1 in enumerate(correlation_matrix.columns):
                    for j, col2 in enumerate(correlation_matrix.columns):
                        if i < j:  # Avoid duplicates
                            corr_value = correlation_matrix.loc[col1, col2]
                            
                            if abs(corr_value) >= 0.7:  # Strong correlation threshold
                                direction = "positive" if corr_value > 0 else "negative"
                                
                                insight = Insight(
                                    insight_id=self._generate_insight_id(),
                                    insight_type=InsightType.CORRELATION,
                                    title=f"Strong {direction} correlation between {col1} and {col2}",
                                    description=f"'{col1}' and '{col2}' show a strong {direction} correlation (r={corr_value:.3f})",
                                    severity=InsightSeverity.MEDIUM,
                                    confidence_score=abs(corr_value),
                                    data_source=data_source,
                                    affected_metrics=[col1, col2],
                                    supporting_data={
                                        "correlation_coefficient": corr_value,
                                        "correlation_strength": self._correlation_strength(abs(corr_value))
                                    }
                                )
                                insights.append(insight)
            
        except Exception as e:
            self.logger.error(f"Error generating correlation insights: {e}")
        
        return insights
    
    async def _generate_pattern_insights(self, df: pd.DataFrame, data_source: str) -> List[Insight]:
        """Generate pattern-based insights"""
        insights = []
        
        try:
            # Look for seasonal patterns, cyclical behavior, etc.
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                
                for column in numeric_columns:
                    # Simple pattern detection - look for cyclical behavior
                    values = df[column].values
                    if len(values) >= 12:  # Need enough data points
                        # Check for weekly patterns (if we have daily data)
                        if len(values) >= 14:
                            weekly_pattern = self._detect_weekly_pattern(values)
                            if weekly_pattern:
                                insight = Insight(
                                    insight_id=self._generate_insight_id(),
                                    insight_type=InsightType.PATTERN,
                                    title=f"Weekly pattern detected in {column}",
                                    description=f"'{column}' shows a recurring weekly pattern",
                                    severity=InsightSeverity.LOW,
                                    confidence_score=0.7,
                                    data_source=data_source,
                                    affected_metrics=[column],
                                    supporting_data={"pattern_type": "weekly"}
                                )
                                insights.append(insight)
            
        except Exception as e:
            self.logger.error(f"Error generating pattern insights: {e}")
        
        return insights
    
    async def _generate_forecast_insights(self, df: pd.DataFrame, data_source: str) -> List[Insight]:
        """Generate forecast-based insights"""
        insights = []
        
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            for column in numeric_columns:
                if len(df[column]) >= 10:
                    # Simple linear forecast
                    values = df[column].values
                    x = np.arange(len(values))
                    
                    # Fit linear model
                    coeffs = np.polyfit(x, values, 1)
                    slope, intercept = coeffs
                    
                    # Forecast next few points
                    future_x = np.arange(len(values), len(values) + 5)
                    forecast = slope * future_x + intercept
                    
                    # Determine forecast direction
                    if slope > 0.1:
                        forecast_trend = "increasing"
                        severity = InsightSeverity.MEDIUM
                    elif slope < -0.1:
                        forecast_trend = "decreasing"
                        severity = InsightSeverity.HIGH
                    else:
                        forecast_trend = "stable"
                        severity = InsightSeverity.LOW
                    
                    insight = Insight(
                        insight_id=self._generate_insight_id(),
                        insight_type=InsightType.FORECAST,
                        title=f"Forecast shows {forecast_trend} trend for {column}",
                        description=f"Based on current trends, '{column}' is expected to {forecast_trend} in the near future",
                        severity=severity,
                        confidence_score=0.6,
                        data_source=data_source,
                        affected_metrics=[column],
                        supporting_data={
                            "forecast_values": forecast.tolist(),
                            "trend_slope": slope,
                            "forecast_direction": forecast_trend
                        }
                    )
                    insights.append(insight)
            
        except Exception as e:
            self.logger.error(f"Error generating forecast insights: {e}")
        
        return insights
    
    def _detect_weekly_pattern(self, values: np.ndarray) -> bool:
        """Detect weekly patterns in data"""
        try:
            if len(values) < 14:
                return False
            
            # Simple autocorrelation check for 7-day lag
            # This is a simplified implementation
            weekly_correlation = np.corrcoef(values[:-7], values[7:])[0, 1]
            return abs(weekly_correlation) > 0.3
            
        except:
            return False
    
    async def _analyze_column_trend(self, df: pd.DataFrame, column: str, time_column: str) -> Dict[str, Any]:
        """Analyze trend for a specific column"""
        try:
            if time_column in df.columns:
                # Time-based trend analysis
                x = np.arange(len(df))
                y = df[column].values
            else:
                # Index-based trend analysis
                x = np.arange(len(df[column]))
                y = df[column].values
            
            # Linear regression
            coeffs = np.polyfit(x, y, 1)
            slope, intercept = coeffs
            
            # Calculate R-squared
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Determine trend strength
            if abs(slope) > 1.0:
                trend_strength = "strong"
            elif abs(slope) > 0.5:
                trend_strength = "moderate"
            elif abs(slope) > 0.1:
                trend_strength = "weak"
            else:
                trend_strength = "none"
            
            return {
                "column": column,
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_squared),
                "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                "trend_strength": trend_strength,
                "data_points": len(y)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing column trend: {e}")
            return {"column": column, "error": str(e)}
    
    async def _detect_column_anomalies(self, series: pd.Series, method: str, sensitivity: float) -> List[Dict[str, Any]]:
        """Detect anomalies in a data series"""
        try:
            anomalies = []
            values = series.dropna()
            
            if len(values) < 10:
                return anomalies
            
            if method == "statistical":
                # Z-score method
                mean_val = values.mean()
                std_val = values.std()
                z_scores = np.abs((values - mean_val) / std_val)
                
                anomaly_indices = values.index[z_scores > sensitivity]
                
                for idx in anomaly_indices:
                    anomalies.append({
                        "index": int(idx),
                        "value": float(values[idx]),
                        "z_score": float(z_scores[idx]),
                        "deviation_from_mean": float(abs(values[idx] - mean_val))
                    })
            
            elif method == "iqr":
                # Interquartile range method
                q1 = values.quantile(0.25)
                q3 = values.quantile(0.75)
                iqr = q3 - q1
                
                lower_bound = q1 - sensitivity * iqr
                upper_bound = q3 + sensitivity * iqr
                
                anomaly_mask = (values < lower_bound) | (values > upper_bound)
                anomaly_indices = values.index[anomaly_mask]
                
                for idx in anomaly_indices:
                    anomalies.append({
                        "index": int(idx),
                        "value": float(values[idx]),
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound)
                    })
            
            return anomalies[:50]  # Limit to 50 anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return []
    
    async def _generate_recommendations_for_insight(self, insight: Insight, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for a specific insight"""
        recommendations = []
        
        try:
            if insight.insight_type == InsightType.TREND:
                if "increasing" in insight.description.lower():
                    recommendations.append({
                        "recommendation": f"Monitor the increasing trend in {', '.join(insight.affected_metrics)}",
                        "priority": "medium",
                        "action_type": "monitor",
                        "estimated_impact": "medium"
                    })
                elif "decreasing" in insight.description.lower():
                    recommendations.append({
                        "recommendation": f"Investigate the decreasing trend in {', '.join(insight.affected_metrics)}",
                        "priority": "high",
                        "action_type": "investigate",
                        "estimated_impact": "high"
                    })
            
            elif insight.insight_type == InsightType.ANOMALY:
                recommendations.append({
                    "recommendation": f"Review anomalous values in {', '.join(insight.affected_metrics)} for data quality issues",
                    "priority": "high",
                    "action_type": "review",
                    "estimated_impact": "high"
                })
            
            elif insight.insight_type == InsightType.CORRELATION:
                recommendations.append({
                    "recommendation": f"Leverage the correlation between {', '.join(insight.affected_metrics)} for predictive modeling",
                    "priority": "medium",
                    "action_type": "optimize",
                    "estimated_impact": "medium"
                })
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    async def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations by impact and urgency"""
        try:
            priority_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            impact_weights = {"high": 3, "medium": 2, "low": 1}
            
            for rec in recommendations:
                priority_score = priority_weights.get(rec.get("priority", "low"), 1)
                impact_score = impact_weights.get(rec.get("estimated_impact", "low"), 1)
                rec["total_score"] = priority_score + impact_score
            
            # Sort by total score
            recommendations.sort(key=lambda x: x.get("total_score", 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error prioritizing recommendations: {e}")
            return recommendations
    
    async def _analyze_business_metric(self, metric: BusinessMetric) -> Dict[str, Any]:
        """Analyze a business metric"""
        try:
            analysis = {
                "metric_id": metric.metric_id,
                "metric_name": metric.metric_name,
                "current_value": metric.current_value,
                "target_value": metric.target_value,
                "performance": "on_track"
            }
            
            # Compare with target
            if metric.target_value:
                if metric.current_value >= metric.target_value:
                    analysis["performance"] = "exceeding"
                elif metric.current_value >= metric.target_value * 0.9:
                    analysis["performance"] = "on_track"
                else:
                    analysis["performance"] = "below_target"
            
            # Analyze historical trend
            if len(metric.historical_values) >= 3:
                recent_trend = self._calculate_trend(metric.historical_values[-5:])
                analysis["trend"] = recent_trend
                
                # Generate insights based on trend
                if recent_trend["direction"] == "decreasing" and metric.metric_type in ["revenue", "efficiency"]:
                    analysis["alert"] = f"Declining trend detected in {metric.metric_name}"
                elif recent_trend["direction"] == "increasing" and metric.metric_type in ["cost", "error_rate"]:
                    analysis["alert"] = f"Increasing trend detected in {metric.metric_name}"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing business metric: {e}")
            return {"metric_id": metric.metric_id, "error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend from a list of values"""
        try:
            if len(values) < 2:
                return {"direction": "stable", "slope": 0}
            
            x = np.arange(len(values))
            y = np.array(values)
            
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > 0.1:
                direction = "increasing"
            elif slope < -0.1:
                direction = "decreasing"
            else:
                direction = "stable"
            
            return {"direction": direction, "slope": float(slope)}
            
        except:
            return {"direction": "stable", "slope": 0}
    
    async def _evaluate_alert_rule(self, rule: Dict[str, Any], data_source: str) -> Optional[Dict[str, Any]]:
        """Evaluate an alert rule"""
        try:
            # This would implement actual alert rule evaluation
            # For now, return a mock alert
            return {
                "alert_id": self._generate_insight_id(),
                "rule_name": rule.get("name", "Unknown Rule"),
                "message": f"Alert triggered by rule: {rule.get('name')}",
                "severity": rule.get("severity", "medium"),
                "data_source": data_source,
                "triggered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating alert rule: {e}")
            return None