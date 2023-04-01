#!/bin/bash
set -e

$HOME/.local/bin/poetry run pytest \
  --cov=buffering_queue_logger \
  --cov=tests \
  --cov-fail-under=100 \
  --cov-report=term-missing \
  tests

set +e
