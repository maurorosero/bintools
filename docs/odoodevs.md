# OdooDevs - Entorno de Desarrollo para Odoo

## Descripción

**OdooDevs** es un entorno de desarrollo profesional para Odoo que proporciona herramientas, configuraciones y scripts optimizados para el desarrollo eficiente de aplicaciones Odoo. Incluye un setup completo con Docker, herramientas de debugging, configuraciones predefinidas y automatización de tareas comunes.

## ¿Qué incluye OdooDevs?

### 🐳 Infraestructura Docker

- **Contenedores optimizados** para desarrollo de Odoo
- **Configuraciones predefinidas** para diferentes versiones de Odoo
- **Bases de datos** configuradas automáticamente
- **Volúmenes persistentes** para desarrollo continuo

### 🛠️ Herramientas de Desarrollo

- **Scripts de automatización** para tareas comunes
- **Herramientas de debugging** integradas
- **Configuraciones de IDE** optimizadas
- **Gestión de dependencias** automática

### 📦 Módulos y Extensiones

- **Módulos de ejemplo** para aprender
- **Templates de desarrollo** preconfigurados
- **Extensiones útiles** para productividad
- **Configuraciones de testing** automatizadas

## Instalación

### Script de Instalación Automática

El script `odevs-install.sh` proporciona una instalación automática con múltiples opciones:

```bash
# Ver todas las opciones disponibles
./odevs-install.sh --help
```

### Tipos de Instalación

#### 1. Instalación para Desarrolladores (`devs`)

Para desarrolladores que quieren contribuir al proyecto odoodevs:

```bash
# Instalación básica (HTTPS)
./odevs-install.sh --type devs

# Con protocolo SSH (requiere configuración SSH)
./odevs-install.sh --type devs --protocol ssh

# Con workspace personalizado
./odevs-install.sh --type devs --workspace mi-proyecto-odoo
```

**¿Qué hace esta instalación?**

- Clona el repositorio completo de odoodevs
- Ejecuta el script de instalación automática
- Configura el entorno de desarrollo
- Establece herramientas y dependencias necesarias

#### 2. Instalación Última Versión (`latest`)

Para usuarios que quieren la última versión estable:

```bash
# Instalar última versión disponible
./odevs-install.sh --type latest
```

**¿Qué hace esta instalación?**

- Descarga e instala la última versión estable
- Configura el entorno básico
- Establece herramientas esenciales

#### 3. Instalación Versión Específica (`version`)

Para usuarios que necesitan una versión específica:

```bash
# Instalar versión específica
./odevs-install.sh --type version --version v1.0.0

# Con workspace personalizado
./odevs-install.sh --type version --version v1.2.0 --workspace proyecto-v1.2
```

**¿Qué hace esta instalación?**

- Descarga e instala la versión exacta especificada
- Configura el entorno para esa versión específica
- Mantiene compatibilidad con esa versión

### Opciones de Configuración

#### Protocolo de Clonado

```bash
# HTTPS (por defecto, recomendado para usuarios nuevos)
./odevs-install.sh --type devs --protocol https

# SSH (recomendado para desarrolladores)
./odevs-install.sh --type devs --protocol ssh
```

**Requisitos para SSH:**

- Clave SSH configurada en GitHub
- Conexión SSH verificada

#### Workspace Personalizado

```bash
# Usar directorio personalizado
./odevs-install.sh --type devs --workspace mi-proyecto

# El directorio se creará automáticamente si no existe
```

## Uso Post-Instalación

### Comandos Disponibles

Después de la instalación, tendrás acceso a varios comandos útiles:

```bash
# Verificar instalación
odoodevs-path

# Crear nuevo proyecto Odoo
odoo-create mi-nuevo-proyecto

# Generar imagen Docker
odoo-image

# Gestionar permisos
odevs-fixperms

# Gestión general del entorno
odevs-manager
```

### Estructura del Proyecto

```text
workdevs/                    # Directorio principal (o el que especifiques)
├── bin/                     # Comandos ejecutables
├── config/                  # Configuraciones
├── docker/                  # Configuraciones Docker
├── modules/                 # Módulos de ejemplo
├── scripts/                 # Scripts de automatización
└── docs/                    # Documentación
```

### Configuración del Entorno

1. **Variables de entorno**: Se configuran automáticamente
2. **Aliases**: Disponibles en tu shell
3. **PATH**: Los comandos están disponibles globalmente
4. **Docker**: Configurado y listo para usar

## Desarrollo con OdooDevs

### Crear un Nuevo Proyecto

```bash
# Crear proyecto básico
odoo-create mi-proyecto

# El comando creará:
# - Estructura de directorios
# - Configuraciones básicas
# - Docker compose listo
# - Módulos de ejemplo
```

### Trabajar con Docker

```bash
# Iniciar entorno completo
docker-compose up -d

# Ver logs
docker-compose logs -f

# Acceder al contenedor
docker-compose exec odoo bash

# Detener entorno
docker-compose down
```

### Desarrollo de Módulos

```bash
# Crear nuevo módulo
odoo-create-module mi-modulo

# Instalar módulo
odoo-install-module mi-modulo

# Actualizar módulo
odoo-update-module mi-modulo
```

## Solución de Problemas

### Problemas Comunes

#### Error de Dependencias

```bash
# Verificar dependencias
./odevs-install.sh --type devs --dry-run

# Instalar dependencias faltantes
sudo apt update && sudo apt install git curl docker.io
```

#### Problemas de SSH

```bash
# Verificar conexión SSH
ssh -T git@github.com

# Configurar SSH si es necesario
ssh-keygen -t ed25519 -C "tu-email@ejemplo.com"
# Agregar clave a GitHub
```

#### Conflictos de Directorio

```bash
# El script detectará directorios existentes
# y te preguntará si quieres:
# 1. Eliminar y continuar
# 2. Cancelar instalación
```

#### Problemas de Docker

```bash
# Verificar Docker
docker --version
docker-compose --version

# Iniciar servicio Docker
sudo systemctl start docker
sudo systemctl enable docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Reiniciar sesión después de esto
```

### Logs y Debugging

```bash
# Ver logs de instalación
tail -f /tmp/odoodevs-install.log

# Verificar configuración
odoodevs-path
odoo-create --help

# Verificar Docker
docker-compose config
```

## Configuración Avanzada

### Personalización del Entorno

Puedes personalizar tu entorno editando los archivos de configuración:

```bash
# Configuración principal
vim ~/workdevs/config/odoodevs.conf

# Configuración Docker
vim ~/workdevs/docker/docker-compose.yml

# Variables de entorno
vim ~/workdevs/config/.env
```

### Integración con IDEs

#### Visual Studio Code

```bash
# Configurar VS Code para Odoo
odoo-configure-vscode

# Esto creará:
# - Configuraciones de debugging
# - Extensiones recomendadas
# - Configuración de Python
# - Snippets útiles
```

#### PyCharm

```bash
# Configurar PyCharm
odoo-configure-pycharm

# Configura:
# - Interpretador Python
# - Configuración de debugging
# - Plantillas de proyecto
```

## Actualizaciones

### Actualizar OdooDevs

```bash
# Para instalaciones tipo 'devs'
cd ~/workdevs
git pull origin main
./install.sh

# Para instalaciones tipo 'latest' o 'version'
./odevs-install.sh --type latest
```

### Actualizar Proyectos Existentes

```bash
# Actualizar configuración del proyecto
odoo-update-config

# Actualizar dependencias
odoo-update-deps

# Actualizar Docker
docker-compose pull
docker-compose up -d
```

## Contribuir

### Para Desarrolladores

Si quieres contribuir al proyecto odoodevs:

1. **Fork el repositorio**

2. **Clona tu fork**:

   ```bash
   git clone git@github.com:tu-usuario/odoodevs.git
   ```

3. **Crea una rama**:

   ```bash
   git checkout -b mi-feature
   ```

4. **Haz tus cambios** y commits

5. **Push a tu fork**:

   ```bash
   git push origin mi-feature
   ```

6. **Crea un Pull Request**

### Reportar Problemas

Si encuentras problemas:

1. **Verifica la documentación** primero
2. **Revisa los logs** de instalación
3. **Abre un issue** en GitHub con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs relevantes
   - Información del sistema

## Recursos Adicionales

### Documentación Oficial

- [Documentación de Odoo](https://www.odoo.com/documentation)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Repository](https://github.com/opentech-solutions/odoodevs)

### Comunidad

- [Odoo Community](https://www.odoo.com/community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/odoo)
- [Reddit r/Odoo](https://www.reddit.com/r/Odoo/)

### Tutoriales

- [Odoo Development Tutorial](https://www.odoo.com/documentation/15.0/developer.html)
- [Docker for Odoo](https://hub.docker.com/_/odoo)
- [Python Development](https://docs.python.org/3/tutorial/)

## Licencia

OdooDevs está bajo la misma licencia que Odoo. Consulta el archivo LICENSE en el repositorio para más detalles.

## Soporte

Para obtener ayuda:

1. **Consulta esta documentación**
2. **Revisa los issues** en GitHub
3. **Abre un nuevo issue** si no encuentras solución
4. **Contacta al equipo** de desarrollo

---

## Créditos

Documentación actualizada para OdooDevs v1.0.0
