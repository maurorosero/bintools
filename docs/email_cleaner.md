# 📚 Documentación: email_cleaner

[⬅️ Volver al Índice Principal](/home/mrosero/bin/README.md)

## Descripción

`email_cleaner` es una herramienta de gestión de correos electrónicos que permite analizar, categorizar y organizar el contenido de tu bandeja de entrada mediante conexión IMAP. La herramienta clasifica automáticamente los correos en categorías basadas en el remitente, asunto y fecha, generando reportes e incluso permitiendo la eliminación selectiva de correos.

## Características

- Conexión a servidores IMAP con soporte SSL
- Categorización automática de correos por:
  - Antigüedad (correos anteriores a 2015)
  - Tipo de remitente (newsletters, notificaciones)
  - Asunto (facturas, confirmaciones)
- Generación de reportes en formato CSV
- Capacidad para eliminar correos por categoría (con modo "prueba" para evitar eliminaciones accidentales)
- Registro detallado de actividades (logging)

## Requisitos

- Python 3.6 o superior
- Paquetes: `imaplib`, `email`, `pandas`, `json`, `logging`
- Acceso a servidor IMAP (Gmail, Outlook, etc.)

## Instalación

1. Asegúrate de tener instalado Python 3.6+
2. Instala las dependencias requeridas:

```bash
pip install pandas
```

Los demás paquetes son parte de la biblioteca estándar de Python.

## Configuración

Antes de ejecutar el script, debes configurar tus credenciales de correo electrónico:

1. Abre el archivo `email_cleaner.py`
2. Localiza la sección de configuración (alrededor de la línea 179)
3. Reemplaza los siguientes valores:
   - `EMAIL_ADDRESS`: Tu dirección de correo electrónico
   - `PASSWORD`: Tu contraseña (o contraseña de aplicación si usas 2FA)
   - `IMAP_SERVER`: El servidor IMAP de tu proveedor de correo
     - Gmail: `imap.gmail.com`
     - Outlook: `outlook.office365.com`
     - Yahoo: `imap.mail.yahoo.com`

**Nota de Seguridad**: Se recomienda usar contraseñas de aplicación específicas en lugar de la contraseña principal de tu cuenta.

## Sintaxis de Uso

```bash
# Uso básico
python email_cleaner.py

# Para ejecutar con permisos
chmod +x email_cleaner.py
./email_cleaner.py
```

## Ejemplos de Uso

### Análisis Básico de Correos

El script, por defecto, analizará los últimos 1000 correos de tu bandeja de entrada:

```python
manager.analyze_emails(limit=1000)
```

Puedes modificar este límite o eliminarlo para analizar todos los correos.

### Generación de Reportes

Después del análisis, se genera automáticamente un reporte en formato CSV:

```python
manager.generate_report()
```

Este reporte incluirá:
- Nombre de cada categoría
- Cantidad de correos en cada categoría
- Ejemplo de remitente para cada categoría

### Eliminación de Correos por Categoría

Para eliminar correos de una categoría específica (por ejemplo, "newsletter"):

```python
# Modo prueba (no elimina realmente)
manager.delete_emails_by_category("newsletter", dry_run=True)

# Eliminación real
manager.delete_emails_by_category("newsletter", dry_run=False)
```

**¡Advertencia!**: Solo usa `dry_run=False` cuando estés seguro de querer eliminar permanentemente estos correos.

## Categorías Predefinidas

El script actualmente reconoce las siguientes categorías:

| Categoría | Criterio de Clasificación |
|-----------|---------------------------|
| `antiguo` | Correos anteriores a 2015 |
| `newsletter` | Remitente contiene "newsletter" o "marketing" |
| `notificaciones` | Remitente contiene "notification" o "alert" |
| `facturas` | Asunto contiene "factura" o "invoice" |
| `confirmaciones` | Asunto contiene "confirmación" o "confirmation" |

## Extensión y Personalización

### Agregar Nuevas Categorías

Para añadir nuevas categorías, modifica la función `get_email_categories` en la clase `EmailManager`:

```python
# Ejemplo: Agregar categoría para correos de redes sociales
if 'facebook' in from_addr or 'twitter' in from_addr or 'instagram' in from_addr:
    categories.append("redes_sociales")
```

### Modificar Comportamiento de Logging

El script genera logs tanto en archivo como en consola. Puedes modificar la configuración en las líneas 14-21.

## Solución de Problemas

### Errores de Autenticación

Si recibes errores al conectar:
1. Verifica tus credenciales
2. Para Gmail: activa "Acceso de aplicaciones menos seguras" o usa una contraseña de aplicación
3. Asegúrate de que tu servidor IMAP es correcto

### Problemas con la Categorización

Si los correos no se categorizan como esperas:
1. Verifica los patrones de búsqueda en `get_email_categories`
2. Considera que algunas fechas de correo pueden estar en formatos diferentes

## Nota de Seguridad

Este script requiere acceso a tu cuenta de correo. Algunas consideraciones:

1. Nunca compartas este script con tus credenciales
2. Considera usar una contraseña de aplicación específica
3. Los archivos generados pueden contener información sensible - mantenlos seguros