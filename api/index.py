import sys
import os

# Añadir el directorio raíz al path de Python para imports de core y app
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Exportar app para el runtime de Vercel Serverless
__all__ = ["app"]
