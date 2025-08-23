"""
Demonstration of SmartHomeController for Jarvis 2.0
"""

from core.modules.smart_home.device_controller import SmartHomeController, DeviceType, DeviceProtocol
from core.interfaces.base_module import Intent, IntentType
from core.interfaces.data_models import SmartDevice
import uuid

def demo_smart_home():
    """
    Demonstrates the SmartHomeController.
    """
    print("--- Smart Home Controller Demo ---")
    controller = SmartHomeController()

    # --- Discover and add devices ---
    print("\n--- Discovering devices ---")
    discover_intent = Intent(action="discover devices", intent_type=IntentType.SMART_HOME, entities={}, confidence=0.9, context={}, timestamp=0)
    response = controller.execute(discover_intent, {"user_id": "test_user"})
    print(response.message)

    # --- List devices ---
    print("\n--- Listing devices ---")
    list_intent = Intent(action="list devices", intent_type=IntentType.SMART_HOME, entities={}, confidence=0.9, context={}, timestamp=0)
    response = controller.execute(list_intent, {"user_id": "test_user"})
    print(response.message)

    # --- Turn on a device ---
    print("\n--- Turning on a device ---")
    turn_on_intent = Intent(action="turn on the living room light", intent_type=IntentType.SMART_HOME, entities={"device": "living room light"}, confidence=0.9, context={}, timestamp=0)
    response = controller.execute(turn_on_intent, {"user_id": "test_user"})
    print(response.message)

    # --- Turn off a device ---
    print("\n--- Turning off a device ---")
    turn_off_intent = Intent(action="turn off the living room light", intent_type=IntentType.SMART_HOME, entities={"device": "living room light"}, confidence=0.9, context={}, timestamp=0)
    response = controller.execute(turn_off_intent, {"user_id": "test_user"})
    print(response.message)

if __name__ == "__main__":
    demo_smart_home()
