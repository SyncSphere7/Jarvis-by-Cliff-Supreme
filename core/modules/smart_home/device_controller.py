"""
Smart Home Device Controller for Jarvis AI Assistant
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import json

from core.interfaces.base_module import BaseModule, Intent, IntentType, ModuleResponse
from core.interfaces.data_models import SmartDevice

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """Types of smart home devices"""
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    LOCK = "lock"
    CAMERA = "camera"
    SPEAKER = "speaker"
    SWITCH = "switch"
    SENSOR = "sensor"
    FAN = "fan"
    BLINDS = "blinds"
    OUTLET = "outlet"

class DeviceProtocol(Enum):
    """Smart home communication protocols"""
    WIFI = "wifi"
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    BLUETOOTH = "bluetooth"
    THREAD = "thread"
    MATTER = "matter"

class DeviceStatus(Enum):
    """Device status states"""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    ERROR = "error"

@dataclass
class DeviceCommand:
    """Command to send to a device"""
    device_id: str
    command: str
    parameters: Dict[str, Any]
    timestamp: datetime
    user_id: str

@dataclass
class DeviceState:
    """Current state of a device"""
    device_id: str
    properties: Dict[str, Any]
    last_updated: datetime
    status: DeviceStatus

class SmartHomeController(BaseModule):
    """Main controller for smart home devices"""
    
    def __init__(self):
        super().__init__("smart_home_controller")
        self.capabilities = [
            "discover_devices", "control_device", "get_device_status",
            "create_scene", "execute_scene", "list_devices"
        ]
        
        # Device registry
        self.devices: Dict[str, SmartDevice] = {}
        self.device_states: Dict[str, DeviceState] = {}
        self.user_devices: Dict[str, List[str]] = {}  # user_id -> device_ids
        
        # Scenes (groups of device commands)
        self.scenes: Dict[str, Dict[str, Any]] = {}
        
        # Protocol handlers (placeholder for actual implementations)
        self.protocol_handlers = {
            DeviceProtocol.WIFI: self._wifi_handler,
            DeviceProtocol.ZIGBEE: self._zigbee_handler,
            DeviceProtocol.ZWAVE: self._zwave_handler,
        }
        
        logger.info("Smart Home Controller initialized")
    
    def can_handle(self, intent: Intent) -> bool:
        """Check if this module can handle the intent"""
        return intent.intent_type == IntentType.SMART_HOME
    
    def execute(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute smart home commands"""
        try:
            user_id = context.get('user_id', 'default')
            action = intent.action.lower()
            
            if any(word in action for word in ['turn on', 'switch on', 'enable']):
                return self._handle_turn_on(intent, user_id)
            elif any(word in action for word in ['turn off', 'switch off', 'disable']):
                return self._handle_turn_off(intent, user_id)
            elif any(word in action for word in ['set', 'adjust', 'change']):
                return self._handle_set_property(intent, user_id)
            elif any(word in action for word in ['dim', 'brighten']):
                return self._handle_lighting_control(intent, user_id)
            elif any(word in action for word in ['lock', 'unlock']):
                return self._handle_lock_control(intent, user_id)
            elif any(word in action for word in ['list', 'show', 'status']):
                return self._handle_list_devices(intent, user_id)
            elif any(word in action for word in ['discover', 'find', 'scan']):
                return self._handle_discover_devices(intent, user_id)
            else:
                return ModuleResponse(
                    success=False,
                    message="I can help you control lights, thermostats, locks, and other smart home devices.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error executing smart home command: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while controlling your smart home devices.",
                data={"error": str(e)}
            )
    
    def _handle_turn_on(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle turning devices on"""
        try:
            device_info = self._extract_device_info(intent.action, intent.entities)
            
            if not device_info:
                return ModuleResponse(
                    success=False,
                    message="Which device would you like to turn on?",
                    data={}
                )
            
            device = self._find_device(user_id, device_info)
            if not device:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't find a device matching '{device_info['name']}'.",
                    data={}
                )
            
            # Execute turn on command
            success = self._execute_device_command(
                device.device_id,
                "turn_on",
                {},
                user_id
            )
            
            if success:
                # Update device state
                self._update_device_state(device.device_id, {"power": "on"})
                
                return ModuleResponse(
                    success=True,
                    message=f"Turned on {device.name}",
                    data={"device": asdict(device), "command": "turn_on"}
                )
            else:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't turn on {device.name}. Please check if it's connected.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error turning on device: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while turning on the device.",
                data={"error": str(e)}
            )
    
    def _handle_turn_off(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle turning devices off"""
        try:
            device_info = self._extract_device_info(intent.action, intent.entities)
            
            if not device_info:
                return ModuleResponse(
                    success=False,
                    message="Which device would you like to turn off?",
                    data={}
                )
            
            device = self._find_device(user_id, device_info)
            if not device:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't find a device matching '{device_info['name']}'.",
                    data={}
                )
            
            # Execute turn off command
            success = self._execute_device_command(
                device.device_id,
                "turn_off",
                {},
                user_id
            )
            
            if success:
                # Update device state
                self._update_device_state(device.device_id, {"power": "off"})
                
                return ModuleResponse(
                    success=True,
                    message=f"Turned off {device.name}",
                    data={"device": asdict(device), "command": "turn_off"}
                )
            else:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't turn off {device.name}. Please check if it's connected.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error turning off device: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while turning off the device.",
                data={"error": str(e)}
            )
    
    def _handle_set_property(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle setting device properties (temperature, brightness, etc.)"""
        try:
            device_info = self._extract_device_info(intent.action, intent.entities)
            property_info = self._extract_property_info(intent.action, intent.entities)
            
            if not device_info or not property_info:
                return ModuleResponse(
                    success=False,
                    message="Please specify which device and what setting you'd like to change.",
                    data={}
                )
            
            device = self._find_device(user_id, device_info)
            if not device:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't find a device matching '{device_info['name']}'.",
                    data={}
                )
            
            # Execute set property command
            success = self._execute_device_command(
                device.device_id,
                "set_property",
                property_info,
                user_id
            )
            
            if success:
                # Update device state
                self._update_device_state(device.device_id, property_info)
                
                property_name = property_info.get('property', 'setting')
                property_value = property_info.get('value', 'new value')
                
                return ModuleResponse(
                    success=True,
                    message=f"Set {device.name} {property_name} to {property_value}",
                    data={"device": asdict(device), "property": property_info}
                )
            else:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't change the {device.name} settings.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error setting device property: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while changing the device settings.",
                data={"error": str(e)}
            )
    
    def _handle_lighting_control(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle lighting-specific controls (dim, brighten)"""
        try:
            device_info = self._extract_device_info(intent.action, intent.entities)
            action = intent.action.lower()
            
            if not device_info:
                device_info = {"name": "lights", "type": "light"}  # Default to lights
            
            device = self._find_device(user_id, device_info)
            if not device:
                return ModuleResponse(
                    success=False,
                    message="I couldn't find any lights to control.",
                    data={}
                )
            
            # Determine brightness adjustment
            if "dim" in action:
                brightness_change = -20  # Decrease by 20%
                command_text = "dimmed"
            elif "brighten" in action:
                brightness_change = 20   # Increase by 20%
                command_text = "brightened"
            else:
                brightness_change = 0
                command_text = "adjusted"
            
            # Get current brightness or default to 50%
            current_state = self.device_states.get(device.device_id)
            current_brightness = 50
            if current_state and "brightness" in current_state.properties:
                current_brightness = current_state.properties["brightness"]
            
            new_brightness = max(0, min(100, current_brightness + brightness_change))
            
            # Execute brightness command
            success = self._execute_device_command(
                device.device_id,
                "set_brightness",
                {"brightness": new_brightness},
                user_id
            )
            
            if success:
                self._update_device_state(device.device_id, {"brightness": new_brightness})
                
                return ModuleResponse(
                    success=True,
                    message=f"{command_text.capitalize()} {device.name} to {new_brightness}%",
                    data={"device": asdict(device), "brightness": new_brightness}
                )
            else:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't adjust {device.name}.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error controlling lighting: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while controlling the lights.",
                data={"error": str(e)}
            )
    
    def _handle_lock_control(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle lock/unlock commands"""
        try:
            device_info = self._extract_device_info(intent.action, intent.entities)
            action = intent.action.lower()
            
            if not device_info:
                device_info = {"name": "door", "type": "lock"}  # Default to door lock
            
            device = self._find_device(user_id, device_info)
            if not device:
                return ModuleResponse(
                    success=False,
                    message="I couldn't find any locks to control.",
                    data={}
                )
            
            # Determine lock command
            if "lock" in action and "unlock" not in action:
                command = "lock"
                new_state = "locked"
                message = f"Locked {device.name}"
            elif "unlock" in action:
                command = "unlock"
                new_state = "unlocked"
                message = f"Unlocked {device.name}"
            else:
                return ModuleResponse(
                    success=False,
                    message="Please specify whether you want to lock or unlock.",
                    data={}
                )
            
            # Execute lock command
            success = self._execute_device_command(
                device.device_id,
                command,
                {},
                user_id
            )
            
            if success:
                self._update_device_state(device.device_id, {"lock_state": new_state})
                
                return ModuleResponse(
                    success=True,
                    message=message,
                    data={"device": asdict(device), "lock_state": new_state}
                )
            else:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't {command} {device.name}.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error controlling lock: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while controlling the lock.",
                data={"error": str(e)}
            )
    
    def _handle_list_devices(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle listing user's devices"""
        try:
            user_device_ids = self.user_devices.get(user_id, [])
            
            if not user_device_ids:
                return ModuleResponse(
                    success=True,
                    message="You don't have any smart home devices registered yet.",
                    data={"devices": []}
                )
            
            devices = []
            for device_id in user_device_ids:
                if device_id in self.devices:
                    device = self.devices[device_id]
                    device_state = self.device_states.get(device_id)
                    
                    device_info = asdict(device)
                    if device_state:
                        device_info['current_state'] = device_state.properties
                        device_info['status'] = device_state.status.value
                    
                    devices.append(device_info)
            
            # Format message
            message = f"Here are your {len(devices)} smart home devices:\\n\\n"
            for i, device in enumerate(devices, 1):
                status_emoji = "🟢" if device.get('status') == 'online' else "🔴"
                device_emoji = self._get_device_emoji(device['device_type'])
                
                message += f"{i}. {device_emoji} {device['name']} {status_emoji}\\n"
                
                # Add current state info
                current_state = device.get('current_state', {})
                if current_state:
                    state_info = []
                    if 'power' in current_state:
                        state_info.append(f"Power: {current_state['power']}")
                    if 'brightness' in current_state:
                        state_info.append(f"Brightness: {current_state['brightness']}%")
                    if 'temperature' in current_state:
                        state_info.append(f"Temperature: {current_state['temperature']}°")
                    
                    if state_info:
                        message += f"   {', '.join(state_info)}\\n"
            
            return ModuleResponse(
                success=True,
                message=message.strip(),
                data={"devices": devices, "count": len(devices)}
            )
            
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while listing your devices.",
                data={"error": str(e)}
            )
    
    def _handle_discover_devices(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle device discovery"""
        try:
            # Simulate device discovery
            discovered_devices = self._simulate_device_discovery()
            
            if not discovered_devices:
                return ModuleResponse(
                    success=True,
                    message="No new devices found. Make sure your devices are in pairing mode.",
                    data={"discovered": []}
                )
            
            # Add discovered devices to user's collection
            if user_id not in self.user_devices:
                self.user_devices[user_id] = []
            
            for device in discovered_devices:
                self.devices[device.device_id] = device
                self.user_devices[user_id].append(device.device_id)
                
                # Initialize device state
                self.device_states[device.device_id] = DeviceState(
                    device_id=device.device_id,
                    properties={"power": "off"},
                    last_updated=datetime.now(),
                    status=DeviceStatus.ONLINE
                )
            
            device_names = [device.name for device in discovered_devices]
            message = f"Discovered {len(discovered_devices)} new devices: {', '.join(device_names)}"
            
            return ModuleResponse(
                success=True,
                message=message,
                data={
                    "discovered": [asdict(device) for device in discovered_devices],
                    "count": len(discovered_devices)
                }
            )
            
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while discovering devices.",
                data={"error": str(e)}
            )
    
    def _extract_device_info(self, action: str, entities: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract device information from command"""
        import re
        
        # Look for device names in entities
        device_name = None
        device_type = None
        
        if 'device' in entities:
            device_entities = entities['device']
            if isinstance(device_entities, list) and device_entities:
                device_name = device_entities[0]
            elif isinstance(device_entities, str):
                device_name = device_entities
        
        # Extract from action text
        device_patterns = {
            'light': r'\b(light|lights|lamp|bulb)\b',
            'thermostat': r'\b(thermostat|temperature|heat|cool)\b',
            'lock': r'\b(lock|door)\b',
            'fan': r'\b(fan|ceiling fan)\b',
            'tv': r'\b(tv|television)\b'
        }
        
        for dev_type, pattern in device_patterns.items():
            if re.search(pattern, action, re.IGNORECASE):
                if not device_name:
                    device_name = dev_type
                device_type = dev_type
                break
        
        if device_name:
            return {
                'name': device_name,
                'type': device_type or 'unknown'
            }
        
        return None
    
    def _extract_property_info(self, action: str, entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract property information from command"""
        import re
        
        property_info = {}
        
        # Temperature extraction
        temp_match = re.search(r'(\d+)\s*degrees?', action, re.IGNORECASE)
        if temp_match:
            property_info['property'] = 'temperature'
            property_info['value'] = int(temp_match.group(1))
            return property_info
        
        # Brightness extraction
        brightness_match = re.search(r'(\d+)\s*percent', action, re.IGNORECASE)
        if brightness_match:
            property_info['property'] = 'brightness'
            property_info['value'] = int(brightness_match.group(1))
            return property_info
        
        # Volume extraction
        volume_match = re.search(r'volume\s+(\d+)', action, re.IGNORECASE)
        if volume_match:
            property_info['property'] = 'volume'
            property_info['value'] = int(volume_match.group(1))
            return property_info
        
        return None if not property_info else property_info
    
    def _find_device(self, user_id: str, device_info: Dict[str, str]) -> Optional[SmartDevice]:
        """Find a device matching the given criteria"""
        user_device_ids = self.user_devices.get(user_id, [])
        
        device_name = device_info['name'].lower()
        device_type = device_info.get('type', '').lower()
        
        # First try exact name match
        for device_id in user_device_ids:
            if device_id in self.devices:
                device = self.devices[device_id]
                if device.name.lower() == device_name:
                    return device
        
        # Then try partial name match
        for device_id in user_device_ids:
            if device_id in self.devices:
                device = self.devices[device_id]
                if device_name in device.name.lower():
                    return device
        
        # Finally try type match
        if device_type:
            for device_id in user_device_ids:
                if device_id in self.devices:
                    device = self.devices[device_id]
                    if device.device_type.lower() == device_type:
                        return device
        
        return None
    
    def _execute_device_command(self, device_id: str, command: str, parameters: Dict[str, Any], user_id: str) -> bool:
        """Execute a command on a device"""
        try:
            device = self.devices.get(device_id)
            if not device:
                return False
            
            # Get protocol handler
            protocol = DeviceProtocol(device.protocol)
            handler = self.protocol_handlers.get(protocol)
            
            if not handler:
                logger.warning(f"No handler for protocol: {protocol}")
                return False
            
            # Create command object
            device_command = DeviceCommand(
                device_id=device_id,
                command=command,
                parameters=parameters,
                timestamp=datetime.now(),
                user_id=user_id
            )
            
            # Execute command through protocol handler
            return handler(device_command)
            
        except Exception as e:
            logger.error(f"Error executing device command: {e}")
            return False
    
    def _update_device_state(self, device_id: str, properties: Dict[str, Any]):
        """Update device state"""
        if device_id in self.device_states:
            self.device_states[device_id].properties.update(properties)
            self.device_states[device_id].last_updated = datetime.now()
        else:
            self.device_states[device_id] = DeviceState(
                device_id=device_id,
                properties=properties,
                last_updated=datetime.now(),
                status=DeviceStatus.ONLINE
            )
    
    def _simulate_device_discovery(self) -> List[SmartDevice]:
        """Simulate discovering smart home devices"""
        # This would be replaced with actual device discovery logic
        sample_devices = [
            SmartDevice(
                device_id=str(uuid.uuid4()),
                name="Living Room Light",
                device_type="light",
                protocol="wifi",
                capabilities=["on_off", "brightness", "color"],
                current_state={"power": "off", "brightness": 50},
                is_online=True
            ),
            SmartDevice(
                device_id=str(uuid.uuid4()),
                name="Main Thermostat",
                device_type="thermostat",
                protocol="wifi",
                capabilities=["temperature", "mode", "schedule"],
                current_state={"temperature": 72, "mode": "auto"},
                is_online=True
            ),
            SmartDevice(
                device_id=str(uuid.uuid4()),
                name="Front Door Lock",
                device_type="lock",
                protocol="zigbee",
                capabilities=["lock", "unlock", "status"],
                current_state={"lock_state": "locked"},
                is_online=True
            )
        ]
        
        return sample_devices
    
    def _get_device_emoji(self, device_type: str) -> str:
        """Get emoji for device type"""
        emoji_map = {
            'light': '💡',
            'thermostat': '🌡️',
            'lock': '🔒',
            'camera': '📹',
            'speaker': '🔊',
            'switch': '🔌',
            'sensor': '📡',
            'fan': '🌀',
            'tv': '📺'
        }
        return emoji_map.get(device_type.lower(), '🏠')
    
    # Protocol handlers (placeholder implementations)
    def _wifi_handler(self, command: DeviceCommand) -> bool:
        """Handle WiFi device commands"""
        logger.info(f"Executing WiFi command '{command.command}' for device {command.device_id} with parameters {command.parameters}")
        # In a real implementation, you would use a library like `pywifi` to interact with the device.
        # For this demo, we'll just simulate a successful command execution.
        return True
    
    def _zigbee_handler(self, command: DeviceCommand) -> bool:
        """Handle Zigbee device commands"""
        logger.info(f"Executing Zigbee command '{command.command}' for device {command.device_id} with parameters {command.parameters}")
        # In a real implementation, you would use a library like `zigpy` to interact with the device.
        # For this demo, we'll just simulate a successful command execution.
        return True
    
    def _zwave_handler(self, command: DeviceCommand) -> bool:
        """Handle Z-Wave device commands"""
        logger.info(f"Executing Z-Wave command '{command.command}' for device {command.device_id} with parameters {command.parameters}")
        # In a real implementation, you would use a library like `python-openzwave` to interact with the device.
        # For this demo, we'll just simulate a successful command execution.
        return True
