import webbrowser
import threading
import time
import socket
import uvicorn
import os
import sys

def find_available_port(start_port=8000, max_attempts=10):
    for p in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return start_port

def open_browser(port):
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    port = find_available_port(8000)
    print("=" * 60)
    print("🚀 INICIANDO QR DIGITAL STUDIO")
    print(f"👉 Servidor disponible en: http://127.0.0.1:{port}")
    print(f"👉 Documentación API:      http://127.0.0.1:{port}/docs")
    print("=" * 60)
    
    # Abrir navegador automáticamente
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    try:
        uvicorn.run("api.index:app", host="127.0.0.1", port=port, reload=True)
    except Exception as e:
        print(f"\n[ERROR] No se pudo iniciar el servidor en el puerto {port}: {e}")
        print("Intentando en puerto alternativo 8080...")
        uvicorn.run("api.index:app", host="127.0.0.1", port=8080, reload=True)
