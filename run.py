import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("Iniciando QR Digital Studio...")
    print("Servidor corriendo en: http://127.0.0.1:8000")
    print("Documentación API: http://127.0.0.1:8000/docs")
    
    # Abrir navegador automáticamente en hilo secundario
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
