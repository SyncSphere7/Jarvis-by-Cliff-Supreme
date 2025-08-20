"""
Climate control system for Jarvis AI Assistant
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, time
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class HVACMode(Enum):
    """HVAC system modes"""
    OFF = "off"
    HEAT = "heat"
    COOL = "cool"
    AUTO = "auto"
    FAN_ONLY = "fan_only"
    DRY = "dry"

class FanSpeed(Enum):
    """Fan speed settings"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AUTO = "auto"

@dataclass
class ClimateSchedule:
    """Climate control schedule"""
    name: str
    device_id: str
    schedule_time: time
    temperature: float
    mode: HVACMode
    days_of_week: List[int]  # 0=Monday, 6=Sunday
    enabled: bool = True

@dataclass
class ClimateZone:
    """Climate zone configuration"""
    name: str
    devices: List[str]  # device_ids
    target_temperature: float
    mode: HVACMode
    priority: int = 1

class ClimateController:
    """Advanced climate control with scheduling and zones"""
    
    def __init__(self, device_controller):
        self.device_controller = device_controller
        self.schedules: Dict[str, ClimateSchedule] = {}
        self.zones: Dict[str, ClimateZone] = {}
        self.user_schedules: Dict[str, List[str]] = {}  # user_id -> schedule_names
        self.user_zones: Dict[str, List[str]] = {}  # user_id -> zone_names
        
        # Default temperature ranges
        self.temp_ranges = {
            "comfortable": (68, 72),
            "energy_saving": (65, 78),
            "sleep": (65, 70)
        }
        
        logger.info("Climate Controller initialized")
    
    def set_temperature(self, user_id: str, device_name: str, temperature: float, unit: str = "F") -> bool:
        """Set temperature for a thermostat"""
        try:
            # Convert to Fahrenheit if needed
            if unit.upper() == "C":
                temperature = (temperature * 9/5) + 32
            
            # Validate temperature range
            if not (50 <= temperature <= 90):
                logger.warning(f"Temperature {temperature}°F is outside safe range")
                return False
            
            device_info = {"name": device_name, "type": "thermostat"}
            device = self.device_controller._find_device(user_id, device_info)
            
            if device:
                success = self.device_controller._execute_device_command(
                    device.device_id,
                    "set_temperature",
                    {"temperature": temperature},
                    user_id
                )
                
                if success:
                    self.device_controller._update_device_state(
                        device.device_id, 
                        {"target_temperature": temperature}
                    )
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting temperature: {e}")
            return False
    
    def set_mode(self, user_id: str, device_name: str, mode: str) -> bool:
        """Set HVAC mode for a thermostat"""
        try:
            # Parse mode
            hvac_mode = self._parse_hvac_mode(mode)
            if not hvac_mode:
                return False
            
            device_info = {"name": device_name, "type": "thermostat"}
            device = self.device_controller._find_device(user_id, device_info)
            
            if device:
                success = self.device_controller._execute_device_command(
                    device.device_id,
                    "set_mode",
                    {"mode": hvac_mode.value},
                    user_id
                )
                
                if success:
                    self.device_controller._update_device_state(
                        device.device_id,
                        {"mode": hvac_mode.value}
                    )
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting mode: {e}")
            return False
    
    def set_fan_speed(self, user_id: str, device_name: str, speed: str) -> bool:
        """Set fan speed for HVAC system"""
        try:
            fan_speed = self._parse_fan_speed(speed)
            if not fan_speed:
                return False
            
            device_info = {"name": device_name, "type": "thermostat"}
            device = self.device_controller._find_device(user_id, device_info)
            
            if device:
                success = self.device_controller._execute_device_command(
                    device.device_id,
                    "set_fan_speed",
                    {"fan_speed": fan_speed.value},
                    user_id
                )
                
                if success:
                    self.device_controller._update_device_state(
                        device.device_id,
                        {"fan_speed": fan_speed.value}
                    )
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting fan speed: {e}")
            return False
    
    def create_schedule(self, user_id: str, name: str, device_name: str, 
                       schedule_time: time, temperature: float, mode: str,
                       days: List[str]) -> bool:
        """Create a climate control schedule"""
        try:
            device_info = {"name": device_name, "type": "thermostat"}
            device = self.device_controller._find_device(user_id, device_info)
            
            if not device:
                return False
            
            hvac_mode = self._parse_hvac_mode(mode)
            if not hvac_mode:
                return False
            
            # Parse days of week
            days_of_week = self._parse_days_of_week(days)
            
            schedule = ClimateSchedule(
                name=name,
                device_id=device.device_id,
                schedule_time=schedule_time,
                temperature=temperature,
                mode=hvac_mode,
                days_of_week=days_of_week
            )
            
            self.schedules[name] = schedule
            
            # Add to user's schedules
            if user_id not in self.user_schedules:
                self.user_schedules[user_id] = []
            self.user_schedules[user_id].append(name)
            
            logger.info(f"Created climate schedule '{name}' for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return False
    
    def create_zone(self, user_id: str, zone_name: str, device_names: List[str],
                   target_temp: float, mode: str) -> bool:
        """Create a climate zone with multiple devices"""
        try:
            device_ids = []
            
            # Find all devices for the zone
            for device_name in device_names:
                device_info = {"name": device_name, "type": "thermostat"}
                device = self.device_controller._find_device(user_id, device_info)
                if device:
                    device_ids.append(device.device_id)
            
            if not device_ids:
                return False
            
            hvac_mode = self._parse_hvac_mode(mode)
            if not hvac_mode:
                return False
            
            zone = ClimateZone(
                name=zone_name,
                devices=device_ids,
                target_temperature=target_temp,
                mode=hvac_mode
            )
            
            self.zones[zone_name] = zone
            
            # Add to user's zones
            if user_id not in self.user_zones:
                self.user_zones[user_id] = []
            self.user_zones[user_id].append(zone_name)
            
            logger.info(f"Created climate zone '{zone_name}' for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating zone: {e}")
            return False
    
    def control_zone(self, user_id: str, zone_name: str, temperature: Optional[float] = None,
                    mode: Optional[str] = None) -> bool:
        """Control all devices in a climate zone"""
        try:
            zone = self.zones.get(zone_name)
            if not zone:
                return False
            
            # Check if user has access to this zone
            user_zones = self.user_zones.get(user_id, [])
            if zone_name not in user_zones:
                return False
            
            # Update zone settings
            if temperature is not None:
                zone.target_temperature = temperature
            
            if mode is not None:
                hvac_mode = self._parse_hvac_mode(mode)
                if hvac_mode:
                    zone.mode = hvac_mode
            
            # Apply settings to all devices in zone
            success_count = 0
            for device_id in zone.devices:
                settings = {
                    "target_temperature": zone.target_temperature,
                    "mode": zone.mode.value
                }
                
                success = self.device_controller._execute_device_command(
                    device_id,
                    "apply_settings",
                    settings,
                    user_id
                )
                
                if success:
                    self.device_controller._update_device_state(device_id, settings)
                    success_count += 1
            
            logger.info(f"Controlled zone '{zone_name}' - {success_count}/{len(zone.devices)} devices updated")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error controlling zone: {e}")
            return False
    
    def get_climate_status(self, user_id: str) -> Dict[str, Any]:
        """Get current climate status for all user devices"""
        try:
            user_device_ids = self.device_controller.user_devices.get(user_id, [])
            climate_devices = []
            
            for device_id in user_device_ids:
                device = self.device_controller.devices.get(device_id)
                if device and device.device_type == "thermostat":
                    state = self.device_controller.device_states.get(device_id)
                    
                    device_status = {
                        "name": device.name,
                        "device_id": device_id,
                        "current_temperature": state.properties.get("current_temperature", "Unknown") if state else "Unknown",
                        "target_temperature": state.properties.get("target_temperature", "Unknown") if state else "Unknown",
                        "mode": state.properties.get("mode", "Unknown") if state else "Unknown",
                        "fan_speed": state.properties.get("fan_speed", "Unknown") if state else "Unknown",
                        "status": state.status.value if state else "Unknown"
                    }
                    
                    climate_devices.append(device_status)
            
            return {
                "devices": climate_devices,
                "total_devices": len(climate_devices),
                "zones": len(self.user_zones.get(user_id, [])),
                "schedules": len(self.user_schedules.get(user_id, []))
            }
            
        except Exception as e:
            logger.error(f"Error getting climate status: {e}")
            return {}
    
    def optimize_energy_usage(self, user_id: str) -> Dict[str, Any]:
        """Provide energy optimization recommendations"""
        try:
            recommendations = []
            energy_savings = 0
            
            user_device_ids = self.device_controller.user_devices.get(user_id, [])
            
            for device_id in user_device_ids:
                device = self.device_controller.devices.get(device_id)
                if device and device.device_type == "thermostat":
                    state = self.device_controller.device_states.get(device_id)
                    if state:
                        current_temp = state.properties.get("target_temperature", 72)
                        mode = state.properties.get("mode", "auto")
                        
                        # Check for optimization opportunities
                        if mode == "heat" and current_temp > 70:
                            recommendations.append({
                                "device": device.name,
                                "suggestion": f"Lower heating to 68°F (currently {current_temp}°F)",
                                "potential_savings": "8-10%"
                            })
                            energy_savings += 9
                        
                        elif mode == "cool" and current_temp < 76:
                            recommendations.append({
                                "device": device.name,
                                "suggestion": f"Raise cooling to 78°F (currently {current_temp}°F)",
                                "potential_savings": "6-8%"
                            })
                            energy_savings += 7
            
            # General recommendations
            if not self.user_schedules.get(user_id):
                recommendations.append({
                    "device": "All thermostats",
                    "suggestion": "Create schedules to automatically adjust temperature when away",
                    "potential_savings": "10-15%"
                })
                energy_savings += 12
            
            return {
                "recommendations": recommendations,
                "estimated_savings": f"{energy_savings}%",
                "optimization_score": min(100, 100 - energy_savings * 2)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing energy usage: {e}")
            return {}
    
    def _parse_hvac_mode(self, mode: str) -> Optional[HVACMode]:
        """Parse HVAC mode string"""
        mode_map = {
            "off": HVACMode.OFF,
            "heat": HVACMode.HEAT,
            "heating": HVACMode.HEAT,
            "cool": HVACMode.COOL,
            "cooling": HVACMode.COOL,
            "ac": HVACMode.COOL,
            "auto": HVACMode.AUTO,
            "automatic": HVACMode.AUTO,
            "fan": HVACMode.FAN_ONLY,
            "fan only": HVACMode.FAN_ONLY,
            "dry": HVACMode.DRY
        }
        
        return mode_map.get(mode.lower())
    
    def _parse_fan_speed(self, speed: str) -> Optional[FanSpeed]:
        """Parse fan speed string"""
        speed_map = {
            "low": FanSpeed.LOW,
            "medium": FanSpeed.MEDIUM,
            "med": FanSpeed.MEDIUM,
            "high": FanSpeed.HIGH,
            "auto": FanSpeed.AUTO,
            "automatic": FanSpeed.AUTO
        }
        
        return speed_map.get(speed.lower())
    
    def _parse_days_of_week(self, days: List[str]) -> List[int]:
        """Parse days of week strings to numbers"""
        day_map = {
            "monday": 0, "mon": 0,
            "tuesday": 1, "tue": 1, "tues": 1,
            "wednesday": 2, "wed": 2,
            "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
            "friday": 4, "fri": 4,
            "saturday": 5, "sat": 5,
            "sunday": 6, "sun": 6
        }
        
        day_numbers = []
        for day in days:
            day_num = day_map.get(day.lower())
            if day_num is not None:
                day_numbers.append(day_num)
        
        return day_numbers
    
    def get_climate_stats(self, user_id: str) -> Dict[str, Any]:
        """Get climate control statistics"""
        try:
            user_device_ids = self.device_controller.user_devices.get(user_id, [])
            climate_devices = [
                device for device_id in user_device_ids
                for device in [self.device_controller.devices.get(device_id)]
                if device and device.device_type == "thermostat"
            ]
            
            total_devices = len(climate_devices)
            active_devices = 0
            avg_temp = 0
            temp_count = 0
            
            for device in climate_devices:
                state = self.device_controller.device_states.get(device.device_id)
                if state:
                    mode = state.properties.get("mode", "off")
                    if mode != "off":
                        active_devices += 1
                    
                    target_temp = state.properties.get("target_temperature")
                    if target_temp:
                        avg_temp += target_temp
                        temp_count += 1
            
            avg_temp = avg_temp / temp_count if temp_count > 0 else 0
            
            return {
                "total_devices": total_devices,
                "active_devices": active_devices,
                "average_target_temperature": round(avg_temp, 1),
                "zones": len(self.user_zones.get(user_id, [])),
                "schedules": len(self.user_schedules.get(user_id, [])),
                "energy_efficiency": "good"  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error getting climate stats: {e}")
            return {}