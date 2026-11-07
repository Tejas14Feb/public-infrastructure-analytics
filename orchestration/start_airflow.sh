#!/usr/bin/env bash
# Start Airflow locally (scheduler, API server, UI) for this project.
set -euo pipefail

ORCH_DIR="$(cd "$(dirname "$0")" && pwd)"

export AIRFLOW_HOME="$ORCH_DIR/airflow_home"
export AIRFLOW__CORE__DAGS_FOLDER="$ORCH_DIR/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
# macOS: avoids crashes when Airflow's processes look up proxy settings
# Put this environment's commands (including `airflow`) first on PATH,
# so the processes standalone starts can find them
export PATH="$ORCH_DIR/.venv/bin:$PATH"

exec airflow standalone