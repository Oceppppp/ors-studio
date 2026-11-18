#!/usr/bin/env sh
set -eu

: "${REDIS_URL:?REDIS_URL must be set for the ORS background worker}"
: "${DATABASE_URL:?DATABASE_URL must be set for the ORS background worker}"

exec rq worker --url "$REDIS_URL" ors-analysis
