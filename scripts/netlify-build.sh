#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${ORS_API_ORIGIN:-}" ]]; then
  echo "ERROR: Set Netlify environment variable ORS_API_ORIGIN to the public Railway API origin." >&2
  echo "Example: https://ors-studio-api-production.up.railway.app" >&2
  exit 1
fi

api_origin="${ORS_API_ORIGIN%/}"
case "$api_origin" in
  https://*) ;;
  *)
    echo "ERROR: ORS_API_ORIGIN must use HTTPS." >&2
    exit 1
    ;;
esac

publish_dir="${NETLIFY_PUBLISH_DIR:-frontend}"
if [[ ! -f "$publish_dir/index.html" ]]; then
  echo "ERROR: $publish_dir/index.html was not found." >&2
  exit 1
fi

# Keep browser requests and HttpOnly session cookies on the Netlify origin.
printf '/api/* %s/api/:splat 200!\n' "$api_origin" > "$publish_dir/_redirects"

echo "Generated $publish_dir/_redirects for $api_origin"
