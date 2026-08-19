import webbrowser
import threading
import time
import socket
import os
import sys

# Asegurar que el directorio raíz esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
import uvicorn

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Verifica si un puerto ya está ocupado por otro proceso."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False  # Está libre
        except OSError:
            return True   # Está ocupado

def get_free_port(preferred_ports=(8000, 8080, 5000, 8001, 8002, 3000)) -> int:
    """Busca el primer puerto disponible de la lista."""
    for p in preferred_ports:
        if not is_port_in_use(p):
            return p
    # Si todos están ocupados, pedir uno dinámico al SO
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
