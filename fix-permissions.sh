#!/usr/bin/env bash
# Normalize only requested paths inside this SMB workspace; never follow symlinks.
set -euo pipefail
workspace=$(cd -- "$(dirname -- "$0")" && pwd -P)
if (( $# == 0 )); then
  printf 'Usage: %s PATH [PATH ...]\n' "$0" >&2
  exit 2
fi
for requested in "$@"; do
  target=$(realpath -e -- "$requested")
  case "$target" in "$workspace"|"$workspace"/*) ;; *) printf 'Outside workspace: %s\n' "$requested" >&2; exit 1;; esac
  find -P "$target" -type d -exec chgrp users {} + -exec chmod g+rwx,g+s {} + -exec setfacl -m d:u::rwx,d:g::rwx,d:g:users:rwx,d:m::rwx,d:o::--- {} +
  find -P "$target" -type f -exec chgrp users {} + -exec chmod g+rw {} +
done
