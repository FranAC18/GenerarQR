-- Ejecuta estas consultas en Supabase > SQL Editor después de guardar el formulario.
-- Muestran el ciphertext completo directamente desde PostgreSQL.

-- 1. Usuario y correo cifrados en seguridad.usuarios.
SELECT
    id,
    usuario AS usuario_cifrado,
    correo AS correo_cifrado,
    usuario LIKE 'enc:v1:%' AS usuario_tiene_prefijo_cifrado,
    correo LIKE 'enc:v1:%' AS correo_tiene_prefijo_cifrado,
    creado_en
FROM seguridad.usuarios
WHERE usuario_hmac IS NOT NULL
ORDER BY creado_en DESC
LIMIT 5;

-- 2. Título y URL cifrados en catalogo.tarjetas.
SELECT
    id,
    title AS titulo_cifrado,
    url AS url_cifrada,
    title LIKE 'enc:v1:%' AS titulo_tiene_prefijo_cifrado,
    url LIKE 'enc:v1:%' AS url_tiene_prefijo_cifrado,
    creado_en
FROM catalogo.tarjetas
WHERE id LIKE 'demo-cifrado-%'
ORDER BY creado_en DESC
LIMIT 5;
