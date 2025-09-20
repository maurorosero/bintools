# Gestión Segura de Secretos y Contraseñas

> **📖 [← Volver al README principal](../README.md)**

## Introducción

En el mundo digital actual, la gestión segura de secretos y contraseñas es fundamental para proteger nuestra información personal y empresarial. Los ataques cibernéticos están en constante evolución, y las contraseñas débiles o reutilizadas representan uno de los vectores de ataque más comunes.

### Problemas Comunes en la Gestión de Contraseñas

Desafortunadamente, muchas personas y organizaciones aún cometen errores críticos al manejar sus credenciales:

- **Compartir Contraseñas por Canales Inseguros**: Enviar contraseñas por email, mensajes de texto, WhatsApp o plataformas de chat sin cifrado
- **Almacenamiento Inseguro**: Guardar contraseñas en documentos de texto plano, hojas de cálculo, notas adhesivas físicas o archivos sin protección
- **Compartir Credenciales de Forma Masiva**: Distribuir la misma contraseña a múltiples usuarios sin control de acceso individual
- **Almacenamiento en Navegadores**: Confiar únicamente en la función "recordar contraseña" del navegador sin cifrado adicional
- **Transmisión Oral**: Compartir contraseñas críticas por teléfono o en conversaciones presenciales sin verificar la identidad del receptor

### Mejores Prácticas para la Gestión de Contraseñas

1. **Contraseñas Únicas**: Cada cuenta debe tener una contraseña diferente y compleja
2. **Autenticación de Dos Factores (2FA)**: Implementar una capa adicional de seguridad
3. **Gestores de Contraseñas**: Utilizar herramientas especializadas para almacenar y gestionar credenciales
4. **Rotación Regular**: Cambiar contraseñas periódicamente, especialmente para cuentas críticas
5. **Evitar Reutilización**: Nunca usar la misma contraseña en múltiples servicios

## Vaultwarden: Una Alternativa Open Source

Vaultwarden es una implementación alternativa del servidor Bitwarden escrita en Rust. Es una solución ligera y eficiente que ofrece compatibilidad total con los clientes oficiales de Bitwarden, pero con la ventaja de ser completamente open source y autohospedable.

### Características Principales

- **Compatibilidad Total**: Funciona con todos los clientes oficiales de Bitwarden
- **Alto Rendimiento**: Escrito en Rust, ofrece mejor rendimiento que la implementación original
- **Bajo Consumo de Recursos**: Requiere menos memoria y CPU que Bitwarden Server
- **Instalación en Servidor Propio**: Se puede desplegar completamente en tu propia infraestructura
- **Fácil Despliegue**: Se puede ejecutar como un contenedor Docker en cualquier servidor
- **Open Source**: Código fuente completamente disponible y auditable
- **API Compatible**: Mantiene la misma API que Bitwarden para máxima compatibilidad

### Ventajas de Vaultwarden

1. **Control Total**: Tienes control completo sobre tus datos y servidor
2. **Costos Reducidos**: No hay costos de suscripción para funcionalidades premium
3. **Personalización**: Puedes modificar y adaptar el código según tus necesidades
4. **Privacidad**: Tus datos nunca salen de tu infraestructura
5. **Escalabilidad**: Puedes escalar según tus necesidades específicas

## Servidor Público: vault.vaultwarden.net

Para aquellos usuarios que desean aprovechar las ventajas de Vaultwarden sin la complejidad de mantener su propio servidor, existe una opción intermedia: el servidor público `vault.vaultwarden.net`.

### ¿Qué es vault.vaultwarden.net?

Es un servidor público de Vaultwarden mantenido por la comunidad, que ofrece una alternativa gratuita al servicio oficial de Bitwarden. Este servidor permite a los usuarios disfrutar de las funcionalidades premium de Vaultwarden sin necesidad de configurar y mantener su propia infraestructura.

### Características del Servidor Público

- **Mantenimiento Comunitario**: Gestionado por voluntarios de la comunidad
- **Fácil Configuración**: Solo necesitas cambiar la URL del servidor en tu cliente
- **Sin Instalación**: No requiere conocimientos técnicos avanzados

### Ventajas de Usar vault.vaultwarden.net

1. **Simplicidad**: Configuración mínima requerida
2. **Sin Mantenimiento**: No necesitas gestionar actualizaciones o seguridad del servidor
3. **Comunidad**: Respaldado por una comunidad activa de usuarios

### Consideraciones Importantes

**Limitaciones:**
- **Dependencia Externa**: Tus datos están en un servidor que no controlas
- **Sin Garantías**: No hay SLA (Service Level Agreement) oficial
- **Capacidad Limitada**: Puede tener restricciones de almacenamiento o usuarios
- **Disponibilidad**: Depende de la disponibilidad del servidor comunitario

**Recomendaciones de Uso:**
- Ideal para usuarios individuales que quieren probar Vaultwarden
- Adecuado para uso personal y no crítico
- Considera migrar a tu propio servidor si necesitas mayor control
- Siempre mantén respaldos locales de tus datos importantes

### Configuración en Clientes

Antes de poder configurar tu cliente de Bitwarden, primero debes ir a `https://vault.vaultwarden.net` y crear una cuenta nueva. Una vez creada la cuenta, configura tu cliente de Bitwarden con:
- **URL del Servidor**: `https://vault.vaultwarden.net`
- **Email y Contraseña**: Usa las credenciales que registraste en el servidor público

## Gestión de Secretos para Desarrolladores y DevOps

### Importancia de la Gestión Segura de Secretos

En el desarrollo de software y operaciones de DevOps, la gestión segura de secretos es crítica para mantener la seguridad de las aplicaciones y la infraestructura. Los secretos incluyen contraseñas, tokens de API, claves de cifrado, certificados SSL y otros datos sensibles que deben protegerse.

### Riesgos de una Gestión Inadecuada

**Exposición de Credenciales:**
- Hardcoding de contraseñas en el código fuente
- Almacenamiento de secretos en repositorios públicos
- Compartir credenciales por canales inseguros
- Uso de contraseñas débiles o reutilizadas

**Consecuencias:**
- Acceso no autorizado a sistemas críticos
- Robo de datos sensibles
- Compromiso de la infraestructura
- Violaciones de cumplimiento normativo
- Pérdida de confianza de los usuarios

### Mejores Prácticas para Desarrolladores

1. **Nunca Hardcodear Secretos**: Usar variables de entorno o servicios de gestión de secretos
2. **Principio de Menor Privilegio**: Otorgar solo los permisos mínimos necesarios
3. **Rotación Regular**: Cambiar credenciales periódicamente
4. **Separación de Entornos**: Diferentes credenciales para desarrollo, testing y producción
5. **Auditoría y Monitoreo**: Registrar y monitorear el acceso a secretos

### Mejores Prácticas para DevOps

1. **Gestión Centralizada**: Usar herramientas como HashiCorp Vault, AWS Secrets Manager, o Azure Key Vault
2. **Cifrado en Tránsito y Reposo**: Proteger secretos durante el transporte y almacenamiento
3. **Automatización Segura**: Integrar gestión de secretos en pipelines CI/CD
4. **Respaldos Seguros**: Mantener copias de seguridad cifradas de secretos críticos
5. **Acceso Basado en Roles**: Implementar RBAC (Role-Based Access Control)

### Herramientas Recomendadas

**Para Gestión de Secretos:**
- **HashiCorp Vault**: Solución enterprise para gestión de secretos
- **AWS Secrets Manager**: Servicio gestionado de AWS
- **Azure Key Vault**: Servicio de Microsoft Azure
- **Google Secret Manager**: Servicio de Google Cloud

**Para Desarrollo:**
- **dotenv**: Variables de entorno para desarrollo local
- **SOPS**: Cifrado de archivos de configuración
- **Ansible Vault**: Gestión de secretos en Ansible
- **Terraform**: Gestión de secretos en infraestructura como código

## Importancia de la Gestión CLI para Equipos DevOps y Desarrollo

### ¿Por qué la Consola es Crucial en DevOps y Desarrollo?

La gestión mediante línea de comandos (CLI) es fundamental en entornos DevOps y de desarrollo por varias razones técnicas y operativas:

#### **Automatización y Escalabilidad**

**Scripts y Automatización:**
- **CI/CD Pipelines**: Los pipelines de integración continua requieren comandos automatizados
- **Despliegues Automáticos**: La gestión de secretos debe integrarse en procesos automatizados
- **Escalabilidad**: Los equipos grandes necesitan herramientas que funcionen sin intervención manual
- **Reproducibilidad**: Los comandos CLI garantizan resultados consistentes en diferentes entornos

#### **Integración con Herramientas DevOps**

**Compatibilidad Universal:**
- **Contenedores**: Docker, Kubernetes, Podman requieren gestión CLI
- **Orquestadores**: Ansible, Terraform, Chef se integran mejor con CLI
- **Monitoreo**: Prometheus, Grafana, ELK Stack funcionan principalmente por CLI
- **Cloud Providers**: AWS CLI, Azure CLI, GCP CLI son herramientas estándar

#### **Eficiencia Operativa**

**Velocidad y Precisión:**
- **Sin Interfaces Gráficas**: Los servidores headless requieren herramientas CLI
- **Acceso Remoto**: SSH y conexiones remotas funcionan mejor con CLI
- **Menor Latencia**: Comandos directos son más rápidos que interfaces web
- **Menos Errores**: Los comandos son más precisos que interfaces gráficas

#### **Seguridad y Auditoría**

**Trazabilidad Completa:**
- **Logs Detallados**: Todos los comandos quedan registrados en historial
- **Auditoría**: Fácil seguimiento de quién hizo qué y cuándo
- **Seguridad**: Menos superficie de ataque que interfaces web
- **Control de Acceso**: Integración con sistemas de autenticación empresariales

#### **Flexibilidad y Personalización**

**Adaptabilidad:**
- **Scripts Personalizados**: Creación de herramientas específicas para cada equipo
- **Integración Custom**: Conexión con herramientas internas de la empresa
- **Configuración Avanzada**: Parámetros específicos para cada entorno
- **Extensibilidad**: Fácil agregar nuevas funcionalidades

### Beneficios de CLI vs Interfaces Gráficas

| Aspecto | CLI | GUI |
|---------|-----|-----|
| **Automatización** | ✅ Excelente | ❌ Limitada |
| **Escalabilidad** | ✅ Sin límites | ❌ Limitada |
| **Integración** | ✅ Nativa | ❌ Compleja |
| **Velocidad** | ✅ Muy rápida | ❌ Más lenta |
| **Recursos** | ✅ Mínimos | ❌ Altos |
| **Acceso Remoto** | ✅ Perfecto | ❌ Problemático |
| **Auditoría** | ✅ Completa | ❌ Limitada |
| **Personalización** | ✅ Total | ❌ Limitada |

## Cómo bintools Aporta al Manejo Seguro de Contraseñas

### Herramientas Especializadas de bintools

El proyecto bintools incluye herramientas específicamente diseñadas para mejorar la gestión segura de contraseñas y secretos, especialmente integradas con Bitwarden y Vaultwarden:

#### **Instalación Automática de Bitwarden**

bintools facilita la instalación de Bitwarden en múltiples sistemas operativos:

```bash
# Instalar o actualizar paquetes base
packages.sh --list base
# Instalar Bitwarden Desktop y CLI automáticamente
packages.sh --list bwdn
```

**Características:**
- **Instalación Multiplataforma**: Ubuntu, Debian, Fedora, CentOS, Arch Linux, macOS
- **Múltiples Métodos**: Snap, AUR, Homebrew según el sistema
- **CLI Incluido**: Instala automáticamente `bw` (Bitwarden CLI)
- **Detección Inteligente**: Usa el método de instalación óptimo para cada sistema

#### **Scripts de Integración con Bitwarden**

##### `bw-send.sh` - Envío Seguro de Archivos y Texto

Herramienta para compartir información sensible de forma segura usando Bitwarden Send:

**Funcionalidades:**
- **Envío de Archivos**: Sube archivos individuales o múltiples archivos
- **Envío de Texto**: Comparte texto directamente desde línea de comandos
- **Expiración Configurable**: Establece cuándo expira el enlace (por defecto: 2 días)
- **Protección con Contraseña**: Protege el enlace con contraseña opcional
- **Límite de Accesos**: Controla cuántas veces se puede acceder al enlace
- **Notas Descriptivas**: Agrega contexto al envío

**Ejemplos de uso:**
```bash
# Enviar texto confidencial
bw-send.sh --text "Token de API: abc123xyz"

# Enviar archivo con expiración personalizada
bw-send.sh --file documento.pdf --expiration 7

# Enviar con contraseña y límite de accesos
bw-send.sh --file config.json --password "secret123" --max-access 3
```

##### `bw-ghpersonal.sh` - Obtención Automática de Tokens GitHub

Automatiza la obtención de tokens de GitHub desde Bitwarden:

**Funcionalidades:**
- **Búsqueda Automática**: Busca el token en Bitwarden usando el usuario actual
- **Usuario Dinámico**: Reemplaza automáticamente el nombre de usuario
- **Integración Completa**: Guarda el token en el keyring de la computadora automáticamente
- **Verificación**: Confirma que el token se guardó correctamente

**Uso:**
```bash
# Obtener y guardar token de GitHub automáticamente
bw-ghpersonal.sh
```

#### **Manejo de 2FA mediante Bitwarden CLI**

Bitwarden CLI (`bw`) proporciona funcionalidades avanzadas para gestionar autenticación de dos factores (2FA) de forma automatizada:

**Configuración Inicial:**
```bash
# Configurar Bitwarden CLI con API key (recomendado para automatización)
bw config server https://vault.vaultwarden.net
bw login --apikey

# O configurar con servidor propio
bw config server https://tu-servidor-vaultwarden.com
bw login --apikey
```

**Gestión de 2FA:**

**1. Generar Códigos TOTP:**
```bash
# Obtener código TOTP para un elemento específico
bw get totp "GitHub Personal"

# Obtener código TOTP usando ID del elemento
bw get totp 12345678-1234-1234-1234-123456789abc

# Obtener código TOTP en formato raw (solo el código)
bw get totp "GitHub Personal" --raw
```

**2. Autenticación Automática:**
```bash
# Usar código TOTP para autenticación automática
export GITHUB_TOTP=$(bw get totp "GitHub Personal" --raw)
# Usar el código TOTP en scripts de automatización
```

**3. Gestión de Sesiones:**
```bash
# Verificar estado de la sesión
bw status

# Cerrar sesión
bw logout

# Iniciar sesión con API key (para automatización)
bw login --apikey
```

**Casos de Uso Prácticos:**

**Para Desarrolladores:**
```bash
# Script para obtener código 2FA de GitHub automáticamente
#!/bin/bash
# get-github-2fa.sh
GITHUB_TOTP=$(bw get totp "GitHub Personal" --raw)
echo "GitHub 2FA Code: $GITHUB_TOTP"
```

**Para DevOps:**
```bash
# Integración con CI/CD usando 2FA
#!/bin/bash
# deploy-with-2fa.sh
export GITHUB_TOTP=$(bw get totp "GitHub CI" --raw)
export GITLAB_TOTP=$(bw get totp "GitLab Production" --raw)

# Usar códigos 2FA en despliegues automatizados
gh auth login --with-token < <(echo "$GITHUB_TOKEN")
```

**Para Administradores:**
```bash
# Script de monitoreo de 2FA
#!/bin/bash
# monitor-2fa.sh
for service in "GitHub Personal" "GitLab Work" "AWS Root"; do
    if bw get totp "$service" --raw >/dev/null 2>&1; then
        echo "✅ 2FA disponible para: $service"
    else
        echo "❌ 2FA no disponible para: $service"
    fi
done
```

**Ventajas del 2FA con Bitwarden CLI:**

1. **Automatización Completa**: Generación automática de códigos TOTP
2. **Integración Transparente**: Se integra perfectamente con scripts existentes
3. **Seguridad Mejorada**: Códigos TOTP generados dinámicamente
4. **Gestión Centralizada**: Todos los códigos 2FA en un solo lugar
5. **Acceso Programático**: Ideal para CI/CD y automatización

**Consideraciones de Seguridad:**

- **API Keys**: Usar API keys para automatización en lugar de contraseñas
- **Rotación**: Rotar API keys periódicamente
- **Acceso Limitado**: Configurar permisos mínimos necesarios
- **Auditoría**: Monitorear el uso de códigos 2FA generados
- **Respaldos**: Mantener respaldos seguros de la configuración

#### **Gestión de Tokens Git (`git-tokens.py`)**

Sistema especializado para gestionar tokens de autenticación de servicios Git usando el keyring del sistema:

**Servicios Git Soportados:**
- **GitHub**: Tokens para API, repositorios privados, GitHub CLI
- **GitLab**: Tokens para API, CI/CD, repositorios privados
- **Forgejo**: Tokens para API y repositorios (servidor auto-hospedado)
- **Gitea**: Tokens para API y repositorios (servidor auto-hospedado)
- **Bitbucket Cloud**: Tokens para API y repositorios
- **Bitbucket Server**: Tokens para API y repositorios on-premise

**Características de Seguridad:**
- **Almacenamiento en Keyring**: Usa el keyring nativo del sistema operativo
- **Cifrado Automático**: Tokens cifrados con base64 antes del almacenamiento
- **Gestión por Usuario**: Soporte para múltiples usuarios por servicio Git
- **Etiquetado Inteligente**: Formato `[servicio]-[modo]-[uso]` para organización
- **Eliminación Segura**: Borra tokens sin dejar rastros en el sistema

**Ejemplos de uso:**
```bash
# Guardar token de GitHub (se pedirá por consola)
git-tokens.py set github-personal

# Guardar token de GitHub con token específico
git-tokens.py set github-personal --token 'ghp_xxxxx'

# Guardar token de GitLab cloud para CI/CD (DEBE especificar modo)
git-tokens.py set gitlab-c-cicd --token 'glpat_xxxxx'

# Guardar token de servidor Gitea auto-hospedado
git-tokens.py set gitea-personal --token 'ghp_xxxxx'

# Guardar token de Forgejo on-premise (DEBE especificar modo)
git-tokens.py set forgejo-o-empresa --token 'ghp_xxxxx'

# Obtener token
git-tokens.py get github-personal

# Obtener token en formato raw (solo el token)
git-tokens.py get github-personal --raw

# Listar todos los tokens guardados
git-tokens.py list

# Eliminar token específico
git-tokens.py delete github-personal

# Listar servicios soportados
git-tokens.py list-services
```

### Ventajas de Usar bintools para Gestión de Secretos

#### **Automatización Completa**
- **Instalación Automática**: Configura Bitwarden/Vaultwarden sin intervención manual
- **Integración Transparente**: Los scripts se conectan automáticamente con Bitwarden CLI
- **Flujo de Trabajo Unificado**: Una sola herramienta para múltiples tareas de seguridad

#### **Seguridad Mejorada**
- **Almacenamiento en Keyring**: Los tokens se guardan usando el keyring del sistema
- **Cifrado Automático**: Todos los secretos se cifran automáticamente
- **Gestión de Expiración**: Control automático de la vida útil de los enlaces
- **Auditoría**: Registro de todas las operaciones de gestión de secretos

#### **Facilidad de Uso**
- **Interfaz Consistente**: Todos los scripts siguen el mismo patrón de uso
- **Documentación Completa**: Ayuda integrada en cada herramienta
- **Modo de Prueba**: Verificación antes de ejecutar cambios
- **Multiplataforma**: Funciona igual en Linux, macOS y Windows

#### **Integración con DevOps**
- **CI/CD Ready**: Los scripts se pueden integrar en pipelines de automatización
- **Variables de Entorno**: Soporte completo para entornos de desarrollo y producción
- **API Compatible**: Integración con herramientas de gestión de secretos empresariales

### Casos de Uso Prácticos

#### **Para Desarrolladores Individuales**
```bash
# Configurar entorno completo de seguridad
packages.sh --list bwdn          # Instalar Bitwarden
bw-ghpersonal.sh                 # Configurar token GitHub
git-tokens.py set gitlab-c-dev --token 'glpat_xxxxx'  # Configurar GitLab
```

#### **Para Equipos de Desarrollo**
```bash
# Compartir credenciales de desarrollo de forma segura
bw-send.sh --text "DB_PASSWORD=secret123" --expiration 7 --max-access 5

# Compartir archivos de configuración
bw-send.sh --file docker-compose.yml --password "team123"
```

#### **Para DevOps y Administradores**
```bash
# Gestionar tokens de servicios Git
git-tokens.py set github-personal --token 'ghp_xxxxx'
git-tokens.py set gitlab-c-prod --token 'glpat_xxxxx'
git-tokens.py set gitea-personal --token 'ghp_xxxxx'

# Compartir certificados SSL
bw-send.sh --file ssl-cert.pem --expiration 30 --password "ssl2024"
```

### Beneficios Específicos de bintools

1. **Reducción de Errores**: Automatización elimina errores humanos en gestión de secretos
2. **Consistencia**: Mismo flujo de trabajo en todos los sistemas operativos
3. **Seguridad por Defecto**: Todas las herramientas implementan mejores prácticas de seguridad
4. **Integración Nativa**: Funciona perfectamente con Bitwarden y Vaultwarden
5. **Escalabilidad**: Se adapta desde desarrolladores individuales hasta equipos grandes
6. **Mantenimiento**: Actualizaciones automáticas y gestión de dependencias

## Diferencias Principales entre Bitwarden y Vaultwarden

### Bitwarden (Servicio Oficial)

**Ventajas:**
- Servicio gestionado profesionalmente
- Soporte técnico oficial
- Actualizaciones automáticas
- Infraestructura robusta y redundante
- Cumplimiento de estándares de seguridad (SOC 2, etc.)

**Desventajas:**
- Costos de suscripción para funcionalidades avanzadas
- Dependencia de servicios externos
- Menos control sobre los datos
- Limitaciones en personalización

### Vaultwarden (Implementación Alternativa)

**Ventajas:**
- Completamente libre
- Control total sobre los datos
- Mejor rendimiento
- Menor consumo de recursos
- Código fuente abierto y auditable
- Funcionalidades premium incluidas por defecto

**Desventajas:**
- Requiere conocimientos técnicos para el despliegue
- Responsabilidad propia del mantenimiento y seguridad
- Sin soporte técnico oficial
- Necesidad de gestionar actualizaciones manualmente

### Comparación Técnica

| Aspecto | Bitwarden | Vaultwarden (Propio) | vault.vaultwarden.net |
|---------|-----------|---------------------|----------------------|
| **Lenguaje** | C# | Rust | Rust |
| **Recursos** | Mayor consumo | Menor consumo | Menor consumo |
| **Despliegue** | Servicio gestionado | Autohospedado | Servidor comunitario |
| **Costo** | Suscripción requerida | Gratuito | Gratuito |
| **Control** | Limitado | Total | Limitado |
| **Soporte** | Oficial | Comunidad | Comunidad |
| **Actualizaciones** | Automáticas | Manuales | Automáticas |
| **Mantenimiento** | Bitwarden Inc. | Usuario | Comunidad |

## Recomendaciones de Implementación

### Para Usuarios Individuales
- **Bitwarden**: Ideal si prefieres simplicidad y no quieres gestionar infraestructura
- **vault.vaultwarden.net**: Excelente opción para probar Vaultwarden sin configuración
- **Vaultwarden (Propio)**: Recomendado si tienes conocimientos técnicos y valoras el control total

### Para Organizaciones
- **Bitwarden**: Mejor opción para empresas que requieren soporte oficial y cumplimiento normativo
- **Vaultwarden (Propio)**: Adecuado para organizaciones con recursos técnicos y necesidades específicas de personalización
- **vault.vaultwarden.net**: No recomendado para uso empresarial por falta de garantías

### Consideraciones de Seguridad

Independientemente de la solución elegida, es fundamental:

1. **Implementar 2FA**: Siempre activar autenticación de dos factores
2. **Respaldos Regulares**: Mantener copias de seguridad de la base de datos
3. **Actualizaciones**: Mantener el software actualizado
4. **Monitoreo**: Implementar sistemas de monitoreo y alertas
5. **Acceso Restringido**: Limitar el acceso al servidor y base de datos