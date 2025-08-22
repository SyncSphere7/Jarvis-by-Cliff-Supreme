"""
Planner for Jarvis 2.0
This module allows Jarvis to create a plan to achieve a goal.
"""

class Planner:
    def __init__(self, actions):
        self.actions = actions

    def plan(self, goal, state):
        """
        Creates a plan to achieve a goal.
        """
        plan = []
        while not self.is_goal_achieved(goal, state):
            action = self.find_best_action(goal, state)
            if action is None:
                return None # No plan found
            plan.append(action)
            state = self.apply_action(action, state)
        return plan

    def is_goal_achieved(self, goal, state):
        """
        Checks if the goal is achieved in the current state.
        """
        return all(item in state for item in goal)

    def find_best_action(self, goal, state):
        """
        Finds the best action to take to achieve the goal.
        """
        best_action = None
        best_score = -1
        for action in self.actions:
            if self.can_apply_action(action, state):
                score = self.heuristic_score(action, goal, state)
                if score > best_score:
                    best_score = score
                    best_action = action
        return best_action

    def heuristic_score(self, action, goal, state):
        """
        Calculates a heuristic score for an action.
        """
        score = 0
        for effect in action["effects"]:
            if effect in goal:
                score += 1
        for precondition in action["preconditions"]:
            if precondition in state:
                score += 1
        return score

    def can_apply_action(self, action, state):
        """
        Checks if an action can be applied in the current state.
        """
        return all(item in state for item in action["preconditions"])

    def apply_action(self, action, state):
        """
        Applies an action to the current state.
        """
        new_state = set(state)
        for effect in action["effects"]:
            if effect.startswith("not "):
                new_state.remove(effect[4:])
            else:
                new_state.add(effect)
        return new_state
