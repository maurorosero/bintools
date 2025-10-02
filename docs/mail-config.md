# mail-config.py - Configurador SMTP con SOPS

Configurador interactivo de SMTP con encriptación SOPS para múltiples proveedores de correo electrónico. Compatible con Ansible, Kubernetes, Docker, Terraform y otros sistemas de automatización.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Pre-requisitos](#pre-requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Proveedores Soportados](#proveedores-soportados)
- [Formatos de Salida](#formatos-de-salida)
- [Estructura de Configuración](#estructura-de-configuración)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Solución de Problemas](#solución-de-problemas)
- [Integración con Otros Sistemas](#integración-con-otros-sistemas)

## 📝 Descripción

`mail-config.py` es una herramienta que permite configurar servidores SMTP de forma interactiva o automática, con encriptación segura de credenciales usando SOPS y GPG. Genera configuraciones compatibles con múltiples sistemas de automatización.

### Características Principales

- 🔐 **Encriptación segura**: Credenciales encriptadas con SOPS + GPG
- 🎯 **Configuración interactiva**: Guía paso a paso para configurar SMTP
- ✅ **Prueba de conexión**: Verificación automática de configuración SMTP
- 📤 **Múltiples formatos**: Genera salidas en JSON, YAML, ENV, Terraform
- 🔧 **Compatibilidad universal**: Compatible con Ansible, Kubernetes, Docker, Terraform
- 🛡️ **Manejo de errores**: Diagnósticos específicos y soluciones automáticas
- 📊 **Logs organizados**: Sistema de logging con colores y categorización

## 🔧 Pre-requisitos

### Sistema Operativo
- Linux (Ubuntu, Debian, Fedora, CentOS, Arch Linux)
- macOS
- Windows (con WSL o Git Bash)

### Dependencias del Sistema
```bash
# Instalar dependencias base
packages.sh --list base

# Esto incluye:
# - Python 3.6+
# - SOPS (mozilla-sops.sh)
# - GPG (gnupg)
# - PyYAML (python3-yaml)
```

### Configuración Inicial
```bash
# 1. Instalar SOPS
mozilla-sops.sh --install

# 2. Configurar GPG (si no tienes claves)
gpg-manager.py --gen-key

# 3. Configurar SOPS con GPG
gpg-manager.py --sops-config
```

## 🚀 Instalación

### Instalación Automática
```bash
# Clonar bintools
git clone https://github.com/maurorosero/bintools.git
cd bintools

# Hacer ejecutable
chmod +x mail-config.py

# Verificar instalación
python3 mail-config.py --help
```

### Verificación de Dependencias
```bash
# Verificar SOPS
sops --version

# Verificar GPG
gpg --list-secret-keys

# Verificar configuración SOPS
cat ~/.config/sops/sops.yaml
```

## 📖 Uso

### Modo Interactivo (Recomendado)
```bash
# Configuración paso a paso
python3 mail-config.py --interactive
```

### Modo Automático
```bash
# Configuración con parámetros
python3 mail-config.py \
  --provider gmail \
  --username user@gmail.com \
  --password "tu-password" \
  --from-name "Tu Nombre" \
  --from-email "user@gmail.com"
```

### Modo Test
```bash
# Probar configuración existente
python3 mail-config.py --test

# Probar con destinatario específico
python3 mail-config.py --test --test-recipient test@example.com
```

### Comandos de Información
```bash
# Mostrar configuración actual
python3 mail-config.py --show-config

# Listar proveedores disponibles
python3 mail-config.py --list-providers

# Solo validar configuración
python3 mail-config.py --validate-only
```

## 🌐 Proveedores Soportados

### Gmail (Google)
- **Host**: `smtp.gmail.com`
- **Puerto**: `587` (TLS) o `465` (SSL)
- **Seguridad**: `tls` o `ssl`
- **Requisitos**: Contraseña de aplicación (no la contraseña normal)

### Outlook (Microsoft)
- **Host**: `smtp-mail.outlook.com`
- **Puerto**: `587`
- **Seguridad**: `tls`
- **Requisitos**: Autenticación moderna habilitada

### Yahoo Mail
- **Host**: `smtp.mail.yahoo.com`
- **Puerto**: `587` (TLS) o `465` (SSL)
- **Seguridad**: `tls` o `ssl`
- **Requisitos**: Contraseña de aplicación

### Office 365
- **Host**: `smtp.office365.com`
- **Puerto**: `587`
- **Seguridad**: `tls`
- **Requisitos**: Autenticación moderna

### Servidor Personalizado
- **Host**: Configurable
- **Puerto**: Configurable
- **Seguridad**: `tls`, `ssl` o `none`
- **Requisitos**: Configuración manual

## 📤 Formatos de Salida

### JSON
```bash
# Generar archivo JSON
python3 mail-config.py --output-format json --output-file config.json

# Salida a consola
python3 mail-config.py --output-format json
```

### YAML
```bash
# Generar archivo YAML
python3 mail-config.py --output-format yaml --output-file config.yaml

# Salida a consola
python3 mail-config.py --output-format yaml
```

### Variables de Entorno (ENV)
```bash
# Generar archivo .env
python3 mail-config.py --output-format env --output-file .env

# Salida a consola
python3 mail-config.py --output-format env
```

### Terraform
```bash
# Generar configuración Terraform para AWS
python3 mail-config.py --output-format terraform --terraform-provider aws --output-dir ./terraform

# Generar para múltiples proveedores
python3 mail-config.py --output-format terraform --terraform-provider all --output-dir ./terraform
```

## 📁 Estructura de Configuración

### Archivo Principal
```yaml
# ~/secure/sops/mail/mail-config.yml
---
# Configuración SMTP estándar - Compatible con Ansible, Kubernetes, Docker, Terraform, etc.
# Autor: Mauro Rosero Pérez
# Fecha: 2025-01-20
# Versión: 1.0.0
# Generado por: mail-config.py

# Configuración principal SMTP
smtp:
  # Configuración del servidor
  host: "smtp.gmail.com"
  port: 587
  security: "tls"  # tls, ssl, none
  
  # Autenticación
  username: "user@gmail.com"
  password: ENC[AES256_GCM,data:...,type:str]  # Encriptado con SOPS
  
  # Configuración del remitente
  from:
    name: "Tu Nombre"
    email: "user@gmail.com"
  
  # Configuración adicional
  timeout: 30
  retries: 3

# Metadatos
metadata:
  created_at: "2025-01-20T10:30:00Z"
  updated_at: "2025-01-20T10:30:00Z"
  version: "1.0.0"
  tool: "mail-config.py"
  author: "Mauro Rosero Pérez"
```

### Directorios de Trabajo
```
~/secure/sops/mail/
├── mail-config.yml          # Configuración principal
├── backups/                 # Backups automáticos
│   └── mail-config-YYYYMMDD-HHMMSS.yml
└── logs/                    # Logs de operaciones
    └── mail-config.log

~/.logs/sops/
└── mail-config.log          # Logs principales
```

## 💡 Ejemplos de Uso

### Configuración Básica
```bash
# 1. Configuración interactiva
python3 mail-config.py --interactive

# 2. Probar configuración
python3 mail-config.py --test

# 3. Mostrar configuración
python3 mail-config.py --show-config
```

### Configuración para Desarrollo
```bash
# Configurar Gmail para desarrollo
python3 mail-config.py \
  --provider gmail \
  --username dev@company.com \
  --password "app-password" \
  --from-name "Dev Team" \
  --test
```

### Generación de Configuraciones
```bash
# Generar configuración para Ansible
python3 mail-config.py --output-format yaml --output-file ansible/mail-config.yml

# Generar variables de entorno para Docker
python3 mail-config.py --output-format env --output-file docker/.env

# Generar configuración Terraform para AWS
python3 mail-config.py --output-format terraform --terraform-provider aws --output-dir ./terraform
```

### Integración con CI/CD
```bash
# En pipeline de CI/CD
python3 mail-config.py --test --test-recipient ci@company.com

# Validar configuración antes de deploy
python3 mail-config.py --validate-only
```

## 🔧 Solución de Problemas

### Errores Comunes

#### 1. SOPS no configurado
```
❌ SOPS no está configurado correctamente
🔧 Soluciones:
   1. Ejecuta: gpg-manager.py --sops-config
   2. Verifica que tienes claves GPG: gpg --list-secret-keys
   3. Verifica el archivo: ~/.config/sops/sops.yaml
```

#### 2. Claves GPG faltantes
```
❌ No hay claves GPG disponibles para SOPS
🔧 Soluciones:
   1. Genera una clave GPG: gpg-manager.py --gen-key
   2. Configura SOPS: gpg-manager.py --sops-config
```

#### 3. Error de autenticación SMTP
```
❌ Error de autenticación SMTP
🔧 Verifica el usuario y contraseña
```

#### 4. Error de conexión SMTP
```
❌ Error conectando al servidor SMTP
🔧 Verifica el host (smtp.gmail.com) y puerto (587)
```

### Comandos de Diagnóstico
```bash
# Verificar SOPS
sops --version
cat ~/.config/sops/sops.yaml

# Verificar GPG
gpg --list-secret-keys --keyid-format LONG

# Verificar configuración
python3 mail-config.py --show-config

# Probar conexión
python3 mail-config.py --test --test-recipient test@example.com
```

### Logs y Debugging
```bash
# Ver logs en tiempo real
tail -f ~/.logs/sops/mail-config.log

# Ver logs con colores
less -R ~/.logs/sops/mail-config.log

# Limpiar logs
rm ~/.logs/sops/mail-config.log
```

## 🔗 Integración con Otros Sistemas

### Ansible
```yaml
# ansible/playbook.yml
- name: Configurar SMTP
  hosts: mail_servers
  vars_files:
    - mail-config.yml
  tasks:
    - name: Configurar servidor SMTP
      lineinfile:
        path: /etc/postfix/main.cf
        line: "relayhost = {{ smtp.host }}:{{ smtp.port }}"
```

### Kubernetes
```yaml
# k8s/mail-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mail-config
type: Opaque
data:
  host: {{ smtp.host | b64encode }}
  port: {{ smtp.port | b64encode }}
  username: {{ smtp.username | b64encode }}
  password: {{ smtp.password | b64encode }}
```

### Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim

# Copiar configuración de mail
COPY .env /app/.env

# Usar variables de entorno
ENV SMTP_HOST=${SMTP_HOST}
ENV SMTP_PORT=${SMTP_PORT}
ENV SMTP_USERNAME=${SMTP_USERNAME}
ENV SMTP_PASSWORD=${SMTP_PASSWORD}
```

### Terraform
```hcl
# terraform/main.tf
resource "aws_secretsmanager_secret" "mail_config" {
  name        = "mail-config"
  description = "SMTP configuration for mail services"
}

resource "aws_secretsmanager_secret_version" "mail_config" {
  secret_id = aws_secretsmanager_secret.mail_config.id
  secret_string = jsonencode({
    host      = var.mail_host
    port      = var.mail_port
    username  = var.mail_username
    password  = var.mail_password
    from_name = var.mail_from_name
    from_email = var.mail_from_email
  })
}
```

## 📚 Referencias

- [Documentación de SOPS](docs/sops.md)
- [Guía de GPG Manager](docs/gpg-manager.md)
- [Gestión de Secretos](docs/secrets.md)
- [Mozilla SOPS](https://github.com/mozilla/sops)
- [GPG Documentation](https://gnupg.org/documentation/)

## 🤝 Contribuir

Para contribuir al desarrollo de `mail-config.py`:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Agrega tests si es necesario
5. Envía un pull request

## 📝 Licencia

GNU General Public License v3.0 - Ver [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Mauro Rosero Pérez**
- Website: [mauro.rosero.one](https://mauro.rosero.one)
- Email: [mauro.rosero@gmail.com](mailto:mauro.rosero@gmail.com)
- GitHub: [@maurorosero](https://github.com/maurorosero)
