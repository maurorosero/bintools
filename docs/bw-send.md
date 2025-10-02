# bw-send.sh - Guía Completa de Envío Seguro Extendido

> **📖 [← Volver al README principal](../README.md)**

## Descripción

**bw-send.sh** es un script wrapper desarrollado para extender las capacidades de envío seguro de Bitwarden CLI, proporcionando múltiples canales de distribución para secretos y archivos sensibles. No se limita solo a URLs temporales, sino que permite el envío directo a través de Telegram, email, WhatsApp (en desarrollo) y otros canales.

## ¿Qué es bw-send.sh?

`bw-send.sh` es una herramienta que actúa como wrapper del comando nativo `bw send` de Bitwarden CLI, añadiendo funcionalidades extendidas para la distribución de contenido seguro a través de múltiples canales de comunicación.

### Características Principales

- 🔐 **Encriptación automática**: Usa Bitwarden Send para encriptar contenido
- 📱 **Múltiples canales**: Telegram, email, WhatsApp (en desarrollo)
- ⏰ **Expiración configurable**: Control temporal del acceso
- 🔒 **Protección por contraseña**: Seguridad adicional opcional
- 📊 **Límite de accesos**: Control de número de visualizaciones
- 🖥️ **Integración CLI**: Fácil uso desde línea de comandos

## Instalación y Requisitos

### Requisitos Previos

```bash
# Instalar Bitwarden CLI
./packages.sh --list bwdn

# O instalar manualmente
sudo snap install bw

# Para envío por email, instalar dependencias
./packages.sh --list base  # Python3 y PyYAML
./mozilla-sops.sh --install  # SOPS para configuración encriptada
```

### Configuración Inicial

```bash
# Configurar Bitwarden CLI
bw login
bw unlock

# Verificar instalación
bw status
```

### Verificar bw-send.sh

```bash
# Verificar que el script está disponible
ls -la bw-send.sh

# Dar permisos de ejecución si es necesario
chmod +x bw-send.sh
```

## Uso Básico

### Sintaxis General

```bash
./bw-send.sh [OPCIONES] [CONTENIDO]
```

### Comandos Principales

```bash
# Ver ayuda completa
./bw-send.sh --help

# Enviar texto simple
./bw-send.sh --text "Información confidencial"

# Enviar archivo
./bw-send.sh --file documento.pdf

# Enviar con configuración personalizada
./bw-send.sh --text "Datos sensibles" --expiration 7 --password "secret123"
```

## Opciones Disponibles

### Opciones de Contenido

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--text` | Texto a enviar | `--text "Mi mensaje"` |
| `--file` | Archivo(s) a enviar | `--file doc.pdf` |
| `--file` | Múltiples archivos | `--file archivo1.txt archivo2.pdf` |

### Opciones de Seguridad

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--password` | Contraseña para proteger | `--password "secret"` |
| `--expiration` | Días hasta expiración | `--expiration 7` |
| `--max-access` | Máximo número de accesos | `--max-access 5` |

### Opciones de Configuración

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--notes` | Notas descriptivas | `--notes "Para proyecto X"` |
| `--console` | Salida por consola (por defecto) | `--console` |
| `--email` | Enviar por email | `--email usuario@ejemplo.com` |
| `--telegram` | Enviar por Telegram | `--telegram @usuario` |

## Canales de Envío

### 1. Consola (Por Defecto)

```bash
# Envío básico por consola
./bw-send.sh --text "Información confidencial"

# Con configuración avanzada
./bw-send.sh --text "Datos sensibles" --expiration 3 --password "secret" --max-access 2
```

### 2. Telegram

```bash
# Enviar a Telegram (requiere configuración previa)
./bw-send.sh --text "Información" --telegram @usuario

# Con archivo adjunto
./bw-send.sh --file documento.pdf --telegram @usuario --expiration 1
```

**Configuración de Telegram:**

```bash
# Configurar bot de Telegram
export TELEGRAM_BOT_TOKEN="tu-bot-token"
export TELEGRAM_CHAT_ID="tu-chat-id"

# O usar archivo de configuración
echo 'TELEGRAM_BOT_TOKEN="tu-bot-token"' >> ~/.bw-send.conf
echo 'TELEGRAM_CHAT_ID="tu-chat-id"' >> ~/.bw-send.conf
```

### 3. Email

```bash
# Enviar por email
./bw-send.sh --text "Información confidencial" --email usuario@ejemplo.com

# Con archivo adjunto
./bw-send.sh --file documento.pdf --email usuario@ejemplo.com

# Múltiples destinatarios
./bw-send.sh --text "Información confidencial" --email usuario1@ejemplo.com,usuario2@ejemplo.com
```

**Configuración de Email:**

El envío por email requiere configuración SMTP usando `mail-config.py`:

```bash
# Configurar SMTP con mail-config.py
./mail-config.py --interactive

# O configuración automática
./mail-config.py --provider gmail --username tu-email@gmail.com
```

**Requisitos para Email:**

- `mail-config.py` configurado con SMTP
- Archivo de configuración en `~/secure/sops/mail/mail-config.yml`
- Plantilla de email en `~/secure/mail/email.bw.template` (opcional)

### 4. WhatsApp (En Desarrollo)

```bash
# WhatsApp (próximamente disponible)
./bw-send.sh --text "Información" --whatsapp +1234567890
```

## Ejemplos de Uso Avanzado

### Envío de Credenciales

```bash
# Enviar credenciales de base de datos
./bw-send.sh --text "DB_HOST=localhost
DB_USER=admin
DB_PASSWORD=secret123
DB_NAME=mi_proyecto" --expiration 1 --max-access 1 --notes "Credenciales DB - Proyecto X"
```

### Envío de Tokens de API

```bash
# Enviar token de API con expiración corta
./bw-send.sh --text "ghp_xxxxxxxxxxxxxxxxxxxx" --expiration 1 --password "api-token-2024" --notes "GitHub Token - Desarrollo"
```

### Envío de Archivos Sensibles

```bash
# Enviar múltiples archivos con protección
./bw-send.sh --file config.json keys.pem --password "proyecto-secreto" --expiration 7 --max-access 3
```

### Envío Automatizado

```bash
#!/bin/bash
# Script para envío automático de logs

LOG_FILE="/tmp/error.log"
if [ -f "$LOG_FILE" ]; then
    ./bw-send.sh --file "$LOG_FILE" --expiration 1 --notes "Log de errores - $(date)" --telegram @admin
fi
```

## Configuración Avanzada

### Archivo de Configuración

```bash
# Crear archivo de configuración
cat > ~/.bw-send.conf << EOF
# Configuración de Telegram
TELEGRAM_BOT_TOKEN="tu-bot-token"
TELEGRAM_CHAT_ID="tu-chat-id"

# Configuración de Email
EMAIL_SMTP_SERVER="smtp.gmail.com"
EMAIL_SMTP_PORT="587"
EMAIL_USERNAME="tu-email@gmail.com"
EMAIL_PASSWORD="tu-contraseña-app"

# Configuración por defecto
DEFAULT_EXPIRATION=2
DEFAULT_MAX_ACCESS=10
DEFAULT_NOTES="Enviado con bw-send.sh"
EOF
```

### Variables de Entorno

```bash
# Configurar variables de entorno
export BW_SEND_DEFAULT_EXPIRATION=3
export BW_SEND_DEFAULT_MAX_ACCESS=5
export BW_SEND_DEFAULT_PASSWORD=""

# Agregar a ~/.bashrc o ~/.zshrc
echo 'export BW_SEND_DEFAULT_EXPIRATION=3' >> ~/.bashrc
echo 'export BW_SEND_DEFAULT_MAX_ACCESS=5' >> ~/.bashrc
```

### Aliases Útiles

```bash
# Crear aliases para uso frecuente
alias bwsend='bw-send.sh'
alias bwsend-telegram='bw-send.sh --telegram'
alias bwsend-email='bw-send.sh --email'

# Agregar a ~/.bashrc
echo 'alias bwsend="bw-send.sh"' >> ~/.bashrc
echo 'alias bwsend-telegram="bw-send.sh --telegram"' >> ~/.bashrc
echo 'alias bwsend-email="bw-send.sh --email"' >> ~/.bashrc
```

## Integración con Herramientas

### Integración con Git

```bash
# Enviar cambios importantes
git log --oneline -5 | ./bw-send.sh --text - --expiration 1 --notes "Últimos commits - $(date)"
```

### Integración con Scripts de Backup

```bash
#!/bin/bash
# Script de backup con envío automático

BACKUP_FILE="/tmp/backup-$(date +%Y%m%d).tar.gz"
tar -czf "$BACKUP_FILE" /ruta/importante

if [ -f "$BACKUP_FILE" ]; then
    ./bw-send.sh --file "$BACKUP_FILE" --expiration 7 --notes "Backup diario - $(date)" --email admin@empresa.com
    rm "$BACKUP_FILE"
fi
```

### Integración con CI/CD

```bash
# En GitHub Actions
- name: Send deployment info
  run: |
    ./bw-send.sh --text "Deployment completed successfully
    Environment: production
    Version: ${{ github.sha }}
    Time: $(date)" --expiration 1 --telegram @deploy-bot
```

### Integración con Monitoreo

```bash
#!/bin/bash
# Script de monitoreo con alertas

if ! systemctl is-active --quiet nginx; then
    ./bw-send.sh --text "ALERTA: Nginx no está funcionando
    Servidor: $(hostname)
    Hora: $(date)
    Acción requerida: Reiniciar servicio" --expiration 1 --telegram @admin --email admin@empresa.com
fi
```

## Solución de Problemas

### Problemas Comunes

#### Error de Autenticación de Bitwarden

```bash
# Verificar estado de Bitwarden
bw status

# Re-autenticarse si es necesario
bw logout && bw login
```

#### Error de Configuración de Telegram

```bash
# Verificar configuración
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# Probar bot manualmente
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```

#### Error de Configuración de Email

```bash
# Verificar configuración SMTP
echo $EMAIL_SMTP_SERVER
echo $EMAIL_USERNAME

# Probar conexión SMTP
telnet $EMAIL_SMTP_SERVER $EMAIL_SMTP_PORT
```

### Logs y Debugging

```bash
# Habilitar modo verbose
./bw-send.sh --text "test" --verbose

# Ver logs del sistema
journalctl -u bitwarden-cli

# Verificar archivos de configuración
cat ~/.bw-send.conf
```

### Verificación de Funcionalidad

```bash
# Probar envío básico
./bw-send.sh --text "Test message" --expiration 1

# Probar con archivo
echo "Test content" > test.txt
./bw-send.sh --file test.txt --expiration 1
rm test.txt
```

## Seguridad y Mejores Prácticas

### Configuración Segura

```bash
# Proteger archivo de configuración
chmod 600 ~/.bw-send.conf

# Usar contraseñas fuertes
./bw-send.sh --text "datos" --password "$(openssl rand -base64 32)"

# Limitar expiración
./bw-send.sh --text "datos" --expiration 1 --max-access 1
```

### Gestión de Secretos

```bash
# No hardcodear tokens en scripts
export TELEGRAM_BOT_TOKEN="$(bw get password 'Telegram Bot Token')"

# Rotar tokens regularmente
bw generate --length 32 --uppercase --lowercase --numbers --symbols
```

### Auditoría y Monitoreo

```bash
# Log de envíos
echo "$(date): Enviado a $DESTINATION" >> ~/.bw-send.log

# Verificar envíos recientes
bw list sends
```

## Desarrollo y Extensibilidad

### Agregar Nuevos Canales

El script está diseñado para ser extensible. Para agregar un nuevo canal:

1. **Crear función de envío**:

   ```bash
   send_slack() {
       local content="$1"
       local webhook_url="$SLACK_WEBHOOK_URL"
       
       curl -X POST -H 'Content-type: application/json' \
           --data "{\"text\":\"$content\"}" \
           "$webhook_url"
   }
   ```

1. **Agregar opción**:

   ```bash
   case "$1" in
       --slack)
           CHANNEL="slack"
           SLACK_WEBHOOK="$2"
           shift 2
           ;;
   esac
   ```

1. **Integrar en flujo principal**:

   ```bash
   case "$CHANNEL" in
       "slack")
           send_slack "$CONTENT"
           ;;
   esac
   ```

### Contribuir

Para contribuir al desarrollo de `bw-send.sh`:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa la funcionalidad
4. Agrega tests
5. Envía un Pull Request

## Recursos Adicionales

### Documentación Relacionada

- [Bitwarden CLI Documentation](docs/bw.md)
- [Gestión de Secretos](docs/secrets.md)
- [Documentación Oficial de Bitwarden](https://bitwarden.com/help/)

### Herramientas Complementarias

- `bw-ghpersonal.sh` - Obtención automática de tokens GitHub
- `git-tokens.py` - Gestión de tokens Git
- `packages.sh --list bwdn` - Instalación de Bitwarden
- `mail-config.py` - Configuración SMTP para envío por email
- `bw-mailer.py` - Script auxiliar para envío de emails

### Comunidad

- [Bitwarden Community](https://community.bitwarden.com/)
- [GitHub Issues](https://github.com/maurorosero/bintools/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/bitwarden)

## Licencia

Este script es parte del proyecto bintools y está bajo la licencia GPL v3. Consulta el archivo LICENSE en el repositorio para más detalles.

## Soporte

Para obtener ayuda:

1. **Consulta esta documentación**
2. **Revisa la documentación de Bitwarden CLI**
3. **Abre un issue** en el repositorio de bintools
4. **Contacta al equipo** de desarrollo

---

## Créditos

Documentación creada para bintools - Herramientas esenciales del sistema.
