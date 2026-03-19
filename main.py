import json
import os
import qrcode
import qrcode.image.svg as svg

CONFIG_FILE = "config.json"
BASE_OUTPUT = "output"


def cargar_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def crear_carpeta(nombre):
    carpeta = os.path.join(BASE_OUTPUT, f"{nombre}_QR")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def generar_qr_svg(nombre, url, carpeta):
    factory = svg.SvgPathImage

    img = qrcode.make(
        url,
        image_factory=factory,
        box_size=10
    )

    path = os.path.join(carpeta, f"{nombre}.svg")
    img.save(path)

    print(f"[SVG] {path}")


def generar_qr_png(nombre, url, carpeta):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    path = os.path.join(carpeta, f"{nombre}.png")
    img.save(path)

    print(f"[PNG] {path}")


def main():
    config = cargar_config()
    tarjetas = config.get("tarjetas", {})

    for nombre, url in tarjetas.items():
        carpeta = crear_carpeta(nombre)

        generar_qr_svg(nombre, url, carpeta)
        generar_qr_png(nombre, url, carpeta)


if __name__ == "__main__":
    main()