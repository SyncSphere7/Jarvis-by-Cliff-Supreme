"""
Goal Management System for Jarvis 2.0
This module allows Jarvis to set, prioritize, and track goals.
"""

class GoalManagementSystem:
    def __init__(self):
        self.goals = []

    def add_goal(self, goal, priority):
        """
        Adds a new goal to the goal list.
        """
        self.goals.append({"goal": goal, "priority": priority, "status": "pending"})
        self.prioritize_goals()

    def prioritize_goals(self):
        """
        Prioritizes goals based on their priority level.
        """
        self.goals.sort(key=lambda x: x["priority"], reverse=True)

    def get_next_goal(self):
        """
        Gets the next goal to be executed.
        """
        if self.goals:
            return self.goals[0]
        return None

    def complete_goal(self, goal):
        """
        Marks a goal as completed.
        """
        for g in self.goals:
            if g["goal"] == goal:
                g["status"] = "completed"
                break
