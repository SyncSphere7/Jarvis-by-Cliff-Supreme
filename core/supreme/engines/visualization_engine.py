"""
Supreme Visualization Engine
Dynamic data visualization and dashboard creation capabilities.
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

from ..base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse

class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    BOX_PLOT = "box_plot"
    AREA = "area"
    GAUGE = "gauge"
    TREEMAP = "treemap"

class VisualizationTheme(Enum):
    LIGHT = "light"
    DARK = "dark"
    CORPORATE = "corporate"
    COLORFUL = "colorful"
    MINIMAL = "minimal"

@dataclass
class VisualizationConfig:
    """Configuration for a visualization"""
    viz_id: str
    title: str
    chart_type: ChartType
    data_source: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    color_by: Optional[str] = None
    size_by: Optional[str] = None
    filters: Dict[str, Any] = None
    aggregations: Dict[str, str] = None
    theme: VisualizationTheme = VisualizationTheme.LIGHT
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = {}
        if self.aggregations is None:
            self.aggregations = {}

@dataclass
class Dashboard:
    """Represents a dashboard with multiple visualizations"""
    dashboard_id: str
    dashboard_name: str
    description: str
    visualizations: List[str]  # List of visualization IDs
    layout: Dict[str, Any] = None
    theme: VisualizationTheme = VisualizationTheme.LIGHT
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.layout is None:
            self.layout = {"type": "grid", "columns": 2}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class VisualizationData:
    """Processed data for visualization"""
    viz_id: str
    chart_type: ChartType
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class SupremeVisualizationEngine(BaseSupremeEngine):
    """
    Supreme visualization engine with dynamic chart generation.
    Automatically selects optimal visualizations and creates interactive dashboards.
    """
    
    def __init__(self, engine_name: str, config):
        super().__init__(engine_name, config)
        
        # Visualization storage
        self.visualizations: Dict[str, VisualizationConfig] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.visualization_data: Dict[str, VisualizationData] = {}
        
        # Visualization capabilities
        self.viz_capabilities = {
            "create_visualization": self._create_visualization,
            "create_dashboard": self._create_dashboard,
            "auto_visualize": self._auto_visualize_data,
            "update_visualization": self._update_visualization,
            "generate_chart_data": self._generate_chart_data,
            "suggest_visualizations": self._suggest_visualizations,
            "export_visualization": self._export_visualization
        }
        
        # Chart type recommendations
        self.chart_recommendations = self._initialize_chart_recommendations()
        
        # Data persistence
        self.data_dir = "data/visualizations"
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def _initialize_engine(self) -> bool:
        """Initialize the visualization engine"""
        try:
            self.logger.info("Initializing Supreme Visualization Engine...")
            
            # Load existing visualization data
            await self._load_visualization_data()
            
            self.logger.info(f"Visualization Engine initialized with {len(self.visualizations)} visualizations")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Visualization Engine: {e}")
            return False
    
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Execute visualization operation"""
        operation = request.operation.lower()
        parameters = request.parameters
        
        # Route to appropriate visualization capability
        if "create" in operation and "visualization" in operation:
            return await self._create_visualization(parameters)
        elif "create" in operation and "dashboard" in operation:
            return await self._create_dashboard(parameters)
        elif "auto" in operation and "visualize" in operation:
            return await self._auto_visualize_data(parameters)
        elif "update" in operation:
            return await self._update_visualization(parameters)
        elif "generate" in operation and "chart" in operation:
            return await self._generate_chart_data(parameters)
        elif "suggest" in operation:
            return await self._suggest_visualizations(parameters)
        elif "export" in operation:
            return await self._export_visualization(parameters)
        else:
            return await self._get_visualization_status(parameters)
    
    async def get_supported_operations(self) -> List[str]:
        """Get supported visualization operations"""
        return [
            "create_visualization", "create_dashboard", "auto_visualize", "update_visualization",
            "generate_chart_data", "suggest_visualizations", "export_visualization", "viz_status"
        ]
    
    async def _create_visualization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new visualization"""
        try:
            title = parameters.get("title", "Untitled Visualization")
            chart_type = parameters.get("chart_type", "auto")
            data_source = parameters.get("data_source")
            data = parameters.get("data")
            x_axis = parameters.get("x_axis")
            y_axis = parameters.get("y_axis")
            color_by = parameters.get("color_by")
            theme = parameters.get("theme", "light")
            
            if not data_source and not data:
                return {"error": "data_source or data is required", "operation": "create_visualization"}
            
            # Load data if needed
            if data_source and not data:
                data = await self._load_data_from_source(data_source)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # Auto-select chart type if needed
            if chart_type == "auto":
                chart_type = await self._auto_select_chart_type(df, x_axis, y_axis)
            
            # Generate visualization ID
            viz_id = self._generate_viz_id(title)
            
            # Create visualization configuration
            viz_config = VisualizationConfig(
                viz_id=viz_id,
                title=title,
                chart_type=ChartType(chart_type),
                data_source=data_source or "provided_data",
                x_axis=x_axis,
                y_axis=y_axis,
                color_by=color_by,
                theme=VisualizationTheme(theme)
            )
            
            # Generate chart data
            chart_data = await self._prepare_chart_data(df, viz_config)
            
            # Store visualization
            self.visualizations[viz_id] = viz_config
            self.visualization_data[viz_id] = VisualizationData(
                viz_id=viz_id,
                chart_type=ChartType(chart_type),
                data=chart_data,
                metadata={
                    "data_shape": df.shape,
                    "columns": df.columns.tolist(),
                    "created_at": datetime.now().isoformat()
                }
            )
            
            result = {
                "operation": "create_visualization",
                "viz_id": viz_id,
                "title": title,
                "chart_type": chart_type,
                "data_points": len(chart_data),
                "chart_config": {
                    "x_axis": x_axis,
                    "y_axis": y_axis,
                    "color_by": color_by,
                    "theme": theme
                },
                "chart_data": chart_data[:100]  # Limit data in response
            }
            
            # Save visualization data
            await self._save_visualization_data()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating visualization: {e}")
            return {"error": str(e), "operation": "create_visualization"}
    
    async def _create_dashboard(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard"""
        try:
            dashboard_name = parameters.get("dashboard_name")
            description = parameters.get("description", "")
            visualizations = parameters.get("visualizations", [])
            layout = parameters.get("layout", {"type": "grid", "columns": 2})
            theme = parameters.get("theme", "light")
            
            if not dashboard_name:
                return {"error": "dashboard_name is required", "operation": "create_dashboard"}
            
            # Generate dashboard ID
            dashboard_id = self._generate_dashboard_id(dashboard_name)
            
            # Validate visualization IDs
            valid_visualizations = []
            for viz_id in visualizations:
                if viz_id in self.visualizations:
                    valid_visualizations.append(viz_id)
                else:
                    self.logger.warning(f"Visualization {viz_id} not found, skipping")
            
            # Create dashboard
            dashboard = Dashboard(
                dashboard_id=dashboard_id,
                dashboard_name=dashboard_name,
                description=description,
                visualizations=valid_visualizations,
                layout=layout,
                theme=VisualizationTheme(theme)
            )
            
            # Store dashboard
            self.dashboards[dashboard_id] = dashboard
            
            result = {
                "operation": "create_dashboard",
                "dashboard_id": dashboard_id,
                "dashboard_name": dashboard_name,
                "visualizations_count": len(valid_visualizations),
                "layout": layout,
                "theme": theme,
                "created_at": dashboard.created_at.isoformat()
            }
            
            # Save visualization data
            await self._save_visualization_data()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            return {"error": str(e), "operation": "create_dashboard"}
    
    async def _auto_visualize_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically create optimal visualizations for data"""
        try:
            data_source = parameters.get("data_source")
            data = parameters.get("data")
            max_visualizations = parameters.get("max_visualizations", 5)
            
            if not data_source and not data:
                return {"error": "data_source or data is required", "operation": "auto_visualize"}
            
            # Load data if needed
            if data_source and not data:
                data = await self._load_data_from_source(data_source)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # Generate multiple visualization suggestions
            suggestions = await self._generate_visualization_suggestions(df, max_visualizations)
            
            created_visualizations = []
            
            # Create visualizations based on suggestions
            for i, suggestion in enumerate(suggestions[:max_visualizations]):
                viz_params = {
                    "title": suggestion["title"],
                    "chart_type": suggestion["chart_type"],
                    "data": df,
                    "x_axis": suggestion.get("x_axis"),
                    "y_axis": suggestion.get("y_axis"),
                    "color_by": suggestion.get("color_by")
                }
                
                viz_result = await self._create_visualization(viz_params)
                if "viz_id" in viz_result:
                    created_visualizations.append({
                        "viz_id": viz_result["viz_id"],
                        "title": viz_result["title"],
                        "chart_type": viz_result["chart_type"],
                        "reasoning": suggestion["reasoning"]
                    })
            
            result = {
                "operation": "auto_visualize",
                "data_source": data_source or "provided_data",
                "data_shape": df.shape,
                "visualizations_created": len(created_visualizations),
                "visualizations": created_visualizations
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error auto-visualizing data: {e}")
            return {"error": str(e), "operation": "auto_visualize"}
    
    async def _update_visualization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing visualization"""
        try:
            viz_id = parameters.get("viz_id")
            updates = parameters.get("updates", {})
            
            if not viz_id:
                return {"error": "viz_id is required", "operation": "update_visualization"}
            
            if viz_id not in self.visualizations:
                return {"error": f"Visualization {viz_id} not found", "operation": "update_visualization"}
            
            viz_config = self.visualizations[viz_id]
            
            # Apply updates
            if "title" in updates:
                viz_config.title = updates["title"]
            if "chart_type" in updates:
                viz_config.chart_type = ChartType(updates["chart_type"])
            if "x_axis" in updates:
                viz_config.x_axis = updates["x_axis"]
            if "y_axis" in updates:
                viz_config.y_axis = updates["y_axis"]
            if "color_by" in updates:
                viz_config.color_by = updates["color_by"]
            if "theme" in updates:
                viz_config.theme = VisualizationTheme(updates["theme"])
            
            # Regenerate chart data if needed
            if any(key in updates for key in ["chart_type", "x_axis", "y_axis", "color_by"]):
                # Load original data and regenerate
                data = await self._load_data_from_source(viz_config.data_source)
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = data
                
                chart_data = await self._prepare_chart_data(df, viz_config)
                
                # Update visualization data
                self.visualization_data[viz_id].chart_type = viz_config.chart_type
                self.visualization_data[viz_id].data = chart_data
            
            result = {
                "operation": "update_visualization",
                "viz_id": viz_id,
                "updates_applied": list(updates.keys()),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save visualization data
            await self._save_visualization_data()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error updating visualization: {e}")
            return {"error": str(e), "operation": "update_visualization"}
    
    async def _generate_chart_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data for a visualization"""
        try:
            viz_id = parameters.get("viz_id")
            
            if not viz_id:
                return {"error": "viz_id is required", "operation": "generate_chart_data"}
            
            if viz_id not in self.visualization_data:
                return {"error": f"Visualization data {viz_id} not found", "operation": "generate_chart_data"}
            
            viz_data = self.visualization_data[viz_id]
            
            result = {
                "operation": "generate_chart_data",
                "viz_id": viz_id,
                "chart_type": viz_data.chart_type.value,
                "data_points": len(viz_data.data),
                "chart_data": viz_data.data,
                "metadata": viz_data.metadata
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating chart data: {e}")
            return {"error": str(e), "operation": "generate_chart_data"}
    
    async def _suggest_visualizations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest optimal visualizations for data"""
        try:
            data_source = parameters.get("data_source")
            data = parameters.get("data")
            max_suggestions = parameters.get("max_suggestions", 10)
            
            if not data_source and not data:
                return {"error": "data_source or data is required", "operation": "suggest_visualizations"}
            
            # Load data if needed
            if data_source and not data:
                data = await self._load_data_from_source(data_source)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # Generate suggestions
            suggestions = await self._generate_visualization_suggestions(df, max_suggestions)
            
            result = {
                "operation": "suggest_visualizations",
                "data_source": data_source or "provided_data",
                "data_shape": df.shape,
                "suggestions_count": len(suggestions),
                "suggestions": suggestions
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error suggesting visualizations: {e}")
            return {"error": str(e), "operation": "suggest_visualizations"}
    
    async def _export_visualization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Export visualization in various formats"""
        try:
            viz_id = parameters.get("viz_id")
            export_format = parameters.get("format", "json")  # json, csv, png, svg
            
            if not viz_id:
                return {"error": "viz_id is required", "operation": "export_visualization"}
            
            if viz_id not in self.visualization_data:
                return {"error": f"Visualization {viz_id} not found", "operation": "export_visualization"}
            
            viz_data = self.visualization_data[viz_id]
            viz_config = self.visualizations[viz_id]
            
            # Export based on format
            if export_format == "json":
                export_data = {
                    "visualization_config": asdict(viz_config),
                    "chart_data": viz_data.data,
                    "metadata": viz_data.metadata
                }
            elif export_format == "csv":
                # Convert chart data to CSV format
                df = pd.DataFrame(viz_data.data)
                export_data = df.to_csv(index=False)
            else:
                # For image formats, return configuration for client-side rendering
                export_data = {
                    "chart_type": viz_data.chart_type.value,
                    "config": asdict(viz_config),
                    "data": viz_data.data,
                    "format": export_format
                }
            
            result = {
                "operation": "export_visualization",
                "viz_id": viz_id,
                "format": export_format,
                "export_data": export_data,
                "exported_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error exporting visualization: {e}")
            return {"error": str(e), "operation": "export_visualization"}
    
    async def _get_visualization_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get visualization engine status"""
        try:
            total_visualizations = len(self.visualizations)
            total_dashboards = len(self.dashboards)
            
            # Visualizations by type
            viz_by_type = {}
            for viz in self.visualizations.values():
                chart_type = viz.chart_type.value
                viz_by_type[chart_type] = viz_by_type.get(chart_type, 0) + 1
            
            # Recent visualizations
            recent_viz = [
                {
                    "viz_id": viz_id,
                    "title": viz.title,
                    "chart_type": viz.chart_type.value,
                    "data_source": viz.data_source
                }
                for viz_id, viz in list(self.visualizations.items())[-10:]
            ]
            
            result = {
                "operation": "viz_status",
                "total_visualizations": total_visualizations,
                "total_dashboards": total_dashboards,
                "visualizations_by_type": viz_by_type,
                "recent_visualizations": recent_viz,
                "supported_chart_types": [chart_type.value for chart_type in ChartType],
                "supported_themes": [theme.value for theme in VisualizationTheme]
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting visualization status: {e}")
            return {"error": str(e), "operation": "viz_status"} 
   
    # Helper methods for visualization
    
    def _initialize_chart_recommendations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize chart type recommendations based on data characteristics"""
        return {
            "single_numeric": {
                "chart_types": ["histogram", "box_plot"],
                "reasoning": "Single numeric variable best shown with distribution charts"
            },
            "two_numeric": {
                "chart_types": ["scatter", "line"],
                "reasoning": "Two numeric variables show relationships well with scatter or line charts"
            },
            "categorical_numeric": {
                "chart_types": ["bar", "box_plot"],
                "reasoning": "Categorical vs numeric data works well with bar charts or box plots"
            },
            "time_series": {
                "chart_types": ["line", "area"],
                "reasoning": "Time series data is best visualized with line or area charts"
            },
            "categorical_only": {
                "chart_types": ["pie", "bar"],
                "reasoning": "Categorical data works well with pie charts or bar charts"
            },
            "multiple_numeric": {
                "chart_types": ["heatmap", "scatter"],
                "reasoning": "Multiple numeric variables can be shown with heatmaps or scatter plots"
            }
        }
    
    async def _load_visualization_data(self):
        """Load existing visualization data"""
        try:
            viz_file = os.path.join(self.data_dir, "visualizations.json")
            if os.path.exists(viz_file):
                with open(viz_file, 'r') as f:
                    viz_data = json.load(f)
                    for viz_id, viz_config_data in viz_data.get("visualizations", {}).items():
                        viz_config = VisualizationConfig(
                            viz_id=viz_id,
                            title=viz_config_data['title'],
                            chart_type=ChartType(viz_config_data['chart_type']),
                            data_source=viz_config_data['data_source'],
                            x_axis=viz_config_data.get('x_axis'),
                            y_axis=viz_config_data.get('y_axis'),
                            color_by=viz_config_data.get('color_by'),
                            theme=VisualizationTheme(viz_config_data.get('theme', 'light'))
                        )
                        self.visualizations[viz_id] = viz_config
                    
                    for dashboard_id, dashboard_data in viz_data.get("dashboards", {}).items():
                        dashboard = Dashboard(
                            dashboard_id=dashboard_id,
                            dashboard_name=dashboard_data['dashboard_name'],
                            description=dashboard_data['description'],
                            visualizations=dashboard_data['visualizations'],
                            layout=dashboard_data['layout'],
                            theme=VisualizationTheme(dashboard_data.get('theme', 'light')),
                            created_at=datetime.fromisoformat(dashboard_data['created_at']),
                            updated_at=datetime.fromisoformat(dashboard_data['updated_at'])
                        )
                        self.dashboards[dashboard_id] = dashboard
                        
        except Exception as e:
            self.logger.warning(f"Could not load visualization data: {e}")
    
    async def _save_visualization_data(self):
        """Save visualization data"""
        try:
            viz_data = {
                "visualizations": {
                    viz_id: {
                        'title': viz.title,
                        'chart_type': viz.chart_type.value,
                        'data_source': viz.data_source,
                        'x_axis': viz.x_axis,
                        'y_axis': viz.y_axis,
                        'color_by': viz.color_by,
                        'theme': viz.theme.value
                    }
                    for viz_id, viz in self.visualizations.items()
                },
                "dashboards": {
                    dashboard_id: {
                        'dashboard_name': dashboard.dashboard_name,
                        'description': dashboard.description,
                        'visualizations': dashboard.visualizations,
                        'layout': dashboard.layout,
                        'theme': dashboard.theme.value,
                        'created_at': dashboard.created_at.isoformat(),
                        'updated_at': dashboard.updated_at.isoformat()
                    }
                    for dashboard_id, dashboard in self.dashboards.items()
                }
            }
            
            viz_file = os.path.join(self.data_dir, "visualizations.json")
            with open(viz_file, 'w') as f:
                json.dump(viz_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Could not save visualization data: {e}")
    
    def _generate_viz_id(self, title: str) -> str:
        """Generate unique visualization ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{title}_{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_dashboard_id(self, name: str) -> str:
        """Generate unique dashboard ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{name}_{timestamp}".encode()).hexdigest()[:16]
    
    async def _load_data_from_source(self, data_source: str) -> pd.DataFrame:
        """Load data from various sources"""
        # This would implement actual data loading logic
        # For now, return mock data
        return pd.DataFrame([
            {"x": 1, "y": 10, "category": "A", "timestamp": "2024-01-01"},
            {"x": 2, "y": 15, "category": "B", "timestamp": "2024-01-02"},
            {"x": 3, "y": 12, "category": "A", "timestamp": "2024-01-03"},
            {"x": 4, "y": 18, "category": "B", "timestamp": "2024-01-04"},
            {"x": 5, "y": 14, "category": "A", "timestamp": "2024-01-05"}
        ])
    
    async def _auto_select_chart_type(self, df: pd.DataFrame, x_axis: str = None, y_axis: str = None) -> str:
        """Automatically select the best chart type for the data"""
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_columns = []
            
            # Check for datetime columns
            for col in df.columns:
                try:
                    pd.to_datetime(df[col])
                    datetime_columns.append(col)
                except:
                    pass
            
            # Decision logic for chart type
            if datetime_columns and numeric_columns:
                return "line"  # Time series data
            elif len(numeric_columns) >= 2:
                return "scatter"  # Two or more numeric variables
            elif len(numeric_columns) == 1 and len(categorical_columns) >= 1:
                return "bar"  # Categorical vs numeric
            elif len(categorical_columns) >= 1 and not numeric_columns:
                return "pie"  # Categorical only
            elif len(numeric_columns) == 1:
                return "histogram"  # Single numeric variable
            else:
                return "bar"  # Default fallback
                
        except Exception as e:
            self.logger.error(f"Error auto-selecting chart type: {e}")
            return "bar"  # Safe fallback
    
    async def _prepare_chart_data(self, df: pd.DataFrame, viz_config: VisualizationConfig) -> List[Dict[str, Any]]:
        """Prepare data for chart rendering"""
        try:
            chart_data = []
            
            if viz_config.chart_type == ChartType.LINE:
                chart_data = self._prepare_line_chart_data(df, viz_config)
            elif viz_config.chart_type == ChartType.BAR:
                chart_data = self._prepare_bar_chart_data(df, viz_config)
            elif viz_config.chart_type == ChartType.SCATTER:
                chart_data = self._prepare_scatter_chart_data(df, viz_config)
            elif viz_config.chart_type == ChartType.PIE:
                chart_data = self._prepare_pie_chart_data(df, viz_config)
            elif viz_config.chart_type == ChartType.HISTOGRAM:
                chart_data = self._prepare_histogram_data(df, viz_config)
            elif viz_config.chart_type == ChartType.HEATMAP:
                chart_data = self._prepare_heatmap_data(df, viz_config)
            else:
                # Default to simple data conversion
                chart_data = df.to_dict('records')
            
            return chart_data
            
        except Exception as e:
            self.logger.error(f"Error preparing chart data: {e}")
            return df.to_dict('records')  # Fallback to raw data
    
    def _prepare_line_chart_data(self, df: pd.DataFrame, viz_config: VisualizationConfig) -> List[Dict[str, Any]]:
        """Prepare data for line chart"""
        try:
            if viz_config.x_axis and viz_config.y_axis:
                data = df[[viz_config.x_axis, viz_config.y_axis]].copy()
                
                # Add color grouping if specified
                if viz_config.color_by and viz_config.color_by in df.columns:
                    data[viz_config.color_by] = df[viz_config.color_by]
                
                return data.to_dict('records')
            else:
                # Auto-select columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_cols) >= 2:
                    return df[numeric_cols[:2]].to_dict('records')
                else:
                    return df.to_dict('records')
                    
        except Exception as e:
            self.logger.error(f"Error preparing line chart data: {e}")
            return df.to_dict('records')
    
    def _prepare_bar_chart_data(self, df: pd.DataFrame, viz_config: VisualizationConfig) -> List[Dict[str, Any]]:
        """Prepare data for bar chart"""
        try:
            if viz_config.x_axis and viz_config.y_axis:
                # Group by x_axis and aggregate y_axis
                grouped = df.groupby(viz_config.x_axis)[viz_config.y_axis].sum().reset_index()
                return grouped.to_dict('records')
            else:
                # Auto-select: categorical column for x, numeric for y
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if categorical_cols and numeric_cols:
                    grouped = df.groupby(categorical_cols[0])[numeric_cols[0]].sum().reset_index()
                    return grouped.to_dict('records')
                else:
                    return df.to_dict('records')
                    
        except Exception as e:
            self.logger.error(f"Error preparing bar chart data: {e}")
            return df.to_dict('records')
    
    def _prepare_scatter_chart_data(self, df: pd.DataFrame, viz_config: VisualizationConfig) -> List[Dict[str, Any]]:
        """Prepare data for scatter plot"""
        try:
            if viz_config.x_axis and viz_config.y_axis:
                data = df[[viz_config.x_axis, viz_config.y_axis]].copy()
                
                # Add color and size dimensions if specified
                if viz_config.color_by and viz_config.color_by in df.columns:
                    data[viz_config.color_by] = df[viz_config.color_by]
                if viz_config.size_by and viz_config.size_by in df.columns:
                    data[viz_config.size_by] = df[viz_config.size_by]
                
                return data.to_dict('records')
            else:
                # Auto-select first two numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_cols) >= 2:
                    return df[numeric_cols[:2]].to_dict('records')
                else:
                    return df.to_dict('records')
                    
        except Exception as e:
            self.logger.error(f"Error preparing scatter chart data: {e}")
            return df.to_dict('records')
    
    def _prepare_pie_chart_data(self, df: pd.DataFrame, viz_config: VisualizationConfig) -> List[Dict[str, Any]]:
        """Prepare data for pie chart"""
        try:
            if viz_config.x_axis:
                # Count occurrences of each category
                value_counts = df[viz_config.x_axis].value_counts()
                return [{"label": str(label), "value": int(count)} for label, count in value_counts.items()]
            else:
                # Auto-select first categorical column
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                if categorical_cols:
                    value_counts = df[categorical_cols[0]].value_counts()
                    return [{"label": str(label), "value": int(count)} for label, count in value_counts.items()]
                else:
                    return df.to_dict('records')
                    
        except Exception as e:
            self.logger.error(f"Error preparing pie chart data: {e}")
            return df.to_dict('records')
    
    def _prepare_histogram_data(self, df: pd.DataFrame, viz_config: VisualizationConfig) -> List[Dict[str, Any]]:
        """Prepare data for histogram"""
        try:
            if viz_config.x_axis:
                column = viz_config.x_axis
            else:
                # Auto-select first numeric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                column = numeric_cols[0] if numeric_cols else df.columns[0]
            
            # Create histogram bins
            values = df[column].dropna()
            hist, bin_edges = np.histogram(values, bins=20)
            
            histogram_data = []
            for i in range(len(hist)):
                histogram_data.append({
                    "bin_start": float(bin_edges[i]),
                    "bin_end": float(bin_edges[i + 1]),
                    "count": int(hist[i])
                })
            
            return histogram_data
            
        except Exception as e:
            self.logger.error(f"Error preparing histogram data: {e}")
            return df.to_dict('records')
    
    def _prepare_heatmap_data(self, df: pd.DataFrame, viz_config: VisualizationConfig) -> List[Dict[str, Any]]:
        """Prepare data for heatmap"""
        try:
            # Use correlation matrix for numeric data
            numeric_df = df.select_dtypes(include=[np.number])
            
            if len(numeric_df.columns) >= 2:
                correlation_matrix = numeric_df.corr()
                
                heatmap_data = []
                for i, row_name in enumerate(correlation_matrix.index):
                    for j, col_name in enumerate(correlation_matrix.columns):
                        heatmap_data.append({
                            "x": col_name,
                            "y": row_name,
                            "value": float(correlation_matrix.iloc[i, j])
                        })
                
                return heatmap_data
            else:
                return df.to_dict('records')
                
        except Exception as e:
            self.logger.error(f"Error preparing heatmap data: {e}")
            return df.to_dict('records')
    
    async def _generate_visualization_suggestions(self, df: pd.DataFrame, max_suggestions: int) -> List[Dict[str, Any]]:
        """Generate visualization suggestions based on data characteristics"""
        suggestions = []
        
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Check for datetime columns
            datetime_columns = []
            for col in df.columns:
                try:
                    pd.to_datetime(df[col])
                    datetime_columns.append(col)
                except:
                    pass
            
            # Generate suggestions based on data characteristics
            
            # Time series suggestions
            if datetime_columns and numeric_columns:
                for dt_col in datetime_columns[:2]:
                    for num_col in numeric_columns[:3]:
                        suggestions.append({
                            "title": f"{num_col} over {dt_col}",
                            "chart_type": "line",
                            "x_axis": dt_col,
                            "y_axis": num_col,
                            "reasoning": "Time series data is best visualized with line charts"
                        })
            
            # Categorical vs Numeric suggestions
            if categorical_columns and numeric_columns:
                for cat_col in categorical_columns[:2]:
                    for num_col in numeric_columns[:3]:
                        suggestions.append({
                            "title": f"{num_col} by {cat_col}",
                            "chart_type": "bar",
                            "x_axis": cat_col,
                            "y_axis": num_col,
                            "reasoning": "Categorical vs numeric data works well with bar charts"
                        })
            
            # Numeric correlation suggestions
            if len(numeric_columns) >= 2:
                for i, col1 in enumerate(numeric_columns[:3]):
                    for col2 in numeric_columns[i+1:4]:
                        suggestions.append({
                            "title": f"{col1} vs {col2}",
                            "chart_type": "scatter",
                            "x_axis": col1,
                            "y_axis": col2,
                            "reasoning": "Scatter plots show relationships between numeric variables"
                        })
            
            # Distribution suggestions
            for num_col in numeric_columns[:3]:
                suggestions.append({
                    "title": f"Distribution of {num_col}",
                    "chart_type": "histogram",
                    "x_axis": num_col,
                    "reasoning": "Histograms show the distribution of numeric data"
                })
            
            # Categorical distribution suggestions
            for cat_col in categorical_columns[:2]:
                suggestions.append({
                    "title": f"Distribution of {cat_col}",
                    "chart_type": "pie",
                    "x_axis": cat_col,
                    "reasoning": "Pie charts show the distribution of categorical data"
                })
            
            # Correlation heatmap suggestion
            if len(numeric_columns) >= 3:
                suggestions.append({
                    "title": "Correlation Heatmap",
                    "chart_type": "heatmap",
                    "reasoning": "Heatmaps show correlations between multiple numeric variables"
                })
            
            # Limit and return suggestions
            return suggestions[:max_suggestions]
            
        except Exception as e:
            self.logger.error(f"Error generating visualization suggestions: {e}")
            return []