# 🚀 QR Digital Studio - Generador & Diseñador de Tarjetas Digitales

Aplicación web profesional e interactiva para la creación, personalización, gestión y exportación en alta definición (PNG HD y SVG Vectorial) de códigos QR para tarjetas de presentación digital, enlaces web, WhatsApp directo, contactos vCard y redes WiFi.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![UI](https://img.shields.io/badge/UI-Vanilla%20CSS%20Glassmorphism-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Características Principales

- **🎨 Interfaz Web Moderna**: Diseñada con estética Glassmorphism, temas claro/oscuro dinámicos y diseño responsivo para móviles y escritorio.
- **⚡ Previsualización en Tiempo Real (Live Preview)**: Renderizado instantáneo y dinámico de cualquier cambio de contenido, color, tamaño o logo.
- **🖼️ Incrustación Inteligente de Logotipos**: Carga de logos mediante *Drag & Drop*, centrado automático con placa de seguridad y corrección de error de nivel **H (30%)** para garantizar escaneabilidad total.
- **📇 Soporte Multiformato de Tarjeta**:
  - **URL Web**: Enlaces directos a sitios web o páginas de tarjeta digital.
  - **Contacto vCard 3.0**: Nombre, empresa, cargo, teléfono, email y enlace para guardar directamente en la agenda telefónica del móvil.
  - **WhatsApp Directo**: Genera enlace `wa.me` con número y mensaje predeterminado.
  - **Conexión WiFi**: Datos de red (SSID, contraseña, tipo de cifrado) para conexión instantánea al escanear.
  - **Texto Libre**: Notas y mensajes de texto.
- **🎨 Personalización Visual**:
  - Selector de color de módulos QR y color de fondo.
  - Paletas de combinaciones rápidas.
  - Sliders para ajustar el tamaño del logo y margen del código.
- **🗂️ Catálogo de Tarjetas ("Mis Tarjetas")**:
  - Gestión visual de tarjetas digitales almacenadas en `config.json`.
  - Búsqueda, edición y eliminación de tarjetas.
  - Generación de miniaturas automáticas.
- **📥 Exportación Avanzada**:
  - Descarga individual en **PNG de Alta Definición** (2000x2000px).
  - Descarga individual en **SVG Vectorial** (escalable para imprenta, con logo incrustado).
  - **Exportación Masiva en ZIP**: Descarga todas las tarjetas del catálogo organizadas en carpetas con sus archivos PNG y SVG con un solo clic.
- **💻 Compatibilidad CLI**: Conserva la capacidad de ejecutarse por consola vía `python main.py` utilizando el nuevo motor unificado `core/qr_engine.py`.

---

## 📁 Estructura del Proyecto

```
scriptQr/
├── app.py               # Servidor Web Backend FastAPI & Endpoints REST
├── run.py               # Script de inicio que arranca el servidor y abre el navegador
├── run.bat              # Lanzador rápido con doble clic para Windows
├── main.py              # Script de ejecución por consola (CLI)
├── mainPng.py           # Script de compatibilidad legacy
├── config.json          # Archivo de almacenamiento de tarjetas digitales
├── requirements.txt     # Dependencias de Python
├── core/
│   ├── __init__.py
│   └── qr_engine.py     # Motor centralizado de generación QR (PNG, SVG, Logos, vCard)
├── img/                 # Directorio de logotipos
│   ├── MacroJG.png
│   └── iconourquizo.png
├── static/              # Frontend web interactivo
│   ├── index.html       # Estructura de la aplicación
│   ├── css/
│   │   └── styles.css   # Estilos modernos y variables de diseño
│   └── js/
│       └── app.js       # Lógica reactiva de la interfaz
└── output/              # Carpeta de salida para exportaciones locales
```

---

## 🛠️ Instalación y Requisitos

### 1. Clonar el repositorio
```bash
git clone https://github.com/FranAC18/GenerarQR.git
cd GenerarQR
```

### 2. Crear y activar el entorno virtual
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate

# Linux / MacOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

---

## 🚀 Uso de la Aplicación

### Opción A: Iniciar la Aplicación Web (Recomendado)

Ejecuta el siguiente comando o haz doble clic en `run.bat`:
```bash
python run.py
```
> Se abrirá automáticamente tu navegador en `http://localhost:8000`. También puedes acceder a la documentación interactiva de la API en `http://localhost:8000/docs`.

### Opción B: Ejecución por Consola (CLI)

Si prefieres generar todos los códigos QR directamente desde `config.json` a la carpeta `output/`:
```bash
python main.py
```

---

## ⚙️ Estructura de `config.json`

Las tarjetas digitales se almacenan de manera persistente en `config.json`:
```json
{
  "tarjetas": {
    "macrojaguar": {
      "url": "https://franac18.github.io/MacrojaguarQR",
      "logo": "img/MacroJG.png",
      "title": "Macro Jaguar QR",
      "fill_color": "#000000",
      "back_color": "#FFFFFF"
    },
    "FredyUrquizo": {
      "url": "https://tarjetas.mostazaweb.net/urquizofotografia",
      "logo": "img/iconourquizo.png",
      "title": "Fredy Urquizo Fotografía",
      "fill_color": "#000000",
      "back_color": "#FFFFFF"
    }
  }
}
```

---

## 📖 Endpoints Principales de la API

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/tarjetas` | Lista todas las tarjetas guardadas |
| `POST` | `/api/tarjetas` | Crea o actualiza una tarjeta en `config.json` |
| `DELETE` | `/api/tarjetas/{id}` | Elimina una tarjeta del catálogo |
| `POST` | `/api/qr/preview` | Genera una previsualización en base64 |
| `POST` | `/api/qr/download` | Descarga el QR en alta resolución (PNG o SVG) |
| `POST` | `/api/upload-logo` | Sube un archivo de logotipo a `img/` |
| `GET` | `/api/logos` | Lista los logotipos disponibles |
| `GET` | `/api/qr/export-all` | Genera y descarga un archivo `.zip` con todas las tarjetas |

---

## 👨‍💻 Autor y Créditos

Desarrollado y mantenido por [FranAC18](https://github.com/FranAC18).
Repositorio oficial: [FranAC18/GenerarQR](https://github.com/FranAC18/GenerarQR)
