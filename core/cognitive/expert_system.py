"""
Expert System for Jarvis 2.0
This module allows Jarvis to reason about a knowledge base of rules.
"""

class ExpertSystem:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        """
        Adds a new rule to the knowledge base.
        """
        self.rules.append(rule)

    def reason(self, facts):
        """
        Reasons about the facts using the rules in the knowledge base.
        """
        inferred_facts = []
        for rule in self.rules:
            if all(fact in facts for fact in rule["if"]):
                inferred_facts.extend(rule["then"])
        return inferred_facts
