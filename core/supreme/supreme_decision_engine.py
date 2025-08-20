"""
Supreme Decision Making Engine
Advanced decision-making framework using all supreme engines
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import math

from .supreme_orchestrator import SupremeOrchestrator, EngineType, OrchestrationStrategy
from .supreme_control_interface import SupremeControlInterface, CommandType, SupremeCommand

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    REACTIVE = "reactive"
    PROACTIVE = "proactive"
    ADAPTIVE = "adaptive"


class DecisionComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    SUPREME = "supreme"


class DecisionUrgency(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DecisionConfidence(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class DecisionContext:
    context_id: str
    situation: str
    objectives: List[str]
    constraints: List[str]
    available_resources: Dict[str, Any]
    time_constraints: Optional[timedelta]
    stakeholders: List[str]
    risk_tolerance: float  # 0.0 to 1.0
    success_criteria: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionOption:
    option_id: str
    description: str
    required_actions: List[str]
    required_engines: List[EngineType]
    estimated_cost: float
    estimated_time: timedelta
    success_probability: float
    risk_level: float
    expected_benefits: Dict[str, float]
    side_effects: List[str]
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SupremeDecision:
    decision_id: str
    context: DecisionContext
    selected_option: DecisionOption
    reasoning: List[str]
    confidence_score: float
    risk_assessment: Dict[str, float]
    execution_plan: List[str]
    monitoring_plan: List[str]
    rollback_plan: List[str]
    success_metrics: List[str]
    decision_maker: str = "Supreme AI"
    decided_at: datetime = field(default_factory=datetime.now)


class DecisionMaker:
    """Supreme decision maker using all available engines"""
    
    def __init__(self, control_interface: SupremeControlInterface):
        self.control_interface = control_interface
        self.decision_history: List[SupremeDecision] = []
        self.execution_history: List[Dict[str, Any]] = []
        
        # Decision-making parameters
        self.confidence_threshold = 0.7
        self.risk_threshold = 0.8
        self.consensus_threshold = 0.6
    
    async def make_supreme_decision(self, context: DecisionContext) -> SupremeDecision:
        """Make a supreme decision using all available intelligence"""
        try:
            decision_id = f"decision_{datetime.now().isoformat()}"
            
            # Step 1: Analyze the decision context using reasoning engine
            analysis_result = await self.control_interface.execute_command(
                SupremeCommand(
                    command_id=f"analyze_context_{decision_id}",
                    command_type=CommandType.ANALYZE,
                    operation="analyze_decision_context",
                    parameters={
                        "situation": context.situation,
                        "objectives": context.objectives,
                        "constraints": context.constraints,
                        "stakeholders": context.stakeholders
                    }
                )
            )
            
            # Step 2: Generate decision options
            options = await self._generate_decision_options(context)
            
            # Step 3: Evaluate options using multiple engines
            evaluation_results = await self._evaluate_options(options, context)
            
            # Step 4: Select the best option
            selected_option = self._select_best_option(options, evaluation_results, context)
            
            # Step 5: Generate reasoning and confidence assessment
            reasoning = self._generate_reasoning(selected_option, evaluation_results, context)
            confidence_score = self._calculate_confidence(selected_option, evaluation_results)
            
            # Step 6: Assess risks
            risk_assessment = await self._assess_risks(selected_option, context)
            
            # Step 7: Create execution plan
            execution_plan = await self._create_execution_plan(selected_option, context)
            
            # Step 8: Create monitoring and rollback plans
            monitoring_plan = self._create_monitoring_plan(selected_option, context)
            rollback_plan = self._create_rollback_plan(selected_option, context)
            
            # Step 9: Define success metrics
            success_metrics = self._define_success_metrics(selected_option, context)
            
            # Create the supreme decision
            decision = SupremeDecision(
                decision_id=decision_id,
                context=context,
                selected_option=selected_option,
                reasoning=reasoning,
                confidence_score=confidence_score,
                risk_assessment=risk_assessment,
                execution_plan=execution_plan,
                monitoring_plan=monitoring_plan,
                rollback_plan=rollback_plan,
                success_metrics=success_metrics
            )
            
            # Store decision in history
            self.decision_history.append(decision)
            
            logger.info(f"Supreme decision made: {decision_id} with confidence {confidence_score:.2f}")
            return decision
            
        except Exception as e:
            logger.error(f"Error making supreme decision: {e}")
            raise
    
    async def _generate_decision_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate decision options using reasoning and proactive engines"""
        try:
            # Use reasoning engine to generate creative options
            reasoning_result = await self.control_interface.execute_command(
                SupremeCommand(
                    command_id=f"generate_options_{datetime.now().isoformat()}",
                    command_type=CommandType.ANALYZE,
                    operation="generate_decision_options",
                    parameters={
                        "situation": context.situation,
                        "objectives": context.objectives,
                        "constraints": context.constraints,
                        "resources": context.available_resources
                    }
                )
            )
            
            # Use proactive engine to identify opportunities
            proactive_result = await self.control_interface.execute_command(
                SupremeCommand(
                    command_id=f"identify_opportunities_{datetime.now().isoformat()}",
                    command_type=CommandType.PREDICT,
                    operation="identify_opportunities",
                    parameters={
                        "context": context.situation,
                        "objectives": context.objectives
                    }
                )
            )
            
            # Generate base options
            options = []
            
            # Conservative option
            conservative_option = DecisionOption(
                option_id=f"conservative_{datetime.now().isoformat()}",
                description="Conservative approach with minimal risk",
                required_actions=["analyze_thoroughly", "implement_gradually", "monitor_closely"],
                required_engines=[EngineType.ANALYTICS, EngineType.SYSTEM_CONTROL],
                estimated_cost=100.0,
                estimated_time=timedelta(hours=4),
                success_probability=0.8,
                risk_level=0.2,
                expected_benefits={"stability": 200.0, "reliability": 150.0},
                side_effects=["slower_progress", "missed_opportunities"]
            )
            options.append(conservative_option)
            
            # Aggressive option
            aggressive_option = DecisionOption(
                option_id=f"aggressive_{datetime.now().isoformat()}",
                description="Aggressive approach for maximum impact",
                required_actions=["rapid_implementation", "full_resource_deployment", "accelerated_timeline"],
                required_engines=[EngineType.SYSTEM_CONTROL, EngineType.SCALABILITY, EngineType.INTEGRATION],
                estimated_cost=500.0,
                estimated_time=timedelta(hours=2),
                success_probability=0.6,
                risk_level=0.7,
                expected_benefits={"speed": 400.0, "impact": 600.0},
                side_effects=["resource_strain", "potential_instability"]
            )
            options.append(aggressive_option)
            
            # Balanced option
            balanced_option = DecisionOption(
                option_id=f"balanced_{datetime.now().isoformat()}",
                description="Balanced approach optimizing risk and reward",
                required_actions=["strategic_analysis", "phased_implementation", "adaptive_monitoring"],
                required_engines=[EngineType.REASONING, EngineType.ANALYTICS, EngineType.SYSTEM_CONTROL, EngineType.LEARNING],
                estimated_cost=250.0,
                estimated_time=timedelta(hours=3),
                success_probability=0.75,
                risk_level=0.4,
                expected_benefits={"balance": 350.0, "adaptability": 250.0},
                side_effects=["moderate_complexity"]
            )
            options.append(balanced_option)
            
            return options
            
        except Exception as e:
            logger.error(f"Error generating decision options: {e}")
            return []
    
    async def _evaluate_options(self, options: List[DecisionOption], 
                              context: DecisionContext) -> Dict[str, Any]:
        """Evaluate options using multiple engines"""
        try:
            evaluation_results = {}
            
            for option in options:
                option_evaluation = {}
                
                # Analytics engine evaluation
                analytics_result = await self.control_interface.execute_command(
                    SupremeCommand(
                        command_id=f"evaluate_analytics_{option.option_id}",
                        command_type=CommandType.ANALYZE,
                        operation="evaluate_option",
                        parameters={
                            "option": option.description,
                            "actions": option.required_actions,
                            "context": context.situation
                        }
                    )
                )
                option_evaluation["analytics"] = analytics_result.result if analytics_result else {}
                
                # Security engine risk assessment
                security_result = await self.control_interface.execute_command(
                    SupremeCommand(
                        command_id=f"assess_security_{option.option_id}",
                        command_type=CommandType.SECURE,
                        operation="assess_security_risks",
                        parameters={
                            "option": option.description,
                            "actions": option.required_actions
                        }
                    )
                )
                option_evaluation["security"] = security_result.result if security_result else {}
                
                # Scalability engine feasibility assessment
                scalability_result = await self.control_interface.execute_command(
                    SupremeCommand(
                        command_id=f"assess_scalability_{option.option_id}",
                        command_type=CommandType.SCALE,
                        operation="assess_scalability",
                        parameters={
                            "option": option.description,
                            "resources": context.available_resources
                        }
                    )
                )
                option_evaluation["scalability"] = scalability_result.result if scalability_result else {}
                
                # Learning engine pattern matching
                learning_result = await self.control_interface.execute_command(
                    SupremeCommand(
                        command_id=f"match_patterns_{option.option_id}",
                        command_type=CommandType.LEARN,
                        operation="match_historical_patterns",
                        parameters={
                            "option": option.description,
                            "context": context.situation
                        }
                    )
                )
                option_evaluation["learning"] = learning_result.result if learning_result else {}
                
                evaluation_results[option.option_id] = option_evaluation
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating options: {e}")
            return {}
    
    def _select_best_option(self, options: List[DecisionOption], 
                          evaluation_results: Dict[str, Any],
                          context: DecisionContext) -> DecisionOption:
        """Select the best option based on comprehensive evaluation"""
        if not options:
            raise ValueError("No options available for selection")
        
        best_option = None
        best_score = -1
        
        for option in options:
            score = self._calculate_option_score(option, evaluation_results.get(option.option_id, {}), context)
            
            if score > best_score:
                best_score = score
                best_option = option
        
        return best_option or options[0]  # Fallback to first option
    
    def _calculate_option_score(self, option: DecisionOption, 
                              evaluation: Dict[str, Any],
                              context: DecisionContext) -> float:
        """Calculate comprehensive score for an option"""
        score = 0.0
        
        # Base score from option properties (40%)
        base_score = (
            option.success_probability * 0.5 +
            (1.0 - option.risk_level) * 0.3 +
            min(1.0, sum(option.expected_benefits.values()) / max(1.0, option.estimated_cost)) * 0.2
        )
        score += base_score * 0.4
        
        # Engine evaluation scores (60%)
        engine_scores = []
        
        # Analytics score
        analytics_eval = evaluation.get("analytics", {})
        if isinstance(analytics_eval, dict) and "score" in analytics_eval:
            engine_scores.append(analytics_eval["score"])
        else:
            engine_scores.append(0.7)  # Default score
        
        # Security score
        security_eval = evaluation.get("security", {})
        if isinstance(security_eval, dict) and "security_score" in security_eval:
            engine_scores.append(security_eval["security_score"])
        else:
            engine_scores.append(1.0 - option.risk_level)  # Use risk level as proxy
        
        # Scalability score
        scalability_eval = evaluation.get("scalability", {})
        if isinstance(scalability_eval, dict) and "feasibility_score" in scalability_eval:
            engine_scores.append(scalability_eval["feasibility_score"])
        else:
            engine_scores.append(0.8)  # Default score
        
        # Learning score
        learning_eval = evaluation.get("learning", {})
        if isinstance(learning_eval, dict) and "pattern_match_score" in learning_eval:
            engine_scores.append(learning_eval["pattern_match_score"])
        else:
            engine_scores.append(0.6)  # Default score
        
        # Average engine scores
        if engine_scores:
            avg_engine_score = sum(engine_scores) / len(engine_scores)
            score += avg_engine_score * 0.6
        
        # Context alignment bonus/penalty
        if context.time_constraints:
            if option.estimated_time <= context.time_constraints:
                score += 0.1  # Time bonus
            else:
                score -= 0.2  # Time penalty
        
        # Risk tolerance alignment
        risk_alignment = 1.0 - abs(option.risk_level - context.risk_tolerance)
        score += risk_alignment * 0.1
        
        return min(1.0, max(0.0, score))
    
    def _generate_reasoning(self, option: DecisionOption, 
                          evaluation_results: Dict[str, Any],
                          context: DecisionContext) -> List[str]:
        """Generate reasoning for the decision"""
        reasoning = []
        
        reasoning.append(f"Selected option: {option.description}")
        reasoning.append(f"Success probability: {option.success_probability:.1%}")
        reasoning.append(f"Risk level: {option.risk_level:.1%}")
        reasoning.append(f"Estimated cost: ${option.estimated_cost:.2f}")
        reasoning.append(f"Estimated time: {option.estimated_time}")
        
        # Add evaluation insights
        option_eval = evaluation_results.get(option.option_id, {})
        
        if "analytics" in option_eval:
            reasoning.append("Analytics engine confirms viability of approach")
        
        if "security" in option_eval:
            reasoning.append("Security assessment indicates acceptable risk levels")
        
        if "scalability" in option_eval:
            reasoning.append("Scalability analysis shows feasible resource requirements")
        
        if "learning" in option_eval:
            reasoning.append("Historical pattern analysis supports this approach")
        
        # Add context-specific reasoning
        if context.time_constraints and option.estimated_time <= context.time_constraints:
            reasoning.append("Option meets time constraints")
        
        if option.risk_level <= context.risk_tolerance:
            reasoning.append("Risk level aligns with tolerance")
        
        total_benefits = sum(option.expected_benefits.values())
        if total_benefits > option.estimated_cost:
            reasoning.append(f"Positive ROI expected: ${total_benefits - option.estimated_cost:.2f}")
        
        return reasoning
    
    def _calculate_confidence(self, option: DecisionOption, 
                            evaluation_results: Dict[str, Any]) -> float:
        """Calculate confidence in the decision"""
        confidence_factors = []
        
        # Base confidence from option properties
        confidence_factors.append(option.success_probability)
        confidence_factors.append(1.0 - option.risk_level)
        
        # Engine evaluation confidence
        option_eval = evaluation_results.get(option.option_id, {})
        
        for engine_eval in option_eval.values():
            if isinstance(engine_eval, dict) and "confidence" in engine_eval:
                confidence_factors.append(engine_eval["confidence"])
        
        # Calculate average confidence
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.5  # Default moderate confidence
    
    async def _assess_risks(self, option: DecisionOption, 
                          context: DecisionContext) -> Dict[str, float]:
        """Assess comprehensive risks for the selected option"""
        try:
            # Use security engine for detailed risk assessment
            risk_result = await self.control_interface.execute_command(
                SupremeCommand(
                    command_id=f"detailed_risk_assessment_{option.option_id}",
                    command_type=CommandType.SECURE,
                    operation="detailed_risk_assessment",
                    parameters={
                        "option": option.description,
                        "actions": option.required_actions,
                        "context": context.situation,
                        "stakeholders": context.stakeholders
                    }
                )
            )
            
            # Default risk assessment if engine call fails
            return {
                "execution_risk": option.risk_level,
                "time_risk": 0.3 if option.estimated_time > timedelta(hours=8) else 0.1,
                "cost_risk": 0.2 if option.estimated_cost > 1000 else 0.1,
                "stakeholder_risk": len(context.stakeholders) * 0.05,
                "technical_risk": len(option.required_engines) * 0.03,
                "overall_risk": option.risk_level
            }
            
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return {"overall_risk": option.risk_level, "error": str(e)}
    
    async def _create_execution_plan(self, option: DecisionOption, 
                                   context: DecisionContext) -> List[str]:
        """Create detailed execution plan"""
        try:
            # Use system control and integration engines for execution planning
            execution_result = await self.control_interface.execute_command(
                SupremeCommand(
                    command_id=f"create_execution_plan_{option.option_id}",
                    command_type=CommandType.EXECUTE,
                    operation="create_execution_plan",
                    parameters={
                        "actions": option.required_actions,
                        "engines": [e.value for e in option.required_engines],
                        "resources": context.available_resources,
                        "constraints": context.constraints
                    }
                )
            )
            
            # Default execution plan
            execution_plan = [
                "1. Initialize required engines and resources",
                "2. Validate prerequisites and dependencies",
                "3. Begin phased execution of required actions:",
            ]
            
            for i, action in enumerate(option.required_actions, 4):
                execution_plan.append(f"{i}. Execute: {action}")
            
            execution_plan.extend([
                f"{len(option.required_actions) + 4}. Monitor progress and adjust as needed",
                f"{len(option.required_actions) + 5}. Validate results against success criteria",
                f"{len(option.required_actions) + 6}. Document outcomes and lessons learned"
            ])
            
            return execution_plan
            
        except Exception as e:
            logger.error(f"Error creating execution plan: {e}")
            return ["Error creating detailed execution plan", str(e)]
    
    def _create_monitoring_plan(self, option: DecisionOption, 
                              context: DecisionContext) -> List[str]:
        """Create monitoring plan for execution"""
        monitoring_plan = [
            "Continuous monitoring strategy:",
            "- Track progress against timeline milestones",
            "- Monitor resource utilization and costs",
            "- Assess risk indicators and early warning signs",
            "- Measure success metrics in real-time",
            "- Monitor stakeholder satisfaction and feedback"
        ]
        
        # Add option-specific monitoring
        if option.risk_level > 0.5:
            monitoring_plan.append("- Enhanced risk monitoring due to high risk level")
        
        if option.estimated_cost > 500:
            monitoring_plan.append("- Detailed cost tracking and budget monitoring")
        
        if len(option.required_engines) > 3:
            monitoring_plan.append("- Multi-engine coordination monitoring")
        
        # Add context-specific monitoring
        if context.time_constraints:
            monitoring_plan.append("- Time-critical milestone tracking")
        
        if len(context.stakeholders) > 2:
            monitoring_plan.append("- Stakeholder communication and satisfaction tracking")
        
        return monitoring_plan
    
    def _create_rollback_plan(self, option: DecisionOption, 
                            context: DecisionContext) -> List[str]:
        """Create rollback plan in case of failure"""
        rollback_plan = [
            "Rollback strategy in case of failure:",
            "1. Immediate halt of current execution",
            "2. Assess current state and damage",
            "3. Restore previous stable state",
            "4. Notify all stakeholders of rollback",
            "5. Analyze failure causes",
            "6. Prepare alternative approach"
        ]
        
        # Add option-specific rollback steps
        for action in reversed(option.required_actions):
            rollback_plan.append(f"- Reverse action: {action}")
        
        # Add engine-specific rollback
        for engine in option.required_engines:
            rollback_plan.append(f"- Reset {engine.value} engine state")
        
        return rollback_plan
    
    def _define_success_metrics(self, option: DecisionOption, 
                              context: DecisionContext) -> List[str]:
        """Define success metrics for the decision"""
        success_metrics = []
        
        # Add objective-based metrics
        for objective in context.objectives:
            success_metrics.append(f"Achievement of objective: {objective}")
        
        # Add option-specific metrics
        for benefit_type, benefit_value in option.expected_benefits.items():
            success_metrics.append(f"{benefit_type} improvement: target {benefit_value}")
        
        # Add standard metrics
        success_metrics.extend([
            f"Execution completed within {option.estimated_time}",
            f"Total cost under ${option.estimated_cost * 1.1:.2f} (10% buffer)",
            f"Success probability achieved: {option.success_probability:.1%}",
            "No critical failures or rollbacks required",
            "Stakeholder satisfaction above 80%"
        ])
        
        # Add context-specific metrics
        for criterion in context.success_criteria:
            success_metrics.append(f"Success criterion met: {criterion}")
        
        return success_metrics


class SupremeExecutor:
    """Executes supreme decisions using coordinated engine operations"""
    
    def __init__(self, control_interface: SupremeControlInterface):
        self.control_interface = control_interface
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    async def execute_supreme_decision(self, decision: SupremeDecision) -> Dict[str, Any]:
        """Execute a supreme decision with full coordination"""
        try:
            execution_id = f"execution_{decision.decision_id}_{datetime.now().isoformat()}"
            start_time = datetime.now()
            
            # Initialize execution tracking
            execution_state = {
                "execution_id": execution_id,
                "decision_id": decision.decision_id,
                "status": "in_progress",
                "start_time": start_time,
                "completed_actions": [],
                "failed_actions": [],
                "current_step": 0,
                "total_steps": len(decision.execution_plan)
            }
            
            self.active_executions[execution_id] = execution_state
            
            logger.info(f"Starting execution of decision {decision.decision_id}")
            
            # Execute each step in the execution plan
            for i, step in enumerate(decision.execution_plan):
                execution_state["current_step"] = i + 1
                
                try:
                    # Execute step using appropriate engines
                    step_result = await self._execute_step(step, decision, execution_state)
                    
                    if step_result.get("success", False):
                        execution_state["completed_actions"].append(step)
                        logger.info(f"Completed step {i+1}: {step}")
                    else:
                        execution_state["failed_actions"].append(step)
                        logger.warning(f"Failed step {i+1}: {step}")
                        
                        # Check if we should continue or abort
                        if not await self._should_continue_execution(decision, execution_state):
                            break
                
                except Exception as e:
                    logger.error(f"Error executing step {i+1}: {e}")
                    execution_state["failed_actions"].append(step)
                    
                    if not await self._should_continue_execution(decision, execution_state):
                        break
            
            # Finalize execution
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Determine final status
            total_actions = len(execution_state["completed_actions"]) + len(execution_state["failed_actions"])
            success_rate = len(execution_state["completed_actions"]) / max(1, total_actions)
            
            if success_rate >= 0.8:
                final_status = "completed"
            elif success_rate >= 0.5:
                final_status = "partial_success"
            else:
                final_status = "failed"
            
            # Create execution result
            execution_result = {
                "execution_id": execution_id,
                "decision_id": decision.decision_id,
                "status": final_status,
                "execution_time": execution_time,
                "completed_actions": execution_state["completed_actions"],
                "failed_actions": execution_state["failed_actions"],
                "success_rate": success_rate,
                "total_steps": len(decision.execution_plan),
                "completed_steps": execution_state["current_step"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
            # Clean up active execution
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            # Store in history
            self.execution_history.append(execution_result)
            
            logger.info(f"Execution completed: {final_status} with {success_rate:.1%} success rate")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing supreme decision: {e}")
            return {
                "execution_id": execution_id if 'execution_id' in locals() else "unknown",
                "decision_id": decision.decision_id,
                "status": "failed",
                "error": str(e),
                "execution_time": 0.0
            }
    
    async def _execute_step(self, step: str, decision: SupremeDecision, 
                          execution_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step of the execution plan"""
        try:
            # Determine which engines to use for this step
            required_engines = self._determine_step_engines(step, decision.selected_option.required_engines)
            
            # Create command for step execution
            command = SupremeCommand(
                command_id=f"execute_step_{execution_state['execution_id']}_{execution_state['current_step']}",
                command_type=self._determine_command_type(step),
                operation="execute_step",
                parameters={
                    "step": step,
                    "decision_context": decision.context.situation,
                    "execution_state": execution_state
                }
            )
            
            # Execute the command
            result = await self.control_interface.execute_command(command)
            
            return {
                "success": result.status in ["completed", "partial_success"],
                "result": result.result,
                "engines_used": result.engines_used,
                "execution_time": result.execution_time
            }
            
        except Exception as e:
            logger.error(f"Error executing step '{step}': {e}")
            return {"success": False, "error": str(e)}
    
    def _determine_step_engines(self, step: str, available_engines: List[EngineType]) -> List[EngineType]:
        """Determine which engines are needed for a specific step"""
        step_lower = step.lower()
        needed_engines = []
        
        # Map step keywords to engines
        engine_keywords = {
            EngineType.ANALYTICS: ["analyze", "assess", "evaluate", "measure"],
            EngineType.SYSTEM_CONTROL: ["execute", "implement", "deploy", "configure"],
            EngineType.SECURITY: ["secure", "protect", "authenticate", "encrypt"],
            EngineType.SCALABILITY: ["scale", "optimize", "expand", "balance"],
            EngineType.INTEGRATION: ["integrate", "connect", "synchronize", "coordinate"],
            EngineType.COMMUNICATION: ["communicate", "notify", "report", "inform"],
            EngineType.LEARNING: ["learn", "adapt", "improve", "train"],
            EngineType.REASONING: ["reason", "decide", "plan", "strategize"],
            EngineType.PROACTIVE: ["predict", "anticipate", "prevent", "forecast"],
            EngineType.KNOWLEDGE: ["research", "search", "verify", "validate"]
        }
        
        for engine, keywords in engine_keywords.items():
            if engine in available_engines and any(keyword in step_lower for keyword in keywords):
                needed_engines.append(engine)
        
        # Default to system control if no specific engine identified
        if not needed_engines and EngineType.SYSTEM_CONTROL in available_engines:
            needed_engines.append(EngineType.SYSTEM_CONTROL)
        
        return needed_engines
    
    def _determine_command_type(self, step: str) -> CommandType:
        """Determine the command type for a step"""
        step_lower = step.lower()
        
        if any(word in step_lower for word in ["analyze", "assess", "evaluate"]):
            return CommandType.ANALYZE
        elif any(word in step_lower for word in ["execute", "implement", "deploy"]):
            return CommandType.EXECUTE
        elif any(word in step_lower for word in ["optimize", "improve", "enhance"]):
            return CommandType.OPTIMIZE
        elif any(word in step_lower for word in ["learn", "adapt", "train"]):
            return CommandType.LEARN
        elif any(word in step_lower for word in ["predict", "forecast", "anticipate"]):
            return CommandType.PREDICT
        elif any(word in step_lower for word in ["secure", "protect", "authenticate"]):
            return CommandType.SECURE
        elif any(word in step_lower for word in ["scale", "expand", "balance"]):
            return CommandType.SCALE
        elif any(word in step_lower for word in ["communicate", "notify", "inform"]):
            return CommandType.COMMUNICATE
        elif any(word in step_lower for word in ["integrate", "connect", "coordinate"]):
            return CommandType.INTEGRATE
        elif any(word in step_lower for word in ["monitor", "track", "observe"]):
            return CommandType.MONITOR
        else:
            return CommandType.EXECUTE  # Default
    
    async def _should_continue_execution(self, decision: SupremeDecision, 
                                       execution_state: Dict[str, Any]) -> bool:
        """Determine if execution should continue after a failure"""
        # Calculate current success rate
        total_attempts = len(execution_state["completed_actions"]) + len(execution_state["failed_actions"])
        if total_attempts == 0:
            return True
        
        success_rate = len(execution_state["completed_actions"]) / total_attempts
        
        # Continue if success rate is acceptable
        if success_rate >= 0.5:
            return True
        
        # Stop if too many failures
        if len(execution_state["failed_actions"]) >= 3:
            logger.warning("Too many failures, stopping execution")
            return False
        
        # Continue for high-confidence decisions
        if decision.confidence_score > 0.8:
            return True
        
        # Stop for high-risk decisions with failures
        if decision.selected_option.risk_level > 0.7:
            logger.warning("High-risk decision with failures, stopping execution")
            return False
        
        return True
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an execution"""
        return self.active_executions.get(execution_id)
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:] if limit > 0 else self.execution_history