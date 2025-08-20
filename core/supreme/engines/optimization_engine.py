"""
Optimization Engine
Advanced optimization algorithms and mathematical optimization.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

class OptimizationType(Enum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"

class OptimizationMethod(Enum):
    GRADIENT_DESCENT = "gradient_descent"
    GENETIC_ALGORITHM = "genetic_algorithm"
    SIMULATED_ANNEALING = "simulated_annealing"
    GREEDY = "greedy"

@dataclass
class OptimizationVariable:
    name: str
    min_value: float
    max_value: float
    current_value: float
    step_size: float = 0.1

@dataclass
class OptimizationConstraint:
    name: str
    constraint_type: str  # "equality", "inequality"
    expression: str
    value: float

@dataclass
class OptimizationResult:
    success: bool
    optimal_values: Dict[str, float]
    optimal_score: float
    iterations: int
    method_used: OptimizationMethod
    convergence_info: Dict[str, Any]
    execution_time: float

class OptimizationEngine:
    """Advanced optimization engine with multiple algorithms."""
    
    def __init__(self):
        self.logger = logging.getLogger("supreme.optimization_engine")
        
        # Optimization methods
        self.methods = {
            OptimizationMethod.GRADIENT_DESCENT: self._gradient_descent,
            OptimizationMethod.GENETIC_ALGORITHM: self._genetic_algorithm,
            OptimizationMethod.SIMULATED_ANNEALING: self._simulated_annealing,
            OptimizationMethod.GREEDY: self._greedy_optimization
        }
    
    def optimize(self, 
                objective_function: str,
                variables: List[OptimizationVariable],
                optimization_type: OptimizationType = OptimizationType.MAXIMIZE,
                constraints: List[OptimizationConstraint] = None,
                method: OptimizationMethod = OptimizationMethod.GRADIENT_DESCENT,
                max_iterations: int = 1000) -> OptimizationResult:
        """Perform optimization using specified method"""
        try:
            if constraints is None:
                constraints = []
            
            self.logger.info(f"Starting optimization with {method.value} method")
            
            import time
            start_time = time.time()
            
            # Select and run optimization method
            if method in self.methods:
                result = self.methods[method](
                    objective_function, variables, optimization_type, 
                    constraints, max_iterations
                )
            else:
                raise ValueError(f"Unknown optimization method: {method}")
            
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            self.logger.info(f"Optimization completed in {execution_time:.3f}s with score {result.optimal_score:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in optimization: {e}")
            return self._create_error_result(str(e))
    
    def multi_objective_optimize(self,
                               objective_functions: List[str],
                               variables: List[OptimizationVariable],
                               weights: List[float] = None,
                               constraints: List[OptimizationConstraint] = None) -> OptimizationResult:
        """Perform multi-objective optimization"""
        try:
            if weights is None:
                weights = [1.0] * len(objective_functions)
            
            if len(weights) != len(objective_functions):
                raise ValueError("Number of weights must match number of objective functions")
            
            # Combine objectives into single weighted function
            combined_objective = self._combine_objectives(objective_functions, weights)
            
            return self.optimize(
                combined_objective, variables, OptimizationType.MAXIMIZE, 
                constraints, OptimizationMethod.GENETIC_ALGORITHM
            )
            
        except Exception as e:
            self.logger.error(f"Error in multi-objective optimization: {e}")
            return self._create_error_result(str(e))
    
    def optimize_resource_allocation(self, 
                                   resources: Dict[str, float],
                                   demands: Dict[str, float],
                                   priorities: Dict[str, float] = None) -> Dict[str, Any]:
        """Optimize resource allocation based on demands and priorities"""
        try:
            if priorities is None:
                priorities = {key: 1.0 for key in demands.keys()}
            
            total_resources = sum(resources.values())
            total_demand = sum(demands.values())
            
            allocation = {}
            
            if total_resources >= total_demand:
                # Sufficient resources - allocate based on demand
                allocation = demands.copy()
                remaining = total_resources - total_demand
                
                # Distribute remaining based on priorities
                total_priority = sum(priorities.values())
                for key in demands.keys():
                    priority_share = priorities.get(key, 1.0) / total_priority
                    allocation[key] += remaining * priority_share
            else:
                # Insufficient resources - allocate based on priorities
                total_priority = sum(priorities.values())
                for key in demands.keys():
                    priority_share = priorities.get(key, 1.0) / total_priority
                    allocation[key] = total_resources * priority_share
            
            return {
                "allocation": allocation,
                "utilization": sum(allocation.values()) / total_resources,
                "satisfaction": self._calculate_satisfaction(allocation, demands),
                "efficiency": self._calculate_efficiency(allocation, priorities)
            }
            
        except Exception as e:
            self.logger.error(f"Error in resource allocation optimization: {e}")
            return {"error": str(e)}
    
    def _gradient_descent(self, 
                         objective_function: str,
                         variables: List[OptimizationVariable],
                         optimization_type: OptimizationType,
                         constraints: List[OptimizationConstraint],
                         max_iterations: int) -> OptimizationResult:
        """Gradient descent optimization"""
        current_values = {var.name: var.current_value for var in variables}
        learning_rate = 0.01
        
        for iteration in range(max_iterations):
            # Calculate gradients (simplified numerical gradient)
            gradients = {}
            current_score = self._evaluate_function(objective_function, current_values)
            
            for var in variables:
                # Numerical gradient calculation
                temp_values = current_values.copy()
                temp_values[var.name] += var.step_size
                new_score = self._evaluate_function(objective_function, temp_values)
                
                gradient = (new_score - current_score) / var.step_size
                gradients[var.name] = gradient
            
            # Update values
            for var in variables:
                if optimization_type == OptimizationType.MAXIMIZE:
                    new_value = current_values[var.name] + learning_rate * gradients[var.name]
                else:
                    new_value = current_values[var.name] - learning_rate * gradients[var.name]
                
                # Apply bounds
                new_value = max(var.min_value, min(var.max_value, new_value))
                current_values[var.name] = new_value
            
            # Check convergence (simplified)
            if iteration > 10 and abs(sum(gradients.values())) < 0.001:
                break
        
        final_score = self._evaluate_function(objective_function, current_values)
        
        return OptimizationResult(
            success=True,
            optimal_values=current_values,
            optimal_score=final_score,
            iterations=iteration + 1,
            method_used=OptimizationMethod.GRADIENT_DESCENT,
            convergence_info={"final_gradient_sum": sum(gradients.values())},
            execution_time=0.0
        )
    
    def _genetic_algorithm(self,
                          objective_function: str,
                          variables: List[OptimizationVariable],
                          optimization_type: OptimizationType,
                          constraints: List[OptimizationConstraint],
                          max_iterations: int) -> OptimizationResult:
        """Genetic algorithm optimization"""
        import random
        
        population_size = 50
        mutation_rate = 0.1
        
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = {}
            for var in variables:
                individual[var.name] = random.uniform(var.min_value, var.max_value)
            population.append(individual)
        
        best_individual = None
        best_score = float('-inf') if optimization_type == OptimizationType.MAXIMIZE else float('inf')
        
        for generation in range(max_iterations // 10):  # Fewer generations for efficiency
            # Evaluate population
            scored_population = []
            for individual in population:
                score = self._evaluate_function(objective_function, individual)
                scored_population.append((individual, score))
            
            # Sort by fitness
            if optimization_type == OptimizationType.MAXIMIZE:
                scored_population.sort(key=lambda x: x[1], reverse=True)
            else:
                scored_population.sort(key=lambda x: x[1])
            
            # Update best
            current_best = scored_population[0]
            if (optimization_type == OptimizationType.MAXIMIZE and current_best[1] > best_score) or \
               (optimization_type == OptimizationType.MINIMIZE and current_best[1] < best_score):
                best_individual = current_best[0].copy()
                best_score = current_best[1]
            
            # Selection and reproduction (simplified)
            new_population = []
            elite_size = population_size // 4
            
            # Keep elite
            for i in range(elite_size):
                new_population.append(scored_population[i][0].copy())
            
            # Generate offspring
            while len(new_population) < population_size:
                parent1 = random.choice(scored_population[:population_size//2])[0]
                parent2 = random.choice(scored_population[:population_size//2])[0]
                
                child = {}
                for var in variables:
                    # Crossover
                    if random.random() < 0.5:
                        child[var.name] = parent1[var.name]
                    else:
                        child[var.name] = parent2[var.name]
                    
                    # Mutation
                    if random.random() < mutation_rate:
                        child[var.name] = random.uniform(var.min_value, var.max_value)
                
                new_population.append(child)
            
            population = new_population
        
        return OptimizationResult(
            success=True,
            optimal_values=best_individual,
            optimal_score=best_score,
            iterations=generation + 1,
            method_used=OptimizationMethod.GENETIC_ALGORITHM,
            convergence_info={"population_size": population_size},
            execution_time=0.0
        )
    
    def _simulated_annealing(self,
                           objective_function: str,
                           variables: List[OptimizationVariable],
                           optimization_type: OptimizationType,
                           constraints: List[OptimizationConstraint],
                           max_iterations: int) -> OptimizationResult:
        """Simulated annealing optimization"""
        import random
        
        # Initialize with random solution
        current_solution = {}
        for var in variables:
            current_solution[var.name] = random.uniform(var.min_value, var.max_value)
        
        current_score = self._evaluate_function(objective_function, current_solution)
        best_solution = current_solution.copy()
        best_score = current_score
        
        initial_temp = 100.0
        final_temp = 0.1
        
        for iteration in range(max_iterations):
            # Calculate temperature
            temp = initial_temp * ((final_temp / initial_temp) ** (iteration / max_iterations))
            
            # Generate neighbor solution
            neighbor = current_solution.copy()
            var = random.choice(variables)
            neighbor[var.name] = random.uniform(var.min_value, var.max_value)
            
            neighbor_score = self._evaluate_function(objective_function, neighbor)
            
            # Accept or reject
            if optimization_type == OptimizationType.MAXIMIZE:
                delta = neighbor_score - current_score
            else:
                delta = current_score - neighbor_score
            
            if delta > 0 or random.random() < math.exp(delta / temp):
                current_solution = neighbor
                current_score = neighbor_score
                
                # Update best
                if (optimization_type == OptimizationType.MAXIMIZE and current_score > best_score) or \
                   (optimization_type == OptimizationType.MINIMIZE and current_score < best_score):
                    best_solution = current_solution.copy()
                    best_score = current_score
        
        return OptimizationResult(
            success=True,
            optimal_values=best_solution,
            optimal_score=best_score,
            iterations=max_iterations,
            method_used=OptimizationMethod.SIMULATED_ANNEALING,
            convergence_info={"final_temperature": temp},
            execution_time=0.0
        )
    
    def _greedy_optimization(self,
                           objective_function: str,
                           variables: List[OptimizationVariable],
                           optimization_type: OptimizationType,
                           constraints: List[OptimizationConstraint],
                           max_iterations: int) -> OptimizationResult:
        """Greedy optimization algorithm"""
        current_values = {var.name: var.current_value for var in variables}
        
        for iteration in range(max_iterations):
            improved = False
            
            for var in variables:
                best_value = current_values[var.name]
                best_score = self._evaluate_function(objective_function, current_values)
                
                # Try different values for this variable
                test_values = [
                    var.min_value,
                    var.max_value,
                    (var.min_value + var.max_value) / 2,
                    current_values[var.name] + var.step_size,
                    current_values[var.name] - var.step_size
                ]
                
                for test_value in test_values:
                    if var.min_value <= test_value <= var.max_value:
                        test_values_dict = current_values.copy()
                        test_values_dict[var.name] = test_value
                        test_score = self._evaluate_function(objective_function, test_values_dict)
                        
                        if (optimization_type == OptimizationType.MAXIMIZE and test_score > best_score) or \
                           (optimization_type == OptimizationType.MINIMIZE and test_score < best_score):
                            best_value = test_value
                            best_score = test_score
                            improved = True
                
                current_values[var.name] = best_value
            
            if not improved:
                break
        
        final_score = self._evaluate_function(objective_function, current_values)
        
        return OptimizationResult(
            success=True,
            optimal_values=current_values,
            optimal_score=final_score,
            iterations=iteration + 1,
            method_used=OptimizationMethod.GREEDY,
            convergence_info={"converged": not improved},
            execution_time=0.0
        )
    
    def _evaluate_function(self, function_str: str, variables: Dict[str, float]) -> float:
        """Evaluate objective function with given variables"""
        try:
            # Simple function evaluation (in practice, this would be more sophisticated)
            # For demo purposes, we'll use a simple quadratic function
            if "x" in variables and "y" in variables:
                x, y = variables.get("x", 0), variables.get("y", 0)
                return -(x**2 + y**2) + 10*x + 10*y  # Example function
            elif "x" in variables:
                x = variables.get("x", 0)
                return -x**2 + 10*x  # Simple quadratic
            else:
                # Generic evaluation
                return sum(variables.values())
        except Exception:
            return 0.0
    
    def _combine_objectives(self, objectives: List[str], weights: List[float]) -> str:
        """Combine multiple objectives into single weighted function"""
        # Simplified combination
        return f"weighted_combination_of_{len(objectives)}_objectives"
    
    def _calculate_satisfaction(self, allocation: Dict[str, float], demands: Dict[str, float]) -> float:
        """Calculate satisfaction score for allocation"""
        total_satisfaction = 0.0
        for key in demands:
            if key in allocation:
                satisfaction = min(1.0, allocation[key] / demands[key])
                total_satisfaction += satisfaction
        
        return total_satisfaction / len(demands) if demands else 0.0
    
    def _calculate_efficiency(self, allocation: Dict[str, float], priorities: Dict[str, float]) -> float:
        """Calculate efficiency score for allocation"""
        weighted_allocation = sum(allocation.get(key, 0) * priorities.get(key, 1) 
                                for key in priorities)
        total_allocation = sum(allocation.values())
        
        return weighted_allocation / total_allocation if total_allocation > 0 else 0.0
    
    def _create_error_result(self, error: str) -> OptimizationResult:
        """Create error result when optimization fails"""
        return OptimizationResult(
            success=False,
            optimal_values={},
            optimal_score=0.0,
            iterations=0,
            method_used=OptimizationMethod.GREEDY,
            convergence_info={"error": error},
            execution_time=0.0
        )