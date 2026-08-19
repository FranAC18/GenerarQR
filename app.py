import os
import io
import json
import zipfile
import urllib.parse
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.qr_engine import QREngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
IMG_DIR = os.path.join(BASE_DIR, "img")
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(
    title="QR Digital Studio API",
    description="API para generación, personalización y gestión de códigos QR para tarjetas digitales.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_FILE):
        default_cfg = {"tarjetas": {}}
        save_config(default_cfg)
        return default_cfg
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tarjetas": {}}


def save_config(cfg: Dict[str, Any]) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# Modelos Pydantic
class VCardData(BaseModel):
    name: str = ""
    org: Optional[str] = ""
    title: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    url: Optional[str] = ""
    note: Optional[str] = ""


class WhatsAppData(BaseModel):
    phone: str = ""
    message: Optional[str] = ""


class WiFiData(BaseModel):
    ssid: str = ""
    password: Optional[str] = ""
    auth_type: str = "WPA"
    hidden: bool = False


class QRGenerateRequest(BaseModel):
    content_type: str = Field(default="url", description="url, vcard, whatsapp, wifi, text")
    data: Optional[str] = ""
    vcard: Optional[VCardData] = None
    whatsapp: Optional[WhatsAppData] = None
    wifi: Optional[WiFiData] = None
    fill_color: str = "#000000"
    back_color: str = "#FFFFFF"
    logo_path: Optional[str] = None
    logo_size_ratio: float = 0.22
    logo_bg_margin_ratio: float = 1.25
    logo_bg_color: str = "#FFFFFF"
    logo_rounded: bool = True
    error_correction: str = "H"
    box_size: int = 20
    border: int = 4
    format: str = "png"  # png or svg
    filename: Optional[str] = "qr_codigo"


class TarjetaSaveRequest(BaseModel):
    id: str
    url: str
    logo: Optional[str] = ""
    title: Optional[str] = None
    fill_color: Optional[str] = "#000000"
    back_color: Optional[str] = "#FFFFFF"


def resolve_payload_text(req: QRGenerateRequest) -> str:
    """Convierte el tipo de contenido al texto o payload final para el QR."""
    c_type = req.content_type.lower()
    if c_type == "vcard" and req.vcard:
        return QREngine.format_vcard(
            name=req.vcard.name,
            org=req.vcard.org or "",
            title=req.vcard.title or "",
            phone=req.vcard.phone or "",
            email=req.vcard.email or "",
            url=req.vcard.url or "",
            note=req.vcard.note or ""
        )
    elif c_type == "whatsapp" and req.whatsapp:
        return QREngine.format_whatsapp(
            phone=req.whatsapp.phone,
            message=req.whatsapp.message or ""
        )
    elif c_type == "wifi" and req.wifi:
        return QREngine.format_wifi(
            ssid=req.wifi.ssid,
            password=req.wifi.password or "",
            auth_type=req.wifi.auth_type,
            hidden=req.wifi.hidden
        )
    return req.data or "https://example.com"


# Rutas API
@app.get("/api/tarjetas")
def get_tarjetas():
    """Obtiene el catálogo de tarjetas registradas en config.json."""
    config = load_config()
    tarjetas = config.get("tarjetas", {})
    return {"tarjetas": tarjetas}


@app.post("/api/tarjetas")
def save_or_update_tarjeta(payload: TarjetaSaveRequest):
    """Guarda o actualiza una tarjeta en config.json."""
    card_id = payload.id.strip()
    if not card_id:
        raise HTTPException(status_code=400, detail="El identificador de la tarjeta es obligatorio.")
    if not payload.url.strip():
        raise HTTPException(status_code=400, detail="La URL o contenido es obligatorio.")

    config = load_config()
    if "tarjetas" not in config:
        config["tarjetas"] = {}

    config["tarjetas"][card_id] = {
        "url": payload.url.strip(),
        "logo": payload.logo.strip() if payload.logo else "",
        "title": payload.title.strip() if payload.title else card_id,
        "fill_color": payload.fill_color or "#000000",
        "back_color": payload.back_color or "#FFFFFF"
    }

    save_config(config)
    return {"status": "success", "message": f"Tarjeta '{card_id}' guardada correctamente.", "card": config["tarjetas"][card_id]}


@app.delete("/api/tarjetas/{card_id}")
def delete_tarjeta(card_id: str):
    """Elimina una tarjeta del catálogo config.json."""
    config = load_config()
    tarjetas = config.get("tarjetas", {})
    if card_id not in tarjetas:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada.")

    del tarjetas[card_id]
    config["tarjetas"] = tarjetas
    save_config(config)
    return {"status": "success", "message": f"Tarjeta '{card_id}' eliminada."}


@app.post("/api/qr/preview")
def generate_preview(req: QRGenerateRequest):
    """Genera la vista previa en base64 (Data URI) para renderizado dinámico en tiempo real."""
    text_data = resolve_payload_text(req)
    
    logo_path = None
    if req.logo_path and req.logo_path.strip():
        resolved_path = os.path.join(BASE_DIR, req.logo_path.strip())
        if os.path.exists(resolved_path):
            logo_path = resolved_path

    try:
        preview_uri = QREngine.generate_png_base64(
            data=text_data,
            fill_color=req.fill_color,
            back_color=req.back_color,
            logo_source=logo_path,
            logo_size_ratio=req.logo_size_ratio,
            logo_bg_margin_ratio=req.logo_bg_margin_ratio,
            logo_bg_color=req.logo_bg_color,
            logo_rounded=req.logo_rounded,
            error_correction=req.error_correction,
            box_size=15,
            border=req.border
        )
        return {
            "status": "success",
            "preview_url": preview_uri,
            "raw_content": text_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando vista previa: {str(e)}")


@app.post("/api/qr/download")
def download_qr(req: QRGenerateRequest):
    """Genera y descarga el archivo QR en alta definición (PNG o SVG)."""
    text_data = resolve_payload_text(req)
    clean_filename = "".join(c for c in (req.filename or "codigo_qr") if c.isalnum() or c in ("-", "_")).strip() or "codigo_qr"
    
    logo_path = None
    if req.logo_path and req.logo_path.strip():
        resolved_path = os.path.join(BASE_DIR, req.logo_path.strip())
        if os.path.exists(resolved_path):
            logo_path = resolved_path

    fmt = req.format.lower()
    if fmt == "svg":
        svg_content = QREngine.generate_svg(
            data=text_data,
            fill_color=req.fill_color,
            back_color=req.back_color,
            logo_source=logo_path,
            logo_size_ratio=req.logo_size_ratio,
            error_correction=req.error_correction,
            box_size=req.box_size,
            border=req.border
        )
        return StreamingResponse(
            io.BytesIO(svg_content.encode("utf-8")),
            media_type="image/svg+xml",
            headers={"Content-Disposition": f'attachment; filename="{clean_filename}.svg"'}
        )
    else:
        png_bytes = QREngine.generate_png_bytes(
            data=text_data,
            fill_color=req.fill_color,
            back_color=req.back_color,
            logo_source=logo_path,
            logo_size_ratio=req.logo_size_ratio,
            logo_bg_margin_ratio=req.logo_bg_margin_ratio,
            logo_bg_color=req.logo_bg_color,
            logo_rounded=req.logo_rounded,
            error_correction=req.error_correction,
            box_size=req.box_size,
            border=req.border
        )
        return StreamingResponse(
            io.BytesIO(png_bytes),
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="{clean_filename}.png"'}
        )


@app.post("/api/upload-logo")
async def upload_logo(file: UploadFile = File(...)):
    """Sube un logo a la carpeta img/ y devuelve su ruta relativa."""
    allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
    filename = file.filename or "logo.png"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado. Usa PNG, JPG, WEBP o SVG.")

    # Guardar en img/
    safe_name = "".join(c for c in filename if c.isalnum() or c in (".", "-", "_"))
    dest_path = os.path.join(IMG_DIR, safe_name)
    
    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    rel_path = f"img/{safe_name}"
    return {
        "status": "success",
        "message": "Logotipo subido exitosamente.",
        "logo_path": rel_path,
        "filename": safe_name
    }


@app.get("/api/logos")
def list_logos():
    """Lista todos los logos disponibles en la carpeta img/."""
    logos = []
    if os.path.exists(IMG_DIR):
        for fname in os.listdir(IMG_DIR):
            if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg")):
                logos.append({
                    "filename": fname,
                    "path": f"img/{fname}",
                    "url": f"/img/{fname}"
                })
    return {"logos": logos}


@app.get("/api/qr/export-all")
def export_all_zip():
    """Genera y empaqueta en un archivo .ZIP todos los QRs registrados en config.json en PNG y SVG."""
    config = load_config()
    tarjetas = config.get("tarjetas", {})

    if not tarjetas:
        raise HTTPException(status_code=404, detail="No hay tarjetas registradas en config.json para exportar.")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for nombre, data in tarjetas.items():
            if isinstance(data, dict):
                url = data.get("url", "")
                logo = data.get("logo", "")
                fill_color = data.get("fill_color", "#000000")
                back_color = data.get("back_color", "#FFFFFF")
            else:
                url = str(data)
                logo = ""
                fill_color = "#000000"
                back_color = "#FFFFFF"

            if not url:
                continue

            logo_full_path = None
            if logo and logo.strip():
                resolved = os.path.join(BASE_DIR, logo.strip())
                if os.path.exists(resolved):
                    logo_full_path = resolved

            # Generar PNG HD
            try:
                png_bytes = QREngine.generate_png_bytes(
                    data=url,
                    fill_color=fill_color,
                    back_color=back_color,
                    logo_source=logo_full_path,
                    box_size=20,
                    border=4
                )
                zip_file.writestr(f"{nombre}_QR/{nombre}.png", png_bytes)
            except Exception as e:
                print(f"Error generando PNG para {nombre}: {e}")

            # Generar SVG Vectorial
            try:
                svg_content = QREngine.generate_svg(
                    data=url,
                    fill_color=fill_color,
                    back_color=back_color,
                    logo_source=logo_full_path,
                    box_size=10,
                    border=4
                )
                zip_file.writestr(f"{nombre}_QR/{nombre}.svg", svg_content)
            except Exception as e:
                print(f"Error generando SVG para {nombre}: {e}")

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="tarjetas_digitales_qr.zip"'}
    )


# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/img", StaticFiles(directory=IMG_DIR), name="img")


@app.get("/")
def serve_index():
    """Sirve la página principal de la aplicación web."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>QR Digital Studio</h1><p>Inicializando frontend...</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
