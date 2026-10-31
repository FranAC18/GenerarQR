-- Ejecuta estas consultas en Supabase > SQL Editor después de enviar el formulario.
-- Las columnas usuario, correo, title y url deben empezar con enc:v1:.
SELECT id, usuario, correo
FROM seguridad.usuarios
WHERE usuario_hmac IS NOT NULL
ORDER BY creado_en DESC
LIMIT 5;

SELECT id, title, url
FROM catalogo.tarjetas
WHERE id LIKE 'demo-cifrado-%'
ORDER BY creado_en DESC
LIMIT 5;
