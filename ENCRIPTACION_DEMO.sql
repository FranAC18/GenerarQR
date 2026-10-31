-- Ejecuta estas consultas en Supabase > SQL Editor después de guardar el formulario.
-- Muestran el HMAC del usuario, el ciphertext del correo y los datos legibles
-- del catálogo directamente desde PostgreSQL.

-- 1. Solo el usuario usa HMAC y el correo queda cifrado en seguridad.usuarios.
SELECT
    id,
    usuario_hmac AS usuario_hmac_sha256,
    correo AS correo_cifrado,
    usuario IS NULL AS usuario_original_no_guardado,
    usuario_hmac ~ '^[0-9a-f]{64}$' AS usuario_es_hmac_sha256,
    correo LIKE 'enc:v1:%' AS correo_tiene_prefijo_cifrado,
    creado_en
FROM seguridad.usuarios
WHERE usuario_hmac IS NOT NULL AND usuario IS NULL
ORDER BY creado_en DESC
LIMIT 5;

-- 2. Título y URL legibles en catalogo.tarjetas.
SELECT
    id,
    title AS titulo_legible,
    url AS url_legible,
    title NOT LIKE 'enc:v1:%' AS titulo_esta_legible,
    url NOT LIKE 'enc:v1:%' AS url_esta_legible,
    creado_en
FROM catalogo.tarjetas
WHERE id LIKE 'demo-cifrado-%'
ORDER BY creado_en DESC
LIMIT 5;
