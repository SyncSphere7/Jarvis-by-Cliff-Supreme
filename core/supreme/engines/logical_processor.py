"""
Logical Processor
Advanced logical reasoning and multi-step analysis capabilities.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json

class LogicType(Enum):
    """Types of logical reasoning"""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    CAUSAL = "causal"
    ANALOGICAL = "analogical"

class ConfidenceLevel(Enum):
    """Confidence levels for logical conclusions"""
    CERTAIN = 1.0
    VERY_HIGH = 0.9
    HIGH = 0.8
    MODERATE = 0.6
    LOW = 0.4
    VERY_LOW = 0.2

@dataclass
class LogicalStep:
    """Represents a single step in logical reasoning"""
    step_number: int
    premise: str
    reasoning: str
    conclusion: str
    logic_type: LogicType
    confidence: float
    supporting_evidence: List[str] = None
    
    def __post_init__(self):
        if self.supporting_evidence is None:
            self.supporting_evidence = []

@dataclass
class LogicalChain:
    """Represents a complete chain of logical reasoning"""
    problem: str
    steps: List[LogicalStep]
    final_conclusion: str
    overall_confidence: float
    reasoning_path: List[str]
    assumptions: List[str] = None
    
    def __post_init__(self):
        if self.assumptions is None:
            self.assumptions = []

class LogicalProcessor:
    """
    Advanced logical processing engine for multi-step reasoning.
    Handles complex logical analysis and problem decomposition.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("supreme.logical_processor")
        
        # Logical patterns and rules
        self.logical_patterns = {
            "if_then": r"if\s+(.+?)\s+then\s+(.+)",
            "cause_effect": r"(.+?)\s+(?:causes?|leads? to|results? in)\s+(.+)",
            "comparison": r"(.+?)\s+(?:is|are)\s+(?:better|worse|similar|different)\s+(?:than|to)\s+(.+)",
            "correlation": r"(.+?)\s+(?:correlates? with|is related to)\s+(.+)",
            "contradiction": r"(.+?)\s+(?:contradicts?|conflicts? with)\s+(.+)"
        }
        
        # Common logical fallacies to detect
        self.fallacy_patterns = {
            "ad_hominem": ["attack", "person", "character"],
            "straw_man": ["misrepresent", "distort", "exaggerate"],
            "false_dichotomy": ["only two", "either or", "black and white"],
            "slippery_slope": ["will lead to", "inevitably", "chain reaction"],
            "appeal_to_authority": ["expert says", "authority", "because X said"]
        }
    
    def analyze_logical_structure(self, text: str) -> Dict[str, Any]:
        """Analyze the logical structure of given text"""
        try:
            structure = {
                "premises": self._extract_premises(text),
                "conclusions": self._extract_conclusions(text),
                "logical_connectors": self._find_logical_connectors(text),
                "argument_type": self._classify_argument_type(text),
                "fallacies": self._detect_fallacies(text),
                "strength": self._assess_argument_strength(text)
            }
            
            self.logger.debug(f"Analyzed logical structure: {len(structure['premises'])} premises found")
            return structure
            
        except Exception as e:
            self.logger.error(f"Error analyzing logical structure: {e}")
            return {"error": str(e)}
    
    def perform_deductive_reasoning(self, premises: List[str], rules: List[str] = None) -> LogicalChain:
        """Perform deductive reasoning from given premises"""
        try:
            if rules is None:
                rules = self._generate_default_rules()
            
            steps = []
            current_conclusions = premises.copy()
            
            for i, premise in enumerate(premises):
                # Apply logical rules to each premise
                for rule in rules:
                    new_conclusion = self._apply_deductive_rule(premise, rule)
                    if new_conclusion and new_conclusion not in current_conclusions:
                        step = LogicalStep(
                            step_number=len(steps) + 1,
                            premise=premise,
                            reasoning=f"Applied rule: {rule}",
                            conclusion=new_conclusion,
                            logic_type=LogicType.DEDUCTIVE,
                            confidence=0.9,
                            supporting_evidence=[premise, rule]
                        )
                        steps.append(step)
                        current_conclusions.append(new_conclusion)
            
            # Generate final conclusion
            final_conclusion = self._synthesize_conclusions(current_conclusions)
            overall_confidence = self._calculate_chain_confidence(steps)
            
            return LogicalChain(
                problem="Deductive reasoning from premises",
                steps=steps,
                final_conclusion=final_conclusion,
                overall_confidence=overall_confidence,
                reasoning_path=[step.conclusion for step in steps],
                assumptions=premises
            )
            
        except Exception as e:
            self.logger.error(f"Error in deductive reasoning: {e}")
            return self._create_error_chain(str(e))
    
    def perform_inductive_reasoning(self, observations: List[str]) -> LogicalChain:
        """Perform inductive reasoning from observations to general principles"""
        try:
            steps = []
            patterns = self._identify_patterns(observations)
            
            for i, pattern in enumerate(patterns):
                step = LogicalStep(
                    step_number=i + 1,
                    premise=f"Observations: {', '.join(observations[:3])}...",
                    reasoning=f"Pattern identified: {pattern['description']}",
                    conclusion=pattern['generalization'],
                    logic_type=LogicType.INDUCTIVE,
                    confidence=pattern['confidence'],
                    supporting_evidence=pattern['supporting_observations']
                )
                steps.append(step)
            
            # Generate general principle
            final_conclusion = self._generate_general_principle(patterns)
            overall_confidence = min([p['confidence'] for p in patterns]) if patterns else 0.5
            
            return LogicalChain(
                problem="Inductive reasoning from observations",
                steps=steps,
                final_conclusion=final_conclusion,
                overall_confidence=overall_confidence,
                reasoning_path=[step.conclusion for step in steps],
                assumptions=[f"Observations are representative and accurate"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in inductive reasoning: {e}")
            return self._create_error_chain(str(e))
    
    def perform_abductive_reasoning(self, observation: str, possible_explanations: List[str] = None) -> LogicalChain:
        """Perform abductive reasoning to find best explanation"""
        try:
            if possible_explanations is None:
                possible_explanations = self._generate_possible_explanations(observation)
            
            steps = []
            scored_explanations = []
            
            for i, explanation in enumerate(possible_explanations):
                score = self._score_explanation(observation, explanation)
                
                step = LogicalStep(
                    step_number=i + 1,
                    premise=f"Observation: {observation}",
                    reasoning=f"Evaluating explanation: {explanation}",
                    conclusion=f"Explanation score: {score:.2f}",
                    logic_type=LogicType.ABDUCTIVE,
                    confidence=score,
                    supporting_evidence=[observation]
                )
                steps.append(step)
                scored_explanations.append((explanation, score))
            
            # Select best explanation
            best_explanation = max(scored_explanations, key=lambda x: x[1])
            final_conclusion = f"Best explanation: {best_explanation[0]} (confidence: {best_explanation[1]:.2f})"
            
            return LogicalChain(
                problem=f"Finding best explanation for: {observation}",
                steps=steps,
                final_conclusion=final_conclusion,
                overall_confidence=best_explanation[1],
                reasoning_path=[step.conclusion for step in steps],
                assumptions=["Available explanations are comprehensive"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in abductive reasoning: {e}")
            return self._create_error_chain(str(e))
    
    def analyze_causal_relationships(self, events: List[str]) -> Dict[str, Any]:
        """Analyze causal relationships between events"""
        try:
            causal_chains = []
            correlations = []
            
            for i, event1 in enumerate(events):
                for j, event2 in enumerate(events[i+1:], i+1):
                    relationship = self._analyze_event_relationship(event1, event2)
                    
                    if relationship['type'] == 'causal':
                        causal_chains.append({
                            'cause': event1,
                            'effect': event2,
                            'strength': relationship['strength'],
                            'evidence': relationship['evidence']
                        })
                    elif relationship['type'] == 'correlation':
                        correlations.append({
                            'event1': event1,
                            'event2': event2,
                            'correlation': relationship['strength'],
                            'evidence': relationship['evidence']
                        })
            
            return {
                'causal_chains': causal_chains,
                'correlations': correlations,
                'primary_causes': self._identify_primary_causes(causal_chains),
                'final_effects': self._identify_final_effects(causal_chains)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing causal relationships: {e}")
            return {"error": str(e)}
    
    def _extract_premises(self, text: str) -> List[str]:
        """Extract premises from text"""
        # Look for premise indicators
        premise_indicators = ["given that", "since", "because", "assuming", "if", "premise:"]
        premises = []
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in premise_indicators):
                premises.append(sentence)
        
        return premises
    
    def _extract_conclusions(self, text: str) -> List[str]:
        """Extract conclusions from text"""
        conclusion_indicators = ["therefore", "thus", "hence", "consequently", "so", "conclusion:"]
        conclusions = []
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in conclusion_indicators):
                conclusions.append(sentence)
        
        return conclusions
    
    def _find_logical_connectors(self, text: str) -> List[str]:
        """Find logical connectors in text"""
        connectors = ["and", "or", "not", "if", "then", "because", "therefore", "however", "but", "although"]
        found_connectors = []
        
        text_lower = text.lower()
        for connector in connectors:
            if connector in text_lower:
                found_connectors.append(connector)
        
        return found_connectors
    
    def _classify_argument_type(self, text: str) -> str:
        """Classify the type of argument"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["if", "then", "given", "premise"]):
            return "deductive"
        elif any(word in text_lower for word in ["pattern", "trend", "usually", "generally"]):
            return "inductive"
        elif any(word in text_lower for word in ["best explanation", "likely", "probably"]):
            return "abductive"
        else:
            return "informal"
    
    def _detect_fallacies(self, text: str) -> List[str]:
        """Detect logical fallacies in text"""
        detected_fallacies = []
        text_lower = text.lower()
        
        for fallacy, keywords in self.fallacy_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_fallacies.append(fallacy)
        
        return detected_fallacies
    
    def _assess_argument_strength(self, text: str) -> float:
        """Assess the strength of an argument"""
        strength_score = 0.5  # Base score
        
        # Positive indicators
        if "evidence" in text.lower():
            strength_score += 0.1
        if "research" in text.lower():
            strength_score += 0.1
        if "data" in text.lower():
            strength_score += 0.1
        
        # Negative indicators
        fallacies = self._detect_fallacies(text)
        strength_score -= len(fallacies) * 0.1
        
        return max(0.0, min(1.0, strength_score))
    
    def _generate_default_rules(self) -> List[str]:
        """Generate default logical rules"""
        return [
            "If A implies B and A is true, then B is true",
            "If A or B is true and A is false, then B is true",
            "If A and B are both true, then (A and B) is true",
            "If A is true and A implies B, then B is true"
        ]
    
    def _apply_deductive_rule(self, premise: str, rule: str) -> Optional[str]:
        """Apply a deductive rule to a premise"""
        # Simplified rule application - in a real system this would be more sophisticated
        if "implies" in rule and "implies" in premise:
            # Extract implication and apply modus ponens
            parts = premise.split("implies")
            if len(parts) == 2:
                return f"Therefore: {parts[1].strip()}"
        
        return None
    
    def _synthesize_conclusions(self, conclusions: List[str]) -> str:
        """Synthesize multiple conclusions into a final conclusion"""
        if not conclusions:
            return "No conclusions reached"
        
        if len(conclusions) == 1:
            return conclusions[0]
        
        return f"Based on {len(conclusions)} logical steps, the synthesis suggests: {conclusions[-1]}"
    
    def _calculate_chain_confidence(self, steps: List[LogicalStep]) -> float:
        """Calculate overall confidence for a logical chain"""
        if not steps:
            return 0.0
        
        # Use minimum confidence (weakest link)
        return min(step.confidence for step in steps)
    
    def _identify_patterns(self, observations: List[str]) -> List[Dict[str, Any]]:
        """Identify patterns in observations"""
        patterns = []
        
        # Simple pattern detection - look for common words/themes
        word_frequency = {}
        for obs in observations:
            words = obs.lower().split()
            for word in words:
                word_frequency[word] = word_frequency.get(word, 0) + 1
        
        # Find frequent patterns
        common_words = [word for word, freq in word_frequency.items() if freq > len(observations) * 0.3]
        
        if common_words:
            patterns.append({
                'description': f"Common themes: {', '.join(common_words)}",
                'generalization': f"Pattern suggests consistent occurrence of: {', '.join(common_words)}",
                'confidence': 0.7,
                'supporting_observations': observations
            })
        
        return patterns
    
    def _generate_general_principle(self, patterns: List[Dict[str, Any]]) -> str:
        """Generate a general principle from patterns"""
        if not patterns:
            return "No clear general principle can be derived"
        
        return f"General principle: {patterns[0]['generalization']}"
    
    def _generate_possible_explanations(self, observation: str) -> List[str]:
        """Generate possible explanations for an observation"""
        # Simplified explanation generation
        explanations = [
            f"Direct cause: Something directly caused {observation}",
            f"Indirect cause: A chain of events led to {observation}",
            f"Random occurrence: {observation} happened by chance",
            f"Systematic factor: An underlying system produced {observation}"
        ]
        
        return explanations
    
    def _score_explanation(self, observation: str, explanation: str) -> float:
        """Score how well an explanation fits an observation"""
        # Simplified scoring - in reality this would be much more sophisticated
        base_score = 0.5
        
        # Check for keyword matches
        obs_words = set(observation.lower().split())
        exp_words = set(explanation.lower().split())
        overlap = len(obs_words.intersection(exp_words))
        
        score = base_score + (overlap * 0.1)
        return min(1.0, score)
    
    def _analyze_event_relationship(self, event1: str, event2: str) -> Dict[str, Any]:
        """Analyze relationship between two events"""
        # Simplified relationship analysis
        if any(word in event1.lower() for word in ["cause", "lead", "result"]):
            return {
                'type': 'causal',
                'strength': 0.8,
                'evidence': ['Causal language detected']
            }
        elif any(word in event1.lower() for word in ["correlate", "relate", "associate"]):
            return {
                'type': 'correlation',
                'strength': 0.6,
                'evidence': ['Correlation language detected']
            }
        else:
            return {
                'type': 'unknown',
                'strength': 0.3,
                'evidence': ['No clear relationship indicators']
            }
    
    def _identify_primary_causes(self, causal_chains: List[Dict[str, Any]]) -> List[str]:
        """Identify primary causes from causal chains"""
        causes = [chain['cause'] for chain in causal_chains]
        effects = [chain['effect'] for chain in causal_chains]
        
        # Primary causes are those that are causes but not effects
        primary_causes = [cause for cause in causes if cause not in effects]
        return primary_causes
    
    def _identify_final_effects(self, causal_chains: List[Dict[str, Any]]) -> List[str]:
        """Identify final effects from causal chains"""
        causes = [chain['cause'] for chain in causal_chains]
        effects = [chain['effect'] for chain in causal_chains]
        
        # Final effects are those that are effects but not causes
        final_effects = [effect for effect in effects if effect not in causes]
        return final_effects
    
    def _create_error_chain(self, error_message: str) -> LogicalChain:
        """Create an error logical chain"""
        return LogicalChain(
            problem="Error in logical processing",
            steps=[],
            final_conclusion=f"Error: {error_message}",
            overall_confidence=0.0,
            reasoning_path=[],
            assumptions=[]
        )