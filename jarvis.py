from voice import listen, speak
from brain import think
import importlib

while True:
    command = listen()
    if "jarvis" in command.lower():
        module = think(f"Which module handles: {command}?")
        mod = importlib.import_module(module)
        mod.execute(command)