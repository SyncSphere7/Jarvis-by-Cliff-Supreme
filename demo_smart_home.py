"""
Demonstration of SmartHomeController for Jarvis 2.0
"""

from core.smart_home.smart_home_controller import SmartHomeController

class Light:
    def turn_on(self):
        print("Light turned on")

    def turn_off(self):
        print("Light turned off")

def demo_smart_home():
    """
    Demonstrates the SmartHomeController.
    """
    print("--- Smart Home Controller Demo ---")
    controller = SmartHomeController()
    light = Light()
    controller.add_device("living room light", light)
    controller.turn_on("living room light")
    controller.turn_off("living room light")

if __name__ == "__main__":
    demo_smart_home()
