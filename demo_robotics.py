"""
Demonstration of RoboticsPlatform for Jarvis 2.0
"""

from core.robotics.robotics_platform import RoboticsPlatform

def demo_robotics():
    """
    Demonstrates the RoboticsPlatform.
    """
    print("--- Robotics Platform Demo ---")
    robot = RoboticsPlatform()
    robot.move("up")
    robot.move("right")
    robot.grasp("ball")
    robot.move("down")
    robot.release()

if __name__ == "__main__":
    demo_robotics()
