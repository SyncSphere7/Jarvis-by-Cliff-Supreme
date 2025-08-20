"""
Problem Solver
Advanced problem decomposition and solving algorithms.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ProblemType(Enum):
    """Types of problems that can be solved"""
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    OPTIMIZATION = "optimization"
    DECISION_MAKING = "decision_making"
    TROUBLESHOOTING = "troubleshooting"
    STRATEGIC = "strategic"

class SolutionApproach(Enum):
    """Different approaches to problem solving"""
    DIVIDE_AND_CONQUER = "divide_and_conquer"
    SYSTEMATIC_ANALYSIS = "systematic_analysis"
    CREATIVE_THINKING = "creative_thinking"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"

@dataclass
class ProblemComponent:
    """Represents a component of a decomposed problem"""
    component_id: str
    description: str
    complexity: float  # 0-1 scale
    dependencies: List[str]
    estimated_effort: float
    priority: int
    solution_approach: SolutionApproach

@dataclass
class Solution:
    """Represents a solution to a problem or component"""
    solution_id: str
    problem_component: str
    description: str
    steps: List[str]
    resources_required: List[str]
    estimated_time: float
    confidence: float
    risks: List[str]
    benefits: List[str]

@dataclass
class ProblemSolution:
    """Complete solution to a complex problem"""
    problem: str
    problem_type: ProblemType
    components: List[ProblemComponent]
    solutions: List[Solution]
    implementation_plan: List[str]
    success_metrics: List[str]
    overall_confidence: float
    total_estimated_time: float

class ProblemSolver:
    """
    Advanced problem solver with multiple solving strategies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("supreme.problem_solver")
    
    def solve_complex_problem(self, problem_description: str, context: Dict[str, Any] = None) -> ProblemSolution:
        """Solve a complex problem using advanced problem-solving techniques"""
        try:
            if context is None:
                context = {}
            
            self.logger.info(f"Starting complex problem solving: {problem_description[:100]}...")
            
            # Step 1: Classify the problem
            problem_type = self._classify_problem(problem_description, context)
            
            # Step 2: Decompose the problem
            components = self._decompose_problem(problem_description, problem_type, context)
            
            # Step 3: Generate solutions for each component
            solutions = []
            for component in components:
                solution = self._generate_component_solution(component, context)
                solutions.append(solution)
            
            # Step 4: Create implementation plan
            implementation_plan = self._create_implementation_plan(components, solutions)
            
            # Step 5: Define success metrics
            success_metrics = self._define_success_metrics(problem_description, solutions)
            
            # Step 6: Calculate overall confidence and time
            overall_confidence = self._calculate_overall_confidence(solutions)
            total_time = sum(solution.estimated_time for solution in solutions)
            
            result = ProblemSolution(
                problem=problem_description,
                problem_type=problem_type,
                components=components,
                solutions=solutions,
                implementation_plan=implementation_plan,
                success_metrics=success_metrics,
                overall_confidence=overall_confidence,
                total_estimated_time=total_time
            )
            
            self.logger.info(f"Problem solving completed with {len(solutions)} solutions")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in complex problem solving: {e}")
            return self._create_error_solution(problem_description, str(e))
    
    def _classify_problem(self, problem: str, context: Dict[str, Any]) -> ProblemType:
        """Classify the type of problem"""
        problem_lower = problem.lower()
        
        if any(word in problem_lower for word in ["optimize", "improve", "maximize", "minimize"]):
            return ProblemType.OPTIMIZATION
        elif any(word in problem_lower for word in ["decide", "choose", "select", "option"]):
            return ProblemType.DECISION_MAKING
        elif any(word in problem_lower for word in ["broken", "error", "issue", "problem", "fix"]):
            return ProblemType.TROUBLESHOOTING
        elif any(word in problem_lower for word in ["strategy", "plan", "future", "goal"]):
            return ProblemType.STRATEGIC
        elif any(word in problem_lower for word in ["create", "design", "innovate", "new"]):
            return ProblemType.CREATIVE
        else:
            return ProblemType.ANALYTICAL
    
    def _decompose_problem(self, problem: str, problem_type: ProblemType, context: Dict[str, Any]) -> List[ProblemComponent]:
        """Decompose a complex problem into manageable components"""
        if problem_type == ProblemType.STRATEGIC:
            return self._decompose_strategic_problem(problem, context)
        elif problem_type == ProblemType.OPTIMIZATION:
            return self._decompose_optimization_problem(problem, context)
        elif problem_type == ProblemType.TROUBLESHOOTING:
            return self._decompose_troubleshooting_problem(problem, context)
        else:
            return self._decompose_generic_problem(problem, context)
    
    def _decompose_strategic_problem(self, problem: str, context: Dict[str, Any]) -> List[ProblemComponent]:
        """Decompose a strategic problem"""
        return [
            ProblemComponent(
                component_id="analysis",
                description="Analyze current situation and context",
                complexity=0.6,
                dependencies=[],
                estimated_effort=0.3,
                priority=1,
                solution_approach=SolutionApproach.SYSTEMATIC_ANALYSIS
            ),
            ProblemComponent(
                component_id="strategy_development",
                description="Develop strategic approach and tactics",
                complexity=0.8,
                dependencies=["analysis"],
                estimated_effort=0.4,
                priority=2,
                solution_approach=SolutionApproach.CREATIVE_THINKING
            )
        ]
    
    def _decompose_optimization_problem(self, problem: str, context: Dict[str, Any]) -> List[ProblemComponent]:
        """Decompose an optimization problem"""
        return [
            ProblemComponent(
                component_id="baseline_measurement",
                description="Measure current performance baseline",
                complexity=0.4,
                dependencies=[],
                estimated_effort=0.2,
                priority=1,
                solution_approach=SolutionApproach.SYSTEMATIC_ANALYSIS
            ),
            ProblemComponent(
                component_id="optimization_opportunities",
                description="Identify optimization opportunities",
                complexity=0.6,
                dependencies=["baseline_measurement"],
                estimated_effort=0.3,
                priority=2,
                solution_approach=SolutionApproach.SYSTEMATIC_ANALYSIS
            )
        ]
    
    def _decompose_troubleshooting_problem(self, problem: str, context: Dict[str, Any]) -> List[ProblemComponent]:
        """Decompose a troubleshooting problem"""
        return [
            ProblemComponent(
                component_id="problem_definition",
                description="Clearly define and scope the problem",
                complexity=0.3,
                dependencies=[],
                estimated_effort=0.1,
                priority=1,
                solution_approach=SolutionApproach.SYSTEMATIC_ANALYSIS
            ),
            ProblemComponent(
                component_id="root_cause_analysis",
                description="Identify root causes of the problem",
                complexity=0.8,
                dependencies=["problem_definition"],
                estimated_effort=0.4,
                priority=2,
                solution_approach=SolutionApproach.ROOT_CAUSE_ANALYSIS
            )
        ]
    
    def _decompose_generic_problem(self, problem: str, context: Dict[str, Any]) -> List[ProblemComponent]:
        """Decompose a generic problem"""
        return [
            ProblemComponent(
                component_id="understanding",
                description="Understand the problem thoroughly",
                complexity=0.5,
                dependencies=[],
                estimated_effort=0.2,
                priority=1,
                solution_approach=SolutionApproach.SYSTEMATIC_ANALYSIS
            ),
            ProblemComponent(
                component_id="solution_generation",
                description="Generate potential solutions",
                complexity=0.7,
                dependencies=["understanding"],
                estimated_effort=0.3,
                priority=2,
                solution_approach=SolutionApproach.CREATIVE_THINKING
            )
        ]
    
    def _generate_component_solution(self, component: ProblemComponent, context: Dict[str, Any]) -> Solution:
        """Generate a solution for a problem component"""
        steps = self._generate_solution_steps(component)
        
        return Solution(
            solution_id=f"sol_{component.component_id}",
            problem_component=component.component_id,
            description=f"Solution for {component.description}",
            steps=steps,
            resources_required=self._estimate_resources(component),
            estimated_time=component.estimated_effort * 10,  # Convert to hours
            confidence=0.8 - (component.complexity * 0.2),
            risks=self._identify_component_risks(component),
            benefits=self._identify_component_benefits(component)
        )
    
    def _generate_solution_steps(self, component: ProblemComponent) -> List[str]:
        """Generate solution steps based on approach"""
        if component.solution_approach == SolutionApproach.SYSTEMATIC_ANALYSIS:
            return [
                f"Gather information about {component.description}",
                f"Analyze the component systematically",
                f"Identify key insights and patterns",
                f"Document findings and recommendations"
            ]
        elif component.solution_approach == SolutionApproach.CREATIVE_THINKING:
            return [
                f"Brainstorm approaches to {component.description}",
                f"Generate creative solutions",
                f"Evaluate and refine ideas",
                f"Select best creative approach"
            ]
        elif component.solution_approach == SolutionApproach.ROOT_CAUSE_ANALYSIS:
            return [
                f"Define the problem for {component.description}",
                f"Apply root cause analysis techniques",
                f"Identify underlying causes",
                f"Develop targeted solutions"
            ]
        else:
            return [
                f"Plan approach to {component.description}",
                f"Execute planned activities",
                f"Monitor and adjust as needed",
                f"Complete component solution"
            ]
    
    def _estimate_resources(self, component: ProblemComponent) -> List[str]:
        """Estimate resources needed for component"""
        resources = ["Time", "Personnel"]
        
        if component.complexity > 0.7:
            resources.extend(["Expert consultation", "Specialized tools"])
        if component.solution_approach == SolutionApproach.CREATIVE_THINKING:
            resources.append("Creative facilitation")
        
        return resources
    
    def _identify_component_risks(self, component: ProblemComponent) -> List[str]:
        """Identify risks for component solution"""
        risks = []
        
        if component.complexity > 0.8:
            risks.append("High complexity may lead to delays")
        if len(component.dependencies) > 2:
            risks.append("Multiple dependencies may cause bottlenecks")
        
        return risks
    
    def _identify_component_benefits(self, component: ProblemComponent) -> List[str]:
        """Identify benefits of component solution"""
        return [
            f"Addresses key aspect: {component.description}",
            f"Contributes to overall problem resolution"
        ]
    
    def _create_implementation_plan(self, components: List[ProblemComponent], solutions: List[Solution]) -> List[str]:
        """Create implementation plan for all solutions"""
        sorted_components = sorted(components, key=lambda x: x.priority)
        
        plan = ["Implementation Plan:"]
        for i, component in enumerate(sorted_components, 1):
            solution = next((s for s in solutions if s.problem_component == component.component_id), None)
            if solution:
                plan.append(f"{i}. {component.description}")
                plan.append(f"   - Estimated time: {solution.estimated_time:.1f} hours")
        
        return plan
    
    def _define_success_metrics(self, problem: str, solutions: List[Solution]) -> List[str]:
        """Define success metrics for the problem solution"""
        return [
            "Problem resolution achieved",
            "All solution components implemented successfully",
            f"Implementation completed within estimated time",
            "Stakeholder satisfaction with solution"
        ]
    
    def _calculate_overall_confidence(self, solutions: List[Solution]) -> float:
        """Calculate overall confidence in the solution"""
        if not solutions:
            return 0.0
        
        return sum(s.confidence for s in solutions) / len(solutions)
    
    def _create_error_solution(self, problem: str, error: str) -> ProblemSolution:
        """Create error solution when problem solving fails"""
        return ProblemSolution(
            problem=problem,
            problem_type=ProblemType.ANALYTICAL,
            components=[],
            solutions=[],
            implementation_plan=[f"Error occurred: {error}"],
            success_metrics=[],
            overall_confidence=0.0,
            total_estimated_time=0.0
        )