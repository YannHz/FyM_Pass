#!/usr/bin/env fish

set -l raiz (path dirname (status filename))
if not command -q python3
    echo "Falta python3. Revisa el README." >&2
    exit 1
end
exec python3 "$raiz/iniciar.py" --red auto $argv
