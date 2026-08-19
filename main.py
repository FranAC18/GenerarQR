import os
import json
from core.qr_engine import QREngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
BASE_OUTPUT = os.path.join(BASE_DIR, "output")


def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return {"tarjetas": {}}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def crear_carpeta(nombre):
    carpeta = os.path.join(BASE_OUTPUT, f"{nombre}_QR")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def generar_qr_svg(nombre, url, carpeta, logo=None, fill_color="#000000", back_color="#FFFFFF"):
    logo_path = os.path.join(BASE_DIR, logo) if logo else None
    svg_data = QREngine.generate_svg(
        data=url,
        fill_color=fill_color,
        back_color=back_color,
        logo_source=logo_path,
        box_size=10,
        border=4
    )
    path = os.path.join(carpeta, f"{nombre}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg_data)
    print(f"[SVG] {path}")


def generar_qr_png(nombre, url, carpeta, logo=None, fill_color="#000000", back_color="#FFFFFF"):
    logo_path = os.path.join(BASE_DIR, logo) if logo else None
    png_bytes = QREngine.generate_png_bytes(
        data=url,
        fill_color=fill_color,
        back_color=back_color,
        logo_source=logo_path,
        box_size=20,
        border=4
    )
    path = os.path.join(carpeta, f"{nombre}.png")
    with open(path, "wb") as f:
        f.write(png_bytes)
    print(f"[PNG] {path}")


def main():
    print("=== Generador de Códigos QR para Tarjetas Digitales ===")
    config = cargar_config()
    tarjetas = config.get("tarjetas", {})

    if not tarjetas:
        print("[WARN] No se encontraron tarjetas en config.json")
        return

    for nombre, data in tarjetas.items():
        if isinstance(data, dict):
            url = data.get("url")
            logo = data.get("logo")
            fill_color = data.get("fill_color", "#000000")
            back_color = data.get("back_color", "#FFFFFF")
        else:
            url = str(data)
            logo = None
            fill_color = "#000000"
            back_color = "#FFFFFF"

        if not url:
            print(f"[ERROR] {nombre} no tiene URL definida")
            continue

        carpeta = crear_carpeta(nombre)
        print(f"\nProcesando tarjeta: {nombre} -> {url}")
        generar_qr_svg(nombre, url, carpeta, logo, fill_color, back_color)
        generar_qr_png(nombre, url, carpeta, logo, fill_color, back_color)

    print("\n[OK] Generación por consola completada exitosamente.")


if __name__ == "__main__":
    main()