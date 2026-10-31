# Segmentación de la base de datos

## Propósito

La base de datos de Kobaia QR se divide por módulos funcionales. Cada módulo
tiene un esquema propio para separar responsabilidades, facilitar permisos y
permitir que la auditoría identifique con claridad el origen de cada operación.

| Esquema | Módulo | Tabla principal | Responsabilidad |
| --- | --- | --- | --- |
| `seguridad` | Usuarios y roles | `usuarios` | Identidades, rol y estado de acceso. |
| `catalogo` | Gestión de tarjetas | `tarjetas` | URL, contenido, diseño y estado de cada tarjeta QR. |
| `analitica` | Métricas | `escaneos` | Registro detallado de cada escaneo, fecha, IP y dispositivo. |
| `auditoria` | Trazabilidad | `try`, `catch` | Operaciones confirmadas y operaciones fallidas. |
| Storage | Archivos | `storage.objects` | Logotipos asociados a las tarjetas. |

## Auditoría

La tabla `auditoria."try"` guarda las operaciones que terminaron correctamente.
La tabla `auditoria."catch"` guarda los errores capturados por la API. Ambas
incluyen como mínimo `id`, `usuario`, `fecha`, `hora` y `accion_realizada`, y
además registran módulo, esquema, tabla, operación, registro afectado, IP,
agente de usuario, identificador de solicitud y datos JSON anteriores/nuevos
cuando están disponibles.

Los triggers de PostgreSQL registran automáticamente los `INSERT`, `UPDATE` y
`DELETE` confirmados sobre `seguridad.usuarios`, `catalogo.tarjetas` y
`analitica.escaneos`. Los errores ocurridos en la API se registran mediante el
manejador `catch` del gestor de base de datos.

## Puesta en marcha

1. Ejecutar `supabase_schema.sql` en el SQL Editor de Supabase.
2. En Supabase, agregar `seguridad`, `catalogo`, `analitica` y `auditoria` a
   los esquemas expuestos por la API REST.
3. Configurar `SUPABASE_URL` y `SUPABASE_KEY` en `.env` o en las variables de
   entorno del despliegue.
4. Probar el alta, modificación, eliminación y escaneo de una tarjeta.
5. Verificar los resultados con:

```sql
SELECT * FROM auditoria."try" ORDER BY fecha_hora DESC;
SELECT * FROM auditoria."catch" ORDER BY fecha_hora DESC;
SELECT * FROM analitica.escaneos ORDER BY fecha_hora DESC;
```

Las políticas incluidas conservan el comportamiento actual de la aplicación.
Para producción se recomienda reemplazarlas por políticas basadas en
`auth.uid()` y en el rol de `seguridad.usuarios`.
