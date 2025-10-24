import logging
import json

# List of standard LogRecord attributes
STANDARD_LOG_RECORD_ATTRIBUTES = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
    "message",
}


class CustomFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)

        extra_data = {}
        for key, value in record.__dict__.items():
            if key not in STANDARD_LOG_RECORD_ATTRIBUTES:
                extra_data[key] = value

        if extra_data:
            message += f" (extra: {json.dumps(extra_data)})\n"
        return message


def init_logging(level=logging.INFO):
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to prevent duplicate output if init_logging is called multiple times
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Create a StreamHandler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Set the custom formatter for the console handler
    formatter = CustomFormatter("%(levelname)s:%(name)s:%(message)s")
    console_handler.setFormatter(formatter)

    # Add the console handler to the root logger
    root_logger.addHandler(console_handler)
