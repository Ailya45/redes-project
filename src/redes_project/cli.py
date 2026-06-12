from __future__ import annotations

import subprocess
import sys


def start():
    """Ejecuta la aplicación principal mediante el módulo de Python."""
    result = subprocess.run(
        [sys.executable, "-m", "redes_project.main", *sys.argv[1:]]
    )
    sys.exit(result.returncode)


def check():
    """Ejecuta Pyright para validar tipos y la estructura del proyecto."""
    try:
        result = subprocess.run([sys.executable, "-m", "pyright", "."])
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ Error: 'pyright' is not installed. Run 'uv add --dev pyright'")
        sys.exit(1)


def lint():
    """Lanza Ruff para encontrar problemas de formato y estilo."""
    try:
        result = subprocess.run(["ruff", "check", "."])
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ Error: 'ruff' is not installed.")
        sys.exit(1)


def fix():
    """Aplica correcciones automáticas de formato y estilo con Ruff."""
    subprocess.run(["ruff", "check", ".", "--fix"])
