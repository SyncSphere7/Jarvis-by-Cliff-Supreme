"""
Content filtering system for Jarvis AI Assistant
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class ContentFilter:
    """Filters content for safety and appropriateness."""
    
    def __init__(self):
        self.inappropriate_patterns = [
            r'\b(violence|violent|harm|hurt|kill|murder)\b',
            r'\b(hate|racist|sexist|discriminat)\w*\b',
            r'\b(explicit|nsfw|adult)\b',
            r'\b(illegal|criminal|unlawful)\b'
        ]
        
        self.family_friendly_replacements = {
            "violence": "conflict resolution",
            "hate": "understanding",
            "explicit": "appropriate",
            "illegal": "legal alternatives"
        }
    
    def filter_content(self, content: str) -> Dict[str, any]:
        """
        Filters content and returns safe version.
        
        Args:
            content: Content to filter
            
        Returns:
            Dict with filtered content and safety info
        """
        original_content = content
        filtered_content = content
        issues_found = []
        
        for pattern in self.inappropriate_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                word = match.group().lower()
                if word in self.family_friendly_replacements:
                    replacement = self.family_friendly_replacements[word]
                    filtered_content = re.sub(
                        pattern, replacement, filtered_content, flags=re.IGNORECASE
                    )
                    issues_found.append({
                        "original": word,
                        "replacement": replacement,
                        "position": match.span()
                    })
        
        is_safe = len(issues_found) == 0
        
        return {
            "is_safe": is_safe,
            "original_content": original_content,
            "filtered_content": filtered_content,
            "issues_found": issues_found,
            "message": "Content filtered for safety" if not is_safe else "Content is safe"
        }
    
    def is_family_friendly(self, content: str) -> bool:
        """Quick check if content is family-friendly."""
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        return True