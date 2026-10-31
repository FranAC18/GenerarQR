-- Ejecutar una sola vez en Supabase > SQL Editor para una base existente.
-- Las instalaciones nuevas ya reciben este cambio desde supabase_schema.sql.

ALTER TABLE seguridad.usuarios ADD COLUMN IF NOT EXISTS usuario_hmac TEXT;
ALTER TABLE seguridad.usuarios ADD COLUMN IF NOT EXISTS correo_hmac TEXT;
ALTER TABLE seguridad.usuarios DROP CONSTRAINT IF EXISTS usuarios_usuario_key;
ALTER TABLE seguridad.usuarios DROP CONSTRAINT IF EXISTS usuarios_correo_key;

CREATE UNIQUE INDEX IF NOT EXISTS ux_usuarios_usuario_hmac
    ON seguridad.usuarios (usuario_hmac) WHERE usuario_hmac IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_usuarios_correo_hmac
    ON seguridad.usuarios (correo_hmac) WHERE correo_hmac IS NOT NULL;

GRANT USAGE ON SCHEMA seguridad, catalogo TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON seguridad.usuarios, catalogo.tarjetas TO anon, authenticated;

NOTIFY pgrst, 'reload schema';
