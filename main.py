from core.utils.log import logger
from core.brain.command_manager import CommandManager
from core.modules.time import get_time
from core.modules.darkweb import credential_stuffing, fake_document_sales
from jarvis_voice import JarvisVoice

class Jarvis:
    def __init__(self):
        self.command_manager = CommandManager()
        self.register_commands()
        self.voice = JarvisVoice(self.command_manager)

    def register_commands(self):
        self.command_manager.register_command(["time", "what time is it"], get_time)
        self.command_manager.register_command(["credential stuffing", "stuff credentials"], credential_stuffing)
        self.command_manager.register_command(["sell fake documents", "fake documents"], fake_document_sales)

    def run(self):
        logger.info("Jarvis is starting...")
        self.voice.start()

if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()