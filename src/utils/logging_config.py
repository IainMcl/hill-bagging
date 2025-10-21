import logging
import json


class CustomFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        if hasattr(record, "extra") and record.extra:
            message += f" (extra: {json.dumps(record.extra)})"
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
