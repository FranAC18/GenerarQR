-- ============================================================================
-- QR DIGITAL STUDIO - ESQUEMA DE BASE DE DATOS Y STORAGE PARA SUPABASE
-- ============================================================================
-- Copia y pega este script completo en el SQL Editor de tu proyecto Supabase.
-- Dashboard -> SQL Editor -> New Query -> Run

-- 1. CREACIÓN DE LA TABLA 'tarjetas'
CREATE TABLE IF NOT EXISTS public.tarjetas (
    id TEXT PRIMARY KEY,                       -- Slug único (ej: 'macrojaguar', 'fredyurquizo')
    title TEXT NOT NULL,                      -- Título visible de la tarjeta
    url TEXT NOT NULL,                        -- URL o payload de destino
    content_type TEXT DEFAULT 'url',          -- 'url', 'vcard', 'whatsapp', 'wifi', 'text'
    logo_url TEXT,                            -- URL pública del logotipo en Supabase Storage
    style_config JSONB DEFAULT '{}'::jsonb,   -- fill_color, back_color, logo_size_ratio, etc.
    vcard_data JSONB,                         -- Datos estructurados si es vCard
    whatsapp_data JSONB,                      -- Datos de WhatsApp (phone, message)
    wifi_data JSONB,                          -- Datos de red WiFi (ssid, pass, auth)
    is_dynamic BOOLEAN DEFAULT false,         -- True si el QR apunta al enlace de redirección /c/{id}
    scan_count INTEGER DEFAULT 0,             -- Contador de escaneos en tiempo real
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Habilitar Row Level Security (RLS)
ALTER TABLE public.tarjetas ENABLE ROW LEVEL SECURITY;

-- Políticas de acceso público (Lectura y Escritura anónima o autenticada)
CREATE POLICY "Permitir lectura publica de tarjetas"
ON public.tarjetas FOR SELECT
USING (true);

CREATE POLICY "Permitir insercion y actualizacion publica de tarjetas"
ON public.tarjetas FOR ALL
USING (true)
WITH CHECK (true);

-- 2. CREACIÓN DEL BUCKET DE STORAGE PARA LOGOTIPOS
INSERT INTO storage.buckets (id, name, public)
VALUES ('qr-logos', 'qr-logos', true)
ON CONFLICT (id) DO NOTHING;

-- Políticas de Storage para el bucket 'qr-logos'
CREATE POLICY "Logos acceso publico"
ON storage.objects FOR SELECT
USING (bucket_id = 'qr-logos');

CREATE POLICY "Logos subida publica"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'qr-logos');

CREATE POLICY "Logos actualizacion publica"
ON storage.objects FOR UPDATE
USING (bucket_id = 'qr-logos');

CREATE POLICY "Logos eliminacion publica"
ON storage.objects FOR DELETE
USING (bucket_id = 'qr-logos');

-- 3. DATOS INICIALES (MIGRACIÓN DESDE CONFIG.JSON)
INSERT INTO public.tarjetas (id, title, url, logo_url, is_dynamic, style_config)
VALUES 
    (
        'kobaia', 
        'Kobaia Dev', 
        'https://www.instagram.com/kobaia.dev/', 
        'img/kobaia.png',
        true,
        '{"fill_color": "#000000", "back_color": "#FFFFFF", "logo_size_ratio": 0.22, "border": 4}'::jsonb
    )
ON CONFLICT (id) DO UPDATE 
SET 
    url = EXCLUDED.url,
    title = EXCLUDED.title,
    logo_url = EXCLUDED.logo_url;
