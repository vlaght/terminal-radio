import logging


class RoundLogBuffer:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.buffer = []

    def add(self, message: str):
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)
        self.buffer.append(message)

    def get(self):
        return self.buffer


class AppLogHandler(logging.Handler):
    formatter: logging.Formatter

    def __init__(self, buffer_size: int = 250) -> None:
        super().__init__()
        self.buffer = RoundLogBuffer(max_size=buffer_size)
        self.formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")

    def emit(self, record):
        # Emit a log message to the terminal
        self.buffer.add(self.format(record))


class LogController:
    def __init__(self):
        # make python logger to log this string
        self.logger = logging.getLogger("terminal_radio")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.logger.handlers.clear()
        # Set up a console handler
        self.logging_handler = AppLogHandler()
        self.logger.addHandler(self.logging_handler)

    def log(self, *args, **kwargs):
        self.logger.log(*args, **kwargs)

    def get_log(self) -> list[str]:
        return self.logging_handler.buffer.get()
