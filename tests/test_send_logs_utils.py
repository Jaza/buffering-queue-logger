import json
from logging import LogRecord
from typing import Any, NamedTuple
from unittest.mock import MagicMock, call, patch

from buffering_queue_logger.send_logs_utils import send_logs_to_destination


class LogAggregatorContextTest(NamedTuple):
    foo: str
    moo: str


class LogAggregatorKeyTest(NamedTuple):
    woo: str
    hoo: str


def get_log_aggregator_context_test_func() -> LogAggregatorContextTest:
    return LogAggregatorContextTest(
        foo="foo123",
        moo="moo123",
    )


def get_log_aggregator_key_for_record_test_func(
    record: LogRecord, context: LogAggregatorContextTest | None
) -> LogAggregatorKeyTest:
    if context is None:  # pragma: no cover
        raise ValueError(
            "context is required by get_log_aggregator_key_for_record_test_func"
        )

    return LogAggregatorKeyTest(
        woo=context.foo,
        hoo=f"{context.moo}/{record.levelname}",
    )


def get_request_headers_test_func(
    headers: dict[str, Any], key: LogAggregatorKeyTest
) -> dict[str, Any]:
    new_headers = headers.copy()

    new_headers["X-Logshmog-Woo"] = key.woo
    new_headers["X-Logshmog-Hoo"] = key.hoo

    return new_headers


def log_formatter_test_func(record: Any) -> Any:
    _record = {
        "timestamp": record.extra["time"],
        "level": record.extra["level"],
        "logger": record.extra["name"],
        "message": record.extra["message"],
    }

    if record.extra.get("foo"):
        _record["foo"] = record.extra["foo"]
    if record.extra.get("moo"):
        _record["moo"] = record.extra["moo"]

    return f"{json.dumps(_record)}\n"


@patch("buffering_queue_logger.send_logs_utils.requests")
def test_send_logs_to_destination(mock_requests):
    mock_resp = MagicMock()
    mock_requests.post.return_value = mock_resp

    record1 = MagicMock()
    record1.levelname = "INFO"
    record1.extra = {
        "time": "2020-01-02 03:04:05.678+0000",
        "level": "INFO",
        "name": "foologger",
        "message": "do foo",
        "foo": "foo123",
        "moo": "moo123",
    }

    record2 = MagicMock()
    record2.levelname = "WARNING"
    record2.extra = {
        "time": "2020-01-02 03:04:06.678+0000",
        "level": "WARNING",
        "name": "foologger",
        "message": "oh my foo",
        "foo": "foo123",
        "moo": "moo123",
    }

    record3 = MagicMock()
    record3.levelname = "INFO"
    record3.extra = {
        "time": "2020-01-02 03:04:07.678+0000",
        "level": "INFO",
        "name": "foologger",
        "message": "do more foo",
        "foo": "foo123",
        "moo": "moo123",
    }

    record4 = MagicMock()
    record4.levelname = "INFO"
    record4.extra = {
        "time": "2020-01-02 03:04:08.678+0000",
        "level": "INFO",
        "name": "foologger",
        "message": "still more foo",
        "foo": "foo123",
        "moo": "moo123",
    }

    records = [record1, record2, record3, record4]
    url = "https://foo.logshmog.com/v1/logs/a1b2c3"
    _headers = {
        "Content-Type": "text/plain",
        "charset": "utf-8",
        "X-Logshmog-Woo": "foo123",
    }

    send_logs_to_destination(
        url,
        records,
        log_formatter_test_func,
        get_log_aggregator_key_for_record_test_func,
        get_request_headers_test_func,
        2,
        get_log_aggregator_context_test_func(),
        False,
    )

    mock_requests.post.assert_has_calls(
        [
            call(
                url,
                data="".join(
                    [
                        f"{json.dumps(_content)}\n"
                        for _content in [
                            {
                                "timestamp": "2020-01-02 03:04:05.678+0000",
                                "level": "INFO",
                                "logger": "foologger",
                                "message": "do foo",
                                "foo": "foo123",
                                "moo": "moo123",
                            },
                            {
                                "timestamp": "2020-01-02 03:04:07.678+0000",
                                "level": "INFO",
                                "logger": "foologger",
                                "message": "do more foo",
                                "foo": "foo123",
                                "moo": "moo123",
                            },
                        ]
                    ]
                ),
                headers=_headers | {"X-Logshmog-Hoo": "moo123/INFO"},
                timeout=5,
            ),
            call().raise_for_status(),
            call(
                url,
                data="".join(
                    [
                        f"{json.dumps(_content)}\n"
                        for _content in [
                            {
                                "timestamp": "2020-01-02 03:04:08.678+0000",
                                "level": "INFO",
                                "logger": "foologger",
                                "message": "still more foo",
                                "foo": "foo123",
                                "moo": "moo123",
                            },
                        ]
                    ]
                ),
                headers=_headers | {"X-Logshmog-Hoo": "moo123/INFO"},
                timeout=5,
            ),
            call().raise_for_status(),
            call(
                url,
                data="".join(
                    [
                        f"{json.dumps(_content)}\n"
                        for _content in [
                            {
                                "timestamp": "2020-01-02 03:04:06.678+0000",
                                "level": "WARNING",
                                "logger": "foologger",
                                "message": "oh my foo",
                                "foo": "foo123",
                                "moo": "moo123",
                            },
                        ]
                    ]
                ),
                headers=_headers | {"X-Logshmog-Hoo": "moo123/WARNING"},
                timeout=5,
            ),
            call().raise_for_status(),
        ],
    )
