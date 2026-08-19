import os
import io
import base64
import urllib.parse
from typing import Optional, Union, Dict, Any, Tuple
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageOps


ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


class QREngine:
    """
    Motor centralizado y de alto rendimiento para generar códigos QR
    personalizados en formatos PNG (rasterizado HD) y SVG (vectorial escalable),
    con soporte para incrustación de logotipos, colores personalizados,
    y esquemas de tarjetas de presentación digital (vCard, WhatsApp, WiFi, URL).
    """

    @staticmethod
    def format_vcard(
        name: str,
        org: str = "",
        title: str = "",
        phone: str = "",
        email: str = "",
        url: str = "",
        note: str = ""
    ) -> str:
        """Formatea información en estándar vCard 3.0 para escaneo directo a contactos móviles."""
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{name.strip()}",
            f"N:;{name.strip()};;;",
        ]
        if org.strip():
            lines.append(f"ORG:{org.strip()}")
        if title.strip():
            lines.append(f"TITLE:{title.strip()}")
        if phone.strip():
            lines.append(f"TEL;TYPE=CELL:{phone.strip()}")
        if email.strip():
            lines.append(f"EMAIL:{email.strip()}")
        if url.strip():
            lines.append(f"URL:{url.strip()}")
        if note.strip():
            lines.append(f"NOTE:{note.strip()}")
        lines.append("END:VCARD")
        return "\n".join(lines)

    @staticmethod
    def format_whatsapp(phone: str, message: str = "") -> str:
        """Genera enlace directo a chat de WhatsApp con número y mensaje predeterminado."""
        clean_phone = "".join(ch for ch in phone if ch.isdigit() or ch == '+').lstrip('+')
        if message:
            encoded_msg = urllib.parse.quote(message)
            return f"https://wa.me/{clean_phone}?text={encoded_msg}"
        return f"https://wa.me/{clean_phone}"

    @staticmethod
    def format_wifi(ssid: str, password: str = "", auth_type: str = "WPA", hidden: bool = False) -> str:
        """Genera formato estándar para conexión automática a red WiFi al escanear."""
        # Formato: WIFI:T:WPA;S:MyNetwork;P:MyPassword;H:false;;
        auth = auth_type.upper() if auth_type else "nopass"
        h_str = "true" if hidden else "false"
        return f"WIFI:T:{auth};S:{ssid};P:{password};H:{h_str};;"

    @classmethod
    def create_qr_instance(
        cls,
        data: str,
        error_correction: str = "H",
        box_size: int = 20,
        border: int = 4
    ) -> qrcode.QRCode:
        """Crea y llena la matriz del código QR."""
        ec = ERROR_LEVELS.get(error_correction.upper(), ERROR_CORRECT_H)
        qr = qrcode.QRCode(
            version=None,
            error_correction=ec,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr

    @classmethod
    def generate_png(
        cls,
        data: str,
        fill_color: str = "#000000",
        back_color: str = "#FFFFFF",
        logo_source: Optional[Union[str, bytes, Image.Image]] = None,
        logo_size_ratio: float = 0.22,
        logo_bg_margin_ratio: float = 1.25,
        logo_bg_color: str = "#FFFFFF",
        logo_rounded: bool = True,
        error_correction: str = "H",
        box_size: int = 20,
        border: int = 4
    ) -> Image.Image:
        """
        Genera una imagen PIL en formato RGBA/RGB con alta resolución,
        colores personalizados e incrustación limpia de logotipo centrado.
        """
        # Si se especifica logo, forzamos error_correction='H' para garantizar lectura
        if logo_source is not None and error_correction != "H":
            error_correction = "H"

        qr = cls.create_qr_instance(data, error_correction, box_size, border)
        
        # Renderizado base
        qr_image = qr.make_image(
            fill_color=fill_color,
            back_color=back_color
        ).convert("RGBA")

        # Inserción de Logo si existe
        if logo_source:
            logo_img = cls._load_image(logo_source)
            if logo_img:
                qr_width, qr_height = qr_image.size
                
                # Tamaño máximo del logo proporcional
                max_logo_w = int(qr_width * logo_size_ratio)
                max_logo_h = int(qr_height * logo_size_ratio)

                # Ajustar manteniendo proporción de aspecto
                logo_img = logo_img.convert("RGBA")
                logo_img.thumbnail((max_logo_w, max_logo_h), Image.LANCZOS)
                lw, lh = logo_img.size

                # Marco/Fondo protector detrás del logo para escaneo impecable
                bg_w = int(lw * logo_bg_margin_ratio)
                bg_h = int(lh * logo_bg_margin_ratio)

                # Crear placa de fondo
                bg_layer = Image.new("RGBA", (bg_w, bg_h), (0, 0, 0, 0))
                draw_bg = ImageDraw.Draw(bg_layer)
                
                radius = int(min(bg_w, bg_h) * 0.2) if logo_rounded else 0
                draw_bg.rounded_rectangle(
                    [(0, 0), (bg_w - 1, bg_h - 1)],
                    radius=radius,
                    fill=logo_bg_color
                )

                # Posición de la placa de fondo en el centro
                bg_pos = ((qr_width - bg_w) // 2, (qr_height - bg_h) // 2)
                qr_image.alpha_composite(bg_layer, bg_pos)

                # Posición del logo dentro de la placa
                logo_pos = ((qr_width - lw) // 2, (qr_height - lh) // 2)
                qr_image.alpha_composite(logo_img, logo_pos)

        return qr_image

    @classmethod
    def generate_png_bytes(cls, **kwargs) -> bytes:
        """Genera el QR en PNG y devuelve los bytes raw en memoria."""
        img = cls.generate_png(**kwargs)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()

    @classmethod
    def generate_png_base64(cls, **kwargs) -> str:
        """Genera el QR en PNG y devuelve una Data URI lista para <img> HTML."""
        png_bytes = cls.generate_png_bytes(**kwargs)
        b64 = base64.b64encode(png_bytes).decode("ascii")
        return f"data:image/png;base64,{b64}"

    @classmethod
    def generate_svg(
        cls,
        data: str,
        fill_color: str = "#000000",
        back_color: str = "#FFFFFF",
        logo_source: Optional[Union[str, bytes, Image.Image]] = None,
        logo_size_ratio: float = 0.22,
        error_correction: str = "H",
        box_size: int = 10,
        border: int = 4
    ) -> str:
        """
        Genera código XML SVG estándar con colores personalizados
        e incrustación del logotipo en base64 de manera vectorial.
        """
        if logo_source is not None and error_correction != "H":
            error_correction = "H"

        qr = cls.create_qr_instance(data, error_correction, box_size, border)
        matrix = qr.get_matrix()
        matrix_size = len(matrix)
        total_size = matrix_size * box_size

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {total_size} {total_size}" width="100%" height="100%">'
        ]

        # Fondo
        if back_color and back_color.lower() != "transparent":
            svg_parts.append(
                f'<rect width="{total_size}" height="{total_size}" fill="{back_color}" />'
            )

        # Módulos del QR agrupados en un solo path para optimización y nitidez máxima
        path_data = []
        for r_idx, row in enumerate(matrix):
            for c_idx, cell in enumerate(row):
                if cell:
                    x = c_idx * box_size
                    y = r_idx * box_size
                    path_data.append(f"M{x},{y}h{box_size}v{box_size}h-{box_size}z")

        if path_data:
            svg_parts.append(
                f'<path d="{" ".join(path_data)}" fill="{fill_color}" shape-rendering="crispEdges" />'
            )

        # Incrustación de Logo si existe
        if logo_source:
            logo_img = cls._load_image(logo_source)
            if logo_img:
                logo_img = logo_img.convert("RGBA")
                # Calcular dimensiones en coordenadas SVG
                max_w = total_size * logo_size_ratio
                max_h = total_size * logo_size_ratio
                
                # Proporción
                lw_orig, lh_orig = logo_img.size
                ratio = min(max_w / lw_orig, max_h / lh_orig)
                lw = lw_orig * ratio
                lh = lh_orig * ratio

                # Fondo protector
                bg_w = lw * 1.25
                bg_h = lh * 1.25
                bg_x = (total_size - bg_w) / 2
                bg_y = (total_size - bg_h) / 2
                rx = min(bg_w, bg_h) * 0.2

                svg_parts.append(
                    f'<rect x="{bg_x:.2f}" y="{bg_y:.2f}" width="{bg_w:.2f}" height="{bg_h:.2f}" '
                    f'rx="{rx:.2f}" fill="#FFFFFF" />'
                )

                # Convertir logo a base64 png para incrustar en SVG
                buf = io.BytesIO()
                logo_img.save(buf, format="PNG")
                b64_logo = base64.b64encode(buf.getvalue()).decode("ascii")
                data_uri = f"data:image/png;base64,{b64_logo}"

                logo_x = (total_size - lw) / 2
                logo_y = (total_size - lh) / 2
                svg_parts.append(
                    f'<image href="{data_uri}" x="{logo_x:.2f}" y="{logo_y:.2f}" '
                    f'width="{lw:.2f}" height="{lh:.2f}" />'
                )

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    @classmethod
    def _load_image(cls, source: Union[str, bytes, Image.Image]) -> Optional[Image.Image]:
        """Carga de manera segura una imagen desde ruta, bytes o instancia PIL."""
        if isinstance(source, Image.Image):
            return source.copy()
        if isinstance(source, bytes):
            return Image.open(io.BytesIO(source))
        if isinstance(source, str):
            if os.path.exists(source):
                return Image.open(source)
        return None
