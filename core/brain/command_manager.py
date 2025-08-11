from core.utils.log import logger

class CommandManager:
    def __init__(self):
        self.commands = {}

    def register_command(self, keywords, function):
        for keyword in keywords:
            self.commands[keyword] = function
            logger.info(f"Registered command for keyword: {keyword}")

    def execute_command(self, text):
        for keyword, function in self.commands.items():
            if keyword in text:
                function()
                return
        logger.info("Unknown command.")