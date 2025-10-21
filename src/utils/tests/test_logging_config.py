import logging
from unittest.mock import patch
from src.utils.logging_config import init_logging
import json


@patch("src.utils.logging_config.logging.StreamHandler")
def test_init_logging_with_extra(mock_stream_handler):
    # Ensure logging is reset for this test to avoid interference
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.setLevel(logging.INFO)

    init_logging(level=logging.INFO)

    # Get the mock handler instance
    handler_instance = mock_stream_handler.return_value

    # Set the level attribute on the mock handler
    handler_instance.level = logging.INFO

    # Assert that a StreamHandler was created and configured
    mock_stream_handler.assert_called_once()

    # Get the formatter instance that was set
    formatter = handler_instance.setFormatter.call_args[0][0]

    test_message = "This is a test message"
    test_extra = {"key": "value", "number": 123}

    # Use a real logger to create a LogRecord with extra attributes
    # This is how logger.info(..., extra=...) works
    temp_logger = logging.getLogger("temp_logger")
    temp_logger.propagate = False  # Prevent it from sending to other handlers

    # Create a dummy handler to capture the record
    # This is a bit convoluted, but necessary to get a LogRecord with extra attributes
    # as they would be passed by logger.info
    class CaptureHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.records = []

        def emit(self, record):
            self.records.append(record)

    capture_handler = CaptureHandler()
    temp_logger.addHandler(capture_handler)

    temp_logger.info(test_message, extra=test_extra)

    record = capture_handler.records[0]

    formatted_message = formatter.format(record)

    assert test_message in formatted_message
    assert f" (extra: {json.dumps(test_extra)})\n" in formatted_message

    # Clean up
    temp_logger.removeHandler(capture_handler)
