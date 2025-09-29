# Gestión de Secretos con Mozilla SOPS

## 📋 Índice
- [¿Qué es SOPS?](#qué-es-sops)
- [¿Por qué usar SOPS?](#por-qué-usar-sops)
- [Instalación](#instalación)
- [Configuración Inicial](#configuración-inicial)
- [Guía de Uso](#guía-de-uso)
- [Ejemplos Prácticos](#ejemplos-prácticos)
- [Mejores Prácticas](#mejores-prácticas)
- [Solución de Problemas](#solución-de-problemas)

---

## ¿Qué es SOPS?

**SOPS** (Secrets OPerationS) es una herramienta desarrollada por Mozilla que permite **gestionar secretos de forma segura** en archivos de configuración. 

### 🔐 En términos simples:
- **Encripta** información sensible (contraseñas, claves API, tokens)
- **Mantiene** la estructura original del archivo
- **Permite** trabajar con archivos encriptados como si fueran normales
- **Integra** con Git sin exponer secretos

### 📁 Formatos soportados:
- **YAML** (.yaml, .yml)
- **JSON** (.json)
- **ENV** (.env)
- **INI** (.ini)
- **BINARIO** (cualquier archivo)

---

## ¿Por qué usar SOPS?

### ❌ **Problema sin SOPS:**
```
# config.yaml
database:
  host: "mi-servidor.com"
  password: "mi-password-secreto"  # ⚠️ EXPUESTO EN GIT
  api_key: "sk-1234567890abcdef"
```

### ✅ **Solución con SOPS:**
```
# config.yaml (encriptado)
database:
  host: "mi-servidor.com"
  password: ENC[AES256_GCM,data:xyz123,iv:abc456,tag:def789,type:str]
  api_key: ENC[AES256_GCM,data:uvw789,iv:rst012,tag:mno345,type:str]
```

### 🎯 **Beneficios:**
- ✅ **Seguridad**: Solo los valores sensibles están encriptados
- ✅ **Colaboración**: Equipos pueden trabajar sin ver secretos
- ✅ **Versionado**: Cambios trackeables en Git
- ✅ **Flexibilidad**: Múltiples métodos de encriptación
- ✅ **Simplicidad**: Comandos fáciles de usar

---

## Instalación

### 🚀 **Instalación Automática (Recomendada)**

Usa nuestro instalador multiplataforma:

```bash
./mozilla-sops.sh
```

Este script:
- ✅ Detecta tu sistema operativo automáticamente
- ✅ Instala SOPS desde la fuente más apropiada
- ✅ Verifica la instalación
- ✅ Ofrece actualizaciones automáticas

### 📦 **Instalación Manual**

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install sops
```

#### macOS:
```bash
brew install sops
```

#### Windows:
```bash
choco install sops
```

### ✅ **Verificar Instalación:**
```bash
sops --version
```

---

## Configuración Inicial

### 🔑 **Paso 1: Generar Clave Age (Recomendado)**

Age es más simple y seguro que PGP:

```bash
# Crear directorio para las claves
mkdir -p ~/.config/sops/age

# Generar par de claves
age-keygen -o ~/.config/sops/age/keys.txt

# Ver la clave pública (la necesitarás)
cat ~/.config/sops/age/keys.txt
```

**Salida esperada:**
```
# created: 2024-01-15T10:30:00Z
# public key: age1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
AGE-SECRET-KEY-1ABC123DEF456GHI789JKL012MNO345PQR678STU901VWX234YZ
```

### 📝 **Paso 2: Verificar Archivo de Configuración**

El comando `age-keygen` ya creó el archivo de claves. Verifica que todo esté correcto:

```bash
# Verificar que el archivo existe
ls -la ~/.config/sops/age/keys.txt

# Ver el contenido completo (incluye clave privada y pública)
cat ~/.config/sops/age/keys.txt
```

**⚠️ Importante:** Este archivo contiene tu **clave privada**. Manténlo seguro y nunca lo compartas públicamente.

### 🔧 **Paso 3: Configurar SOPS**

Crea `~/.config/sops/sops.yaml`:

```yaml
keys:
  - &age age1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
  - age: *age
```

**⚠️ Importante:** Reemplaza la clave con la tuya real.

---

## Guía de Uso

### 📝 **Crear Archivo de Secretos**

1. **Crear archivo normal:**
```bash
cat > secrets.yaml << EOF
database:
  host: "mi-servidor.com"
  port: 5432
  username: "admin"
  password: "mi-password-secreto"
  api_key: "sk-1234567890abcdef"
  
redis:
  host: "redis-servidor.com"
  password: "redis-password-123"
EOF
```

2. **Encriptar el archivo:**
```bash
sops --encrypt --in-place secrets.yaml
```

3. **Verificar encriptación:**
```bash
cat secrets.yaml
```

**Resultado encriptado:**
```yaml
database:
    host: mi-servidor.com
    port: 5432
    username: admin
    password: ENC[AES256_GCM,data:xyz123,iv:abc456,tag:def789,type:str]
    api_key: ENC[AES256_GCM,data:uvw789,iv:rst012,tag:mno345,type:str]
redis:
    host: redis-servidor.com
    password: ENC[AES256_GCM,data:ghi012,iv:jkl345,tag:mno678,type:str]
sops:
    kms: []
    gcp_kms: []
    azure_kv: []
    hc_vault: []
    age:
        - recipient: age1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
          enc: |
            -----BEGIN AGE ENCRYPTED FILE-----
            YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBaaVlWU0pQb1dKcW5m
            -----END AGE ENCRYPTED FILE-----
    lastmodified: "2024-01-15T10:30:00Z"
    mac: ENC[AES256_GCM,data:pqr901,iv:stu234,tag:vwx567,type:str]
    pgp: []
    encrypted_regex: ^(password|api_key|secret|token)$
    version: 3.8.1
```

### 🔓 **Desencriptar y Editar**

**Opción 1: Editar directamente (Recomendado)**
```bash
sops secrets.yaml
```
- Se abre en tu editor predeterminado
- Puedes editar valores normalmente
- Al guardar, se encripta automáticamente

**Opción 2: Desencriptar a archivo temporal**
```bash
sops --decrypt secrets.yaml > secrets-decrypted.yaml
# Editar secrets-decrypted.yaml
sops --encrypt --in-place secrets-decrypted.yaml
mv secrets-decrypted.yaml secrets.yaml
```

### 📖 **Ver Contenido Desencriptado**

```bash
sops --decrypt secrets.yaml
```

### 🔄 **Agregar Nuevo Secreto**

```bash
# Editar archivo encriptado
sops secrets.yaml

# O usar línea de comandos
echo "nuevo_secreto: mi-valor-secreto" | sops --encrypt --input-type yaml --output-type yaml /dev/stdin >> secrets.yaml
```

---

## Ejemplos Prácticos

### 🌐 **Configuración de Aplicación Web**

**Archivo original (`app-config.yaml`):**
```yaml
app:
  name: "Mi Aplicación"
  version: "1.0.0"
  debug: false

database:
  host: "db.miapp.com"
  port: 5432
  name: "miapp_db"
  username: "app_user"
  password: "super-secret-password"
  
redis:
  host: "redis.miapp.com"
  port: 6379
  password: "redis-secret-key"

external_apis:
  stripe:
    api_key: "sk_live_1234567890abcdef"
    webhook_secret: "whsec_abcdef1234567890"
  sendgrid:
    api_key: "SG.abcdef1234567890.xyz"
```

**Encriptar:**
```bash
sops --encrypt --in-place app-config.yaml
```

### 🐳 **Variables de Entorno Docker**

**Archivo original (`.env`):**
```bash
# Base de datos
DB_HOST=db.miapp.com
DB_PORT=5432
DB_NAME=miapp_db
DB_USER=app_user
DB_PASSWORD=super-secret-password

# Redis
REDIS_HOST=redis.miapp.com
REDIS_PASSWORD=redis-secret-key

# APIs externas
STRIPE_API_KEY=sk_live_1234567890abcdef
SENDGRID_API_KEY=SG.abcdef1234567890.xyz
```

**Encriptar:**
```bash
sops --encrypt --in-place .env
```

### ☸️ **Configuración Kubernetes**

**Archivo original (`k8s-secrets.yaml`):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-password: bXktZGF0YWJhc2UtcGFzc3dvcmQ=  # Base64 encoded
  api-key: bXktYXBpLWtleQ==                        # Base64 encoded
```

**Encriptar:**
```bash
sops --encrypt --in-place k8s-secrets.yaml
```

---

## Mejores Prácticas

### 🔐 **Seguridad**

1. **Nunca commitees claves privadas:**
```bash
# .gitignore
*.key
*.pem
*.p12
~/.config/sops/age/keys.txt
```

2. **Usa múltiples claves para equipos:**
```yaml
# ~/.config/sops/sops.yaml
keys:
  - &dev age1dev123...
  - &prod age1prod456...
  - age: [*dev, *prod]
```

3. **Rota claves periódicamente:**
```bash
# Generar nueva clave
age-keygen -o ~/.config/sops/age/keys-new.txt

# Actualizar configuración
# Re-encriptar archivos con nueva clave
```

### 📁 **Organización de Archivos**

```
proyecto/
├── secrets/
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
├── configs/
│   ├── app.yaml
│   └── database.yaml
└── .sops.yaml  # Configuración local
```

### 🔄 **Workflow Recomendado**

1. **Desarrollo local:**
```bash
# Editar secretos
sops secrets/development.yaml

# Verificar cambios
sops --decrypt secrets/development.yaml

# Commit cambios encriptados
git add secrets/development.yaml
git commit -m "Update development secrets"
```

2. **Despliegue:**
```bash
# Desencriptar para uso
sops --decrypt secrets/production.yaml > /tmp/secrets.yaml

# Usar en aplicación
export $(cat /tmp/secrets.yaml | grep -v '^#' | xargs)

# Limpiar archivo temporal
rm /tmp/secrets.yaml
```

### 👥 **Trabajo en Equipo**

1. **Compartir claves públicas:**
```bash
# Exportar clave pública
age-keygen -y ~/.config/sops/age/keys.txt > public-key.txt

# Compartir public-key.txt con el equipo
```

2. **Configuración de equipo:**
```yaml
# ~/.config/sops/sops.yaml (compartido)
keys:
  - &alice age1alice123...
  - &bob age1bob456...
  - &charlie age1charlie789...
  - age: [*alice, *bob, *charlie]
```

---

## Solución de Problemas

### ❌ **Error: "No key could decrypt the data"**

**Causa:** Clave privada incorrecta o no encontrada.

**Solución:**
```bash
# Verificar que la clave existe
ls ~/.config/sops/age/keys.txt

# Verificar configuración
cat ~/.config/sops/sops.yaml

# Regenerar clave si es necesario
age-keygen -o ~/.config/sops/age/keys.txt
```

### ❌ **Error: "sops: command not found"**

**Causa:** SOPS no está instalado o no está en el PATH.

**Solución:**
```bash
# Reinstalar con nuestro script
./mozilla-sops.sh

# O verificar PATH
echo $PATH
which sops
```

### ❌ **Error: "Failed to get the data key"**

**Causa:** Problema con la configuración de Age.

**Solución:**
```bash
# Verificar archivo de configuración
cat ~/.config/sops/sops.yaml

# Regenerar configuración
age-keygen -o ~/.config/sops/age/keys.txt
```

### ❌ **Archivo no se encripta correctamente**

**Causa:** Patrón de encriptación no configurado.

**Solución:**
```bash
# Especificar patrones manualmente
sops --encrypt --encrypted-regex '^(password|secret|key|token)$' archivo.yaml
```

### 🔍 **Comandos de Diagnóstico**

```bash
# Verificar instalación
sops --version

# Verificar configuración
sops --help

# Ver metadatos de archivo encriptado
sops --decrypt --output /dev/null archivo.yaml

# Listar claves disponibles
age-keygen -y ~/.config/sops/age/keys.txt
```

---

## 🎯 **Resumen**

SOPS es una herramienta esencial para gestionar secretos de forma segura:

- ✅ **Instalación simple** con `./mozilla-sops.sh`
- ✅ **Configuración rápida** con Age
- ✅ **Uso intuitivo** para encriptar/desencriptar
- ✅ **Integración perfecta** con Git
- ✅ **Seguridad robusta** para equipos

**¡Comienza a proteger tus secretos hoy mismo!** 🔐
