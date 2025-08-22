"""
Robotics Platform for Jarvis 2.0
This module contains the implementation of the robotics platform.
"""

import numpy as np

class RoboticsPlatform:
    def __init__(self):
        self.position = np.array([0, 0])
        self.held_object = None

    def move(self, direction):
        """
        Moves the robot in the given direction.
        """
        if direction == "up":
            self.position[1] += 1
        elif direction == "down":
            self.position[1] -= 1
        elif direction == "left":
            self.position[0] -= 1
        elif direction == "right":
            self.position[0] += 1
        print(f"Robot moved to {self.position}")

    def grasp(self, obj):
        """
        Grasps the given object.
        """
        self.held_object = obj
        print(f"Grasping {obj}")

    def release(self):
        """
        Releases the currently held object.
        """
        print(f"Releasing {self.held_object}")
        self.held_object = None
