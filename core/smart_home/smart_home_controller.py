"""
Smart Home Controller for Jarvis 2.0
This module allows Jarvis to control smart home devices.
"""

class SmartHomeController:
    def __init__(self):
        self.devices = {}

    def add_device(self, device_name, device):
        """
        Adds a new device to the smart home.
        """
        self.devices[device_name] = device

    def turn_on(self, device_name):
        """
        Turns on the given device.
        """
        if device_name in self.devices:
            self.devices[device_name].turn_on()
        else:
            print(f"Device {device_name} not found")

    def turn_off(self, device_name):
        """
        Turns off the given device.
        """
        if device_name in self.devices:
            self.devices[device_name].turn_off()
        else:
            print(f"Device {device_name} not found")
