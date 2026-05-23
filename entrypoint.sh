#!/usr/bin/env sh
# Entrypoint for both `docker run` and the GitHub Action.
#
# GitHub passes action `inputs` as INPUT_<NAME> env vars. Map them to the
# variables DocDigester2MD.py reads, falling back to any directly-provided env
# (so plain `docker run -e AI_API_KEY=...` keeps working).
set -e

export AI_API_KEY="${INPUT_AI_API_KEY:-${AI_API_KEY:-}}"
export AI_BASE_URL="${INPUT_AI_BASE_URL:-${AI_BASE_URL:-}}"
export AI_MODEL="${INPUT_AI_MODEL:-${AI_MODEL:-}}"

exec python /app/DocDigester2MD.py "$@"
