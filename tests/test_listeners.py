from unittest.mock import MagicMock

from buffering_queue_logger.listeners import _monitor_queue_and_flush_buffer


def test_monitor_queue_and_flush_buffer():
    mock_curr_time_ns_func = MagicMock()
    mock_curr_time_ns_func.side_effect = [
        13_000_000_000,
        14_000_000_000,
        15_000_000_000,
        16_000_000_000,
        17_000_000_000,
        18_000_000_000,
        19_000_000_000,
        20_000_000_000,
        21_000_000_000,
        22_000_000_000,
        23_000_000_000,
        24_000_000_000,
        25_000_000_000,
        26_000_000_000,
        27_000_000_000,
        28_000_000_000,
        29_000_000_000,
        30_000_000_000,
        31_000_000_000,
        32_000_000_000,
        33_000_000_000,
        34_000_000_000,
        35_000_000_000,
        36_000_000_000,
        37_000_000_000,
        38_000_000_000,
        39_000_000_000,
        40_000_000_000,
        41_000_000_000,
        42_000_000_000,
        43_000_000_000,
    ]
    mock_handler = MagicMock()

    _monitor_queue_and_flush_buffer(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        mock_handler,
        10,
        max_iterations=31,
        curr_time_ns_func=mock_curr_time_ns_func,
    )

    assert mock_handler.flush.call_count == 4
