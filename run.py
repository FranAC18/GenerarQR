import webbrowser
import threading
import time
import os
import sys

# Asegurar que el directorio raíz esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
import uvicorn

PORT = 8000

def open_browser():
    """Abre el navegador web una vez que el servidor esté activo."""
    time.sleep(1.0)
    webbrowser.open(f"http://127.0.0.1:{PORT}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO QR DIGITAL STUDIO")
    print(f"👉 Aplicación Web:    http://127.0.0.1:{PORT}")
    print(f"👉 Documentación API: http://127.0.0.1:{PORT}/docs")
    print("=" * 60)
    print("\nPresiona CTRL+C en esta consola para detener el servidor.\n")
    
    # Abrir navegador en hilo secundario
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor Uvicorn con la instancia directa para máxima estabilidad en Windows
    try:
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
    except OSError as e:
        print(f"\n[AVISO] El puerto {PORT} está ocupado. Intentando en puerto 8080...")
        PORT = 8080
        threading.Thread(target=open_browser, daemon=True).start()
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
