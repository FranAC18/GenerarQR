import os
import io
import zipfile
import urllib.parse
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.qr_engine import QREngine
from core.db_manager import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
IMG_DIR = os.path.join(BASE_DIR, "img")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

app = FastAPI(
    title="QR Digital Studio API",
    description="API Serverless para generación, personalización y gestión de códigos QR para tarjetas digitales con Supabase y Vercel.",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    is_dynamic: bool = False
    base_url: Optional[str] = None


class TarjetaSaveRequest(BaseModel):
    id: str
    url: str
    logo: Optional[str] = ""
    title: Optional[str] = None
    fill_color: Optional[str] = "#000000"
    back_color: Optional[str] = "#FFFFFF"
    logo_size_ratio: Optional[float] = 0.22
    border: Optional[int] = 4
    error_correction: Optional[str] = "H"
    content_type: Optional[str] = "url"
    is_dynamic: Optional[bool] = False
    vcard_data: Optional[Dict[str, Any]] = None
    whatsapp_data: Optional[Dict[str, Any]] = None
    wifi_data: Optional[Dict[str, Any]] = None


def get_base_url(req: Optional[Request] = None, override: Optional[str] = None) -> str:
    """Calcula la URL base del servidor para generar enlaces dinámicos /c/{slug}."""
    if override and override.strip():
        return override.strip().rstrip("/")
    env_base = os.getenv("BASE_URL", "").strip().rstrip("/")
    if env_base:
        return env_base
    if req:
        scheme = req.headers.get("x-forwarded-proto", req.url.scheme)
        host = req.headers.get("x-forwarded-host", req.url.netloc)
        return f"{scheme}://{host}"
    return "http://localhost:8000"


def resolve_payload_text(req: QRGenerateRequest, base_url_str: str) -> str:
    """Convierte el tipo de contenido al texto o payload final para el QR."""
    c_type = req.content_type.lower()
    
    # Si es QR Dinámico, apunta a la URL corta de redirección
    if req.is_dynamic and req.filename:
        clean_id = req.filename.strip()
        return f"{base_url_str}/c/{clean_id}"

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


# =============================================================================
# REDIRECCIÓN DE CÓDIGOS QR DINÁMICOS CON ANALÍTICAS
# =============================================================================
@app.get("/c/{card_id}")
def redirect_dynamic_qr(card_id: str):
    """
    Endpoint de redirección para Códigos QR Dinámicos.
    Registra el escaneo (+1 en scan_count) y redirige al usuario a la URL final.
    """
    card = db.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Tarjeta digital no encontrada.")

    # Incrementar analíticas de escaneo
    db.increment_scan(card_id)

    target_url = card.get("url", "").strip()
    if not target_url:
        raise HTTPException(status_code=400, detail="La tarjeta no tiene URL de destino configurada.")

    # Asegurar esquema http/https si es enlace web
    if not target_url.startswith(("http://", "https://", "tel:", "mailto:", "BEGIN:VCARD", "WIFI:")):
        target_url = f"https://{target_url}"

    return RedirectResponse(url=target_url, status_code=307)


# =============================================================================
# ENDPOINTS REST DE LA API
# =============================================================================
@app.get("/api/status")
def get_system_status():
    """Retorna el estado de la conexión a Supabase o Modo Local."""
    return db.get_status()


@app.get("/api/tarjetas")
def get_tarjetas():
    """Obtiene el catálogo de tarjetas guardadas (desde Supabase o config.json)."""
    tarjetas = db.get_cards()
    return {"tarjetas": tarjetas, "source": db.get_status()["mode"]}


@app.post("/api/tarjetas")
def save_or_update_tarjeta(payload: TarjetaSaveRequest):
    """Guarda o actualiza una tarjeta en la base de datos."""
    card_id = payload.id.strip()
    if not card_id:
        raise HTTPException(status_code=400, detail="El identificador de la tarjeta es obligatorio.")
    if not payload.url.strip():
        raise HTTPException(status_code=400, detail="La URL o contenido es obligatorio.")

    card_dict = payload.model_dump()
    res = db.save_card(card_id, card_dict)
    return {"status": "success", "message": f"Tarjeta '{card_id}' guardada correctamente.", "card": res.get("card")}


@app.delete("/api/tarjetas/{card_id}")
def delete_tarjeta(card_id: str):
    """Elimina una tarjeta del catálogo."""
    success = db.delete_card(card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada o no se pudo eliminar.")
    return {"status": "success", "message": f"Tarjeta '{card_id}' eliminada."}


@app.post("/api/qr/preview")
def generate_preview(req: QRGenerateRequest, request: Request):
    """Genera la vista previa en base64 para renderizado dinámico en tiempo real."""
    base_url_str = get_base_url(request, req.base_url)
    text_data = resolve_payload_text(req, base_url_str)
    
    logo_src = req.logo_path.strip() if req.logo_path else None
    # Si es ruta local relativa que existe, resolverla
    if logo_src and not logo_src.startswith(("http://", "https://", "data:")):
        local_p = os.path.join(BASE_DIR, logo_src)
        if os.path.exists(local_p):
            logo_src = local_p

    try:
        preview_uri = QREngine.generate_png_base64(
            data=text_data,
            fill_color=req.fill_color,
            back_color=req.back_color,
            logo_source=logo_src,
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
            "raw_content": text_data,
            "is_dynamic": req.is_dynamic
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando vista previa: {str(e)}")


@app.post("/api/qr/download")
def download_qr(req: QRGenerateRequest, request: Request):
    """Genera y descarga el archivo QR en alta definición (PNG o SVG) 100% en memoria."""
    base_url_str = get_base_url(request, req.base_url)
    text_data = resolve_payload_text(req, base_url_str)
    clean_filename = "".join(c for c in (req.filename or "codigo_qr") if c.isalnum() or c in ("-", "_")).strip() or "codigo_qr"
    
    logo_src = req.logo_path.strip() if req.logo_path else None
    if logo_src and not logo_src.startswith(("http://", "https://", "data:")):
        local_p = os.path.join(BASE_DIR, logo_src)
        if os.path.exists(local_p):
            logo_src = local_p

    fmt = req.format.lower()
    if fmt == "svg":
        svg_content = QREngine.generate_svg(
            data=text_data,
            fill_color=req.fill_color,
            back_color=req.back_color,
            logo_source=logo_src,
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
            logo_source=logo_src,
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
    """Sube un logo a Supabase Storage (o img/ local) y devuelve su URL pública o relativa."""
    allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
    filename = file.filename or "logo.png"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado. Usa PNG, JPG, WEBP o SVG.")

    contents = await file.read()
    content_type = file.content_type or "image/png"
    
    upload_res = await db.upload_logo(contents, filename, content_type)
    return {
        "status": "success",
        "message": f"Logotipo subido exitosamente a {upload_res.get('storage')}.",
        "logo_path": upload_res.get("path"),
        "url": upload_res.get("url"),
        "filename": upload_res.get("filename"),
        "storage": upload_res.get("storage")
    }


@app.get("/api/logos")
def list_logos():
    """Lista todos los logos disponibles (en Supabase Storage o en img/)."""
    logos = db.list_logos()
    return {"logos": logos}


@app.get("/api/qr/export-all")
def export_all_zip(request: Request):
    """Genera y empaqueta en un archivo .ZIP en memoria todos los QRs registrados."""
    tarjetas = db.get_cards()

    if not tarjetas:
        raise HTTPException(status_code=404, detail="No hay tarjetas registradas para exportar.")

    base_url_str = get_base_url(request)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for nombre, data in tarjetas.items():
            if isinstance(data, dict):
                url = data.get("url", "")
                logo = data.get("logo", "")
                fill_color = data.get("fill_color", "#000000")
                back_color = data.get("back_color", "#FFFFFF")
                is_dynamic = data.get("is_dynamic", False)
            else:
                url = str(data)
                logo = ""
                fill_color = "#000000"
                back_color = "#FFFFFF"
                is_dynamic = False

            if not url:
                continue

            # Payload a codificar en el QR
            target_data = f"{base_url_str}/c/{nombre}" if is_dynamic else url

            # Resolver logo
            logo_src = logo if logo else None
            if logo_src and not logo_src.startswith(("http://", "https://", "data:")):
                local_p = os.path.join(BASE_DIR, logo_src)
                if os.path.exists(local_p):
                    logo_src = local_p

            # Generar PNG HD
            try:
                png_bytes = QREngine.generate_png_bytes(
                    data=target_data,
                    fill_color=fill_color,
                    back_color=back_color,
                    logo_source=logo_src,
                    box_size=20,
                    border=4
                )
                zip_file.writestr(f"{nombre}_QR/{nombre}.png", png_bytes)
            except Exception as e:
                print(f"Error generando PNG para {nombre}: {e}")

            # Generar SVG Vectorial
            try:
                svg_content = QREngine.generate_svg(
                    data=target_data,
                    fill_color=fill_color,
                    back_color=back_color,
                    logo_source=logo_src,
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


@app.get("/img/{file_name}")
def get_image_file(file_name: str):
    """Sirve imágenes locales de la carpeta img/ de forma garantizada."""
    clean_name = os.path.basename(file_name)
    file_path = os.path.join(IMG_DIR, clean_name)
    if os.path.exists(file_path):
        media_type = "image/png"
        if clean_name.lower().endswith(".jpg") or clean_name.lower().endswith(".jpeg"):
            media_type = "image/jpeg"
        elif clean_name.lower().endswith(".svg"):
            media_type = "image/svg+xml"
        elif clean_name.lower().endswith(".webp"):
            media_type = "image/webp"
        return FileResponse(file_path, media_type=media_type)
    raise HTTPException(status_code=404, detail="Logotipo no encontrado")


# Montar archivos estáticos para servidor local
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if os.path.exists(IMG_DIR):
    app.mount("/img", StaticFiles(directory=IMG_DIR), name="img")


@app.get("/")
def serve_index():
    """Sirve la página principal de la aplicación web."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Kobaia QR</h1><p>Frontend inicializándose...</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
