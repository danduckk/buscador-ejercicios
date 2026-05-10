#!/bin/bash
# Lanza el buscador con el Python del venv, sin tener que activarlo a mano.
# Funciona desde cualquier directorio: nos movemos al del propio script.

# Sale al primer error: si falla algún paso, no seguimos adelante
set -e

# Directorio donde vive este script (por si se llama desde otra ruta)
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Comprobamos que el venv exista; si no, avisamos con instrucciones claras
if [ ! -x ".venv/bin/python" ]; then
    echo "Error: no se encuentra .venv. Créalo primero con:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Llamamos directamente al python del venv: equivale a activarlo, pero sin
# modificar el shell del usuario. "$@" reenvía cualquier argumento extra
# (por si en el futuro main.py acepta flags).
.venv/bin/python main.py "$@"
