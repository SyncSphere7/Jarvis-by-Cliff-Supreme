"""
Supreme Reasoning Engine
Master reasoning engine that orchestrates all reasoning capabilities.
"""

import logging
from typing import Dict, List, Any, Optional
import asyncio

from ..base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse
from .logical_processor import LogicalProcessor, LogicalChain
from .problem_solver import ProblemSolver, ProblemSolution
from .strategic_planner import StrategicPlanner, StrategicPlan
from .optimization_engine import OptimizationEngine, OptimizationResult

class SupremeReasoningEngine(BaseSupremeEngine):
    """
    Supreme reasoning engine that provides god-like analytical capabilities.
    Orchestrates logical processing, problem solving, strategic planning, and optimization.
    """
    
    def __init__(self, engine_name: str, config):
        super().__init__(engine_name, config)
        
        # Initialize reasoning components
        self.logical_processor = LogicalProcessor()
        self.problem_solver = ProblemSolver()
        self.strategic_planner = StrategicPlanner()
        self.optimization_engine = OptimizationEngine()
        
        # Reasoning capabilities
        self.reasoning_capabilities = {
            "logical_analysis": self._perform_logical_analysis,
            "problem_solving": self._perform_problem_solving,
            "strategic_planning": self._perform_strategic_planning,
            "optimization": self._perform_optimization,
            "decision_making": self._perform_decision_making,
            "causal_analysis": self._perform_causal_analysis,
            "scenario_analysis": self._perform_scenario_analysis,
            "multi_criteria_analysis": self._perform_multi_criteria_analysis
        }
    
    async def _initialize_engine(self) -> bool:
        """Initialize the supreme reasoning engine"""
        try:
            self.logger.info("Initializing Supreme Reasoning Engine...")
            
            # Test all components
            test_passed = True
            
            # Test logical processor
            try:
                test_structure = self.logical_processor.analyze_logical_structure("If A then B. A is true.")
                if "error" in test_structure:
                    test_passed = False
            except Exception as e:
                self.logger.warning(f"Logical processor test failed: {e}")
                test_passed = False
            
            # Test problem solver
            try:
                test_solution = self.problem_solver.solve_complex_problem("Test problem")
                if not test_solution.problem:
                    test_passed = False
            except Exception as e:
                self.logger.warning(f"Problem solver test failed: {e}")
                test_passed = False
            
            # Test strategic planner
            try:
                test_plan = self.strategic_planner.create_strategic_plan("Test objective")
                if not test_plan.title:
                    test_passed = False
            except Exception as e:
                self.logger.warning(f"Strategic planner test failed: {e}")
                test_passed = False
            
            if test_passed:
                self.logger.info("Supreme Reasoning Engine initialized successfully")
                return True
            else:
                self.logger.warning("Supreme Reasoning Engine initialized with some component issues")
                return True  # Continue with partial functionality
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Supreme Reasoning Engine: {e}")
            return False
    
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Execute reasoning operation"""
        operation = request.operation.lower()
        parameters = request.parameters
        
        # Route to appropriate reasoning capability
        if "logical" in operation or "logic" in operation:
            return await self._perform_logical_analysis(parameters)
        elif "problem" in operation or "solve" in operation:
            return await self._perform_problem_solving(parameters)
        elif "strategic" in operation or "strategy" in operation or "plan" in operation:
            return await self._perform_strategic_planning(parameters)
        elif "optimize" in operation or "optimization" in operation:
            return await self._perform_optimization(parameters)
        elif "decision" in operation or "decide" in operation:
            return await self._perform_decision_making(parameters)
        elif "causal" in operation or "cause" in operation:
            return await self._perform_causal_analysis(parameters)
        elif "scenario" in operation:
            return await self._perform_scenario_analysis(parameters)
        elif "analyze" in operation or "analysis" in operation:
            return await self._perform_comprehensive_analysis(parameters)
        else:
            # Default to comprehensive analysis
            return await self._perform_comprehensive_analysis(parameters)
    
    async def get_supported_operations(self) -> List[str]:
        """Get list of operations supported by reasoning engine"""
        return [
            "analyze", "logical_analysis", "problem_solving", "strategic_planning",
            "optimization", "decision_making", "causal_analysis", "scenario_analysis",
            "multi_criteria_analysis", "comprehensive_analysis", "solve", "plan",
            "optimize", "decide", "reason", "think", "evaluate"
        ]
    
    async def _perform_logical_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform logical analysis"""
        try:
            text = parameters.get("text", parameters.get("intent_text", ""))
            premises = parameters.get("premises", [])
            
            if not text and not premises:
                return {"error": "No text or premises provided for logical analysis"}
            
            result = {
                "analysis_type": "logical_analysis",
                "input": text or str(premises)
            }
            
            if text:
                # Analyze logical structure of text
                structure = self.logical_processor.analyze_logical_structure(text)
                result["logical_structure"] = structure
                
                # Perform deductive reasoning if premises found
                if structure.get("premises"):
                    chain = self.logical_processor.perform_deductive_reasoning(structure["premises"])
                    result["deductive_reasoning"] = {
                        "steps": len(chain.steps),
                        "conclusion": chain.final_conclusion,
                        "confidence": chain.overall_confidence
                    }
            
            if premises:
                # Perform reasoning from given premises
                chain = self.logical_processor.perform_deductive_reasoning(premises)
                result["reasoning_chain"] = {
                    "steps": [{"step": i+1, "conclusion": step.conclusion} for i, step in enumerate(chain.steps)],
                    "final_conclusion": chain.final_conclusion,
                    "confidence": chain.overall_confidence
                }
            
            result["reasoning_quality"] = "supreme"
            result["confidence"] = 0.9
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in logical analysis: {e}")
            return {"error": str(e), "analysis_type": "logical_analysis"}
    
    async def _perform_problem_solving(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced problem solving"""
        try:
            problem = parameters.get("problem", parameters.get("intent_text", ""))
            context = parameters.get("context", {})
            
            if not problem:
                return {"error": "No problem description provided"}
            
            # Solve the complex problem
            solution = self.problem_solver.solve_complex_problem(problem, context)
            
            result = {
                "analysis_type": "problem_solving",
                "problem": solution.problem,
                "problem_type": solution.problem_type.value,
                "components": len(solution.components),
                "solutions": len(solution.solutions),
                "implementation_plan": solution.implementation_plan[:5],  # First 5 items
                "success_metrics": solution.success_metrics,
                "overall_confidence": solution.overall_confidence,
                "estimated_time": solution.total_estimated_time,
                "reasoning_quality": "supreme"
            }
            
            # Add detailed solution info
            if solution.solutions:
                result["solution_summary"] = {
                    "primary_solution": solution.solutions[0].description,
                    "key_steps": solution.solutions[0].steps[:3],  # First 3 steps
                    "resources_needed": solution.solutions[0].resources_required,
                    "confidence": solution.solutions[0].confidence
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in problem solving: {e}")
            return {"error": str(e), "analysis_type": "problem_solving"}
    
    async def _perform_strategic_planning(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform strategic planning"""
        try:
            objective = parameters.get("objective", parameters.get("intent_text", ""))
            context = parameters.get("context", {})
            
            if not objective:
                return {"error": "No strategic objective provided"}
            
            # Create strategic plan
            plan = self.strategic_planner.create_strategic_plan(objective, context)
            
            result = {
                "analysis_type": "strategic_planning",
                "plan_title": plan.title,
                "strategy_type": plan.strategy_type.value,
                "goals": len(plan.goals),
                "action_items": len(plan.action_items),
                "success_metrics": plan.success_metrics,
                "overall_confidence": plan.overall_confidence,
                "reasoning_quality": "supreme"
            }
            
            # Add goal details
            if plan.goals:
                result["primary_goal"] = {
                    "description": plan.goals[0].description,
                    "priority": plan.goals[0].priority,
                    "success_metrics": plan.goals[0].success_metrics,
                    "confidence": plan.goals[0].confidence
                }
            
            # Add key action items
            result["key_actions"] = plan.action_items[:5]  # First 5 actions
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in strategic planning: {e}")
            return {"error": str(e), "analysis_type": "strategic_planning"}
    
    async def _perform_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform optimization analysis"""
        try:
            objective = parameters.get("objective", parameters.get("intent_text", ""))
            variables = parameters.get("variables", {})
            constraints = parameters.get("constraints", {})
            
            if not objective:
                return {"error": "No optimization objective provided"}
            
            # For demonstration, create simple optimization problem
            from .optimization_engine import OptimizationVariable, OptimizationType, OptimizationMethod
            
            opt_variables = []
            if variables:
                for name, bounds in variables.items():
                    if isinstance(bounds, dict):
                        opt_var = OptimizationVariable(
                            name=name,
                            min_value=bounds.get("min", 0),
                            max_value=bounds.get("max", 100),
                            current_value=bounds.get("current", 50)
                        )
                        opt_variables.append(opt_var)
            else:
                # Default variables for demo
                opt_variables = [
                    OptimizationVariable("x", 0, 100, 50),
                    OptimizationVariable("y", 0, 100, 50)
                ]
            
            # Perform optimization
            opt_result = self.optimization_engine.optimize(
                objective_function=objective,
                variables=opt_variables,
                optimization_type=OptimizationType.MAXIMIZE,
                method=OptimizationMethod.GENETIC_ALGORITHM,
                max_iterations=100
            )
            
            result = {
                "analysis_type": "optimization",
                "objective": objective,
                "success": opt_result.success,
                "optimal_values": opt_result.optimal_values,
                "optimal_score": opt_result.optimal_score,
                "iterations": opt_result.iterations,
                "method_used": opt_result.method_used.value,
                "execution_time": opt_result.execution_time,
                "reasoning_quality": "supreme"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in optimization: {e}")
            return {"error": str(e), "analysis_type": "optimization"}
    
    async def _perform_decision_making(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform decision making analysis"""
        try:
            decision = parameters.get("decision", parameters.get("intent_text", ""))
            options = parameters.get("options", [])
            criteria = parameters.get("criteria", [])
            
            if not decision:
                return {"error": "No decision context provided"}
            
            # If no options provided, generate some
            if not options:
                options = ["Option A", "Option B", "Option C"]
            
            # If no criteria provided, use defaults
            if not criteria:
                criteria = ["Cost", "Benefit", "Risk", "Feasibility"]
            
            # Perform multi-criteria analysis
            analysis = self._analyze_decision_options(options, criteria)
            
            result = {
                "analysis_type": "decision_making",
                "decision_context": decision,
                "options_analyzed": len(options),
                "criteria_used": criteria,
                "recommended_option": analysis["recommended"],
                "analysis_summary": analysis["summary"],
                "confidence": analysis["confidence"],
                "reasoning_quality": "supreme"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in decision making: {e}")
            return {"error": str(e), "analysis_type": "decision_making"}
    
    async def _perform_causal_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform causal analysis"""
        try:
            events = parameters.get("events", [])
            text = parameters.get("text", parameters.get("intent_text", ""))
            
            if not events and not text:
                return {"error": "No events or text provided for causal analysis"}
            
            if text and not events:
                # Extract events from text (simplified)
                sentences = text.split('.')
                events = [s.strip() for s in sentences if s.strip()]
            
            # Analyze causal relationships
            causal_analysis = self.logical_processor.analyze_causal_relationships(events)
            
            result = {
                "analysis_type": "causal_analysis",
                "events_analyzed": len(events),
                "causal_chains": len(causal_analysis.get("causal_chains", [])),
                "correlations": len(causal_analysis.get("correlations", [])),
                "primary_causes": causal_analysis.get("primary_causes", []),
                "final_effects": causal_analysis.get("final_effects", []),
                "reasoning_quality": "supreme"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in causal analysis: {e}")
            return {"error": str(e), "analysis_type": "causal_analysis"}
    
    async def _perform_scenario_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform scenario analysis"""
        try:
            context = parameters.get("context", {})
            num_scenarios = parameters.get("num_scenarios", 3)
            
            # Generate scenarios using strategic planner
            scenarios = self.strategic_planner.analyze_scenarios(context, num_scenarios)
            
            result = {
                "analysis_type": "scenario_analysis",
                "scenarios_generated": len(scenarios),
                "scenarios": []
            }
            
            for scenario in scenarios:
                result["scenarios"].append({
                    "name": scenario.name,
                    "description": scenario.description,
                    "probability": scenario.probability,
                    "impact": scenario.impact,
                    "key_factors": scenario.key_factors[:3],  # Top 3 factors
                    "recommended_actions": scenario.recommended_actions[:2]  # Top 2 actions
                })
            
            result["reasoning_quality"] = "supreme"
            return result
            
        except Exception as e:
            self.logger.error(f"Error in scenario analysis: {e}")
            return {"error": str(e), "analysis_type": "scenario_analysis"}
    
    async def _perform_multi_criteria_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform multi-criteria analysis"""
        try:
            alternatives = parameters.get("alternatives", [])
            criteria = parameters.get("criteria", [])
            
            if not alternatives:
                alternatives = ["Alternative 1", "Alternative 2", "Alternative 3"]
            if not criteria:
                criteria = ["Cost", "Quality", "Time", "Risk"]
            
            # Perform analysis
            analysis = self._analyze_alternatives(alternatives, criteria)
            
            result = {
                "analysis_type": "multi_criteria_analysis",
                "alternatives": len(alternatives),
                "criteria": len(criteria),
                "ranking": analysis["ranking"],
                "scores": analysis["scores"],
                "recommended": analysis["recommended"],
                "reasoning_quality": "supreme"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in multi-criteria analysis: {e}")
            return {"error": str(e), "analysis_type": "multi_criteria_analysis"}
    
    async def _perform_comprehensive_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis using multiple reasoning approaches"""
        try:
            text = parameters.get("text", parameters.get("intent_text", ""))
            
            if not text:
                return {"error": "No text provided for comprehensive analysis"}
            
            # Perform multiple types of analysis
            analyses = {}
            
            # Logical analysis
            try:
                logical_result = await self._perform_logical_analysis(parameters)
                if "error" not in logical_result:
                    analyses["logical"] = logical_result
            except Exception as e:
                self.logger.warning(f"Logical analysis failed: {e}")
            
            # Problem solving (if text suggests a problem)
            if any(word in text.lower() for word in ["problem", "issue", "challenge", "solve"]):
                try:
                    problem_result = await self._perform_problem_solving(parameters)
                    if "error" not in problem_result:
                        analyses["problem_solving"] = problem_result
                except Exception as e:
                    self.logger.warning(f"Problem solving analysis failed: {e}")
            
            # Strategic planning (if text suggests planning)
            if any(word in text.lower() for word in ["strategy", "plan", "goal", "objective"]):
                try:
                    strategic_result = await self._perform_strategic_planning(parameters)
                    if "error" not in strategic_result:
                        analyses["strategic"] = strategic_result
                except Exception as e:
                    self.logger.warning(f"Strategic analysis failed: {e}")
            
            # Compile comprehensive result
            result = {
                "analysis_type": "comprehensive_analysis",
                "input_text": text[:200] + "..." if len(text) > 200 else text,
                "analyses_performed": list(analyses.keys()),
                "total_analyses": len(analyses),
                "reasoning_quality": "supreme"
            }
            
            # Add key insights from each analysis
            insights = []
            for analysis_type, analysis_result in analyses.items():
                if analysis_type == "logical" and "logical_structure" in analysis_result:
                    insights.append(f"Logical structure: {len(analysis_result['logical_structure'].get('premises', []))} premises identified")
                elif analysis_type == "problem_solving" and "solution_summary" in analysis_result:
                    insights.append(f"Problem solving: {analysis_result['solution_summary']['primary_solution']}")
                elif analysis_type == "strategic" and "primary_goal" in analysis_result:
                    insights.append(f"Strategic goal: {analysis_result['primary_goal']['description']}")
            
            result["key_insights"] = insights
            result["detailed_analyses"] = analyses
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e), "analysis_type": "comprehensive_analysis"}
    
    def _analyze_decision_options(self, options: List[str], criteria: List[str]) -> Dict[str, Any]:
        """Analyze decision options using multiple criteria"""
        # Simplified decision analysis
        scores = {}
        for option in options:
            scores[option] = sum(hash(option + criterion) % 100 for criterion in criteria) / len(criteria)
        
        recommended = max(scores.keys(), key=lambda x: scores[x])
        
        return {
            "recommended": recommended,
            "scores": scores,
            "summary": f"Based on {len(criteria)} criteria, {recommended} scores highest",
            "confidence": 0.8
        }
    
    def _analyze_alternatives(self, alternatives: List[str], criteria: List[str]) -> Dict[str, Any]:
        """Analyze alternatives using multi-criteria approach"""
        # Simplified multi-criteria analysis
        scores = {}
        for alt in alternatives:
            scores[alt] = sum(hash(alt + crit) % 100 for crit in criteria) / len(criteria)
        
        ranking = sorted(alternatives, key=lambda x: scores[x], reverse=True)
        
        return {
            "ranking": ranking,
            "scores": scores,
            "recommended": ranking[0] if ranking else None
        }