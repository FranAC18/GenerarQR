# Guion del video: cifrado de datos en dos tablas

**Duración objetivo:** 3:30–4:00 minutos (máximo permitido: 5 minutos).

## Antes de grabar

1. La aplicación desplegada ya está conectada a Supabase. Publica esta versión del repositorio para que aparezca la pestaña **Cifrado**.
2. En las variables de entorno de Vercel, agrega `FIELD_ENCRYPTION_KEY`. Genera una clave nueva de 32 bytes con este comando:

   ```powershell
   python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
   ```

   Conserva la clave en Vercel y no la muestres ni la publiques. No cambies las variables `SUPABASE_URL` ni `SUPABASE_KEY` existentes. Después de agregar la clave, vuelve a desplegar.

3. Como la base de datos ya existe, ejecuta una vez `MIGRACION_CIFRADO.sql` en Supabase SQL Editor. Confirma que `seguridad` y `catalogo` estén entre los esquemas expuestos en la configuración de la API de Supabase.
4. Abre `https://qr-kobaia.vercel.app/api/status` y confirma `mode: supabase`, `connected: true` y `encryption_ready: true`. Luego abre la app y comprueba que la pestaña **Cifrado** esté habilitada.
5. Si vas a grabar desde una copia local, instala dependencias con `pip install -r requirements.txt` y añade al `.env` local las variables `SUPABASE_URL`, `SUPABASE_KEY` ya existentes en Vercel y la misma `FIELD_ENCRYPTION_KEY`.
6. Prepara valores ficticios y únicos para que no choque con una grabación previa:
   - Usuario: `demo_estudiante_01`
   - Correo: `estudiante.demo@example.com`
   - Título: `Tarjeta privada de demostración`
   - URL: `https://example.com/demo-cifrado`
7. Abre `ENCRIPTACION_DEMO.sql` en una pestaña lista para ejecutarse después de enviar el formulario.
8. Abre OBS, Teams o una grabadora con cámara. Deja tu rostro visible en una esquina durante toda la captura; ubica la cámara donde no tape los campos ni los resultados SQL. Cierra ventanas con claves, correo real o notificaciones.

## Guion y demostración

### 0:00–0:20 | Presentación

**Mostrar:** la aplicación y tu cámara en una esquina.

**Decir:**

> “Hola, voy a demostrar el cifrado de campos en mi sistema Kobaia QR. Voy a ingresar datos ficticios desde el formulario y después consultar directamente las dos tablas con SQL para comprobar que la base no los recibe en texto claro.”

### 0:20–1:05 | Ingresar los datos por el formulario

**Mostrar:** pestaña **Cifrado**. Completa los cuatro campos con los datos de prueba preparados y pulsa **Guardar datos cifrados**. Señala el ID que la app genera en el mensaje de confirmación.

**Decir:**

> “El formulario guarda el usuario y el correo en `seguridad.usuarios`. También guarda el título y la URL de una tarjeta en `catalogo.tarjetas`. Los datos se cifran en el servidor antes de enviarse a Supabase.”

Espera el mensaje de confirmación antes de cambiar de ventana.

### 1:05–1:25 | Método de cifrado

**Mostrar:** el mensaje de éxito y la etiqueta **AES-256-GCM**.

**Decir:**

> “Se utiliza AES-256-GCM, un cifrado autenticado de doble vía. La clave está configurada como variable de entorno del servidor y no se envía al navegador ni se guarda en la base de datos. La aplicación descifra estos campos al volver a leer una tarjeta.”

### 1:25–2:40 | Consulta directa de usuarios

**Mostrar:** Supabase SQL Editor. Ejecuta la primera consulta de `ENCRIPTACION_DEMO.sql`.

**Decir:**

> “Esta consulta lee directamente `seguridad.usuarios`. Aunque ingresé el usuario y el correo como texto normal en el formulario, aquí las dos columnas aparecen con el prefijo `enc:v1:` seguido de texto cifrado.”

Deja visibles las columnas `usuario` y `correo` en el resultado.

### 2:40–3:25 | Consulta directa de tarjetas

**Mostrar:** ejecuta la segunda consulta del mismo archivo.

**Decir:**

> “Ahora consulto directamente `catalogo.tarjetas`. El título y la URL también aparecen cifrados. Así queda comprobado el almacenamiento de cuatro campos sensibles repartidos en dos tablas.”

### 3:25–3:50 | Cierre

**Mostrar:** resultados SQL y rostro todavía visible.

**Decir:**

> “En resumen, el dato entra desde el formulario, el servidor aplica AES-256-GCM y PostgreSQL conserva el ciphertext. Las consultas SQL confirman el cifrado en `seguridad.usuarios` y `catalogo.tarjetas`. Gracias.”

## Al terminar

- Revisa que el video dure menos de cinco minutos y que tu rostro haya estado visible en una esquina durante toda la demostración.
- Sube el video a la plataforma indicada por la clase, con acceso para quien lo califique.
- Copia aquí el enlace final para entregar la actividad: **[PEGAR AQUÍ EL ENLACE DEL VIDEO]**.
