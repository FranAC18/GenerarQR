# Guion exacto del video: segmentación de la base de datos

Duración: aproximadamente 3 minutos.

## Preparación antes de grabar

1. Abre el proyecto de Supabase:
   `https://supabase.com/dashboard/project/cfxvksrvnvymckimxlup`.
2. Entra a **Database > Schema Visualizer**. La pantalla inicialmente mostrará
   el selector `schema public` y la tabla `public.tarjetas`.
3. Deja preparada esta consulta en **SQL Editor**:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('seguridad', 'catalogo', 'analitica', 'auditoria')
ORDER BY table_schema, table_name;
```

4. Abre también **Table Editor** para mostrar las tablas de cada esquema.
5. Ten abierta en otra pestaña la aplicación:
   `https://qr-kobaia.vercel.app/`.
6. No es necesario insertar datos de prueba. Explica que una tabla puede estar
   vacía y aun así estar correctamente creada.

## 0:00 - 0:20 | Presentación

### Qué mostrar

Muestra la aplicación Kobaia QR y luego cambia a Supabase.

### Qué decir

“En este video voy a mostrar la segmentación de la base de datos del sistema
Kobaia QR. La aplicación permite crear tarjetas digitales, generar códigos QR,
registrar escaneos y conservar una auditoría de las operaciones realizadas.”

## 0:20 - 0:45 | Diferencia entre public y la segmentación nueva

### Qué hacer

Comienza en **Schema Visualizer** con el selector `schema public`. Muestra la
tabla `public.tarjetas` de la captura. Después, abre el selector y muestra que
puedes cambiar a `catalogo`, `seguridad`, `analitica` y `auditoria`.

Luego entra a **SQL Editor**, pega la consulta preparada y pulsa **Run**.
Muestra el resultado con estas cinco filas:

```text
analitica   escaneos
auditoria   catch
auditoria   try
catalogo    tarjetas
seguridad   usuarios
```

### Qué decir

“Inicialmente Supabase muestra el esquema `public`, donde aparece
`public.tarjetas`. Esta es la tabla anterior y se conserva por compatibilidad.
La segmentación nueva no está dentro de `public`; está separada en los
esquemas `seguridad`, `catalogo`, `analitica` y `auditoria`. Por eso debo
cambiar el esquema desde este selector.”

“Esta consulta confirma que no existe solamente una tabla: hay cinco tablas
distribuidas en cuatro esquemas.”

## 0:45 - 1:15 | Esquema seguridad

### Qué hacer

En el selector de esquema, cambia de `public` a `seguridad`. Abre la tabla
`usuarios`. Muestra sus columnas: `id`, `usuario`, `correo`, `rol`, `activo`,
`creado_en` y `actualizado_en`.

### Qué decir

“El esquema `seguridad` pertenece al módulo de usuarios y roles. La tabla
`usuarios` ya está creada aunque actualmente no tenga registros, porque la
versión actual de la aplicación todavía no incluye inicio de sesión. La
estructura está preparada para almacenar administradores, operadores y
auditores.”

## 1:15 - 1:45 | Esquema catalogo

### Qué hacer

En el selector, cambia a `catalogo` y abre `tarjetas`. Muestra algunos registros
y las columnas principales: identificador, título, URL, tipo de contenido,
configuración visual, estado dinámico y contador de escaneos.

### Qué decir

“El esquema `catalogo` contiene la información principal del sistema. Aquí se
guardan las tarjetas digitales. Cada registro contiene su URL, tipo de
contenido, logotipo, configuración visual, indicador de QR dinámico y cantidad
de escaneos. En esta base ya existen cuatro tarjetas migradas.”

## 1:45 - 2:10 | Esquema analitica

### Qué hacer

En el selector, cambia a `analitica` y abre `escaneos`. Muestra las columnas `tarjeta_id`,
`fecha_hora`, `ip`, `user_agent`, `referer`, `dispositivo` y `resultado`.

### Qué decir

“El esquema `analitica` registra el detalle de cada escaneo. La tabla se
relaciona con `catalogo.tarjetas` mediante `tarjeta_id`. También permite
guardar fecha, hora, IP, navegador, dispositivo y resultado de la operación.
Actualmente está vacía porque todavía no se ha registrado un nuevo escaneo en
la tabla segmentada.”

## 2:10 - 2:45 | Esquema auditoria

### Qué hacer

En el selector, cambia a `auditoria` y muestra las dos tablas: `try` y `catch`. Abre cada una
y enseña sus columnas principales.

### Qué decir

“El esquema `auditoria` contiene las dos tablas solicitadas. `try` registra las
operaciones confirmadas y `catch` registra las operaciones que fallan o generan
una excepción. Ambas tienen los campos mínimos solicitados: `id`, `usuario`,
`fecha`, `hora` y `accion_realizada`. Además, guardan módulo, esquema, tabla,
operación, registro afectado, IP, agente de usuario, código de error y detalle
de la operación.”

## 2:45 - 3:00 | Triggers y cierre

### Qué hacer

En **SQL Editor**, ejecuta:

```sql
SELECT * FROM auditoria."try" ORDER BY fecha_hora DESC;
SELECT * FROM auditoria."catch" ORDER BY fecha_hora DESC;
```

Muestra que `try` tiene al menos un registro y que `catch` puede estar vacío
mientras no hayan ocurrido errores.

### Qué decir

“Finalmente, los triggers registran automáticamente los cambios realizados en
usuarios, tarjetas y escaneos. Por eso la base queda organizada por módulos y
también conserva la trazabilidad de las operaciones exitosas y fallidas. Con
esta estructura se cumple la segmentación solicitada y la auditoría queda
preparada para futuras operaciones del sistema.”

## Qué debes mostrar exactamente en el selector

Haz esta secuencia visible durante la grabación:

```text
schema public     -> public.tarjetas (tabla anterior)
schema seguridad  -> usuarios
schema catalogo   -> tarjetas
schema analitica  -> escaneos
schema auditoria  -> try y catch
```

## Frase clave si preguntan por las tablas vacías

“Una tabla vacía no significa que falte. La tabla ya existe con sus columnas,
restricciones y relaciones; simplemente todavía no tiene movimientos
registrados.”
