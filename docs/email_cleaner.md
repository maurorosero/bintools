# 📚 Email Cleaner

[⬅️ Volver al Índice Principal](/home/mrosero/bin/README.md)

## Descripción

**Email Cleaner** `email_cleaner` es una herramienta avanzada de gestión de correos electrónicos que permite analizar, categorizar y organizar el contenido de tu bandeja de entrada mediante conexión IMAP. La herramienta clasifica automáticamente los correos en categorías basadas en el remitente, asunto y fecha, generando reportes e incluso permitiendo la eliminación selectiva de correos.

## Características

- Conexión a servidores IMAP con soporte SSL
- Ambiente virtual Python automático
- Categorización automática de correos por:
  - Antigüedad (correos anteriores a 2015)
  - Tipo de remitente (newsletters, notificaciones)
  - Asunto (facturas, confirmaciones)
  - Categorías personalizables mediante archivo de configuración
- Detección de spam mediante DNSBLs y reglas tipo SpamAssassin
- Generación de reportes en formato CSV
- Interfaz de usuario con colores para mejor legibilidad
- Soporte especial para cuentas Gmail con instrucciones para contraseñas de aplicación
- Capacidad para eliminar correos por categoría (con modo "prueba" para evitar eliminaciones accidentales)
- Registro detallado de actividades (logging)
- Guardado de progreso para reanudar análisis interrumpidos
- Manejo automático de interrupciones (Ctrl+C)
- Instalación automática de dependencias
- Configuración mediante argumentos de línea de comandos o archivo JSON
- Almacenamiento centralizado de datos en ~/emails/

## Requisitos

- Python 3.6 o superior
- Paquetes principales: `imaplib`, `email` (incluidos en la biblioteca estándar)
- Paquetes opcionales: `dnspython`, `beautifulsoup4`, `html2text`, `requests` (para detección de spam)
- Entorno virtual Python (creado automáticamente si no existe)
- Acceso a servidor IMAP (Gmail, Outlook, etc.)

## Instalación

El script puede instalar automáticamente sus dependencias y crear un entorno virtual:

```bash
# Instalar dependencias necesarias
python email_cleaner.py --install
```

El script verificará si el entorno virtual existe, lo creará si es necesario, e instalará todas las dependencias requeridas. Si ya estás ejecutando el script dentro de un entorno virtual, utilizará ese entorno para instalar los paquetes.

El ambiente virtual se crea dentro del directorio `.venv` en la misma ubicación que el script.

## Configuración

La configuración se realiza de manera interactiva con un asistente:

```bash
python email_cleaner.py --config
```

Este comando te guiará por la configuración de tu cuenta de correo, creando automáticamente el archivo de configuración en `~/emails/config.json`.

También puedes especificar credenciales directamente mediante argumentos:

```bash
python email_cleaner.py --email "tu_correo@dominio.com" --password "tu_contraseña" --server "imap.tu_servidor.com"
```

### Archivo de Configuración

El archivo generado por el asistente tendrá esta estructura:

```json
{
  "email": "tu_correo@dominio.com",
  "password": "tu_contraseña",
  "server": "imap.tu_servidor.com"
}
```

El script establece automáticamente permisos restrictivos (600) para proteger tu contraseña.

### Servidores IMAP Comunes

- Gmail: `imap.gmail.com`
- Outlook: `outlook.office365.com`
- Yahoo: `imap.mail.yahoo.com`
- Hotmail: `outlook.office365.com`
- AOL: `imap.aol.com`
- iCloud: `imap.mail.me.com`

**Nota de Seguridad para Gmail**: El script detecta automáticamente cuentas de Gmail y muestra instrucciones específicas para usar contraseñas de aplicación, que son obligatorias si tienes la verificación en dos pasos activada.

## Sintaxis de Uso

```bash
# Instalar dependencias
python email_cleaner.py --install

# Uso básico (usando archivo de configuración)
python email_cleaner.py --analyze --report

# Especificar credenciales directamente
python email_cleaner.py --email "tu_correo@dominio.com" --password "tu_contraseña" --server "imap.tu_servidor.com" --analyze

# Analizar todos los correos (sin límite)
python email_cleaner.py --analyze --limit all

# Analizar los últimos N correos
python email_cleaner.py --analyze --limit 500

# Generar reporte de categorías
python email_cleaner.py --report

# Listar categorías disponibles
python email_cleaner.py --list

# Eliminar correos de una categoría (modo prueba)
python email_cleaner.py --delete "newsletter"

# Eliminar correos de una categoría (eliminación real)
python email_cleaner.py --delete "newsletter" --force

# Iniciar análisis desde cero (ignorar progreso guardado)
python email_cleaner.py --init --analyze

# Para ejecutar con permisos
chmod +x email_cleaner.py
./email_cleaner.py --analyze
```

## Flujo de Trabajo Típico

A continuación se describe un flujo de trabajo típico para usar esta herramienta:

### 1. Instalación de Dependencias

Primero, asegúrate de tener todas las dependencias necesarias:

```bash
python email_cleaner.py --install
```

### 2. Configuración

Crea un archivo de configuración en `~/Documents/emails/config.json` con tus credenciales de correo.

### 3. Análisis de Correos

Analiza los correos de tu bandeja de entrada:

```bash
python email_cleaner.py --analyze --limit 1000
```

Esto categorizará los últimos 1000 correos. El progreso se guarda automáticamente, por lo que puedes interrumpir el proceso con Ctrl+C y reanudarlo más tarde.

### 4. Revisar Categorías

Verifica qué categorías se han identificado:

```bash
python email_cleaner.py --list
```

### 5. Generar Reporte

Crea un reporte detallado en formato CSV:

```bash
python email_cleaner.py --report
```

El reporte se guardará en `~/Documents/emails/email_report.csv` e incluirá:
- Nombre de cada categoría
- Cantidad de correos en cada categoría
- Ejemplo de remitente para cada categoría

### 6. Limpieza de Correos

Para eliminar correos de una categoría específica, primero ejecuta en modo prueba:

```bash
python email_cleaner.py --delete "newsletter"
```

Cuando estés seguro de querer eliminar permanentemente los correos:

```bash
python email_cleaner.py --delete "newsletter" --force
```

**¡Advertencia!**: La eliminación es permanente. Asegúrate de revisar bien las categorías antes de usar la opción `--force`.

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

Las categorías ahora son personalizables mediante un archivo de configuración llamado `categories.dat` ubicado en `~/emails/`:

```
# Formato: categoria|palabras_clave|dominios|emails
# Ejemplo: redes_sociales|facebook,twitter,instagram|facebook.com,twitter.com|noreply@facebook.com,info@twitter.com
# Las palabras clave, dominios y emails son opcionales, separados por comas
trabajo|compañía,proyecto,tareas|miempresa.com|boss@miempresa.com,rrhh@miempresa.com
```

Cada línea define una categoría con el siguiente formato:
1. Nombre de la categoría
2. Palabras clave (separadas por comas) que se buscarán en el asunto
3. Dominios de correo (separados por comas) que identifican esta categoría
4. Direcciones de correo específicas (separadas por comas)

### Ubicación de Archivos

El script almacena todos los archivos en el directorio `~/emails/`:

- `config.json`: Configuración del usuario
- `progress.json`: Progreso del análisis para continuar sesiones interrumpidas
- `categories.dat`: Configuración de categorías personalizadas
- `spam_rules.json`: Reglas para la detección de spam
- `email_report.csv`: Informe generado de las categorías
- `email_cleaner.log`: Registros de actividad del script

### Modificar Comportamiento de Logging

El script genera logs tanto en archivo como en consola. La configuración se encuentra en las primeras líneas del script.

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

### Problemas con Privilegios de Superusuario

Si el script solicita privilegios de superusuario:
1. La instalación de dependencias puede requerir privilegios elevados
2. El script intentará escalar automáticamente con `sudo`
3. Proporciona tu contraseña cuando se solicite

### Interrupciones y Progreso

Si necesitas interrumpir el análisis:
1. Usa Ctrl+C para detener el proceso
2. El progreso se guardará automáticamente
3. La próxima vez que ejecutes el script continuará desde donde lo dejaste
4. Para comenzar un nuevo análisis desde cero, usa la opción `--init`

## Nota de Seguridad

Este script requiere acceso a tu cuenta de correo. Algunas consideraciones:

1. Nunca compartas este script con tus credenciales
2. Considera usar una contraseña de aplicación específica
3. Los archivos generados pueden contener información sensible - mantenlos seguros
4. El archivo de configuración (`config.json`) almacena tu contraseña en texto plano
5. El directorio `~/Documents/emails/` debe tener permisos restrictivos

## Opciones Adicionales

### Manejo de Dependencias

El script puede administrar automáticamente sus dependencias:

```bash
# Verificar e instalar dependencias necesarias
python email_cleaner.py --install
```

Esto verificará si todas las dependencias están instaladas y, si es necesario, instalará las faltantes usando pip.

### Ejecutar Múltiples Acciones

Puedes combinar diferentes acciones en un solo comando:

```bash
# Analizar correos y generar reporte
python email_cleaner.py --analyze --report

# Listar categorías y eliminar una específica
python email_cleaner.py --list --delete "newsletter"
```

### Documentación y Ayuda

```bash
# Ver ayuda y opciones disponibles
python email_cleaner.py --help
```
