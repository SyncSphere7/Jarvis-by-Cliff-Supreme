"""
Strategic Planner
Advanced strategic planning and scenario analysis capabilities.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class StrategyType(Enum):
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    OPERATIONAL = "operational"
    GROWTH = "growth"

@dataclass
class StrategicGoal:
    goal_id: str
    description: str
    priority: int
    success_metrics: List[str]
    confidence: float

@dataclass
class StrategicPlan:
    plan_id: str
    title: str
    strategy_type: StrategyType
    goals: List[StrategicGoal]
    action_items: List[str]
    success_metrics: List[str]
    overall_confidence: float

class StrategicPlanner:
    """Advanced strategic planning engine."""
    
    def __init__(self):
        self.logger = logging.getLogger("supreme.strategic_planner")
    
    def create_strategic_plan(self, objective: str, context: Dict[str, Any] = None) -> StrategicPlan:
        """Create a comprehensive strategic plan"""
        try:
            if context is None:
                context = {}
            
            self.logger.info(f"Creating strategic plan for: {objective}")
            
            strategy_type = self._classify_strategy_type(objective)
            goals = self._define_strategic_goals(objective, strategy_type)
            action_items = self._create_action_items(goals)
            success_metrics = self._define_success_metrics(goals)
            overall_confidence = self._calculate_plan_confidence(goals)
            
            plan = StrategicPlan(
                plan_id=f"plan_{hash(objective) % 10000}",
                title=f"Strategic Plan: {objective}",
                strategy_type=strategy_type,
                goals=goals,
                action_items=action_items,
                success_metrics=success_metrics,
                overall_confidence=overall_confidence
            )
            
            self.logger.info(f"Strategic plan created with {len(goals)} goals")
            return plan
            
        except Exception as e:
            self.logger.error(f"Error creating strategic plan: {e}")
            return self._create_error_plan(objective, str(e))
    
    def _classify_strategy_type(self, objective: str) -> StrategyType:
        """Classify the type of strategy"""
        objective_lower = objective.lower()
        
        if any(word in objective_lower for word in ["technology", "digital", "tech"]):
            return StrategyType.TECHNOLOGY
        elif any(word in objective_lower for word in ["operations", "process", "efficiency"]):
            return StrategyType.OPERATIONAL
        elif any(word in objective_lower for word in ["growth", "expand", "scale"]):
            return StrategyType.GROWTH
        else:
            return StrategyType.BUSINESS
    
    def _define_strategic_goals(self, objective: str, strategy_type: StrategyType) -> List[StrategicGoal]:
        """Define strategic goals based on objective and type"""
        if strategy_type == StrategyType.BUSINESS:
            return [
                StrategicGoal(
                    goal_id="business_goal_1",
                    description="Increase market share and competitive position",
                    priority=1,
                    success_metrics=["Market share growth", "Revenue increase"],
                    confidence=0.7
                )
            ]
        elif strategy_type == StrategyType.TECHNOLOGY:
            return [
                StrategicGoal(
                    goal_id="tech_goal_1",
                    description="Implement advanced technology solutions",
                    priority=1,
                    success_metrics=["Technology adoption", "System performance"],
                    confidence=0.6
                )
            ]
        else:
            return [
                StrategicGoal(
                    goal_id="generic_goal_1",
                    description=f"Achieve strategic objective: {objective}",
                    priority=1,
                    success_metrics=["Objective completion"],
                    confidence=0.6
                )
            ]
    
    def _create_action_items(self, goals: List[StrategicGoal]) -> List[str]:
        """Create action items based on goals"""
        action_items = []
        for goal in goals:
            action_items.append(f"Develop detailed plan for: {goal.description}")
            action_items.append(f"Allocate resources for: {goal.description}")
        return action_items
    
    def _define_success_metrics(self, goals: List[StrategicGoal]) -> List[str]:
        """Define overall success metrics"""
        metrics = set()
        for goal in goals:
            metrics.update(goal.success_metrics)
        return list(metrics)
    
    def _calculate_plan_confidence(self, goals: List[StrategicGoal]) -> float:
        """Calculate overall plan confidence"""
        if not goals:
            return 0.0
        return sum(goal.confidence for goal in goals) / len(goals)
    
    def _create_error_plan(self, objective: str, error: str) -> StrategicPlan:
        """Create error plan when strategic planning fails"""
        return StrategicPlan(
            plan_id="error_plan",
            title=f"Error in strategic planning for: {objective}",
            strategy_type=StrategyType.BUSINESS,
            goals=[],
            action_items=[f"Error occurred: {error}"],
            success_metrics=[],
            overall_confidence=0.0
        )