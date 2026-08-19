# 🚀 Kobaia QR - Generador & Gestor de Tarjetas Digitales y QRs Dinámicos

Aplicación web profesional e interactiva para la creación, personalización, gestión y exportación en alta definición (PNG HD y SVG Vectorial) de códigos QR para tarjetas de presentación digital, con soporte nativo para **Códigos QR Dinámicos (Redirigibles)**, analíticas de escaneo en tiempo real y arquitectura lista para desplegar en **Vercel** respaldada por **Supabase**.

![Vercel](https://img.shields.io/badge/Vercel-Serverless%20Ready-black.svg?logo=vercel)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL%20%26%20Storage-green.svg?logo=supabase)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

> 📖 **Para la especificación técnica completa, consulta el archivo [DOCUMENTACION.md](DOCUMENTACION.md)**.

---

## 🌟 Características Principales

- **⚡ Códigos QR Dinámicos (`/c/{slug}`)**:
  - Los códigos QR apuntan a tu dominio y redirigen al destino real de forma instantánea.
  - Puedes actualizar el enlace de destino, teléfono o red social en cualquier momento **sin necesidad de volver a imprimir la tarjeta física**.
- **📊 Métricas y Analíticas de Escaneo**:
  - Contador de escaneos en tiempo real (`scan_count`) para medir el impacto de cada tarjeta.
- **💾 Flujo de Guardado y Activación Inteligente**:
  - Botón principal de **Guardar y Activar** que registra la tarjeta antes de habilitar las descargas de PNG y SVG.
- **☁️ Supabase Cloud (PostgreSQL + Object Storage)**:
  - Base de datos en la nube para persistencia global sincronizada.
  - Bucket `qr-logos` para hospedar logotipos de clientes con CDN pública permanente.
  - Script SQL listo para ejecutar en 1 clic (`supabase_schema.sql`).
- **🛡️ Modo Híbrido Resiliente (Zero Config)**:
  - Si no configuras claves de Supabase, la app funciona de inmediato en **Modo Local** (`config.json` + `img/`).
  - Al agregar `SUPABASE_URL` y `SUPABASE_KEY` (en `.env` o en Vercel), se conecta automáticamente a la nube.
- **⚡ Despliegue Serverless en Vercel**:
  - Motor de generación QR **100% en memoria** (PNG HD y SVG) sin colisiones con el sistema de archivos de solo lectura.
  - Enrutamiento configurado mediante `vercel.json` y `api/index.py`.

---

## 📁 Estructura del Proyecto

```
scriptQr/
├── api/
│   └── index.py            # Punto de entrada Serverless para Vercel (@vercel/python)
├── core/
│   ├── __init__.py
│   ├── qr_engine.py        # Motor de generación de QRs en memoria (PNG, SVG, Logos remotos y locales)
│   └── db_manager.py       # Gestor de base de datos híbrido (Supabase Cloud + Local Fallback)
├── img/
│   └── kobaia.png          # Logotipo predeterminado
├── static/                 # Frontend Web Moderno
│   ├── index.html          # Estructura de la aplicación SPA
│   ├── css/
│   │   └── styles.css      # Sistema de diseño Glassmorphism, Dark/Light mode
│   └── js/
│       └── app.js          # Lógica reactiva del cliente con analíticas
├── app.py                  # Servidor FastAPI principal y endpoints de redirección
├── run.py                  # Lanzador local con auto-detección de entorno virtual y puertos
├── run.bat                 # Lanzador rápido con doble clic para Windows
├── supabase_schema.sql     # Script SQL para inicializar Supabase en 1 clic
├── vercel.json             # Archivo de configuración de despliegue en Vercel
├── DOCUMENTACION.md        # Documentación técnica completa
├── .env.example            # Plantilla de variables de entorno
└── requirements.txt        # Dependencias de Python
```

---

## 🚀 Guía de Despliegue en Vercel con Supabase

### Paso 1: Configurar Supabase (100% Gratuito)
1. Crea una cuenta gratuita en [supabase.com](https://supabase.com) y crea un nuevo proyecto.
2. Ve a la pestaña **SQL Editor** en el panel de Supabase.
3. Abre el archivo [supabase_schema.sql](supabase_schema.sql) de este repositorio, copia su contenido, pégalo en el editor y haz clic en **Run**.
4. En **Project Settings -> API**, copia:
   - **Project URL** (`SUPABASE_URL`)
   - **anon / public key** (`SUPABASE_KEY`)

---

### Paso 2: Desplegar en Vercel en 1 Clic
1. Entra a [vercel.com](https://vercel.com) e inicia sesión con tu cuenta de GitHub.
2. Haz clic en **Add New -> Project** e importa el repositorio `FranAC18/GenerarQR`.
3. En la sección **Environment Variables**, añade:
   - `SUPABASE_URL`: `https://tu-proyecto.supabase.co`
   - `SUPABASE_KEY`: `tu_clave_anon_o_service`
   - `BASE_URL`: `https://tu-proyecto.vercel.app` (la URL que te asigna Vercel)
4. Haz clic en **Deploy**. ¡Tu generador estará en línea en segundos!

---

## 💻 Ejecución Local

### Iniciar la Aplicación Web
```bash
python run.py
```
> O haz doble clic en `run.bat` en Windows. La aplicación se abrirá automáticamente en tu navegador.

---

## 👨‍💻 Autor & Branding
Desarrollado con ❤️ por **[Kobaia Dev](https://www.instagram.com/kobaia.dev/)**.
