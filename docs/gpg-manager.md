# Gestor de Claves GPG (gpg-manager.py)

> **📖 [← Volver al README principal](../README.md)**

## 📖 Introducción

`gpg-manager.py` es un gestor completo de claves GPG que automatiza la creación, gestión y configuración de claves de cifrado para desarrolladores. Proporciona una interfaz unificada para manejar claves maestras, subclaves, backups y configuración de Git con GPG.

### Características Principales

- 🔑 **Gestión de Claves**: Creación de claves maestras y subclaves con configuración automática
- 🔐 **Estrategia Offline**: Exportación y eliminación segura de claves maestras del keyring local
- 📦 **Backup y Restore**: Sistema completo de backup portable con verificación de integridad
- 🖥️ **Detección Automática**: Configuración automática de pinentry gráfico o terminal según el entorno
- 🐍 **Automatización**: Generación automática de subclaves sin intervención manual
- 🔧 **Integración Git**: Configuración automática de Git para firmar commits con GPG
- ✅ **Multiplataforma**: Compatible con Linux, macOS y Windows
- 📝 **Logging**: Sistema de logs para seguimiento de operaciones

## 🔧 Pre-requisitos

### Requisitos del Sistema

- **Python 3.6+** instalado en el sistema
- **GPG 2.1+** instalado y configurado
- **Herramientas base del sistema** (`packages.sh --list base`)
- **Entorno gráfico** (opcional, para pinentry gráfico)

### Verificación de Requisitos

```bash
# Verificar Python instalado
python3 --version

# Verificar GPG instalado
gpg --version

# Instalar herramientas base si es necesario
./packages.sh --list base

# Verificar entorno gráfico (opcional)
echo $DISPLAY
echo $WAYLAND_DISPLAY
```

### Instalación de GPG

Si no tienes GPG instalado, puedes usar `packages.sh`:

```bash
# Instalar GPG del sistema
./packages.sh --list base
```

## 🚀 Uso Básico

### Estructura de Comandos

```bash
./gpg-manager.py <comando> [argumentos...]
```

### Comandos Principales

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `--init` | Inicializar configuración GPG | `./gpg-manager.py --init` |
| `--gen-key` | Generar llave maestra y subclaves | `./gpg-manager.py --gen-key` |
| `--export-master` | Exportar llave maestra para almacenamiento offline | `./gpg-manager.py --export-master` |
| `--git-config` | Configurar Git para GPG | `./gpg-manager.py --git-config` |
| `--revoke-key` | Generar certificado de revocación de emergencia | `./gpg-manager.py --revoke-key` |
| `--backup` | Crear backup portable | `./gpg-manager.py --backup` |
| `--restore` | Restaurar backup | `./gpg-manager.py --restore archivo.tar.gz` |
| `--verify` | Verificar integridad de backup | `./gpg-manager.py --verify archivo.tar.gz` |
| `--list` | Listar backups disponibles | `./gpg-manager.py --list` |

## 🔑 Gestión de Claves

### Inicialización de GPG

```bash
# Inicializar configuración GPG básica
./gpg-manager.py --init
```

**¿Qué hace `--init`?**

- Crea el directorio `~/.gnupg` con permisos correctos
- Configura `gpg.conf` con opciones optimizadas
- Configura `gpg-agent.conf` con pinentry apropiado
- Detecta automáticamente entorno gráfico vs terminal
- Establece configuración de confianza básica

### Generación de Claves

```bash
# Generar llave maestra y subclaves completas
./gpg-manager.py --gen-key
```

**¿Qué hace `--gen-key`?**

1. **Solicita información del usuario**:
   - Nombre completo
   - Email
   - Comentario (opcional)
   - Contraseña maestra

2. **Genera llave maestra**:
   - Algoritmo: RSA 4096
   - Uso: Certificación (C) + Firma (S)
   - Expiración: Nunca
   - Configuración automática

3. **Genera subclaves automáticamente**:
   - **Firma (S)**: RSA 4096, expira en 1 año
   - **Cifrado (E)**: RSA 4096, expira en 1 año
   - **Autenticación (A)**: RSA 4096, expira en 1 año

4. **Crea certificado de revocación**:
   - Generado automáticamente por GPG
   - Guardado en `~/secure/gpg/`

5. **Exporta llave maestra offline**:
   - Exporta llave maestra completa
   - Exporta solo subclaves
   - Elimina llave maestra del keyring local
   - Reimporta subclaves para funcionamiento normal

### Configuración de Git

```bash
# Configurar Git para usar GPG
./gpg-manager.py --git-config
```

**¿Qué hace `--git-config`?**

- Detecta automáticamente la subclave de firma
- Configura `user.signingkey` con la subclave correcta
- Habilita `commit.gpgsign` y `tag.gpgSign`
- Configura `user.name` y `user.email` desde la llave GPG
- Establece `GPG_TTY` si hay TTY disponible
- Configura GPG para automatización si es necesario

## 📦 Sistema de Backup

### Crear Backup

```bash
# Crear backup portable completo
./gpg-manager.py --backup
```

**¿Qué incluye el backup?**

- Configuración completa de `~/.gnupg/`
- Claves públicas y privadas
- Configuración de confianza
- Archivos de configuración
- Verificación de integridad SHA256

**Ubicación del backup:**
- Directorio: `~/secure/gpg/backup/`
- Formato: `gpg-YYYYMMDD_HHMMSS.tar.gz`
- Checksum: `gpg-YYYYMMDD_HHMMSS.tar.gz.sha256`

### Restaurar Backup

```bash
# Restaurar backup específico
./gpg-manager.py --restore gpg-20241214_143022.tar.gz
```

**¿Qué hace `--restore`?**

- Detiene procesos GPG activos
- Crea backup de configuración existente
- Extrae y restaura configuración GPG
- Verifica integridad del backup
- Recarga configuración GPG

### Verificar Integridad

```bash
# Verificar integridad de backup
./gpg-manager.py --verify gpg-20241214_143022.tar.gz
```

### Listar Backups

```bash
# Listar todos los backups disponibles
./gpg-manager.py --list
```

## 🔐 Estrategia de Seguridad

### Llave Maestra Offline

La llave maestra se mantiene offline por seguridad:

1. **Generación**: Se crea con capacidad de certificación y firma
2. **Exportación**: Se exporta a `~/secure/gpg/master-key-*.asc`
3. **Eliminación**: Se elimina del keyring local
4. **Almacenamiento**: Se guarda en lugar seguro (USB, papel)
5. **Uso**: Solo para revocar subclaves o crear nuevas

### Subclaves de Trabajo

Las subclaves permanecen en el keyring local:

- **Firma (S)**: Para firmar commits, emails, paquetes
- **Cifrado (E)**: Para cifrar mensajes y archivos
- **Autenticación (A)**: Para autenticación SSH (opcional)

### Certificado de Revocación

- Se genera automáticamente al crear la llave maestra
- Se guarda en `~/secure/gpg/revocation-cert-*.asc`
- Se usa solo si la llave es comprometida
- Permite revocar la llave maestra y todas las subclaves

#### Estrategia de Recuperación Directa

El comando `--revoke-key` implementa una estrategia de recuperación directa que permite generar un certificado de revocación de emergencia en cualquier momento:

**Características:**
- **Verificación de disponibilidad**: Valida que la clave maestra esté en el keyring
- **Solicitud segura de contraseña**: Usa `getpass` para proteger la contraseña
- **Generación automática**: Usa `gpg --gen-revoke` con parámetros optimizados
- **Validación de integridad**: Verifica que el certificado generado sea válido
- **Logging completo**: Registra todas las operaciones para auditoría

**Cuándo usar:**
- Antes de eliminar la clave maestra del keyring (uso preventivo)
- Cuando la clave maestra aún está disponible pero se necesita un certificado adicional
- Para tener un certificado de revocación con timestamp específico
- Como backup adicional al certificado generado automáticamente

## 🖥️ Configuración de Entorno

### Detección Automática

El script detecta automáticamente el entorno:

**Entorno Gráfico** (DISPLAY o WAYLAND_DISPLAY):
- Configura `pinentry-program` con el mejor programa disponible
- Prioridad: `pinentry-gnome3` > `pinentry-gtk-2` > `pinentry-gtk` > `pinentry-qt` > `pinentry`
- Funciona en Cursor, VS Code, terminales gráficos

**Solo Terminal**:
- Configura `pinentry-mode loopback`
- Configura `allow-loopback-pinentry`
- Funciona en servidores, SSH, terminales sin GUI

### Configuración Manual

Si necesitas configurar manualmente:

```bash
# Verificar configuración actual
cat ~/.gnupg/gpg.conf
cat ~/.gnupg/gpg-agent.conf

# Recargar configuración
gpg-connect-agent reloadagent /bye
```

## 🚨 Solución de Problemas

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| **Error de permisos** | Verificar permisos de `~/.gnupg` (700) |
| **Pinentry no funciona** | Ejecutar `--init` para reconfigurar |
| **Git no firma commits** | Ejecutar `--git-config` |
| **Llave maestra no encontrada** | Verificar que esté en `~/secure/gpg/` |
| **Subclaves no funcionan** | Verificar que estén en el keyring local |

### Logs y Debugging

```bash
# Ver logs del script
cat /tmp/gpg_manager.log

# Verificar configuración GPG
gpg --list-keys
gpg --list-secret-keys

# Verificar configuración Git
git config --global --get user.signingkey
git config --global --get commit.gpgsign

# Probar firma GPG
echo "test" | gpg --clearsign --default-key TU_SUBCLAVE
```

### Verificación de Funcionamiento

```bash
# Verificar que GPG funciona
gpg --version

# Verificar que las subclaves están disponibles
gpg --list-secret-keys

# Probar firma de commit
git commit --allow-empty -m "Test GPG signature"

# Verificar firma
git log --show-signature
```

## 💡 Mejores Prácticas

### 1. Flujo de Trabajo Recomendado

```bash
# 1. Inicializar GPG
./gpg-manager.py --init

# 2. Generar claves
./gpg-manager.py --gen-key

# 3. Configurar Git
./gpg-manager.py --git-config

# 4. Crear backup
./gpg-manager.py --backup

# 5. Guardar llave maestra offline
# (Copiar ~/secure/gpg/master-key-*.asc a lugar seguro)
```

### 2. Gestión de Contraseñas

- **Llave maestra**: Contraseña fuerte y única
- **Subclaves**: Misma contraseña que la llave maestra
- **Almacenamiento**: Considerar usar gestor de contraseñas

### 3. Backup Regular

```bash
# Crear backup antes de cambios importantes
./gpg-manager.py --backup

# Verificar integridad regularmente
./gpg-manager.py --list
./gpg-manager.py --verify gpg-YYYYMMDD_HHMMSS.tar.gz
```

### 4. Publicación de Claves Públicas

```bash
# Exportar clave pública
gpg --armor --export TU_LLAVE_MAESTRA > mi_clave_publica.asc

# Subir a keyserver
gpg --send-keys TU_LLAVE_MAESTRA

# Verificar publicación
gpg --search-keys tu@email.com
```

#### Publicación y verificación con gpg-manager.py

```bash
# Publicar usando la lista por defecto (recommended)
./gpg-manager.py --publish

# Verificar publicación (desacoplado)
./gpg-manager.py --confirm-publish

# Seleccionar lista específica de servidores
./gpg-manager.py --confirm-publish --servers ubuntu

# Verificar una llave específica (si tienes varias)
./gpg-manager.py --confirm-publish --key-id 0xABCDEF1234567890
```

Notas:
- **recommended** actualmente incluye `hkps://keys.openpgp.org` y `hkp://keyserver.ubuntu.com`.
- El servidor del MIT fue removido de la lista recommended por inestabilidad; sigue disponible vía lista `mit` si se requiere.
- La verificación puede tardar 5–15 minutos debido a sincronización entre keyservers.

## 🔄 Mantenimiento

### Renovación de Subclaves

Las subclaves expiran automáticamente en 1 año:

```bash
# Verificar expiración
gpg --list-keys --keyid-format LONG

# Crear nuevas subclaves (requiere llave maestra)
gpg --edit-key TU_LLAVE_MAESTRA
# addkey -> seleccionar tipo -> configurar expiración -> save
```

### Revocación de Claves

#### Generar Certificado de Revocación de Emergencia

```bash
# Generar certificado de revocación de emergencia
./gpg-manager.py --revoke-key

# Especificar clave maestra específica
./gpg-manager.py --revoke-key --key-id <KEY_ID>
```

**¿Qué hace `--revoke-key`?**

1. **Verifica disponibilidad de clave maestra**: 
   - Verifica que la clave maestra esté disponible en el keyring
   - Si hay múltiples claves, solicita especificar con `--key-id`

2. **Solicita contraseña de forma segura**:
   - Usa `getpass` para solicitar contraseña sin mostrarla
   - Valida que la contraseña no esté vacía

3. **Genera certificado con `gpg --gen-revoke`**:
   - Usa pinentry-mode loopback para automatización
   - Configura razón de revocación (clave comprometida)
   - Genera certificado en `~/secure/gpg/emergency-revocation-*.asc`

4. **Valida integridad del certificado**:
   - Verifica formato PGP válido
   - Verifica que sea un certificado de revocación
   - Verifica tamaño mínimo del archivo

5. **Proporciona instrucciones de uso**:
   - Indica dónde se guardó el certificado
   - Muestra comandos para importar y publicar revocación

**Flujo de uso:**

```bash
# 1. Generar certificado de revocación de emergencia
./gpg-manager.py --revoke-key

# 2. Guardar certificado en lugar seguro
# (El certificado se genera en ~/secure/gpg/)

# 3. Si la clave es comprometida, importar certificado
gpg --import ~/secure/gpg/emergency-revocation-*.asc

# 4. Publicar revocación en keyservers
gpg --send-keys TU_LLAVE_MAESTRA
```

**⚠️ IMPORTANTE:**
- Solo usar el certificado si la clave fue comprometida
- Una vez importado, la clave quedará revocada permanentemente
- Guardar el certificado en un lugar seguro y separado de las claves
- Considerar generar el certificado preventivamente

#### Usar Certificado de Revocación Existente

```bash
# Usar certificado de revocación
gpg --import ~/secure/gpg/revocation-cert-*.asc

# Publicar revocación
gpg --send-keys TU_LLAVE_MAESTRA
```

### Limpieza de Backups

```bash
# Listar backups antiguos
./gpg-manager.py --list

# Eliminar backups antiguos manualmente
rm ~/secure/gpg/backup/gpg-YYYYMMDD_HHMMSS.tar.gz*
```

## 📚 Referencias

### Documentación Oficial

- **bintools**: [GitHub Repository](https://github.com/maurorosero/bintools)
- **Autor**: [Mauro Rosero Pérez](https://mauro.rosero.one)

### GPG y Criptografía

- **GPG Manual**: [GNU Privacy Guard Manual](https://www.gnupg.org/documentation/manuals/gnupg/)
- **Best Practices**: [GPG Best Practices](https://riseup.net/en/security/message-security/openpgp/best-practices)
- **Key Management**: [GPG Key Management](https://www.gnupg.org/gph/en/manual/x334.html)

### Git y GPG

- **Git Signing**: [Git Documentation - Signing](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- **GitHub GPG**: [GitHub Documentation - GPG](https://docs.github.com/en/authentication/managing-commit-signature-verification)

### Herramientas Relacionadas

- **Bitwarden CLI**: [Bitwarden CLI Documentation](https://bitwarden.com/help/cli/)
- **Mozilla SOPS**: [Mozilla SOPS Documentation](https://github.com/mozilla/sops)

---

**¡Disfruta usando gpg-manager.py para gestionar tus claves GPG de forma segura y profesional!** 🔐
