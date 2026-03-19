# Descripción del proyecto
Este proyecto permite generar y mostrar un código QR enlazando a un link de una página web.
## Características principales

- Generación de un código QR 
- Configuración mediante `config.json` donde se almacenan los links de las páginas web.
- Genera un archivo SVG y PNG del código QR.
- Dependencias listadas en `requirements.txt` para una instalación rápida.

## Estructura del proyecto

```
scriptQr/
├─ main.py          # Archivo principal que genera y muestra el QR
├─ config.json      # Configuración de la tarjeta digital
├─ requirements.txt # Lista de paquetes Python necesarios
└─ README.md        # Descripción del proyecto (este archivo)
```

## Tecnologías utilizadas

- **Python**: lenguaje de programación principal.
- **qrcode**: biblioteca para generar códigos QR.
- **Pillow**: para manipular imágenes del QR.

## Instalación

Se recomienda crear un entorno virtual para instalar las dependencias.
Los comandos son:

Para activar el entorno virtual:
```bash
python -m venv .venv
.\.venv\Scripts\Activate
```
Luego de activar el entorno virtual, se deben instalar las dependencias:

1. Clonar el repositorio o copiar los archivos del proyecto.
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configurar `config.json` con los datos de la tarjeta.
4. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## Uso

Al ejecutar `main.py`, se generará un código QR basado en la información del `config.json` 

---

