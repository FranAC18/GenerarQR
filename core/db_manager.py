import os
import json
import io
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from core.field_encryption import blind_index, decrypt_text, encrypt_text

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
        self.security_schema = "seguridad"
        self.catalog_schema = "catalogo"
        self.analytics_schema = "analitica"
        self.audit_schema = "auditoria"

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
            "bucket": self.bucket_name if self.is_supabase else None,
            "schemas": [self.security_schema, self.catalog_schema,
                        self.analytics_schema, self.audit_schema]
                if self.is_supabase else []
        }

    def _catalog_table(self):
        """Devuelve la tabla del módulo de catálogo en el esquema segmentado."""
        return self.client.schema(self.catalog_schema).table("tarjetas")

    def _analytics_table(self):
        """Devuelve la tabla de escaneos del módulo de analítica."""
        return self.client.schema(self.analytics_schema).table("escaneos")

    def _audit_table(self, table_name: str):
        """Devuelve una tabla de auditoría; se usa para eventos fuera de SQL."""
        return self.client.schema(self.audit_schema).table(table_name)

    def _audit_failure(self, action: str, error: Exception, module: str,
                       table: Optional[str] = None, record_id: Optional[str] = None,
                       context: Optional[Dict[str, Any]] = None) -> None:
        """Intenta guardar un error sin ocultar la excepción original."""
        if not self.is_supabase:
            return
        try:
            ctx = context or {}
            self._audit_table("catch").insert({
                "usuario": os.getenv("AUDIT_USER", "sistema_api"),
                "accion_realizada": action,
                "modulo": module,
                "esquema": {
                    "seguridad": self.security_schema,
                    "catalogo": self.catalog_schema,
                    "analitica": self.analytics_schema,
                    "auditoria": self.audit_schema,
                }.get(module),
                "tabla": table,
                "operacion": action.split(" ", 1)[0].upper(),
                "registro_id": record_id,
                "ip": ctx.get("ip"),
                "user_agent": ctx.get("user_agent"),
                "request_id": ctx.get("request_id"),
                "codigo_error": type(error).__name__,
                "mensaje_error": str(error),
                "detalle": ctx,
            }).execute()
        except Exception as audit_error:
            print(f"[WARN] No se pudo registrar auditoría catch: {audit_error}")

    def audit_success(self, action: str, module: str, table: str,
                      operation: str, record_id: Optional[str] = None,
                      context: Optional[Dict[str, Any]] = None) -> None:
        """Registra operaciones fuera de tablas transaccionales, como Storage."""
        if not self.is_supabase:
            return
        try:
            ctx = context or {}
            self._audit_table("try").insert({
                "usuario": os.getenv("AUDIT_USER", "sistema_api"),
                "accion_realizada": action,
                "modulo": module,
                "esquema": module,
                "tabla": table,
                "operacion": operation,
                "registro_id": record_id,
                "ip": ctx.get("ip"),
                "user_agent": ctx.get("user_agent"),
                "request_id": ctx.get("request_id"),
                "detalle": ctx,
            }).execute()
        except Exception as audit_error:
            print(f"[WARN] No se pudo registrar auditoría try: {audit_error}")

    # =========================================================================
    # GESTIÓN DE TARJETAS (CRUD)
    # =========================================================================
    def get_cards(self) -> Dict[str, Any]:
        """Obtiene todas las tarjetas guardadas."""
        if self.is_supabase:
            try:
                res = self._catalog_table().select("*").order("creado_en", desc=True).execute()
                cards_dict = {}
                for row in res.data:
                    cid = row["id"]
                    style = row.get("style_config") or {}
                    cards_dict[cid] = {
                        "url": decrypt_text(row.get("url", ""), "catalogo.tarjetas.url"),
                        "title": decrypt_text(row.get("title", cid), "catalogo.tarjetas.title"),
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
                res = self._catalog_table().select("*").eq("id", card_id).single().execute()
                if res.data:
                    row = res.data
                    style = row.get("style_config") or {}
                    return {
                        "id": row["id"],
                        "url": decrypt_text(row.get("url", ""), "catalogo.tarjetas.url"),
                        "title": decrypt_text(row.get("title", card_id), "catalogo.tarjetas.title"),
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

    def save_card(self, card_id: str, data: Dict[str, Any], require_supabase: bool = False) -> Dict[str, Any]:
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
                    "title": encrypt_text(data.get("title", card_id), "catalogo.tarjetas.title"),
                    "url": encrypt_text(data.get("url", ""), "catalogo.tarjetas.url"),
                    "content_type": data.get("content_type", "url"),
                    "logo_url": data.get("logo", ""),
                    "style_config": style_config,
                    "is_dynamic": data.get("is_dynamic", False),
                    "vcard_data": data.get("vcard_data"),
                    "whatsapp_data": data.get("whatsapp_data"),
                    "wifi_data": data.get("wifi_data"),
                }
                res = self._catalog_table().upsert(record).execute()
                public_record = {
                    **record,
                    "title": decrypt_text(record["title"], "catalogo.tarjetas.title"),
                    "url": decrypt_text(record["url"], "catalogo.tarjetas.url"),
                }
                return {"status": "success", "storage": "supabase", "card": public_record}
            except Exception as e:
                self._audit_failure("guardar tarjeta", e, "catalogo", "tarjetas", card_id)
                if require_supabase:
                    raise RuntimeError("No se pudo guardar la tarjeta en Supabase.") from e
                print(f"[ERROR] Error guardando en Supabase: {e}. Guardando en local.")

        # Fallback local
        config = self._load_local_config()
        if "tarjetas" not in config:
            config["tarjetas"] = {}
        
        config["tarjetas"][card_id] = {
            "url": encrypt_text(data.get("url", ""), "catalogo.tarjetas.url"),
            "logo": data.get("logo", ""),
            "title": encrypt_text(data.get("title", card_id), "catalogo.tarjetas.title"),
            "fill_color": style_config["fill_color"],
            "back_color": style_config["back_color"],
            "is_dynamic": data.get("is_dynamic", False),
            "scan_count": data.get("scan_count", 0),
            "content_type": data.get("content_type", "url"),
        }
        self._save_local_config(config)
        public_card = {
            **config["tarjetas"][card_id],
            "url": decrypt_text(config["tarjetas"][card_id]["url"], "catalogo.tarjetas.url"),
            "title": decrypt_text(config["tarjetas"][card_id]["title"], "catalogo.tarjetas.title"),
        }
        return {"status": "success", "storage": "local", "card": public_card}

    def save_demo_user(self, username: str, email: str) -> None:
        """Store the demo user's sensitive fields encrypted in seguridad.usuarios."""
        if not self.is_supabase:
            raise RuntimeError("El formulario de evidencia requiere una conexión a Supabase.")

        record = {
            "usuario": encrypt_text(username, "seguridad.usuarios.usuario"),
            "correo": encrypt_text(email, "seguridad.usuarios.correo"),
            "usuario_hmac": blind_index(username, "usuario"),
            "correo_hmac": blind_index(email, "correo"),
            "rol": "operador",
        }
        try:
            self.client.schema(self.security_schema).table("usuarios").insert(
                record, returning="minimal"
            ).execute()
        except Exception as e:
            self._audit_failure("guardar usuario de demostración", e, "seguridad", "usuarios")
            if "23505" in str(e) or "duplicate key" in str(e).lower():
                raise RuntimeError(
                    "El usuario o correo de prueba ya están registrados; usa valores ficticios distintos."
                ) from e
            raise RuntimeError(
                "No se pudo guardar el usuario. Compruebe la migración y los permisos de Supabase."
            ) from e

    def delete_card(self, card_id: str) -> bool:
        """Elimina una tarjeta del catálogo."""
        if self.is_supabase:
            try:
                self._catalog_table().delete().eq("id", card_id).execute()
                return True
            except Exception as e:
                self._audit_failure("eliminar tarjeta", e, "catalogo", "tarjetas", card_id)
                print(f"[ERROR] Error eliminando en Supabase: {e}")

        config = self._load_local_config()
        tarjetas = config.get("tarjetas", {})
        if card_id in tarjetas:
            del tarjetas[card_id]
            config["tarjetas"] = tarjetas
            self._save_local_config(config)
            return True
        return False

    def increment_scan(self, card_id: str, context: Optional[Dict[str, Any]] = None) -> int:
        """Incrementa el contador de escaneos para analíticas en tiempo real."""
        if self.is_supabase:
            try:
                scan_record = {"tarjeta_id": card_id, **(context or {})}
                self._analytics_table().insert(scan_record).execute()
                card = self.get_card(card_id)
                current_count = (card.get("scan_count") or 0) + 1 if card else 1
                self._catalog_table().update({"scan_count": current_count}).eq("id", card_id).execute()
                return current_count
            except Exception as e:
                self._audit_failure("registrar escaneo", e, "analitica", "escaneos", card_id, context)
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
                self.audit_success(
                    "subir logotipo",
                    "archivos",
                    "storage.objects",
                    "INSERT",
                    safe_name,
                )
                return {
                    "path": public_url,
                    "url": public_url,
                    "filename": safe_name,
                    "storage": "supabase"
                }
            except Exception as e:
                self._audit_failure("subir logotipo", e, "archivos", "storage.objects", safe_name)
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
        cards = cfg.get("tarjetas", {})
        readable_cards = {}
        for card_id, card in cards.items():
            if isinstance(card, dict):
                readable_cards[card_id] = {
                    **card,
                    "url": decrypt_text(card.get("url", ""), "catalogo.tarjetas.url"),
                    "title": decrypt_text(card.get("title", card_id), "catalogo.tarjetas.title"),
                }
            else:
                readable_cards[card_id] = card
        return readable_cards


# Instancia singleton
db = DatabaseManager()
