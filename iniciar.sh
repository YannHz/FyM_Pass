#!/usr/bin/env bash
set -eu

raiz="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
    echo "Falta python3. Revisa el README." >&2
    exit 1
fi
exec python3 "$raiz/iniciar.py" "$@"
