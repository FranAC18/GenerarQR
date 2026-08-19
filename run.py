import os
import sys
import subprocess

# 1. AUTO-ACTIVACIÓN DE ENTORNO VIRTUAL (.venv)
# Si el usuario ejecuta con python global, conmuta automáticamente a .venv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")

if os.path.exists(venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(venv_python).lower():
    sys.exit(subprocess.call([venv_python, os.path.abspath(__file__)] + sys.argv[1:]))

# Asegurar que el directorio raíz esté en sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import webbrowser
import threading
import time
import socket

try:
    from app import app
    import uvicorn
except ImportError as e:
    print("\n" + "=" * 60)
    print(f"[ERROR DE DEPENDENCIAS] {e}")
    print("Instalando dependencias necesarias...")
    print("=" * 60)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(BASE_DIR, "requirements.txt")])
    from app import app
    import uvicorn

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Verifica si un puerto ya está ocupado por otro proceso."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True

def get_free_port(preferred_ports=(8000, 8080, 5000, 8001, 8002, 3000)) -> int:
    """Busca el primer puerto disponible de la lista."""
    for p in preferred_ports:
        if not is_port_in_use(p):
            return p
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def open_browser(port: int):
    """Abre el navegador web automáticamente."""
    time.sleep(1.0)
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    PORT = get_free_port()
    
    print("=" * 60)
    print("🚀 INICIANDO QR DIGITAL STUDIO")
    print(f"👉 Aplicación Web:    http://127.0.0.1:{PORT}")
    print(f"👉 Documentación API: http://127.0.0.1:{PORT}/docs")
    print("=" * 60)
    print("\nPresiona CTRL+C en esta consola para detener el servidor.\n")
    
    # Abrir navegador en segundo plano
    threading.Thread(target=open_browser, args=(PORT,), daemon=True).start()
    
    # Iniciar servidor Uvicorn en el puerto garantizado
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
