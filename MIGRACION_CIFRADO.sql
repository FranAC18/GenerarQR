-- Ejecutar una sola vez en Supabase > SQL Editor para una base existente.
-- Las instalaciones nuevas ya reciben este cambio desde supabase_schema.sql.

ALTER TABLE seguridad.usuarios ADD COLUMN IF NOT EXISTS usuario_hmac TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS ux_usuarios_usuario_hmac
    ON seguridad.usuarios (usuario_hmac) WHERE usuario_hmac IS NOT NULL;

-- El usuario queda solo como HMAC; el correo permanece cifrado con AES-256-GCM.
ALTER TABLE seguridad.usuarios ALTER COLUMN usuario DROP NOT NULL;

-- El formulario solo inserta el HMAC del usuario y el correo cifrado; no lee filas.
ALTER TABLE seguridad.usuarios ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS api_usuarios ON seguridad.usuarios;
DROP POLICY IF EXISTS api_usuarios_insert ON seguridad.usuarios;
CREATE POLICY api_usuarios_insert ON seguridad.usuarios
    FOR INSERT TO anon, authenticated WITH CHECK (true);
REVOKE SELECT, UPDATE, DELETE ON TABLE seguridad.usuarios FROM anon, authenticated;
GRANT INSERT ON TABLE seguridad.usuarios TO anon, authenticated;

GRANT USAGE ON SCHEMA seguridad, catalogo TO anon, authenticated;

NOTIFY pgrst, 'reload schema';
