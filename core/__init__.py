"""
Módulo Core del Generador QR.
Provee utilidades avanzadas para renderizado PNG/SVG, inserción de logotipos,
y formateo de contenidos de tarjetas digitales (vCard, WhatsApp, WiFi, etc.).
"""

from .qr_engine import QREngine

__all__ = ["QREngine"]
