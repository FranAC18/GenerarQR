# Guion para el video: HMAC de usuario y cifrado del correo

**Duración objetivo:** 2:30–3:00 minutos (máximo: 5 minutos).

## Antes de grabar

1. Publica la última versión de la app en `https://qr-kobaia.vercel.app` y confirma que la pestaña **Cifrado** está disponible.
2. En la app, verifica que Supabase aparece conectado y que la clave de cifrado está configurada.
3. Abre `ENCRIPTACION_DEMO.sql` en Supabase SQL Editor y deja listas las dos consultas.
4. Prepara datos completamente ficticios y únicos: usuario `demo_estudiante_01`, correo `estudiante.demo@example.com`, título `Tarjeta demo` y URL `https://example.com/demo`.
5. En OBS, Teams u otra grabadora, coloca tu rostro en una esquina y mantenlo visible durante todo el video. Evita mostrar claves o datos personales reales.

## Guion y demostración

### 0:00–0:20 | Presentación

**Mostrar:** la app, tu rostro en una esquina y la pestaña **Cifrado**.

**Decir:**

> “Hola. En esta demostración voy a guardar datos ficticios desde el formulario de Kobaia QR y comprobaré directamente en Supabase cómo quedan almacenados.”

### 0:20–0:55 | Ingreso desde el formulario

**Mostrar:** completa los cuatro campos y pulsa **Guardar demostración**. Espera el mensaje de éxito y señala el ID de la tarjeta.

**Decir:**

> “El nombre de usuario se transforma en un HMAC-SHA-256 de una sola vía. El correo se cifra con AES-256-GCM, que solo puede descifrarse con la clave privada del servidor. El título y la URL de la tarjeta se guardan legibles.”

### 0:55–1:50 | Evidencia SQL del usuario y correo

**Mostrar:** en Supabase SQL Editor ejecuta la primera consulta de `ENCRIPTACION_DEMO.sql`.

**Decir:**

> “Esta consulta lee `seguridad.usuarios` directamente desde PostgreSQL. La columna `usuario_hmac_sha256` muestra el resumen HMAC de 64 caracteres hexadecimales; el usuario original no se almacena. La columna `correo_cifrado` empieza con `enc:v1:`, que identifica el valor cifrado. El formulario recibió ambos datos como texto normal.”

Deja visibles `usuario_hmac_sha256`, `correo_cifrado` y las columnas de comprobación.

### 1:50–2:25 | Evidencia SQL de la segunda tabla

**Mostrar:** ejecuta la segunda consulta.

**Decir:**

> “Esta segunda consulta muestra el registro creado en `catalogo.tarjetas`. El título y la URL se ven directamente porque esos campos no se cifran en esta implementación.”

### 2:25–2:45 | Cierre

**Mostrar:** los resultados SQL y tu rostro.

**Decir:**

> “Queda comprobado que el usuario se almacena como un HMAC irreversible y el correo como ciphertext AES-256-GCM. Los datos de la tarjeta permanecen legibles. Gracias.”

## Al terminar

- Confirma que el video dure menos de cinco minutos y que tu rostro aparezca en una esquina durante toda la grabación.
- Sube el video a la plataforma de la clase y copia el enlace para entregar la actividad.
