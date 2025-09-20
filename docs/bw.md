# Bitwarden CLI - Guía Completa

## Descripción

**Bitwarden CLI** es la interfaz de línea de comandos de Bitwarden, un gestor de contraseñas de código abierto y gratuito. Permite automatizar tareas de gestión de contraseñas, tokens y datos sensibles desde scripts y aplicaciones.

## ¿Qué es Bitwarden?

Bitwarden es una plataforma de gestión de contraseñas que ofrece:

- 🔐 **Almacenamiento seguro**: Encriptación de extremo a extremo
- 🌐 **Sincronización multiplataforma**: Acceso desde cualquier dispositivo
- 🆓 **Código abierto**: Transparente y auditable
- 🏢 **Opciones empresariales**: Para equipos y organizaciones
- 🛠️ **API y CLI**: Para automatización e integración

## Instalación

### Instalación Automática

```bash
# Instalar Bitwarden CLI usando bintools
./packages.sh --list bwdn
```

### Instalación Manual por Sistema Operativo

#### Ubuntu/Debian

```bash
# Instalar desde Snap (recomendado)
sudo snap install bw

# O desde el repositorio oficial
wget -O bw.zip https://vault.bitwarden.com/download/?app=cli&platform=linux
unzip bw.zip
sudo mv bw /usr/local/bin/
```

#### Fedora/CentOS

```bash
# Instalar desde Snap
sudo snap install bw

# O desde RPM
wget https://github.com/bitwarden/clients/releases/download/cli-v2023.12.1/bw-linux-2023.12.1.zip
unzip bw-linux-*.zip
sudo mv bw /usr/local/bin/
```

#### Arch Linux

```bash
# Desde AUR
yay -S bitwarden-cli

# O desde Snap
sudo snap install bw
```

#### macOS

```bash
# Desde Homebrew
brew install bitwarden-cli

# O desde MacPorts
sudo port install bitwarden-cli
```

#### Windows

```powershell
# Desde Chocolatey
choco install bitwarden-cli

# O desde Scoop
scoop install bitwarden-cli
```

## Configuración Inicial

### 1. Iniciar Sesión

```bash
# Iniciar sesión con tu cuenta
bw login

# O especificar servidor personalizado
bw login --server https://vault.bitwarden.com
```

### 2. Desbloquear la Bóveda

```bash
# Desbloquear con contraseña maestra
bw unlock

# O guardar sesión por un tiempo específico
bw unlock --passwordenv BW_PASSWORD
```

### 3. Configurar Variables de Entorno

```bash
# Agregar a ~/.bashrc o ~/.zshrc
export BW_SESSION="$(bw unlock --raw)"

# O usar archivo de configuración
echo 'export BW_SESSION="$(bw unlock --raw)"' >> ~/.bashrc
```

## Comandos Básicos

### Gestión de Elementos

```bash
# Listar todos los elementos
bw list items

# Buscar elementos
bw list items --search "github"

# Obtener elemento específico
bw get item "GitHub Personal"

# Crear nuevo elemento
bw create item login --name "Nuevo Sitio" --username "usuario" --password "contraseña"
```

### Gestión de Organizaciones

```bash
# Listar organizaciones
bw list organizations

# Obtener elementos de organización
bw list items --organizationid <org-id>
```

### Gestión de Colecciones

```bash
# Listar colecciones
bw list collections

# Obtener elementos de colección
bw list items --collectionid <collection-id>
```

## Comandos Avanzados

### Exportar Datos

```bash
# Exportar a JSON
bw export --format json --output export.json

# Exportar a CSV
bw export --format csv --output export.csv

# Exportar con contraseña
bw export --format json --password "contraseña" --output export.json
```

### Importar Datos

```bash
# Importar desde JSON
bw import bitwardenjson import.json

# Importar desde CSV
bw import csv import.csv

# Importar con contraseña
bw import bitwardenjson import.json --password "contraseña"
```

### Gestión de Archivos Adjuntos

```bash
# Listar archivos adjuntos
bw get item "Elemento" --include-organization

# Descargar archivo adjunto
bw get attachment "archivo.pdf" --itemid <item-id> --output archivo.pdf

# Subir archivo adjunto
bw create attachment --itemid <item-id> --file archivo.pdf
```

## Automatización y Scripts

### Scripts de Shell

```bash
#!/bin/bash

# Obtener token de GitHub desde Bitwarden
GITHUB_TOKEN=$(bw get password "GitHub Personal")
export GITHUB_TOKEN

# Usar en script
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### Integración con Git

```bash
# Configurar credenciales Git desde Bitwarden
git config --global credential.helper '!bw get password "Git Credentials"'
```

### Scripts de Python

```python
import subprocess
import json

# Obtener credenciales
result = subprocess.run(['bw', 'get', 'item', 'GitHub Personal'], 
                       capture_output=True, text=True)
item = json.loads(result.stdout)

username = item['login']['username']
password = item['login']['password']

# Usar credenciales
print(f"Username: {username}")
```

## Bitwarden Send

### Envío de Texto

```bash
# Enviar texto simple
bw send create --text "Información confidencial"

# Enviar con contraseña
bw send create --text "Datos sensibles" --password "contraseña123"

# Enviar con expiración
bw send create --text "Temporal" --expiration 7
```

### Envío de Archivos

```bash
# Enviar archivo
bw send create --file documento.pdf

# Enviar múltiples archivos
bw send create --file archivo1.txt --file archivo2.pdf

# Enviar con configuración completa
bw send create --file documento.pdf --password "secret" --expiration 3 --maxaccess 5
```

### Gestión de Sends

```bash
# Listar sends activos
bw list sends

# Obtener send específico
bw get send <send-id>

# Eliminar send
bw delete send <send-id>
```

## Seguridad y Mejores Prácticas

### Variables de Entorno

```bash
# Configurar variables seguras
export BW_CLIENTID="tu-client-id"
export BW_CLIENTSECRET="tu-client-secret"
export BW_PASSWORD="tu-contraseña-maestra"
```

### Archivo de Configuración

```bash
# Crear configuración personalizada
bw config server https://tu-servidor-bitwarden.com
bw config apiUrl https://tu-api-bitwarden.com
```

### Rotación de Sesiones

```bash
# Rotar sesión automáticamente
bw logout && bw login

# O usar script de rotación
#!/bin/bash
bw logout
bw login
export BW_SESSION="$(bw unlock --raw)"
```

## Solución de Problemas

### Problemas Comunes

#### Error de Autenticación

```bash
# Verificar estado de sesión
bw status

# Re-autenticarse
bw logout && bw login
```

#### Error de Sincronización

```bash
# Forzar sincronización
bw sync

# Verificar conectividad
bw status
```

#### Problemas de Permisos

```bash
# Verificar permisos del archivo
ls -la ~/.config/Bitwarden\ CLI/

# Recrear configuración
rm -rf ~/.config/Bitwarden\ CLI/
bw login
```

### Logs y Debugging

```bash
# Habilitar logs detallados
bw --verbose list items

# Ver logs del sistema
journalctl -u bitwarden-cli

# Verificar configuración
bw config
```

## Integración con Herramientas

### GitHub CLI

```bash
# Configurar GitHub CLI con Bitwarden
gh auth login --with-token < <(bw get password "GitHub Token")
```

### Docker

```bash
# Usar Bitwarden CLI en contenedor
docker run -it --rm -v ~/.config/Bitwarden\ CLI:/root/.config/Bitwarden\ CLI bitwarden/cli:latest bw status
```

### CI/CD

```bash
# En GitHub Actions
- name: Setup Bitwarden
  run: |
    bw login --apikey
    export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"
  
- name: Get secrets
  run: |
    export API_KEY="$(bw get password 'API Key')"
    export DB_PASSWORD="$(bw get password 'Database Password')"
```

## Comandos de Utilidad

### Información del Sistema

```bash
# Ver información de la cuenta
bw status

# Ver configuración actual
bw config

# Ver versión
bw --version
```

### Limpieza y Mantenimiento

```bash
# Limpiar caché local
bw logout --clear-cache

# Verificar integridad
bw list items --search "" | jq '.[] | select(.name == null)'
```

## Recursos Adicionales

### Documentación Oficial

- [Documentación de Bitwarden CLI](https://bitwarden.com/help/cli/)
- [API Reference](https://bitwarden.com/help/api/)
- [GitHub Repository](https://github.com/bitwarden/clients)

### Comunidad

- [Bitwarden Community](https://community.bitwarden.com/)
- [Reddit r/Bitwarden](https://www.reddit.com/r/Bitwarden/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/bitwarden)

### Tutoriales

- [Bitwarden CLI Tutorial](https://bitwarden.com/help/cli/)
- [Automation Guide](https://bitwarden.com/help/cli-commands/)
- [Security Best Practices](https://bitwarden.com/help/security/)

## Licencia

Bitwarden CLI es software de código abierto bajo la licencia GPL v3. Consulta el archivo LICENSE en el repositorio oficial para más detalles.

## Soporte

Para obtener ayuda:

1. **Consulta esta documentación**
2. **Revisa la documentación oficial** de Bitwarden
3. **Visita la comunidad** de Bitwarden
4. **Abre un issue** en el repositorio oficial si encuentras bugs

---

## Créditos

Documentación creada para bintools - Herramientas esenciales del sistema.
