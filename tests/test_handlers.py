from unittest.mock import MagicMock, patch

from buffering_queue_logger.handlers import BufferingQueueHandler


@patch("buffering_queue_logger.handlers.send_logs_to_destination")
def test_buffering_queue_handler(mock_send_logs_to_destination):
    url = "https://foo.logshmog.com/v1/logs/a1b2c3"
    get_log_aggregator_key_func = MagicMock()
    get_request_headers_func = MagicMock()
    chunk_size = 99
    context = MagicMock()

    handler = BufferingQueueHandler(
        42,
        url,
        get_log_aggregator_key_func,
        get_request_headers_func,
        chunk_size,
        context=context,
    )
    handler.buffer.append("foo123")
    handler.flush()

    mock_send_logs_to_destination.assert_called_with(
        url=url,
        records=["foo123"],
        format_func=handler.format,
        get_log_aggregator_key_func=get_log_aggregator_key_func,
        get_request_headers_func=get_request_headers_func,
        chunk_size=chunk_size,
        context=context,
        ignore_runtime_errors_on_send=True,
    )


@patch("buffering_queue_logger.handlers.send_logs_to_destination")
def test_buffering_queue_handler_buffer_empty(mock_send_logs_to_destination):
    get_log_aggregator_key_func = MagicMock()
    get_request_headers_func = MagicMock()
    chunk_size = 99
    context = MagicMock()

    handler = BufferingQueueHandler(
        42,
        "https://foo.logshmog.com/v1/logs/a1b2c3",
        get_log_aggregator_key_func,
        get_request_headers_func,
        chunk_size,
        context=context,
    )
    handler.flush()

    mock_send_logs_to_destination.assert_not_called()
