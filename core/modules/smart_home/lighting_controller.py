"""
Lighting control system for Jarvis AI Assistant
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, time
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class LightingMode(Enum):
    """Lighting modes"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCENE = "scene"
    SCHEDULE = "schedule"

class ColorTemperature(Enum):
    """Color temperature presets"""
    WARM = 2700  # Warm white
    NEUTRAL = 4000  # Neutral white
    COOL = 6500  # Cool white
    DAYLIGHT = 5500  # Daylight

@dataclass
class LightingScene:
    """Lighting scene configuration"""
    name: str
    description: str
    devices: Dict[str, Dict[str, Any]]  # device_id -> settings
    created_by: str
    created_at: datetime

@dataclass
class LightingSchedule:
    """Lighting schedule configuration"""
    name: str
    device_id: str
    schedule_time: time
    settings: Dict[str, Any]
    days_of_week: List[int]  # 0=Monday, 6=Sunday
    enabled: bool = True

class LightingController:
    """Advanced lighting control with scenes and scheduling"""
    
    def __init__(self, device_controller):
        self.device_controller = device_controller
        self.scenes: Dict[str, LightingScene] = {}
        self.schedules: Dict[str, LightingSchedule] = {}
        self.user_scenes: Dict[str, List[str]] = {}  # user_id -> scene_names
        
        # Initialize default scenes
        self._create_default_scenes()
        
        logger.info("Lighting Controller initialized")
    
    def set_brightness(self, user_id: str, device_name: str, brightness: int, room: Optional[str] = None) -> bool:
        """Set brightness for a light or group of lights"""
        try:
            if room:
                # Control all lights in a room
                return self._control_room_lights(user_id, room, {"brightness": brightness})
            else:
                # Control specific device
                device_info = {"name": device_name, "type": "light"}
                device = self.device_controller._find_device(user_id, device_info)
                
                if device:
                    return self.device_controller._execute_device_command(
                        device.device_id,
                        "set_brightness",
                        {"brightness": max(0, min(100, brightness))},
                        user_id
                    )
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
            return False
    
    def set_color(self, user_id: str, device_name: str, color: str, room: Optional[str] = None) -> bool:
        """Set color for RGB lights"""
        try:
            color_values = self._parse_color(color)
            if not color_values:
                return False
            
            if room:
                return self._control_room_lights(user_id, room, {"color": color_values})
            else:
                device_info = {"name": device_name, "type": "light"}
                device = self.device_controller._find_device(user_id, device_info)
                
                if device and "color" in device.capabilities:
                    return self.device_controller._execute_device_command(
                        device.device_id,
                        "set_color",
                        {"color": color_values},
                        user_id
                    )
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting color: {e}")
            return False
    
    def set_color_temperature(self, user_id: str, device_name: str, temperature: str, room: Optional[str] = None) -> bool:
        """Set color temperature for lights"""
        try:
            temp_value = self._parse_color_temperature(temperature)
            if not temp_value:
                return False
            
            settings = {"color_temperature": temp_value}
            
            if room:
                return self._control_room_lights(user_id, room, settings)
            else:
                device_info = {"name": device_name, "type": "light"}
                device = self.device_controller._find_device(user_id, device_info)
                
                if device:
                    return self.device_controller._execute_device_command(
                        device.device_id,
                        "set_color_temperature",
                        settings,
                        user_id
                    )
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting color temperature: {e}")
            return False
    
    def create_scene(self, user_id: str, scene_name: str, description: str = "") -> bool:
        """Create a lighting scene from current device states"""
        try:
            # Get current state of all user's lights
            user_device_ids = self.device_controller.user_devices.get(user_id, [])
            scene_devices = {}
            
            for device_id in user_device_ids:
                device = self.device_controller.devices.get(device_id)
                if device and device.device_type == "light":
                    current_state = self.device_controller.device_states.get(device_id)
                    if current_state:
                        scene_devices[device_id] = current_state.properties.copy()
            
            if not scene_devices:
                return False
            
            # Create scene
            scene = LightingScene(
                name=scene_name,
                description=description,
                devices=scene_devices,
                created_by=user_id,
                created_at=datetime.now()
            )
            
            self.scenes[scene_name] = scene
            
            # Add to user's scenes
            if user_id not in self.user_scenes:
                self.user_scenes[user_id] = []
            self.user_scenes[user_id].append(scene_name)
            
            logger.info(f"Created lighting scene '{scene_name}' for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating scene: {e}")
            return False
    
    def activate_scene(self, user_id: str, scene_name: str) -> bool:
        """Activate a lighting scene"""
        try:
            scene = self.scenes.get(scene_name)
            if not scene:
                return False
            
            # Check if user has access to this scene
            user_scenes = self.user_scenes.get(user_id, [])
            if scene_name not in user_scenes and scene.created_by != user_id:
                return False
            
            # Apply scene settings to all devices
            success_count = 0
            for device_id, settings in scene.devices.items():
                if device_id in self.device_controller.devices:
                    success = self.device_controller._execute_device_command(
                        device_id,
                        "apply_settings",
                        settings,
                        user_id
                    )
                    if success:
                        self.device_controller._update_device_state(device_id, settings)
                        success_count += 1
            
            logger.info(f"Activated scene '{scene_name}' - {success_count}/{len(scene.devices)} devices updated")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error activating scene: {e}")
            return False
    
    def list_scenes(self, user_id: str) -> List[Dict[str, Any]]:
        """List available lighting scenes for user"""
        try:
            user_scenes = self.user_scenes.get(user_id, [])
            scenes_info = []
            
            for scene_name in user_scenes:
                scene = self.scenes.get(scene_name)
                if scene:
                    scenes_info.append({
                        "name": scene.name,
                        "description": scene.description,
                        "device_count": len(scene.devices),
                        "created_at": scene.created_at.isoformat()
                    })
            
            return scenes_info
            
        except Exception as e:
            logger.error(f"Error listing scenes: {e}")
            return []
    
    def delete_scene(self, user_id: str, scene_name: str) -> bool:
        """Delete a lighting scene"""
        try:
            scene = self.scenes.get(scene_name)
            if not scene or scene.created_by != user_id:
                return False
            
            # Remove from scenes
            del self.scenes[scene_name]
            
            # Remove from user's scenes
            if user_id in self.user_scenes and scene_name in self.user_scenes[user_id]:
                self.user_scenes[user_id].remove(scene_name)
            
            logger.info(f"Deleted scene '{scene_name}' for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting scene: {e}")
            return False
    
    def _control_room_lights(self, user_id: str, room: str, settings: Dict[str, Any]) -> bool:
        """Control all lights in a specific room"""
        try:
            user_device_ids = self.device_controller.user_devices.get(user_id, [])
            room_lower = room.lower()
            success_count = 0
            
            for device_id in user_device_ids:
                device = self.device_controller.devices.get(device_id)
                if (device and 
                    device.device_type == "light" and 
                    room_lower in device.name.lower()):
                    
                    success = self.device_controller._execute_device_command(
                        device_id,
                        "apply_settings",
                        settings,
                        user_id
                    )
                    if success:
                        self.device_controller._update_device_state(device_id, settings)
                        success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error controlling room lights: {e}")
            return False
    
    def _parse_color(self, color: str) -> Optional[Dict[str, int]]:
        """Parse color string to RGB values"""
        color_map = {
            "red": {"r": 255, "g": 0, "b": 0},
            "green": {"r": 0, "g": 255, "b": 0},
            "blue": {"r": 0, "g": 0, "b": 255},
            "white": {"r": 255, "g": 255, "b": 255},
            "yellow": {"r": 255, "g": 255, "b": 0},
            "purple": {"r": 128, "g": 0, "b": 128},
            "orange": {"r": 255, "g": 165, "b": 0},
            "pink": {"r": 255, "g": 192, "b": 203}
        }
        
        return color_map.get(color.lower())
    
    def _parse_color_temperature(self, temperature: str) -> Optional[int]:
        """Parse color temperature string to Kelvin value"""
        temp_map = {
            "warm": ColorTemperature.WARM.value,
            "neutral": ColorTemperature.NEUTRAL.value,
            "cool": ColorTemperature.COOL.value,
            "daylight": ColorTemperature.DAYLIGHT.value,
            "soft": ColorTemperature.WARM.value,
            "bright": ColorTemperature.COOL.value
        }
        
        return temp_map.get(temperature.lower())
    
    def _create_default_scenes(self):
        """Create default lighting scenes"""
        default_scenes = [
            {
                "name": "Movie Night",
                "description": "Dim lighting for watching movies",
                "settings": {"brightness": 20, "color_temperature": ColorTemperature.WARM.value}
            },
            {
                "name": "Reading",
                "description": "Bright, focused lighting for reading",
                "settings": {"brightness": 80, "color_temperature": ColorTemperature.NEUTRAL.value}
            },
            {
                "name": "Relaxing",
                "description": "Soft, warm lighting for relaxation",
                "settings": {"brightness": 40, "color_temperature": ColorTemperature.WARM.value}
            },
            {
                "name": "Energizing",
                "description": "Bright, cool lighting to boost energy",
                "settings": {"brightness": 100, "color_temperature": ColorTemperature.COOL.value}
            }
        ]
        
        for scene_config in default_scenes:
            scene = LightingScene(
                name=scene_config["name"],
                description=scene_config["description"],
                devices={},  # Will be populated when user activates
                created_by="system",
                created_at=datetime.now()
            )
            self.scenes[scene_config["name"]] = scene
    
    def get_lighting_stats(self, user_id: str) -> Dict[str, Any]:
        """Get lighting usage statistics"""
        try:
            user_device_ids = self.device_controller.user_devices.get(user_id, [])
            light_devices = []
            
            for device_id in user_device_ids:
                device = self.device_controller.devices.get(device_id)
                if device and device.device_type == "light":
                    light_devices.append(device)
            
            total_lights = len(light_devices)
            lights_on = 0
            total_brightness = 0
            
            for device in light_devices:
                state = self.device_controller.device_states.get(device.device_id)
                if state and state.properties.get("power") == "on":
                    lights_on += 1
                    brightness = state.properties.get("brightness", 50)
                    total_brightness += brightness
            
            avg_brightness = (total_brightness / lights_on) if lights_on > 0 else 0
            user_scenes_count = len(self.user_scenes.get(user_id, []))
            
            return {
                "total_lights": total_lights,
                "lights_on": lights_on,
                "lights_off": total_lights - lights_on,
                "average_brightness": round(avg_brightness, 1),
                "custom_scenes": user_scenes_count,
                "energy_usage": "moderate"  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error getting lighting stats: {e}")
            return {}