# 📖 Documentación Completa — Kobaia QR Digital Studio

**Kobaia QR** es una plataforma profesional de generación, gestión y personalización de Códigos QR y Tarjetas Digitales interactivas, con soporte para **QRs Dinámicos**, analíticas de escaneo en tiempo real, respaldo en **Supabase (PostgreSQL & Storage)** y arquitectura Serverless lista para **Vercel**.

---

## 📑 Tabla de Contenidos
1. [Arquitectura del Sistema](#-1-arquitectura-del-sistema)
2. [Flujo de Trabajo y Experiencia de Usuario](#-2-flujo-de-trabajo-y-experiencia-de-usuario)
3. [Tipos de Contenido Soportados](#-3-tipos-de-contenido-soportados)
4. [QRs Dinámicos vs. QRs Estáticos](#-4-qrs-dinámicos-vs-qrs-estáticos)
5. [Referencia Completa de la API REST](#-5-referencia-completa-de-la-api-rest)
6. [Estructura y Esquema de Base de Datos (Supabase)](#-6-estructura-y-esquema-de-base-de-datos-supabase)
7. [Guía de Despliegue en Vercel](#-7-guía-de-despliegue-en-vercel)
8. [Ejecución en Entorno Local](#-8-ejecución-en-entorno-local)
9. [Estructura del Proyecto](#-9-estructura-del-proyecto)
10. [Preguntas Frecuentes y Solución de Problemas](#-10-preguntas-frecuentes-y-solución-de-problemas)

---

## 🏗️ 1. Arquitectura del Sistema

El proyecto opera bajo un modelo **Híbrido y Serverless**:

```
                                  ┌────────────────────────┐
                                  │   Cliente Web (SPA)    │
                                  │   HTML5 / CSS / JS     │
                                  └───────────┬────────────┘
                                              │ HTTP / JSON
                                              ▼
                             ┌─────────────────────────────────┐
                             │    Backend FastAPI (Serverless) │
                             │        `api/index.py`           │
                             └────────┬───────────────┬────────┘
                                      │               │
                     (Producción)     │               │  (Modo Local)
                                      ▼               ▼
                       ┌──────────────────────┐  ┌───────────────────┐
                       │  Supabase Database   │  │   `config.json`   │
                       │     (PostgreSQL)     │  │  (Fallback local) │
                       ├──────────────────────┤  └───────────────────┘
                       │   Supabase Storage   │
                       │ (Bucket: `qr-logos`) │
                       └──────────────────────┘
```

### Principios de Diseño:
* **Stateless & Memory-Only**: En entornos Serverless (como Vercel donde el sistema de archivos es de solo lectura), la generación de PNG en alta definición y SVG vectorial se realiza 100% en memoria RAM (`io.BytesIO()`).
* **Fallback Automático**: Si no se configuran credenciales de Supabase en `.env`, el sistema opera automáticamente en **Modo Local** persistiendo en `config.json`.
* **Zero Dependencies Bundle**: El frontend utiliza Vanilla JS y CSS con variables de diseño, garantizando tiempos de carga ultrarrápidos sin sobrecargas de frameworks.

---

## 🎯 2. Flujo de Trabajo y Experiencia de Usuario

### 1. Creación Limpia e Intuitiva
Los campos de entrada inician completamente vacíos para evitar la molestia de tener que borrar datos de ejemplo.
1. Ingresas un **Identificador único (slug)** (ej. `mi_empresa`).
2. Ingresas un **Nombre descriptivo** (ej. `Kobaia Dev`).
3. Eliges el tipo de contenido y completas los datos.
4. Personalizas los colores (selector RGB/Hex o combinaciones rápidas), tamaño de logo y margen.

### 2. Guardar y Activar Tarjeta
* El botón principal destacado: **`💾 Guardar y Generar Código QR`**.
* Al hacer clic, la tarjeta se registra de inmediato en la base de datos (PostgreSQL o local).
* Una vez guardada, se despliega fluidamente el **Panel de Descargas y Acciones**:
  - **📥 Descargar PNG (HD)**: Imagen de alta resolución para impresión y diseño.
  - **📐 Descargar SVG**: Archivo vectorial escalable sin pérdida de calidad.
  - **📋 Copiar Imagen**: Copia el código QR generado directamente al portapapeles.
  - **🔗 Probar Enlace**: Abre el enlace de redirección dinámica `/c/{slug}` en una nueva pestaña para verificar el destino.

---

## 📱 3. Tipos de Contenido Soportados

| Tipo | Icono | Descripción | Formato de Salida |
| :--- | :---: | :--- | :--- |
| **URL Web** | 🔗 | Enlace a sitios web, redes sociales o tiendas online | `https://tusitio.com` o URL dinámica `/c/{slug}` |
| **vCard (Contacto)** | 📇 | Tarjeta de contacto completa con Nombre, Teléfono, Empresa, Cargo, Email y Web | Estándar `BEGIN:VCARD ... END:VCARD` |
| **WhatsApp** | 💬 | Enlace directo para abrir chat con mensaje prediseñado | `https://wa.me/{numero}?text={mensaje}` |
| **Red WiFi** | 📶 | Conexión automática a red inalámbrica (WPA, WEP o Abierta) | `WIFI:T:WPA;S:{ssid};P:{password};;` |
| **Texto Libre** | 📝 | Texto sin formato, códigos de serie o notas | Texto en plano |

---

## ⚡ 4. QRs Dinámicos vs. QRs Estáticos

### ⚡ QR Dinámico (Recomendado)
* **¿Cómo funciona?**: El QR codifica una URL corta del sistema: `https://tudominio.com/c/{slug}`.
* **Ventajas**:
  1. **Destino Modificable**: Puedes cambiar la URL final en cualquier momento desde el catálogo sin tener que reimprimir el código QR físico.
  2. **Métricas de Escaneo**: Cada vez que alguien escanea el código, el sistema registra el escaneo en tiempo real (`scan_count`) y redirige instantáneamente con un código de estado `HTTP 307 (Temporary Redirect)`.
  3. **Menor Densidad Visual**: La URL corta genera un código QR más simple, limpio y fácil de leer por cualquier smartphone.

### 📌 QR Estático
* El QR codifica el contenido directamente en sus módulos.
* No requiere conexión a servidor para funcionar, pero su contenido **no se puede editar** una vez impreso ni registra estadísticas de escaneo.

---

## 🔌 5. Referencia Completa de la API REST

### Base URL:
- Local: `http://127.0.0.1:8000`
- Producción: `https://tu-proyecto.vercel.app`

---

### `GET /api/status`
Verifica el estado del motor y la conexión a la base de datos.

**Respuesta exitosa (`200 OK`):**
```json
{
  "mode": "supabase",
  "connected": true,
  "supabase_url": "https://xyz.supabase.co",
  "bucket": "qr-logos"
}
```

---

### `GET /api/tarjetas`
Obtiene la lista de todas las tarjetas registradas en el catálogo.

**Respuesta exitosa (`200 OK`):**
```json
{
  "status": "success",
  "count": 1,
  "mode": "supabase",
  "tarjetas": {
    "kobaia": {
      "url": "https://www.instagram.com/kobaia.dev/",
      "title": "Kobaia Dev",
      "logo": "img/kobaia.png",
      "fill_color": "#000000",
      "back_color": "#FFFFFF",
      "is_dynamic": true,
      "scan_count": 42
    }
  }
}
```

---

### `POST /api/tarjetas`
Guarda una nueva tarjeta o actualiza una existente.

**Body (`application/json`):**
```json
{
  "id": "kobaia",
  "url": "https://www.instagram.com/kobaia.dev/",
  "title": "Kobaia Dev",
  "logo": "img/kobaia.png",
  "fill_color": "#000000",
  "back_color": "#FFFFFF",
  "is_dynamic": true
}
```

---

### `DELETE /api/tarjetas/{card_id}`
Elimina una tarjeta del catálogo.

**Respuesta (`200 OK`):**
```json
{
  "status": "success",
  "message": "Tarjeta 'kobaia' eliminada."
}
```

---

### `POST /api/qr/preview`
Genera una vista previa instantánea en Base64 para el Live Preview.

**Body (`application/json`):**
```json
{
  "data": "https://kobaia.dev",
  "fill_color": "#000000",
  "back_color": "#FFFFFF",
  "logo_path": "img/kobaia.png",
  "logo_size_ratio": 0.22,
  "border": 4,
  "error_correction": "H",
  "is_dynamic": true,
  "filename": "kobaia"
}
```

**Respuesta (`200 OK`):**
```json
{
  "status": "success",
  "preview_url": "data:image/png;base64,iVBORw0KGgo...",
  "raw_content": "http://localhost:8000/c/kobaia",
  "is_dynamic": true
}
```

---

### `POST /api/qr/download`
Genera y descarga el código QR en archivo binario PNG o SVG.

---

### `GET /api/qr/export-all`
Empaqueta y descarga todas las tarjetas registradas en un archivo comprimido `.zip` conteniendo los formatos PNG y SVG de cada una.

---

### `POST /api/upload-logo`
Sube una imagen de logotipo a Supabase Storage (o almacenamiento local).

**Form-Data (`multipart/form-data`):**
- `file`: Archivo binario (PNG, JPG, SVG, WebP).

---

### `GET /c/{card_id}`
**Endpoint de Redirección Dinámica**. Registra el escaneo y redirige mediante HTTP 307 a la URL destino configurada.

---

## 🗄️ 6. Estructura y Esquema de Base de Datos (Supabase)

El script SQL completo se encuentra en [supabase_schema.sql](file:///f:/Prácticas/Tarjetas%20digitales/scriptQr/supabase_schema.sql).

### Tabla: `public.tarjetas`
```sql
CREATE TABLE IF NOT EXISTS public.tarjetas (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    logo_url TEXT,
    is_dynamic BOOLEAN DEFAULT true,
    scan_count INTEGER DEFAULT 0,
    style_config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Bucket de Storage:
- Nombre: `qr-logos` (Público).

---

## ☁️ 7. Guía de Despliegue en Vercel

1. **Subir el código a GitHub**:
   Asegúrate de que tus últimos cambios estén en la rama `main`.
2. **Importar proyecto en Vercel**:
   - Conecta tu cuenta de GitHub y selecciona el repositorio `FranAC18/GenerarQR`.
3. **Variables de Entorno en Vercel**:
   En el panel de Vercel (**Project Settings > Environment Variables**), añade:
   - `SUPABASE_URL`: `https://tu-proyecto.supabase.co`
   - `SUPABASE_KEY`: `tu-anon-public-key`
   - `BASE_URL`: `https://tu-dominio-en-vercel.vercel.app`
4. **Desplegar**:
   Haz clic en **Deploy**. Vercel compilará la función Serverless Python y servirá el frontend estático a través de su CDN global.

---

## 💻 8. Ejecución en Entorno Local

### Opción 1: Un solo clic
Haz doble clic sobre el archivo **`run.bat`**.

### Opción 2: Desde Terminal
```bash
python run.py
```
> `run.py` detecta automáticamente el entorno virtual `.venv` y verifica la disponibilidad de puertos (`8000`, `8080`, etc.) para evitar conflictos de sockets.

---

## 📂 9. Estructura del Proyecto

```
scriptQr/
├── api/
│   └── index.py            # Punto de entrada Serverless para Vercel (@vercel/python)
├── core/
│   ├── __init__.py
│   ├── db_manager.py       # Capa de datos híbrida (Supabase PostgreSQL + config.json)
│   └── qr_engine.py        # Motor de renderizado en memoria (PNG HD, SVG, vCard, WiFi)
├── img/
│   └── kobaia.png          # Logotipo predeterminado
├── static/
│   ├── css/
│   │   └── styles.css      # Sistema de diseño moderno Glassmorphism y Dark/Light Mode
│   ├── js/
│   │   └── app.js          # Lógica reactiva del cliente y gestor de catálogo
│   └── index.html          # Estructura de la aplicación web SPA
├── app.py                  # Servidor FastAPI local
├── run.py                  # Lanzador con auto-detección de entorno virtual y puertos
├── run.bat                 # Lanzador de un solo clic para Windows
├── config.json             # Almacenamiento local de respaldo
├── supabase_schema.sql     # Script DDL para inicializar Supabase
├── vercel.json             # Configuración de rutas y runtime para Vercel
├── requirements.txt        # Dependencias Python
├── DOCUMENTACION.md        # Documentación técnica exhaustiva
└── README.md               # Guía rápida del proyecto
```

---

## ❓ 10. Preguntas Frecuentes y Solución de Problemas

#### ¿Por qué el código QR dinámico necesita guardarse primero?
Para que un QR dinámico funcione, su identificador (`/c/{slug}`) debe existir registrado en la base de datos con su URL destino correspondiente. El botón **"Guardar y Generar Código QR"** garantiza que el QR que descargues ya esté activo y listo para ser escaneado inmediatamente.

#### ¿Puedo usar mis propios logos?
Sí. Puedes arrastrar cualquier archivo PNG, JPG o SVG al recuadro de logotipo en el diseñador. Si estás conectado a Supabase, se subirá automáticamente a tu bucket `qr-logos`.

#### ¿Qué hago si modifico la URL de una tarjeta ya impresa?
Ingresa a la pestaña **"Mis Tarjetas"**, haz clic en **Editar**, modifica la URL de destino y pulsa **Guardar**. El código QR físico seguirá siendo el mismo y comenzará a redirigir al nuevo enlace de inmediato.
