# pritunl-vpn.py - Guía Completa

> **📖 [← Volver al README principal](../README.md)**

## Descripción

**pritunl-vpn.py** es un script multiplataforma para instalar o desinstalar el cliente VPN de Pritunl de forma automatizada en diferentes sistemas operativos.

## ¿Qué es una VPN?

### Definición
Una **VPN (Virtual Private Network)** es una tecnología que crea una conexión segura y encriptada entre tu dispositivo e internet, estableciendo un "túnel" virtual que protege tu tráfico de datos.

### ¿Para qué sirve una VPN?

- **🔐 Seguridad**: Encripta tu conexión para proteger datos sensibles
- **🌍 Privacidad**: Oculta tu ubicación real y dirección IP
- **🏢 Acceso remoto**: Conecta de forma segura a redes corporativas
- **🚫 Bypass de restricciones**: Accede a contenido bloqueado geográficamente
- **📡 Protección en redes públicas**: Navega seguro en WiFi públicos
- **🔄 Anonimato**: Navega sin exponer tu identidad real

### ¿Por qué usamos VPN?

En el contexto de desarrollo y empresas:

1. **Desarrollo remoto**: Acceso seguro a servidores de desarrollo y producción
2. **Colaboración**: Conexión a redes internas de la empresa desde cualquier lugar
3. **Seguridad corporativa**: Protección de datos confidenciales y proyectos
4. **Compliance**: Cumplimiento de políticas de seguridad empresariales
5. **Testing**: Pruebas desde diferentes ubicaciones geográficas

## ¿Qué es Pritunl?

### Descripción
**Pritunl** es una plataforma VPN de código abierto y gratuita que proporciona una alternativa moderna y segura a las soluciones VPN tradicionales. Está diseñada para ser fácil de usar tanto para administradores como para usuarios finales.

### Características Principales

- **🌐 Web UI moderna**: Interfaz web intuitiva y responsiva
- **🔐 Seguridad avanzada**: Encriptación AES-256 y protocolos seguros
- **👥 Gestión centralizada**: Administración de usuarios y organizaciones
- **📱 Multiplataforma**: Soporte para Windows, macOS, Linux, iOS, Android
- **⚡ Alto rendimiento**: Optimizado para conexiones rápidas y estables
- **🔄 Escalabilidad**: Soporte para miles de usuarios simultáneos
- **📊 Monitoreo**: Dashboard con estadísticas y logs en tiempo real

### ¿Qué necesitamos tener?

#### **Pritunl Server**
Para usar `pritunl-vpn.py`, necesitas:

1. **Servidor Pritunl instalado y configurado**
   - Puede ser un servidor propio o cloud
   - Debe estar accesible desde internet
   - Configurado con organizaciones y usuarios

2. **Acceso administrativo al servidor**
   - Para crear/eliminar usuarios
   - Para generar perfiles de conexión
   - Para configurar políticas de seguridad

3. **Perfiles de conexión**
   - Archivos `.ovpn` generados desde el servidor
   - Credenciales de usuario válidas

### ¿Por qué elegimos Pritunl?

#### **Ventajas sobre otros gestores VPN:**

| Característica | Pritunl | OpenVPN | WireGuard | IPSec |
|---|---|---|---|---|
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Interfaz web** | ✅ Moderna | ❌ Básica | ❌ CLI | ❌ Compleja |
| **Gestión de usuarios** | ✅ Centralizada | ⭐ Manual | ⭐ Manual | ⭐ Compleja |
| **Escalabilidad** | ✅ Excelente | ⭐ Buena | ⭐ Buena | ⭐ Buena |
| **Configuración** | ✅ Automática | ❌ Manual | ⭐ Semi-automática | ❌ Compleja |
| **Monitoreo** | ✅ Dashboard | ❌ Logs | ❌ Básico | ❌ Logs |
| **Costo** | ✅ Gratuito | ✅ Gratuito | ✅ Gratuito | ✅ Gratuito |

#### **Razones específicas:**

1. **🚀 Simplicidad**: Configuración en minutos vs horas
2. **👨‍💼 Gestión empresarial**: Perfecto para equipos de desarrollo
3. **🔧 Automatización**: API REST para integración con scripts
4. **📈 Escalabilidad**: Soporte nativo para múltiples organizaciones
5. **🎯 Enfoque moderno**: Diseñado para la era cloud y DevOps
6. **📱 UX superior**: Cliente nativo para todas las plataformas

## Instalación y Requisitos

### Requisitos Previos

```bash
# Instalar dependencias base
packages.sh --list base

# Verificar que Python 3 está instalado
python3 --version

# Verificar que pip está disponible
pip3 --version
```

### Dependencias Python

El script requiere las siguientes librerías Python:

- **rich**: Para interfaz de consola moderna y barras de progreso
- **requests**: Para descargas HTTP
- **questionary**: ~~Para prompts interactivos~~ (removido - no utilizado)

### Verificar Instalación

```bash
# Verificar que el script está disponible
ls -la pritunl-vpn.py

# Dar permisos de ejecución si es necesario
chmod +x pritunl-vpn.py
```

## Uso

### Sintaxis General

```bash
python3 pritunl-vpn.py [OPCIONES]
```

### Comandos Principales

#### **Mostrar Ayuda**

```bash
# Mostrar ayuda completa
python3 pritunl-vpn.py --help

# Mostrar versión
python3 pritunl-vpn.py --version

# Ejecutar sin parámetros (muestra ayuda)
python3 pritunl-vpn.py
```

#### **Instalar Cliente Pritunl**

```bash
# Instalar el cliente VPN de Pritunl
python3 pritunl-vpn.py --install
```

**Lo que hace:**
1. Detecta el sistema operativo
2. Verifica si ya está instalado
3. Descarga e instala el cliente apropiado
4. Configura permisos y accesos
5. Verifica la instalación

#### **Desinstalar Cliente Pritunl**

```bash
# Desinstalar el cliente VPN de Pritunl
python3 pritunl-vpn.py --remove
```

**Lo que hace:**
1. Detecta el sistema operativo
2. Verifica si está instalado
3. Desinstala el cliente y archivos relacionados
4. Limpia configuraciones y caché
5. Confirma la desinstalación

## Sistemas Operativos Soportados

### **Linux**
- **Ubuntu/Debian**: Instalación via repositorios oficiales
- **Fedora/CentOS**: Instalación via RPM packages
- **Arch Linux**: Instalación via AUR o AppImage
- **Otras distribuciones**: Instalación via AppImage

### **macOS**
- **Homebrew**: Instalación via brew
- **MacPorts**: Instalación via port
- **PKG directo**: Descarga e instalación manual

### **Windows**
- **Chocolatey**: Instalación via choco
- **Scoop**: Instalación via scoop
- **MSI directo**: Descarga e instalación manual

## Ejemplos de Uso

### **Flujo Típico de Instalación**

```bash
# 1. Instalar dependencias base
packages.sh --list base

# 2. Instalar cliente Pritunl
python3 pritunl-vpn.py --install

# 3. Verificar instalación
pritunl-client --version
```

### **Gestión de Cliente**

```bash
# Verificar si está instalado
python3 pritunl-vpn.py --install
# Si ya está instalado, muestra mensaje informativo

# Desinstalar si es necesario
python3 pritunl-vpn.py --remove

# Reinstalar desde cero
python3 pritunl-vpn.py --remove
python3 pritunl-vpn.py --install
```

### **Integración con Scripts**

```bash
#!/bin/bash
# Script de configuración automática

echo "Configurando entorno de desarrollo..."

# Instalar paquetes base
packages.sh --list base,devs

# Instalar cliente VPN
python3 pritunl-vpn.py --install

# Configurar perfil VPN (requiere archivo .ovpn)
# pritunl-client import /path/to/profile.ovpn

echo "Configuración completada"
```

## Solución de Problemas

### **Error: "Faltan dependencias"**

```bash
# Instalar dependencias Python
packages.sh --list base

# O instalar manualmente
pip3 install rich requests
```

### **Error: "No se pudo instalar"**

```bash
# Verificar permisos
sudo python3 pritunl-vpn.py --install

# Verificar conectividad
ping -c 3 github.com
```

### **Cliente no se ejecuta**

```bash
# Verificar instalación
which pritunl-client

# Verificar permisos
ls -la /usr/local/bin/pritunl-client

# Reinstalar si es necesario
python3 pritunl-vpn.py --remove
python3 pritunl-vpn.py --install
```

### **Problemas de conectividad**

```bash
# Verificar configuración de red
ip route show

# Verificar DNS
nslookup pritunl.example.com

# Probar conectividad al servidor
telnet pritunl.example.com 443
```

## Configuración Post-Instalación

### **Importar Perfil VPN**

```bash
# Importar perfil desde archivo
pritunl-client import /path/to/profile.ovpn

# Importar desde URL
pritunl-client import https://server.example.com/profile.ovpn
```

### **Conectar a VPN**

```bash
# Listar perfiles disponibles
pritunl-client list

# Conectar a un perfil
pritunl-client start profile_name

# Desconectar
pritunl-client stop profile_name
```

### **Configuración Avanzada**

```bash
# Configurar servidor personalizado
pritunl-client set server https://your-server.com

# Configurar proxy
pritunl-client set proxy http://proxy.example.com:8080

# Ver configuración actual
pritunl-client status
```

## Integración con bintools

### **Uso con otros scripts**

```bash
# Instalación completa de entorno de desarrollo
packages.sh --list base,devs,dops
python3 pritunl-vpn.py --install

# Configuración de usuario VPN
vpn_users.sh  # Requiere servidor Pritunl configurado

# Envío seguro de perfiles
bw-send.sh --file profile.ovpn --email user@company.com
```

### **Automatización**

```bash
#!/bin/bash
# setup-dev-environment.sh

set -e

echo "🚀 Configurando entorno de desarrollo..."

# Instalar herramientas base
packages.sh --list base,devs

# Instalar cliente VPN
python3 pritunl-vpn.py --install

# Configurar VPN (si hay servidor disponible)
if [ -f "vpn-profile.ovpn" ]; then
    pritunl-client import vpn-profile.ovpn
    echo "✅ Perfil VPN importado"
fi

echo "🎉 Configuración completada"
```

## Seguridad

### **Mejores Prácticas**

1. **🔐 Usar perfiles oficiales**: Solo importar perfiles de fuentes confiables
2. **🔄 Rotar credenciales**: Cambiar contraseñas regularmente
3. **📱 Dispositivos seguros**: Solo conectar desde dispositivos confiables
4. **🚫 Redes públicas**: Siempre usar VPN en WiFi públicos
5. **📊 Monitoreo**: Revisar logs de conexión regularmente

### **Consideraciones de Seguridad**

- **Certificados**: Verificar que los certificados son válidos
- **Encriptación**: Usar solo protocolos seguros (OpenVPN, WireGuard)
- **Autenticación**: Habilitar autenticación de dos factores
- **Logs**: Mantener logs de acceso y conexiones

## Soporte y Recursos

### **Documentación Oficial**
- [Pritunl Documentation](https://docs.pritunl.com/)
- [Pritunl GitHub](https://github.com/pritunl/pritunl)
- [Pritunl Client](https://client.pritunl.com/)

### **Comunidad**
- [Pritunl Community](https://community.pritunl.com/)
- [GitHub Issues](https://github.com/pritunl/pritunl/issues)
- [Reddit r/Pritunl](https://www.reddit.com/r/Pritunl/)

### **Soporte en bintools**
- **Issues**: Reportar problemas en el repositorio
- **Documentación**: Consultar otros archivos en `docs/`
- **Scripts relacionados**: `vpn_users.sh`, `bw-send.sh`

## Conclusión

`pritunl-vpn.py` es una herramienta esencial para equipos de desarrollo que necesitan acceso VPN seguro y confiable. Su integración con el ecosistema bintools proporciona una solución completa para la gestión de conexiones VPN en entornos de desarrollo y producción.

La combinación de facilidad de uso, seguridad robusta y automatización hace de Pritunl la elección ideal para organizaciones que requieren conectividad VPN moderna y escalable.
