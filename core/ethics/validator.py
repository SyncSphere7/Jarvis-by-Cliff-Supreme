"""
Ethical Validation Framework for Jarvis AI Assistant
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class EthicsViolationType(Enum):
    ILLEGAL_ACTIVITY = "illegal_activity"
    PRIVACY_VIOLATION = "privacy_violation"
    HARMFUL_CONTENT = "harmful_content"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DECEPTIVE_PRACTICE = "deceptive_practice"

class EthicsValidator:
    """Validates commands and operations for ethical compliance."""
    
    def __init__(self, security_monitor=None):
        self.security_monitor = security_monitor
        
        self.prohibited_keywords = [
            # Illegal activities
            "credential stuffing", "fake documents", "identity theft",
            "fraud", "scam", "hack", "exploit", "breach", "steal",
            "darkweb", "dark web", "illegal", "contraband",
            
            # Privacy violations
            "spy", "stalk", "track without consent", "unauthorized access",
            
            # Harmful content
            "violence", "harm", "threat", "abuse", "harassment",
            
            # Financial crimes
            "money laundering", "tax evasion", "ponzi", "pyramid scheme"
        ]
        
        self.ethical_alternatives = {
            "hack": "learn cybersecurity",
            "steal": "find legal alternatives",
            "fraud": "learn about fraud prevention",
            "spy": "use privacy-respecting monitoring tools"
        }
    
    def validate_command(self, command: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Validates a command for ethical compliance."""
        command_lower = command.lower()
        
        violations = []
        for keyword in self.prohibited_keywords:
            if keyword in command_lower:
                violations.append({
                    "type": EthicsViolationType.ILLEGAL_ACTIVITY,
                    "keyword": keyword,
                    "alternative": self.ethical_alternatives.get(keyword.split()[0])
                })
        
        is_valid = len(violations) == 0
        
        # Log to security monitor if violations found
        if not is_valid and self.security_monitor:
            self.security_monitor.log_security_event(
                source="ethics_validator",
                event_data=command,
                user_id=user_id,
                additional_details={
                    "violations": violations,
                    "validation_result": "blocked"
                }
            )
        
        result = {
            "is_valid": is_valid,
            "violations": violations,
            "message": self._generate_response_message(violations)
        }
        
        if not is_valid:
            logger.warning(f"Ethics violation detected in command: {command}")
        
        return result
    
    def _generate_response_message(self, violations: List[Dict]) -> str:
        """Generate appropriate response message for ethics violations."""
        if not violations:
            return "Command approved for execution."
        
        base_message = "I can't help with that request as it involves activities that could be harmful or illegal."
        
        alternatives = [v.get("alternative") for v in violations if v.get("alternative")]
        if alternatives:
            alt_text = ", ".join(alternatives)
            return f"{base_message} Instead, I can help you {alt_text}."
        
        return f"{base_message} Is there something else I can help you with?"
    
    def log_ethical_decision(self, command: str, decision: str, reason: str):
        """Log ethical decisions for audit purposes."""
        logger.info(f"Ethical Decision - Command: {command}, Decision: {decision}, Reason: {reason}")