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
            bindings = self.match(rule["if"], facts)
            if bindings:
                for then_clause in rule["then"]:
                    inferred_fact = self.substitute(then_clause, bindings)
                    inferred_facts.append(inferred_fact)
        return inferred_facts

    def match(self, patterns, facts):
        """
        Matches patterns against facts to find bindings for variables.
        """
        bindings = {}
        for pattern in patterns:
            matched = False
            for fact in facts:
                if self.unify(pattern, fact, bindings):
                    matched = True
                    break
            if not matched:
                return None
        return bindings

    def unify(self, pattern, fact, bindings):
        """
        Unifies a pattern with a fact, updating bindings.
        """
        if isinstance(pattern, str) and pattern.startswith("?"):
            if pattern in bindings:
                return bindings[pattern] == fact
            else:
                bindings[pattern] = fact
                return True
        else:
            return pattern == fact

    def substitute(self, pattern, bindings):
        """
        Substitutes variables in a pattern with their bound values.
        """
        if isinstance(pattern, str) and pattern.startswith("?"):
            return bindings.get(pattern, pattern)
        else:
            return pattern
