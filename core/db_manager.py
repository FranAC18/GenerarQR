import os
import json
import io
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
IMG_DIR = os.path.join(BASE_DIR, "img")

os.makedirs(IMG_DIR, exist_ok=True)


class DatabaseManager:
    """
    Gestor de base de datos híbrido y resiliente.
    - Si SUPABASE_URL y SUPABASE_KEY están configuradas, utiliza Supabase (PostgreSQL + Storage).
    - Si no están configuradas (modo local/desarrollo), utiliza config.json y la carpeta img/.
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "").strip()
        self.supabase_key = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_ANON_KEY", "")).strip()
        self.client = None
        self.bucket_name = "qr-logos"

        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.supabase_key)
                print(f"[OK] Supabase conectado exitosamente: {self.supabase_url}")
            except Exception as e:
                print(f"[WARN] Error inicializando cliente Supabase: {e}. Usando modo local.")
                self.client = None

    @property
    def is_supabase(self) -> bool:
        return self.client is not None

    def get_status(self) -> Dict[str, Any]:
        return {
            "mode": "supabase" if self.is_supabase else "local",
            "connected": self.is_supabase,
            "supabase_url": self.supabase_url if self.is_supabase else None,
            "bucket": self.bucket_name if self.is_supabase else None
        }

    # =========================================================================
    # GESTIÓN DE TARJETAS (CRUD)
    # =========================================================================
    def get_cards(self) -> Dict[str, Any]:
        """Obtiene todas las tarjetas guardadas."""
        if self.is_supabase:
            try:
                res = self.client.table("tarjetas").select("*").order("created_at", desc=True).execute()
                cards_dict = {}
                for row in res.data:
                    cid = row["id"]
                    style = row.get("style_config") or {}
                    cards_dict[cid] = {
                        "url": row.get("url", ""),
                        "title": row.get("title", cid),
                        "logo": row.get("logo_url", ""),
                        "content_type": row.get("content_type", "url"),
                        "fill_color": style.get("fill_color", "#000000"),
                        "back_color": style.get("back_color", "#FFFFFF"),
                        "logo_size_ratio": style.get("logo_size_ratio", 0.22),
                        "border": style.get("border", 4),
                        "error_correction": style.get("error_correction", "H"),
                        "is_dynamic": row.get("is_dynamic", False),
                        "scan_count": row.get("scan_count", 0),
                        "vcard_data": row.get("vcard_data"),
                        "whatsapp_data": row.get("whatsapp_data"),
                        "wifi_data": row.get("wifi_data"),
                    }
                return cards_dict
            except Exception as e:
                print(f"[ERROR] Error consultando Supabase: {e}. Fallback a local.")

        return self._get_local_cards()

    def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una tarjeta específica por su identificador."""
        if self.is_supabase:
            try:
                res = self.client.table("tarjetas").select("*").eq("id", card_id).single().execute()
                if res.data:
                    row = res.data
                    style = row.get("style_config") or {}
                    return {
                        "id": row["id"],
                        "url": row.get("url", ""),
                        "title": row.get("title", card_id),
                        "logo": row.get("logo_url", ""),
                        "content_type": row.get("content_type", "url"),
                        "fill_color": style.get("fill_color", "#000000"),
                        "back_color": style.get("back_color", "#FFFFFF"),
                        "is_dynamic": row.get("is_dynamic", False),
                        "scan_count": row.get("scan_count", 0),
                        "vcard_data": row.get("vcard_data"),
                        "whatsapp_data": row.get("whatsapp_data"),
                        "wifi_data": row.get("wifi_data"),
                    }
            except Exception as e:
                print(f"[WARN] Error obteniendo tarjeta {card_id} en Supabase: {e}")

        cards = self._get_local_cards()
        if card_id in cards:
            c = cards[card_id]
            if isinstance(c, dict):
                return {"id": card_id, **c}
            return {"id": card_id, "url": str(c), "logo": ""}
        return None

    def save_card(self, card_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea o actualiza una tarjeta."""
        style_config = {
            "fill_color": data.get("fill_color", "#000000"),
            "back_color": data.get("back_color", "#FFFFFF"),
            "logo_size_ratio": data.get("logo_size_ratio", 0.22),
            "border": data.get("border", 4),
            "error_correction": data.get("error_correction", "H"),
        }

        if self.is_supabase:
            try:
                record = {
                    "id": card_id,
                    "title": data.get("title", card_id),
                    "url": data.get("url", ""),
                    "content_type": data.get("content_type", "url"),
                    "logo_url": data.get("logo", ""),
                    "style_config": style_config,
                    "is_dynamic": data.get("is_dynamic", False),
                    "vcard_data": data.get("vcard_data"),
                    "whatsapp_data": data.get("whatsapp_data"),
                    "wifi_data": data.get("wifi_data"),
                }
                res = self.client.table("tarjetas").upsert(record).execute()
                return {"status": "success", "card": record}
            except Exception as e:
                print(f"[ERROR] Error guardando en Supabase: {e}. Guardando en local.")

        # Fallback local
        config = self._load_local_config()
        if "tarjetas" not in config:
            config["tarjetas"] = {}
        
        config["tarjetas"][card_id] = {
            "url": data.get("url", ""),
            "logo": data.get("logo", ""),
            "title": data.get("title", card_id),
            "fill_color": style_config["fill_color"],
            "back_color": style_config["back_color"],
            "is_dynamic": data.get("is_dynamic", False),
            "scan_count": data.get("scan_count", 0),
            "content_type": data.get("content_type", "url"),
        }
        self._save_local_config(config)
        return {"status": "success", "card": config["tarjetas"][card_id]}

    def delete_card(self, card_id: str) -> bool:
        """Elimina una tarjeta del catálogo."""
        if self.is_supabase:
            try:
                self.client.table("tarjetas").delete().eq("id", card_id).execute()
                return True
            except Exception as e:
                print(f"[ERROR] Error eliminando en Supabase: {e}")

        config = self._load_local_config()
        tarjetas = config.get("tarjetas", {})
        if card_id in tarjetas:
            del tarjetas[card_id]
            config["tarjetas"] = tarjetas
            self._save_local_config(config)
            return True
        return False

    def increment_scan(self, card_id: str) -> int:
        """Incrementa el contador de escaneos para analíticas en tiempo real."""
        if self.is_supabase:
            try:
                card = self.get_card(card_id)
                current_count = (card.get("scan_count") or 0) + 1 if card else 1
                self.client.table("tarjetas").update({"scan_count": current_count}).eq("id", card_id).execute()
                return current_count
            except Exception as e:
                print(f"[WARN] Error incrementando escaneo en Supabase: {e}")
        
        config = self._load_local_config()
        tarjetas = config.get("tarjetas", {})
        if card_id in tarjetas and isinstance(tarjetas[card_id], dict):
            current = tarjetas[card_id].get("scan_count", 0) + 1
            tarjetas[card_id]["scan_count"] = current
            self._save_local_config(config)
            return current
        return 1

    # =========================================================================
    # GESTIÓN DE LOGOTIPOS Y STORAGE
    # =========================================================================
    async def upload_logo(self, file_bytes: bytes, filename: str, content_type: str = "image/png") -> Dict[str, str]:
        """Sube un logo a Supabase Storage o a la carpeta local img/."""
        safe_name = "".join(c for c in filename if c.isalnum() or c in (".", "-", "_"))

        if self.is_supabase:
            try:
                # Subir archivo al bucket de Supabase
                res = self.client.storage.from_(self.bucket_name).upload(
                    path=safe_name,
                    file=file_bytes,
                    file_options={"content-type": content_type, "upsert": "true"}
                )
                public_url = self.client.storage.from_(self.bucket_name).get_public_url(safe_name)
                return {
                    "path": public_url,
                    "url": public_url,
                    "filename": safe_name,
                    "storage": "supabase"
                }
            except Exception as e:
                print(f"[WARN] Error subiendo a Supabase Storage: {e}. Guardando localmente.")

        # Guardar localmente
        dest_path = os.path.join(IMG_DIR, safe_name)
        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        rel_path = f"img/{safe_name}"
        return {
            "path": rel_path,
            "url": f"/{rel_path}",
            "filename": safe_name,
            "storage": "local"
        }

    def list_logos(self) -> List[Dict[str, str]]:
        """Lista los logos disponibles."""
        logos = []
        if self.is_supabase:
            try:
                files = self.client.storage.from_(self.bucket_name).list()
                for f in files:
                    name = f.get("name")
                    if name and not name.startswith("."):
                        p_url = self.client.storage.from_(self.bucket_name).get_public_url(name)
                        logos.append({
                            "filename": name,
                            "path": p_url,
                            "url": p_url,
                            "storage": "supabase"
                        })
                if logos:
                    return logos
            except Exception as e:
                print(f"[WARN] Error listando logos en Supabase: {e}")

        # Local
        if os.path.exists(IMG_DIR):
            for fname in os.listdir(IMG_DIR):
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg")):
                    logos.append({
                        "filename": fname,
                        "path": f"img/{fname}",
                        "url": f"/img/{fname}",
                        "storage": "local"
                    })
        return logos

    # =========================================================================
    # HELPERS LOCALES
    # =========================================================================
    def _load_local_config(self) -> Dict[str, Any]:
        if not os.path.exists(CONFIG_FILE):
            return {"tarjetas": {}}
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"tarjetas": {}}

    def _save_local_config(self, cfg: Dict[str, Any]) -> None:
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] No se pudo guardar config.json (entorno read-only): {e}")

    def _get_local_cards(self) -> Dict[str, Any]:
        cfg = self._load_local_config()
        return cfg.get("tarjetas", {})


# Instancia singleton
db = DatabaseManager()
