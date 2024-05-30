class Logger:
    def __init__(self):
        self.messages = []

    def debug(self, message):
        self._log("debug", message)

    def info(self, message):
        self._log("info", message)

    def warning(self, message):
        self._log("warning", message)

    def error(self, message):
        self._log("error", message)

    def _log(self, level, message):
        formatted_message = "{}: {}".format(level, message)
        print(formatted_message)
        self.messages.append(formatted_message)
    def get_messages(self):
        return self.messages