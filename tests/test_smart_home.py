"""
Unit tests for smart home system
"""

import unittest
from datetime import datetime

from core.modules.smart_home.device_controller import SmartHomeController
from core.modules.smart_home.lighting_controller import LightingController
from core.modules.smart_home.climate_controller import ClimateController
from core.interfaces.base_module import Intent, IntentType
from core.interfaces.data_models import SmartDevice

class TestSmartHomeController(unittest.TestCase):
    """Test cases for Smart Home Controller"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.controller = SmartHomeController()
        self.user_id = "test_user"
        self.context = {"user_id": self.user_id}
        
        # Add some test devices
        self._add_test_devices()
    
    def _add_test_devices(self):
        """Add test devices for testing"""
        test_devices = [
            SmartDevice(
                device_id="light_1",
                name="Living Room Light",
                device_type="light",
                protocol="wifi",
                capabilities=["on_off", "brightness", "color"],
                current_state={"power": "off", "brightness": 50},
                is_online=True
            ),
            SmartDevice(
                device_id="thermostat_1",
                name="Main Thermostat",
                device_type="thermostat",
                protocol="wifi",
                capabilities=["temperature", "mode", "fan_speed"],
                current_state={"target_temperature": 72, "mode": "auto"},
                is_online=True
            ),
            SmartDevice(
                device_id="lock_1",
                name="Front Door Lock",
                device_type="lock",
                protocol="zigbee",
                capabilities=["lock", "unlock", "status"],
                current_state={"lock_state": "locked"},
                is_online=True
            )
        ]
        
        # Add devices to controller
        for device in test_devices:
            self.controller.devices[device.device_id] = device
            
            if self.user_id not in self.controller.user_devices:
                self.controller.user_devices[self.user_id] = []
            self.controller.user_devices[self.user_id].append(device.device_id)
    
    def test_initialization(self):
        """Test smart home controller initialization"""
        self.assertEqual(self.controller.name, "smart_home_controller")
        self.assertIn("control_device", self.controller.capabilities)
        self.assertIsInstance(self.controller.devices, dict)
    
    def test_can_handle_smart_home_intent(self):
        """Test that module can handle smart home intents"""
        intent = Intent(
            action="turn on lights",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        self.assertTrue(self.controller.can_handle(intent))
    
    def test_turn_on_device(self):
        """Test turning on a device"""
        intent = Intent(
            action="turn on living room light",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.controller.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Turned on", response.message)
        
        # Check device state was updated
        device_state = self.controller.device_states.get("light_1")
        self.assertIsNotNone(device_state)
        self.assertEqual(device_state.properties.get("power"), "on")
    
    def test_turn_off_device(self):
        """Test turning off a device"""
        intent = Intent(
            action="turn off living room light",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.controller.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Turned off", response.message)
    
    def test_set_temperature(self):
        """Test setting thermostat temperature"""
        intent = Intent(
            action="set thermostat to 75 degrees",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.controller.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Set", response.message)
    
    def test_dim_lights(self):
        """Test dimming lights"""
        intent = Intent(
            action="dim the living room light",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.controller.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Dimmed", response.message)
    
    def test_lock_control(self):
        """Test lock control"""
        intent = Intent(
            action="lock the front door",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.controller.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Locked", response.message)
    
    def test_list_devices(self):
        """Test listing devices"""
        intent = Intent(
            action="list my smart home devices",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.controller.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("smart home devices", response.message)
        self.assertEqual(response.data["count"], 3)
    
    def test_discover_devices(self):
        """Test device discovery"""
        intent = Intent(
            action="discover new devices",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.controller.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Discovered", response.message)
    
    def test_device_not_found(self):
        """Test handling when device is not found"""
        intent = Intent(
            action="turn on nonexistent device",
            intent_type=IntentType.SMART_HOME,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.controller.execute(intent, self.context)
        
        self.assertFalse(response.success)
        self.assertIn("couldn't find", response.message)
    
    def test_device_info_extraction(self):
        """Test device information extraction"""
        test_cases = [
            ("turn on the lights", {"name": "light", "type": "light"}),
            ("adjust the thermostat", {"name": "thermostat", "type": "thermostat"}),
            ("lock the door", {"name": "lock", "type": "lock"}),
            ("turn on living room lamp", {"name": "light", "type": "light"})
        ]
        
        for action, expected in test_cases:
            result = self.controller._extract_device_info(action, {})
            if expected:
                self.assertIsNotNone(result)
                self.assertEqual(result["type"], expected["type"])
            else:
                self.assertIsNone(result)

class TestLightingController(unittest.TestCase):
    """Test cases for Lighting Controller"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.device_controller = SmartHomeController()
        self.lighting_controller = LightingController(self.device_controller)
        self.user_id = "test_user"
        
        # Add test light device
        light_device = SmartDevice(
            device_id="light_1",
            name="Test Light",
            device_type="light",
            protocol="wifi",
            capabilities=["on_off", "brightness", "color"],
            current_state={"power": "on", "brightness": 50},
            is_online=True
        )
        
        self.device_controller.devices["light_1"] = light_device
        self.device_controller.user_devices[self.user_id] = ["light_1"]
        
        # Add device state
        from core.modules.smart_home.device_controller import DeviceState, DeviceStatus
        self.device_controller.device_states["light_1"] = DeviceState(
            device_id="light_1",
            properties={"power": "on", "brightness": 50},
            last_updated=datetime.now(),
            status=DeviceStatus.ONLINE
        )
    
    def test_set_brightness(self):
        """Test setting light brightness"""
        success = self.lighting_controller.set_brightness(
            self.user_id, "Test Light", 75
        )
        
        self.assertTrue(success)
    
    def test_set_color(self):
        """Test setting light color"""
        success = self.lighting_controller.set_color(
            self.user_id, "Test Light", "red"
        )
        
        self.assertTrue(success)
    
    def test_create_scene(self):
        """Test creating a lighting scene"""
        success = self.lighting_controller.create_scene(
            self.user_id, "Test Scene", "A test lighting scene"
        )
        
        self.assertTrue(success)
        self.assertIn("Test Scene", self.lighting_controller.scenes)
    
    def test_activate_scene(self):
        """Test activating a lighting scene"""
        # First create a scene
        self.lighting_controller.create_scene(
            self.user_id, "Test Scene", "A test scene"
        )
        
        # Then activate it
        success = self.lighting_controller.activate_scene(
            self.user_id, "Test Scene"
        )
        
        self.assertTrue(success)
    
    def test_list_scenes(self):
        """Test listing lighting scenes"""
        # Create a test scene
        self.lighting_controller.create_scene(
            self.user_id, "Test Scene", "A test scene"
        )
        
        scenes = self.lighting_controller.list_scenes(self.user_id)
        
        self.assertEqual(len(scenes), 1)
        self.assertEqual(scenes[0]["name"], "Test Scene")
    
    def test_color_parsing(self):
        """Test color parsing functionality"""
        test_cases = [
            ("red", {"r": 255, "g": 0, "b": 0}),
            ("blue", {"r": 0, "g": 0, "b": 255}),
            ("green", {"r": 0, "g": 255, "b": 0}),
            ("invalid", None)
        ]
        
        for color, expected in test_cases:
            result = self.lighting_controller._parse_color(color)
            self.assertEqual(result, expected)

class TestClimateController(unittest.TestCase):
    """Test cases for Climate Controller"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.device_controller = SmartHomeController()
        self.climate_controller = ClimateController(self.device_controller)
        self.user_id = "test_user"
        
        # Add test thermostat device
        thermostat_device = SmartDevice(
            device_id="thermostat_1",
            name="Test Thermostat",
            device_type="thermostat",
            protocol="wifi",
            capabilities=["temperature", "mode", "fan_speed"],
            current_state={"target_temperature": 72, "mode": "auto"},
            is_online=True
        )
        
        self.device_controller.devices["thermostat_1"] = thermostat_device
        self.device_controller.user_devices[self.user_id] = ["thermostat_1"]
    
    def test_set_temperature(self):
        """Test setting thermostat temperature"""
        success = self.climate_controller.set_temperature(
            self.user_id, "Test Thermostat", 75
        )
        
        self.assertTrue(success)
    
    def test_set_mode(self):
        """Test setting HVAC mode"""
        success = self.climate_controller.set_mode(
            self.user_id, "Test Thermostat", "heat"
        )
        
        self.assertTrue(success)
    
    def test_set_fan_speed(self):
        """Test setting fan speed"""
        success = self.climate_controller.set_fan_speed(
            self.user_id, "Test Thermostat", "high"
        )
        
        self.assertTrue(success)
    
    def test_get_climate_status(self):
        """Test getting climate status"""
        status = self.climate_controller.get_climate_status(self.user_id)
        
        self.assertIn("devices", status)
        self.assertEqual(status["total_devices"], 1)
    
    def test_hvac_mode_parsing(self):
        """Test HVAC mode parsing"""
        from core.modules.smart_home.climate_controller import HVACMode
        
        test_cases = [
            ("heat", HVACMode.HEAT),
            ("cool", HVACMode.COOL),
            ("auto", HVACMode.AUTO),
            ("off", HVACMode.OFF),
            ("invalid", None)
        ]
        
        for mode_str, expected in test_cases:
            result = self.climate_controller._parse_hvac_mode(mode_str)
            self.assertEqual(result, expected)
    
    def test_energy_optimization(self):
        """Test energy optimization recommendations"""
        recommendations = self.climate_controller.optimize_energy_usage(self.user_id)
        
        self.assertIn("recommendations", recommendations)
        self.assertIn("estimated_savings", recommendations)

if __name__ == '__main__':
    unittest.main(verbosity=1)