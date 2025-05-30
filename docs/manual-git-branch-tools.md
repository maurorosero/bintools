# Manual Completo del Ecosistema Git Branch Tools

<!-- PARSEABLE_METADATA_START
purpose: Manual completo y detallado del ecosistema de herramientas Git Branch Tools
technology: Python, Git, Bash, APIs Git
status: Development
PARSEABLE_METADATA_END -->

<!-- CURRENT_VERSION_PLACEHOLDER -->

## Tabla de Contenidos

1. [Introducción y Visión General](#introducción-y-visión-general)
   - [¿Qué es el Ecosistema Git Branch Tools?](#qué-es-el-ecosistema-git-branch-tools)
   - [Filosofía y Principios de Diseño](#filosofía-y-principios-de-diseño)
   - [Componentes del Ecosistema](#componentes-del-ecosistema)
   - [Requisitos y Dependencias](#requisitos-y-dependencias)
   - [Instalación y Configuración Inicial](#instalación-y-configuración-inicial)

2. [Arquitectura del Sistema](#arquitectura-del-sistema)
   - [Diagrama de Componentes](#diagrama-de-componentes)
   - [Flujo de Datos entre Herramientas](#flujo-de-datos-entre-herramientas)
   - [Detección Automática de Contexto](#detección-automática-de-contexto)
   - [Niveles de Capacidades](#niveles-de-capacidades)
   - [Integración con Plataformas Git](#integración-con-plataformas-git)

3. [Git Tokens Manager - Gestión Segura de Tokens](#git-tokens-manager---gestión-segura-de-tokens)
   - [Introducción y Propósito](#introducción-y-propósito)
   - [Servicios Git Soportados](#servicios-git-soportados)
   - [Modos de Operación](#modos-de-operación)
   - [Sistema de Encriptación y Keyring](#sistema-de-encriptación-y-keyring)
   - [Comandos y Sintaxis](#comandos-y-sintaxis)
   - [Modo Interactivo vs Línea de Comandos](#modo-interactivo-vs-línea-de-comandos)
   - [Integración con el Ecosistema](#integración-con-el-ecosistema)
   - [Configuración y Seguridad](#configuración-y-seguridad)

4. [Branch Git Helper - Gestión Inteligente de Ramas](#branch-git-helper---gestión-inteligente-de-ramas)
   - [Introducción y Propósito](#introducción-y-propósito)
   - [Tipos de Branch Soportados](#tipos-de-branch-soportados)
   - [Detección Automática de Contexto](#detección-automática-de-contexto)
   - [Prioridades de Branch Base](#prioridades-de-branch-base)
   - [Comandos y Sintaxis](#comandos-y-sintaxis)
   - [Ejemplos Prácticos](#ejemplos-prácticos)

5. [Git Integration Manager - Orquestador de Workflows](#git-integration-manager---orquestador-de-workflows)
   - [Introducción y Propósito](#introducción-y-propósito-2)
   - [Funcionalidades Principales](#funcionalidades-principales)
   - [Sistema de Validación Híbrida](#sistema-de-validación-híbrida)
   - [Configuración Automática del Remoto](#configuración-automática-del-remoto)
   - [Comandos y Sintaxis](#comandos-y-sintaxis-2)
   - [Workflows Automatizados](#workflows-automatizados)
   - [Integración con APIs](#integración-con-apis)

6. [Branch Workflow Validator - Validación Contextual](#branch-workflow-validator---validación-contextual)
   - [Introducción y Propósito](#introducción-y-propósito-3)
   - [Niveles de Validación](#niveles-de-validación)
   - [Reglas de Validación](#reglas-de-validación)
   - [Integración con Git Hooks](#integración-con-git-hooks)
   - [Comandos y Sintaxis](#comandos-y-sintaxis-3)

7. [Workflows Completos End-to-End](#workflows-completos-end-to-end)
   - [Workflow de Feature Development](#workflow-de-feature-development)
   - [Workflow de Hotfix](#workflow-de-hotfix)
   - [Workflow de Release](#workflow-de-release)
   - [Workflow Empresarial Completo](#workflow-empresarial-completo)

8. [Configuración Avanzada](#configuración-avanzada)
   - [Variables de Entorno](#variables-de-entorno)
   - [Archivos de Configuración](#archivos-de-configuración)
   - [Personalización por Proyecto](#personalización-por-proyecto)
   - [Integración con CI/CD](#integración-con-cicd)

9. [Troubleshooting y FAQ](#troubleshooting-y-faq)
   - [Problemas Comunes](#problemas-comunes)
   - [Diagnóstico de Errores](#diagnóstico-de-errores)
   - [Preguntas Frecuentes](#preguntas-frecuentes)
   - [Logs y Debugging](#logs-y-debugging)

10. [Casos de Uso Avanzados](#casos-de-uso-avanzados)
    - [Desarrollo Multi-repositorio](#desarrollo-multi-repositorio)
    - [Equipos Distribuidos](#equipos-distribuidos)
    - [Integración Empresarial](#integración-empresarial)
    - [Automatización DevOps](#automatización-devops)

---

## Introducción y Visión General

### ¿Qué es el Ecosistema Git Branch Tools?

El Ecosistema Git Branch Tools es una suite integrada de herramientas Python diseñada para automatizar y optimizar los flujos de trabajo con Git. Este ecosistema está compuesto por cuatro componentes principales que trabajan en conjunto para proporcionar una experiencia de desarrollo fluida y adaptativa.

El ecosistema se adapta automáticamente al contexto de tu proyecto, detectando si trabajas en un entorno local, híbrido o remoto, y ajustando su comportamiento en consecuencia. Esto significa que las mismas herramientas pueden funcionar tanto para un desarrollador individual trabajando en proyectos personales como para equipos grandes con workflows complejos de CI/CD.

**¿Por qué existe este ecosistema?**

Las herramientas Git nativas son poderosas pero de bajo nivel. Los desarrolladores constantemente repiten las mismas secuencias de comandos, cometen errores evitables y pierden tiempo en tareas repetitivas. El ecosistema Git Branch Tools elimina esta fricción proporcionando:

- **Automatización inteligente** de operaciones Git comunes
- **Validación contextual** que previene errores antes de que ocurran
- **Adaptación automática** al tamaño y complejidad del proyecto
- **Integración nativa** con plataformas Git (GitHub, GitLab, etc.)
- **Fallbacks elegantes** cuando las funcionalidades avanzadas no están disponibles

### Filosofía y Principios de Diseño

#### Adaptabilidad Contextual

El principio fundamental del ecosistema es la adaptabilidad contextual. Las herramientas detectan automáticamente el contexto de trabajo (LOCAL, HYBRID, REMOTE) y ajustan su comportamiento, validaciones y flujos de trabajo en consecuencia.

**¿Cómo funciona en la práctica?**

```bash
# Mismo comando, comportamiento diferente según contexto

# Proyecto personal (LOCAL): Permisivo y educativo
branch-git-helper.py feature "nueva-idea"
# → Crea branch, sugiere mejores prácticas, no bloquea

# Proyecto de equipo (HYBRID): Balanceado
branch-git-helper.py feature "nueva-idea"
# → Valida formato, configura upstream, hace push automático

# Proyecto empresarial (REMOTE): Estricto y compliant
branch-git-helper.py feature "nueva-idea"
# → Valida políticas corporativas, requiere formato específico, auditoría completa
```

#### Progresividad

El ecosistema está diseñado para crecer con tus proyectos. Puedes comenzar con flujos simples en contexto LOCAL y evolucionar hacia workflows empresariales complejos sin cambiar las herramientas básicas.

&nbsp;&nbsp;**Evolución natural del workflow:**

 1. **Desarrollador individual**: Herramientas sugieren mejores prácticas.
 2. **Equipo pequeño**: Herramientas aplican convenciones básicas
 3. **Organización**: Herramientas enforzan políticas corporativas

#### Interoperabilidad

Cada componente puede funcionar de forma independiente, pero su verdadero poder se revela cuando trabajan en conjunto. Las herramientas comparten información de contexto, configuración y estado para proporcionar una experiencia cohesiva.

#### Fallback Graceful

Cuando las funcionalidades avanzadas (APIs, tokens) no están disponibles, el ecosistema degrada graciosamente a operaciones locales básicas, manteniendo siempre la funcionalidad core.

### Componentes del Ecosistema

#### Git Tokens Manager (`git-tokens.py`)

**Propósito**: Gestión segura de tokens de autenticación para APIs Git

Herramienta auxiliar fundamental que centraliza y securiza el acceso a las APIs de las plataformas Git. Utiliza el keyring del sistema operativo para almacenamiento seguro y soporta tanto servicios cloud como on-premise.

**Funcionalidades clave:**
- Almacenamiento encriptado en keyring del sistema
- Soporte para múltiples plataformas (GitHub, GitLab, Bitbucket, Gitea, Forgejo)
- Modo interactivo y línea de comandos
- Configuración automática de servicios

#### Branch Git Helper (`branch-git-helper.py`)

**Propósito**: Creación inteligente de branches con convenciones automáticas

Sistema inteligente de gestión de branches que automatiza la creación, naming y configuración de ramas de trabajo. Detecta automáticamente el contexto del proyecto y selecciona las mejores prácticas apropiadas.

**Funcionalidades clave:**
- Detección automática de contexto (LOCAL/HYBRID/REMOTE)
- Tipos de branch predefinidos (feature, fix, hotfix, docs, etc.)
- Selección inteligente de rama base
- Configuración automática de upstream tracking

#### Git Integration Manager (`git-integration-manager.py`)

**Propósito**: Orquestación completa de workflows de integración

Orquestador de workflows completos que automatiza procesos desde la creación de branches hasta el merge final. Integra con APIs de plataformas Git cuando están disponibles y proporciona fallbacks manuales cuando no.

**Funcionalidades clave:**
- Configuración automática de branch protection rules remotas
- Creación automática de Pull Requests
- Validación pre-integración completa
- Workflows end-to-end automatizados

#### Branch Workflow Validator (`branch-workflow-validator.py`)

**Propósito**: Validación contextual de operaciones Git

Validador contextual que verifica operaciones Git antes de ejecutarlas. Implementa diferentes niveles de validación según el contexto detectado y puede integrarse con git hooks para validación automática.

**Funcionalidades clave:**
- Validación adaptativa por contexto
- Integración con git hooks (pre-commit, pre-push)
- Prevención de operaciones riesgosas
- Educación sobre mejores prácticas

### Requisitos y Dependencias

#### Requisitos Básicos

- **Python 3.8 o superior**
- **Git 2.20 o superior**
- **Sistema operativo**: Linux, macOS, Windows

#### Dependencias Python

**Obligatorias:**
- `keyring` - Para gestión segura de tokens
- `subprocess` - Para ejecución de comandos Git (incluido en Python)
- `pathlib` - Para manejo de rutas (incluido en Python)

**Opcionales pero Recomendadas:**
- `colorama` - Para salida colorizada en terminal
- `rich` - Para interfaces interactivas mejoradas
- `requests` - Para integración con APIs Git

#### Dependencias del Sistema

- `git` - Cliente Git instalado y configurado
- Keyring del sistema operativo configurado
- Acceso a internet (para funcionalidades de API)

### Instalación y Configuración Inicial

#### Instalación

**IMPORTANTE**: Las Git Branch Tools son parte del ecosistema **braintools** y se instalan automáticamente con él. No requieren instalación separada.

#### Verificación de Instalación

```bash
# Verificar que las herramientas están disponibles
which git-integration-manager.py
which branch-git-helper.py
which git-tokens.py
which branch-workflow-validator.py

# O verificar versiones
git-integration-manager.py --version
branch-git-helper.py --version
git-tokens.py --version
branch-workflow-validator.py --version
```

#### Configuración Inicial de Git

```bash
# Configurar identidad Git (si no está configurada)
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@ejemplo.com"

# Verificar configuración
git config --list
```

#### Configuración de Tokens (Opcional)

```bash
# Servicios Cloud
git-tokens.py set github-integration              # GitHub
git-tokens.py set gitlab-c-integration            # GitLab Cloud
git-tokens.py set bitbucket-c-integration         # Bitbucket Cloud
git-tokens.py set forgejo-c-integration           # Forgejo Cloud

# Servicios On-Premise
git-tokens.py set gitlab-o-integration --host gitlab.empresa.com    # GitLab Self-Hosted
git-tokens.py set bitbucket-o-integration --host bitbucket.empresa.com  # Bitbucket Server
git-tokens.py set gitea-integration --host gitea.empresa.com        # Gitea
git-tokens.py set forgejo-o-integration --host forgejo.empresa.com  # Forgejo Self-Hosted

# Listar todos los servicios soportados
git-tokens.py list-services

# Verificar si un token específico está configurado
git-tokens.py get github-integration
git-tokens.py get gitlab-c-integration
```

#### Verificación de Funcionamiento

```bash
# Verificar que las herramientas funcionan
branch-git-helper.py status
git-integration-manager.py status
branch-workflow-validator.py status
```

---

## Componentes y Estructura
### Arquitectura del Ecosistema

La arquitectura del Ecosistema Git Branch Tools está diseñada siguiendo principios de modularidad, extensibilidad y adaptabilidad. El sistema se compone de tres capas principales que trabajan en conjunto para proporcionar una experiencia de desarrollo fluida y segura.

La arquitectura del ecosistema está diseñada para proporcionar cuatro características fundamentales que garantizan su efectividad y longevidad.

En primer lugar, el sistema es **robusto** gracias a su implementación de manejo de errores y mecanismos de recuperación que aseguran la continuidad de las operaciones incluso en situaciones adversas.

La **escalabilidad** es otra característica clave, permitiendo que el ecosistema se adapte sin problemas a proyectos de cualquier envergadura, desde pequeños repositorios personales hasta grandes proyectos empresariales.

El código está estructurado de manera **mantenible**, siguiendo principios de modularidad y documentación exhaustiva que facilitan su actualización y mantenimiento a largo plazo.

Finalmente, el sistema es **extensible** por diseño, permitiendo la incorporación de nuevas funcionalidades y características de manera sencilla sin comprometer la estabilidad del núcleo existente.


### Diagrama de Componentes

El ecosistema Git Branch Tools sigue una arquitectura modular donde cada componente tiene responsabilidades específicas pero puede interactuar con los demás para proporcionar funcionalidades avanzadas.

```
┌─────────────────────────────────────────────────────────────┐
│                    ECOSISTEMA GIT BRANCH TOOLS              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Git Tokens    │  │  Branch Helper  │  │ Integration  │ │
│  │    Manager      │◄─┤                 │◄─┤   Manager    │ │
│  │                 │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│           ▲                     ▲                    ▲      │
│           │                     │                    │      │
│           └─────────────────────┼────────────────────┘      │
│                                 ▼                           │
│                    ┌─────────────────────────┐              │
│                    │   Workflow Validator    │              │
│                    │                         │              │
│                    └─────────────────────────┘              │
├─────────────────────────────────────────────────────────────┤
│                     CAPA DE DETECCIÓN                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │    Context      │  │   Platform      │  │  Repository  │ │
│  │   Detector      │  │   Detector      │  │   Analyzer   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      CAPA DE DATOS                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │     Keyring     │  │   Git Config    │  │   API Cache  │ │
│  │    (Tokens)     │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos entre Herramientas

#### Flujo de Información Contextual

El flujo de información contextual es fundamental para la operación coordinada del ecosistema. Este flujo describe cómo las diferentes herramientas intercambian información y se adaptan al contexto del repositorio.

1. **Detección de Contexto**: Cada herramienta inicia detectando el contexto del repositorio (LOCAL, HYBRID, REMOTE)
2. **Configuración Adaptativa**: Basándose en el contexto, se cargan las configuraciones apropiadas
3. **Intercambio de Estado**: Las herramientas comparten información de estado a través de archivos temporales y variables de entorno
4. **Validación Cruzada**: El validator verifica las operaciones propuestas por otras herramientas

#### Flujo de Autenticación

El flujo de autenticación es un proceso crítico que garantiza la seguridad de las operaciones con servicios remotos. Este flujo está diseñado para manejar credenciales de forma segura y eficiente, minimizando la exposición de datos sensibles.

El proceso de autenticación sigue un patrón de cuatro pasos:

1. **Solicitud de Token**: Integration Manager solicita tokens al Token Manager
2. **Recuperación Segura**: Token Manager recupera credenciales del keyring del sistema
3. **Validación de Token**: Se verifica la validez del token con la plataforma
4. **Cache Temporal**: Tokens válidos se cachean temporalmente para operaciones múltiples

### Detección Automática de Contexto

> **📖 Para información completa sobre detección de contexto, ver:** [Detección Automática de Contexto - Arquitectura del Sistema](#detección-automática-de-contexto)

El Branch Git Helper utiliza el mismo sistema de detección automática de contexto descrito en la arquitectura del sistema. Esta detección influye directamente en:

#### Comportamiento Específico por Contexto

**En Contexto LOCAL:**
- Validaciones permisivas (warnings en lugar de errores)
- Push automático deshabilitado (control manual)
- Mensajes educativos sin bloqueos
- Upstream tracking opcional

**En Contexto HYBRID:**
- Validaciones moderadas (balance productividad/control)
- Push automático habilitado
- Upstream tracking requerido
- Sincronización automática con remoto

**En Contexto REMOTE:**
- Validaciones estrictas (cumplimiento obligatorio)
- Push automático con auditoría
- Upstream tracking obligatorio
- Integración completa con políticas corporativas

#### Adaptación del Naming y Validación

El contexto detectado determina:
- **Formato de naming**: Desde sugerencias hasta requisitos estrictos
- **Validación de rama base**: Automática según disponibilidad
- **Configuración de upstream**: Manual, automática u obligatoria
- **Sincronización previa**: Opcional, recomendada u obligatoria

### Niveles de Capacidades

El sistema de detección automática de contexto evalúa tres factores principales para determinar el contexto:

1. **Estructura del Repositorio**

   - Presencia de ramas específicas (develop, staging, etc.)
   - Configuración de remotos
   - Estado del repositorio (inicializado, clonado, etc.)

2. **Historia del Proyecto**

   - Número de contribuidores
   - Cantidad de commits
   - Patrones de commits y ramas

3. **Configuración del Entorno**

   - Presencia de CI/CD
   - Configuración de hooks
   - Integración con servicios externos

### Contextos Soportados

El sistema puede detectar tres tipos de contextos:

**LOCAL**: Repositorios sin remotos, ideales para desarrollo personal y proyectos pequeños. Caracterizado por:

  - Sin integración con servicios remotos
  - Máxima flexibilidad en el flujo de trabajo
  - Ideal para prototipos y experimentación
  - Sin restricciones de políticas empresariales

**HYBRID**: Repositorios con remotos pero sin estructura compleja, perfecto para equipos pequeños o proyectos en transición. Caracterizado por:

  - Integración básica con servicios remotos
  - Estructura de ramas adaptable
  - Balance entre flexibilidad y control
  - Soporte para CI/CD opcional

**REMOTE**: Repositorios con estructura empresarial completa, diseñado para equipos grandes y proyectos corporativos. Caracterizado por:

  - Integración completa con servicios empresariales
  - Estructura de ramas estricta y definida
  - Cumplimiento de políticas y estándares corporativos
  - CI/CD y validaciones automatizadas obligatorias

### Impacto en el Comportamiento

El contexto detectado influye en:

1. **Reglas de Validación**

   - LOCAL: Reglas mínimas, máxima flexibilidad
   - HYBRID: Reglas moderadas, balance entre flexibilidad y estructura
   - REMOTE: Reglas estrictas, cumplimiento de políticas empresariales

2. **Flujos de Trabajo**

   - LOCAL: Flujos simplificados, sin validaciones complejas
   - HYBRID: Flujos adaptables según necesidades
   - REMOTE: Flujos completos con todas las validaciones

3. **Integración con Servicios**

   - LOCAL: Sin integración con servicios externos
   - HYBRID: Integración opcional
   - REMOTE: Integración completa con todos los servicios

### Ejemplo de Adaptación

#### Algoritmo de Detección

La herramienta analiza múltiples factores para determinar el contexto:

```python
def detect_context(self) -> str:
    contributors = self.git_repo.get_contributor_count()
    commits = self.git_repo.get_commit_count()
    remotes = self.git_repo.get_remote_count()
    has_ci = self.git_repo.detect_ci_presence()
    has_develop = self.git_repo.branch_exists("develop")
    has_staging = self.git_repo.branch_exists("staging")

    if remotes == 0:
        return "LOCAL"
    elif contributors <= 2 and commits < 100 and not has_ci:
        return "HYBRID"
    elif has_ci or has_staging or contributors > 5:
        return "REMOTE"
    else:
        return "HYBRID"
```

#### Factores de Análisis Detallados

El sistema analiza múltiples factores para determinar el contexto más apropiado del repositorio. Estos factores se evalúan de forma dinámica y se combinan para crear una imagen completa del entorno de desarrollo.

A continuación se detallan los factores principales que el sistema considera:

##### **Factor 1: Número de Contribuidores**

**¿Cómo se calcula?**

```bash
# El sistema analiza el historial de commits
git log --format='%ae' | sort -u | wc -l
```

**Rangos y significado:**

- **1-2 contribuidores**: Proyecto personal o dúo de desarrollo
- **3-5 contribuidores**: Equipo pequeño, startup o proyecto colaborativo
- **6+ contribuidores**: Equipo grande, empresa o proyecto open source

**¿Por qué importa?**

Más contribuidores = mayor necesidad de coordinación y reglas. Un desarrollador solo puede experimentar libremente, pero 10 desarrolladores necesitan estructura para no chocar entre sí.

##### **Factor 2: Número de Commits**

**¿Cómo se evalúa?**

```bash
# Cuenta todos los commits en todas las ramas
git rev-list --all --count
```

**Rangos de madurez:**

- **< 100 commits**: Proyecto nuevo o experimental
- **100-1000 commits**: Proyecto establecido en desarrollo activo
- **1000+ commits**: Proyecto maduro con historial extenso

**¿Por qué importa?**

El número de commits indica la madurez y estabilidad del proyecto. Proyectos con miles de commits suelen tener procesos establecidos y no toleran cambios disruptivos.

##### **Factor 3: Configuración de Remotos**

**¿Qué detecta?**

```bash
# Analiza remotos configurados
git remote -v
```

**Tipos de configuración:**

- **Sin remotos**: Proyecto completamente local
- **1 remoto**: Configuración típica (origin)
- **Múltiples remotos**: Forks, upstream, deploy, etc.

**¿Por qué importa?**

Los remotos indican colaboración. Sin remotos = trabajo individual. Múltiples remotos = workflows complejos con diferentes entornos.

##### **Factor 4: Presencia de CI/CD**

**¿Qué archivos busca?**

```bash
# Detecta archivos de configuración de CI/CD
.github/workflows/
.gitlab-ci.yml
.travis.yml
.circleci/
Jenkinsfile
bitbucket-pipelines.yml
.buildkite/
azure-pipelines.yml
```

**¿Por qué es crítico?**

CI/CD indica que el proyecto tiene automatización de calidad. Esto sugiere:
- Tests automatizados
- Deployment automático
- Revisión de código sistemática
- Estándares de calidad

##### **Factor 5: Estructura de Branches**

**¿Qué branches busca?**

```bash
# Analiza branches especiales
git branch -a | grep -E "(develop|staging|release|production)"
```

**Indicadores de complejidad:**

- **Solo main/master**: Estructura simple
- **develop**: Git flow implementado
- **staging**: Entorno de pruebas
- **release branches**: Proceso de release formal

#### Contexto LOCAL

**Características Detectadas:**

- Repositorio sin remotos O proyecto muy pequeño
- 1-2 contribuidores únicos
- Menos de 100 commits
- Sin archivos CI/CD detectados
- Estructura de branches simple (solo main/master)

**¿Cuándo se activa LOCAL?**

**Escenario 1: Proyecto Completamente Local**

```bash
mkdir mi-experimento
cd mi-experimento
git init
# Sin git remote add
# → Contexto LOCAL activado automáticamente
```

**Escenario 2: Proyecto Personal Nuevo**

```bash
git clone mi-repo-personal  # 1 contribuidor, 15 commits
cd mi-repo-personal
branch-git-helper.py status
# → "Contexto LOCAL detectado (proyecto personal pequeño)"
```

**Comportamiento Específico:**

- **Validaciones permisivas**: Warnings en lugar de errores
- **No requiere upstream tracking**: `git push` funciona sin `-u`
- **Push automático deshabilitado**: Control manual del desarrollador
- **Branches protegidas mínimas**: Solo `main` y `master`
- **Mensajes educativos**: Explica mejores prácticas sin forzarlas

**Ejemplo de Salida LOCAL:**

```bash
$ branch-git-helper.py feature "nueva-funcionalidad"

🎭 Contexto detectado: LOCAL (validación permisiva)
📊 Análisis del repositorio:
   - Contribuidores: 1 (solo tú)
   - Commits: 23 (proyecto pequeño)
   - Remotos: 0 (completamente local)
   - CI/CD: No detectado

💡 Modo educativo activado: Te ayudo a aprender sin bloquearte

📍 Rama base seleccionada: main
✅ Rama creada: feature/nueva-funcionalidad
🔄 Cambiado a feature/nueva-funcionalidad

💡 SUGERENCIAS (opcionales):
   • Considera configurar un remoto: git remote add origin <URL>
   • Formato recomendado para commits: [TIPO] Descripción
   • Cuando sea momento, sube tu trabajo: git push -u origin feature/nueva-funcionalidad

🎓 ¿Necesitas ayuda? Usa: branch-git-helper.py --help
```

#### Contexto HYBRID

**Características Detectadas:**

- Remotos configurados (colaboración iniciada)
- 2-5 contribuidores (equipo pequeño)
- 100-1000 commits (proyecto establecido)
- CI/CD básico o ausente
- Puede tener rama `develop` (cierta organización)

**¿Cuándo se activa HYBRID?**

**Escenario 1: Startup o Equipo Pequeño**

```bash
git clone equipo-startup/proyecto  # 4 contribuidores, 234 commits
cd proyecto
branch-git-helper.py status
# → "Contexto HYBRID detectado (equipo colaborativo)"
```

**Escenario 2: Proyecto Personal que Creció**

```bash
# Proyecto que empezó como LOCAL pero añadió colaboradores
git log --format='%ae' | sort -u | wc -l  # → 3 contribuidores
git rev-list --all --count  # → 156 commits
# → Contexto HYBRID activado automáticamente
```

**Comportamiento Específico:**

- **Validaciones moderadas**: Errores para reglas importantes, warnings para menores
- **Upstream tracking requerido**: Evita confusiones en el equipo
- **Push automático habilitado**: Facilita colaboración inmediata
- **Branches protegidas moderadas**: `main`, `master`, `develop`
- **Balance productividad/orden**: Reglas que ayudan sin frenar

**Ejemplo de Salida HYBRID:**

```bash
$ branch-git-helper.py feature "nueva-api"

🎭 Contexto detectado: HYBRID (validación moderada)
📊 Análisis del repositorio:
   - Contribuidores: 4 (equipo pequeño)
   - Commits: 156 (proyecto establecido)
   - Remotos: 1 (origin configurado)
   - CI/CD: Básico detectado (.github/workflows)

⚖️ Modo balanceado: Productividad con orden

🔍 Validando formato de branch... ✅
📡 Sincronizando con remoto...
   git fetch origin develop... ✅
   git pull origin develop... ✅ (ya actualizado)

📍 Rama base seleccionada: develop (detectado automáticamente)
✅ Rama creada: feature/nueva-api
🔄 Cambiado a feature/nueva-api
📤 Configurando upstream tracking...
   git push -u origin feature/nueva-api... ✅

🎉 ¡Branch lista para colaboración!
📋 Configuración aplicada:
   ✓ Upstream tracking configurado
   ✓ Branch sincronizada con equipo
   ✓ Formato validado para consistencia

💼 Workflow recomendado:
   1. Desarrolla tu feature
   2. git push (automático gracias al upstream)
   3. Crea Pull Request cuando esté listo
   4. Solicita review de al menos 1 compañero
```

#### Contexto REMOTE

**Características Detectadas:**

- Múltiples remotos (workflows complejos)
- Más de 5 contribuidores (equipo grande)
- Más de 1000 commits (proyecto maduro)
- CI/CD complejo presente (automatización avanzada)
- Estructura de branches completa (develop, staging, release)

**¿Cuándo se activa REMOTE?**

**Escenario 1: Proyecto Empresarial**

```bash
git clone empresa/proyecto-critico  # 23 contribuidores, 2,847 commits
cd proyecto-critico
branch-git-helper.py status
# → "Contexto REMOTE detectado (entorno empresarial)"
```

**Escenario 2: Proyecto Open Source Grande**

```bash
git clone opensource/proyecto-popular  # 156 contribuidores, 15,000 commits
cd proyecto-popular
ls .github/workflows/  # 12 archivos de CI/CD
# → Contexto REMOTE activado automáticamente
```

**Comportamiento Específico:**

- **Validaciones estrictas**: Cero tolerancia a desviaciones
- **Upstream tracking obligatorio**: Auditoría y trazabilidad
- **Push automático habilitado**: Integración inmediata con procesos
- **Branches protegidas extensas**: `main`, `master`, `develop`, `staging`, `release`
- **Compliance total**: Todas las operaciones deben cumplir políticas

**Ejemplo de Salida REMOTE:**

```bash
$ branch-git-helper.py feature "microservicio-pagos"

🎭 Contexto detectado: REMOTE (validación estricta)
📊 Análisis del repositorio:
   - Contribuidores: 23 (equipo grande)
   - Commits: 2,847 (proyecto maduro)
   - Remotos: 3 (origin, upstream, deploy)
   - CI/CD: Complejo (.github/workflows/, .gitlab-ci.yml)

🔒 Modo compliance: Políticas corporativas activadas

🔍 VALIDACIONES CORPORATIVAS:
   ✅ Formato de branch: Cumple estándares
   ✅ Usuario autorizado: Permisos verificados
   ✅ Rama base: develop (política corporativa)
   ✅ Naming convention: Aprobado

📡 Sincronización empresarial...
   git fetch origin develop... ✅
   git fetch upstream develop... ✅
   git pull origin develop... ✅

📍 Rama base seleccionada: develop (política corporativa)
✅ Rama creada: feature/microservicio-pagos
🔄 Cambiado a feature/microservicio-pagos
📤 Configurando tracking completo...
   git push -u origin feature/microservicio-pagos... ✅
🔗 Upstream tracking configurado (obligatorio para auditoría)

🏢 CONFIGURACIÓN EMPRESARIAL APLICADA:
   ✓ Trazabilidad completa habilitada
   ✓ Integración con sistemas corporativos
   ✓ Compliance con políticas de seguridad
   ✓ Auditoría automática configurada

📋 WORKFLOW CORPORATIVO:
   1. Desarrolla siguiendo estándares corporativos
   2. Commits con formato obligatorio: [TIPO] TICKET-123: Descripción
   3. Push automático con validaciones de seguridad
   4. PR automático creado con plantilla corporativa
   5. Revisión obligatoria de 2+ arquitectos
   6. CI/CD completo (tests, security, performance)
   7. Approval de DevOps requerido
   8. Merge automático tras compliance total
```

#### ¿Por Qué Esta Detección es Revolucionaria?

La detección automática de contexto representa un cambio paradigmático en la gestión de ramas Git por tres razones fundamentales:

1. **Adaptación Dinámica sin Fricción**

   - Elimina la necesidad de configuración manual
   - Se ajusta automáticamente según la madurez del proyecto
   - Reduce la curva de aprendizaje para nuevos desarrolladores
   - Previene errores comunes en cada etapa del desarrollo

2. **Inteligencia Contextual**

   - Analiza múltiples factores del repositorio
   - Toma decisiones basadas en datos reales
   - Aplica políticas proporcionales al tamaño del equipo
   - Mantiene consistencia en el flujo de trabajo

3. **Evolución Natural del Proyecto**

   - Permite que el proyecto crezca orgánicamente
   - No requiere reconfiguración al escalar
   - Mantiene el balance entre flexibilidad y control
   - Facilita la transición entre diferentes etapas de desarrollo

Esta capacidad de adaptación inteligente transforma la gestión de ramas de un proceso manual y propenso a errores en un sistema autoadaptativo que crece con el proyecto.

##### **Evolución Natural Sin Fricciones**

**El Problema Tradicional:**

```bash
# Desarrollador junior en su primer día en empresa
git checkout -b "mi-feature"  # ❌ Formato incorrecto
git commit -m "fix"           # ❌ No cumple estándares
git push origin main          # ❌ Violación de política

# Resultado: 3 horas perdidas en configuración y regaños
```

**La Solución del Branch Helper:**

```bash
# Mismo desarrollador con Branch Helper
branch-git-helper.py feature "mi-primera-feature"
# ✅ Detecta contexto REMOTE automáticamente
# ✅ Aplica formato corporativo
# ✅ Configura todo correctamente
# ✅ Desarrollador productivo desde minuto 1
```

##### **Adaptación Inteligente por Madurez**

**Proyecto en Evolución:**

```bash
# Mes 1: Solo yo (LOCAL)
branch-git-helper.py feature "idea-inicial"
# → Permisivo, educativo, sin fricciones

# Mes 6: Añadí un compañero (HYBRID)
branch-git-helper.py feature "nueva-funcionalidad"
# → Balance, algunas reglas, upstream tracking

# Año 2: Equipo de 10 personas (REMOTE)
branch-git-helper.py feature "sistema-complejo"
# → Estricto, compliance, proceso formal

# Misma herramienta, crecimiento natural sin reconfiguración
```

##### **Eliminación de Configuración Manual**

**Sin Branch Helper (configuración tradicional):**

```bash
# Cada desarrollador debe configurar manualmente:
git config --global alias.feature '!sh -c "git checkout -b feature/$1" -'
git config --global push.default current
git config --global branch.autoSetupMerge always
# ... 20+ configuraciones más según el contexto
```

**Con Branch Helper:**

```bash
# Una sola herramienta, configuración automática para cualquier contexto
branch-git-helper.py feature "cualquier-cosa"
# → Todo configurado automáticamente según el contexto detectado
```

---

## Git Tokens Manager - Gestión Segura de Tokens

### Introducción y Propósito

Git Tokens Manager es la herramienta auxiliar fundamental del ecosistema que gestiona de forma segura los tokens de autenticación para múltiples plataformas Git. Su propósito principal es centralizar y securizar el acceso a las APIs de las plataformas Git, eliminando la necesidad de hardcodear tokens o manejarlos de forma insegura.

La herramienta utiliza el keyring del sistema operativo para almacenamiento seguro, lo que significa que los tokens se almacenan usando los mismos mecanismos de seguridad que utiliza el sistema para passwords y credenciales sensibles.

**¿Por qué necesitas un Token Manager?**

La seguridad es una prioridad fundamental en el Token Manager. Todos los tokens se almacenan de forma segura utilizando el keyring del sistema, evitando completamente el almacenamiento en texto plano en archivos de configuración.

La centralización de la gestión de tokens es otro aspecto clave. El Token Manager proporciona un único punto de control para administrar todos los tokens de las diferentes plataformas Git, simplificando significativamente su gestión.

La automatización es una característica esencial que facilita la integración con el resto del ecosistema. Las demás herramientas pueden acceder a los tokens de forma transparente y automática, sin necesidad de configuración adicional.

La compatibilidad con el sistema operativo es garantizada mediante la integración con el keyring nativo. Esto asegura que los tokens se manejen de manera consistente y segura, independientemente del sistema operativo utilizado.

### Servicios Git Soportados

#### Servicios Cloud

**GitHub** (github)

* API: REST v4 + GraphQL
* Tokens: PAT
* ID: github

**GitLab** (gitlab)

* API: REST v4
* Tokens: PAT
* ID: gitlab-c

**Bitbucket** (bitbucket)

* API: REST v2
* Tokens: App Pass
* ID: bitbucket-c

**Forgejo** (forgejo)

* API: GitHub API
* Tokens: Access
* ID: forgejo-c

#### Servicios On-Premise

**Gitea** (gitea)

* API: GitHub API
* Tokens: Access
* ID: gitea
* Host: No requerido

**GitLab** (gitlab)

* API: REST v4
* Tokens: PAT
* ID: gitlab-o
* Host: Requerido

**Bitbucket** (bitbucket)

* API: REST v2
* Tokens: PAT
* ID: bitbucket-o
* Host: Requerido

Nota: Los IDs se usan como [id]-integration (ej: github-integration, gitlab-o-integration)

### Modos de Operación

#### Cloud vs On-Premise

**Cloud (c):**

- Servicios hospedados por el proveedor
- URLs estándar (github.com, gitlab.com)
- APIs públicas
- Rate limiting estándar
- Configuración simplificada

**On-Premise (o):**

- Servicios auto-hospedados
- URLs personalizadas
- APIs privadas
- Rate limiting personalizable
- Requiere configuración de host

#### Formato de Identificación

Los servicios se identifican usando el formato: `[servicio]-[modo]-integration`

```bash
# Ejemplos válidos para el ecosistema
github-integration          # GitHub cloud para integración
gitlab-c-integration       # GitLab cloud para integración
gitlab-o-integration       # GitLab on-premise para integración
gitea-integration          # Gitea on-premise para integración
forgejo-c-integration      # Forgejo cloud para integración
forgejo-o-integration      # Forgejo on-premise para integración
bitbucket-c-integration    # Bitbucket cloud para integración
bitbucket-o-integration    # Bitbucket server para integración
```

### Sistema de Encriptación y Keyring

#### Encriptación Base64

Por defecto, todos los tokens se almacenan encriptados usando Base64. Aunque no es encriptación criptográfica fuerte, proporciona una capa básica de ofuscación que previene la lectura accidental de tokens.

```python
# Proceso de almacenamiento (conceptual)
token_original = "ghp_xxxxxxxxxxxxxxxxxxxx"
token_encriptado = base64.b64encode(token_original.encode()).decode()
keyring.set_password(service_name, username, token_encriptado)
```

#### Integración con Keyring del Sistema

**Linux:**

- Secret Service (GNOME Keyring, KDE Wallet)
- D-Bus integration
- Fallback a archivos encriptados

**macOS:**

- Keychain nativo
- Integración con Touch ID/Face ID
- Security framework nativo

**Windows:**

- Windows Credential Manager
- Integración con Windows Hello
- DPAPI encryption

### Comandos y Sintaxis

El sistema de tokens proporciona una interfaz de línea de comandos intuitiva para gestionar las credenciales de acceso a los diferentes servicios Git. Los comandos siguen un patrón consistente y están diseñados para ser fáciles de recordar y usar.


#### Comando Set - Guardar Tokens

```bash
# Sintaxis básica
git-tokens.py set [servicio-modo-integration] [usuario] [--token TOKEN] [--host HOST]

# Ejemplos para servicios cloud
git-tokens.py set github-integration                    # Modo interactivo
git-tokens.py set github-integration miusuario          # Usuario específico
git-tokens.py set gitlab-c-integration miusuario --token glpat_xxx  # Token directo

# Ejemplos para servicios on-premise
git-tokens.py set gitlab-o-integration miusuario --host gitlab.empresa.com
git-tokens.py set gitea-integration miusuario --host gitea.local
git-tokens.py set bitbucket-o-integration miusuario --host bitbucket.empresa.com
```

#### Comando Get - Recuperar Tokens

```bash
# Sintaxis básica
git-tokens.py get [servicio-modo-integration] [usuario]

# Ejemplos para el ecosistema
git-tokens.py get github-integration                    # Usuario del sistema
git-tokens.py get gitlab-c-integration miusuario       # Usuario específico
git-tokens.py get gitea-integration miusuario          # Gitea on-premise
```

#### Comando Delete - Eliminar Tokens

```bash
# Sintaxis básica
git-tokens.py delete [servicio-modo-integration] [usuario]

# Ejemplos para el ecosistema
git-tokens.py delete github-integration                 # Usuario del sistema
git-tokens.py delete gitlab-c-integration miusuario    # Usuario específico
git-tokens.py delete gitea-integration miusuario       # Gitea on-premise
```

#### Comandos de Información

```bash
# Listar servicios soportados
git-tokens.py list-services

# Mostrar versión
git-tokens.py --version

# Ayuda completa
git-tokens.py --help

# Ayuda de comando específico
git-tokens.py set --help
```

### Modo Interactivo vs Línea de Comandos

#### Modo Interactivo

Cuando no se proporcionan argumentos suficientes, la herramienta entra en modo interactivo:

```bash
# Activar modo interactivo
git-tokens.py set

# La herramienta mostrará:
# 1. Tabla de servicios disponibles
# 2. Selector de servicio
# 3. Selector de modo (cloud/on-premise si aplica)
# 4. Input para host (si es on-premise)
# 5. Input para usuario
# 6. Input seguro para token (oculto)
```

**Ejemplo de sesión interactiva:**

```bash
$ git-tokens.py set

🔐 Git Tokens Manager - Configuración Interactiva

📋 Servicios disponibles:
[1] GitHub (cloud)
[2] GitLab (cloud/on-premise)
[3] Bitbucket (cloud/server)
[4] Gitea (on-premise)
[5] Forgejo (cloud/on-premise)

Selecciona servicio [1-5]: 2

📋 GitLab - Modos disponibles:
[1] Cloud (gitlab.com)
[2] On-Premise (self-hosted)

Selecciona modo [1-2]: 2

🌐 Host GitLab on-premise: gitlab.empresa.com
👤 Usuario: miusuario
🔑 Token (oculto): ************************

✅ Token configurado exitosamente para gitlab-o-integration
🔒 Almacenado seguramente en keyring del sistema
```

#### Modo Línea de Comandos

Para automatización y scripts, todos los parámetros pueden proporcionarse directamente:

```bash
# Completamente no-interactivo para scripts/CI
echo "ghp_token_here" | git-tokens.py set github-integration miusuario --token -

# Con todos los parámetros explícitos
git-tokens.py set gitlab-o-integration miusuario \
  --host gitlab.empresa.com \
  --token glpat_xxxxxxxxxxxxxxxxxxxx
```

### Integración con el Ecosistema

#### Uso Automático por Otras Herramientas

```python
# Uso interno por Git Integration Manager (conceptual)
token_manager = TokenManager()
platform_token = token_manager.get_platform_token(platform_info)

if platform_token:
    # Usar APIs con autenticación
    api_client = create_api_client(platform_info, platform_token)
    # Operaciones automatizadas disponibles
else:
    # Fallback a operaciones manuales
    print("Token no disponible, usando fallback manual")
```

#### Variables de Entorno (Alternativa)

Los tokens pueden también configurarse via variables de entorno para CI/CD:

```bash
# Variables de entorno soportadas
export GIT_TOKEN_GITHUB="ghp_xxxxxxxxxxxx"
export GIT_TOKEN_GITLAB="glpat_xxxxxxxxxxxx"
export GIT_TOKEN_GITEA="gitea_xxxxxxxxxxxx"

# Las herramientas detectan automáticamente estas variables
# como fallback si no hay tokens en keyring
```

#### Detección Automática de Plataforma

```bash
# El ecosistema detecta automáticamente qué token usar
cd proyecto-github
git-integration-manager.py status
# → Usa automáticamente github-integration token

cd proyecto-gitlab-empresa
git-integration-manager.py status
# → Detecta gitlab.empresa.com y usa gitlab-o-integration token
```

### Configuración y Seguridad

### Configuración Inicial

La configuración inicial del sistema de tokens es un proceso simple pero importante que establece la base para una gestión segura de credenciales. Este proceso se realiza una sola vez por servicio y usuario, y las herramientas del ecosistema lo utilizan automáticamente.

#### Requisitos Previos

1. **Backend de Keyring**: El sistema requiere un backend de keyring funcional
2. **Tokens Válidos**: Tokens con los permisos mínimos necesarios
3. **Acceso a Repositorios**: Permisos de lectura/escritura según necesidad

#### Pasos de Configuración

La configuración inicial del sistema de tokens es un proceso simple pero importante que establece la base para una gestión segura de credenciales. Este proceso se realiza una sola vez por servicio y usuario, y las herramientas del ecosistema lo utilizan automáticamente.

#### Mejores Prácticas de Seguridad

**Permisos de Tokens:**

- Usar permisos mínimos necesarios
- Tokens de solo lectura cuando sea posible
- Expiración automática configurada
- Scope limitado al repositorio específico

**Gestión de Tokens:**

- Rotar tokens regularmente (cada 3-6 meses)
- Usar tokens diferentes por proyecto/uso
- Monitorear uso de tokens en la plataforma
- Revocar tokens inmediatamente si se comprometen

**Almacenamiento:**

- Nunca hardcodear tokens en código
- Usar keyring del sistema siempre
- Backup seguro de configuraciones importantes
- No compartir tokens entre usuarios

#### Configuración por Servicio/Usuario

```bash
# Los tokens se configuran globalmente por servicio/usuario
# Un token por servicio es válido para todos los proyectos

# Configurar token para GitHub (válido para todos los proyectos GitHub)
git-tokens.py set github-integration miusuario

# Configurar token para GitLab empresarial (válido para todos los proyectos de esa instancia)
git-tokens.py set gitlab-o-integration --host gitlab.empresa.com miusuario

# Configurar diferentes usuarios para el mismo servicio
git-tokens.py set github-integration usuario-personal
git-tokens.py set github-integration usuario-trabajo

# El token se usa automáticamente según el contexto del repositorio
```

#### Troubleshooting Común

**Error: Keyring no disponible**

```bash
# Instalar backend de keyring
pip install keyrings.alt

# O configurar backend específico
export PYTHON_KEYRING_BACKEND=keyring.backends.file.PlaintextKeyring
```

**Error: Token inválido**

```bash
# Verificar token manualmente
curl -H "Authorization: token $TOKEN" https://api.github.com/user

# Regenerar token en la plataforma
# Actualizar token
git-tokens.py set github-integration --token nuevo_token
```

**Error: Servicio no encontrado**

```bash
# Listar servicios disponibles
git-tokens.py list-services

# Verificar formato correcto
git-tokens.py set github-integration  # ✅ Correcto
git-tokens.py set github             # ❌ Incorrecto
```

**Error: Host requerido para on-premise**

```bash
# Servicios on-premise requieren --host
git-tokens.py set gitlab-o-integration miusuario --host gitlab.empresa.com
git-tokens.py set gitea-integration miusuario --host gitea.local
```

---

## Branch Git Helper - Gestión Inteligente de Ramas

### Introducción y Propósito

Branch Git Helper es el sistema inteligente de gestión de branches que automatiza la creación, naming y configuración de ramas de trabajo. Su propósito principal es eliminar la fricción en la creación de branches y asegurar que se sigan las mejores prácticas apropiadas para cada contexto de proyecto.

La herramienta detecta automáticamente el contexto del proyecto y adapta su comportamiento, desde proyectos personales simples hasta workflows empresariales complejos. Esto significa que puedes usar los mismos comandos independientemente de la complejidad de tu proyecto.

**¿Por qué necesitas un Branch Helper?**

La creación manual de branches en Git es una de las tareas más repetitivas y propensas a errores en el desarrollo de software. El Branch Git Helper resuelve estos problemas fundamentales transformando una secuencia compleja de comandos en una operación simple e inteligente.

**Automatización que Elimina la Fricción Diaria**

Cada vez que necesitas crear una nueva rama, tradicionalmente debes recordar y ejecutar una secuencia específica de comandos: verificar tu rama actual, sincronizar con el remoto, crear la nueva rama con el formato correcto, cambiar a ella, y configurar el tracking. El Branch Helper automatiza toda esta secuencia, reduciendo 5-8 comandos manuales a una sola instrucción. Esto no solo ahorra tiempo, sino que elimina la posibilidad de errores humanos como olvidar sincronizar antes de crear la rama o usar un formato de naming incorrecto.

**Consistencia que Escala con tu Equipo**

Los naming conventions inconsistentes son la pesadilla de cualquier equipo de desarrollo. Sin una herramienta que los enforce, inevitablemente acabas con un repositorio lleno de ramas como "fix", "nueva-feature", "temp-branch", "johns-experiment", creando caos organizacional. El Branch Helper asegura que todas las ramas sigan las convenciones apropiadas para tu contexto de proyecto, desde formatos simples en proyectos personales hasta estándares corporativos estrictos en entornos empresariales.

**Inteligencia Contextual que Toma Decisiones por Ti**

Una de las decisiones más frecuentes pero tediosas es determinar desde qué rama crear tu nueva branch. ¿Desarrollo desde `main`, `develop`, o `master`? ¿Qué pasa si algunas de estas ramas no existen? El Branch Helper analiza la estructura de tu repositorio y selecciona automáticamente la rama base más apropiada según el tipo de trabajo que vas a realizar. Los hotfixes siempre se crean desde la rama de producción, mientras que las features se crean desde la rama de desarrollo, con fallbacks inteligentes cuando la configuración ideal no está disponible.

**Configuración Transparente que Previene Problemas Futuros**

El upstream tracking es uno de esos conceptos de Git que muchos desarrolladores no entienden completamente hasta que tienen problemas. Sin la configuración correcta, comandos simples como `git push` fallan o se comportan de manera inesperada. El Branch Helper configura automáticamente el upstream tracking según las mejores prácticas de tu contexto, asegurando que todos tus comandos Git futuros funcionen como esperas, sin configuración manual adicional.

**Adaptabilidad que Crece con tu Proyecto**

Quizás la característica más revolucionaria es cómo el Branch Helper se adapta automáticamente a la evolución de tu proyecto. Un proyecto personal que comienza con validaciones permisivas puede crecer hasta convertirse en un proyecto empresarial con reglas estrictas, y la herramienta evoluciona naturalmente sin requerir reconfiguración. Esto significa que puedes empezar con simplicidad y obtener complejidad organizacional cuando realmente la necesites, no antes.

### Tipos de Branch Soportados

#### Feature Branches

**Propósito**: Nuevas características y funcionalidades

**Naming**: `feature/descripcion-clara`

**Branch de Origen**: `develop` (o `main` si develop no existe)

**Ejemplos**:

```bash
branch-git-helper.py feature "nueva-autenticacion"
# Crea: feature/nueva-autenticacion desde develop

branch-git-helper.py feature "sistema-de-pagos"
# Crea: feature/sistema-de-pagos desde develop
```

#### Fix Branches

**Propósito**: Correcciones de errores y bugs no críticos

**Naming**: `fix/descripcion-del-problema`

**Branch de Origen**: `develop` (o `main` si develop no existe)

**Ejemplos**:

```bash
branch-git-helper.py fix "validacion-email"
# Crea: fix/validacion-email desde develop

branch-git-helper.py fix "error-calculo-iva"
# Crea: fix/error-calculo-iva desde develop
```

#### Hotfix Branches

**Propósito**: Correcciones urgentes en producción

**Naming**: `hotfix/descripcion-urgente`

**Branch de Origen**: `main` (soporta `master` por compatibilidad)

**Ejemplos**:

```bash
branch-git-helper.py hotfix "vulnerabilidad-critica"
# Crea: hotfix/vulnerabilidad-critica desde main

branch-git-helper.py hotfix "caida-servidor-login"
# Crea: hotfix/caida-servidor-login desde main
```

#### Documentation Branches

**Propósito**: Documentación y cambios en docs

**Naming**: `docs/tema-documentacion`

**Branch de Origen**: `develop` (o `main` si develop no existe)

**Ejemplos**:

```bash
branch-git-helper.py docs "api-reference"
# Crea: docs/api-reference desde develop

branch-git-helper.py docs "guia-instalacion"
# Crea: docs/guia-instalacion desde develop
```

#### Refactor Branches

**Propósito**: Refactorización de código sin cambios funcionales

**Naming**: `refactor/area-refactorizada`

**Branch de Origen**: `develop` (o `main` si develop no existe)

**Ejemplos**:

```bash
branch-git-helper.py refactor "estructura-modulos"
# Crea: refactor/estructura-modulos desde develop

branch-git-helper.py refactor "optimizacion-queries"
# Crea: refactor/optimizacion-queries desde develop
```

#### Test Branches

**Propósito**: Añadir o mejorar tests

**Naming**: `test/area-testing`

**Branch de Origen**: `develop` (o `main` si develop no existe)

**Ejemplos**:

```bash
branch-git-helper.py test "unit-tests-auth"
# Crea: test/unit-tests-auth desde develop

branch-git-helper.py test "integration-tests"
# Crea: test/integration-tests desde develop
```

#### Chore Branches

**Propósito**: Tareas de mantenimiento y build

**Naming**: `chore/tarea-mantenimiento`

**Branch de Origen**: `develop` (o `main` si develop no existe)

**Ejemplos**:

```bash
branch-git-helper.py chore "actualizar-dependencias"
# Crea: chore/actualizar-dependencias desde develop

branch-git-helper.py chore "configurar-ci"
# Crea: chore/configurar-ci desde develop
```

### Detección Automática de Contexto

### Detección Automática de Contexto

> **📖 Para información completa sobre detección de contexto, ver:** [Detección Automática de Contexto - Arquitectura del Sistema](#detección-automática-de-contexto)

El Branch Git Helper utiliza el mismo sistema de detección automática de contexto descrito en la arquitectura del sistema. Esta detección influye directamente en:

#### Comportamiento Específico por Contexto

**En Contexto LOCAL:**
- Validaciones permisivas (warnings en lugar de errores)
- Push automático deshabilitado (control manual)
- Mensajes educativos sin bloqueos
- Upstream tracking opcional

**En Contexto HYBRID:**
- Validaciones moderadas (balance productividad/control)
- Push automático habilitado
- Upstream tracking requerido
- Sincronización automática con remoto

**En Contexto REMOTE:**
- Validaciones estrictas (cumplimiento obligatorio)
- Push automático con auditoría
- Upstream tracking obligatorio
- Integración completa con políticas corporativas

#### Adaptación del Naming y Validación

El contexto detectado determina:
- **Formato de naming**: Desde sugerencias hasta requisitos estrictos
- **Validación de rama base**: Automática según disponibilidad
- **Configuración de upstream**: Manual, automática u obligatoria
- **Sincronización previa**: Opcional, recomendada u obligatoria

### Prioridades de Branch Base

El sistema de prioridades de branch base es un componente fundamental que determina automáticamente desde qué rama debe crearse cada nuevo branch. Esta decisión se basa en el tipo de branch y el contexto del proyecto, asegurando que cada rama se cree desde el punto más apropiado del árbol de desarrollo.

La herramienta implementa un sistema de prioridades que:

- Define una lista ordenada de ramas base preferidas para cada tipo de branch
- Se adapta automáticamente según la estructura existente del repositorio
- Garantiza consistencia en la creación de ramas sin importar quién las crea
- Mantiene la integridad del flujo de trabajo del proyecto

Este sistema elimina la necesidad de decisiones manuales sobre la rama base, reduciendo errores y manteniendo la consistencia del árbol de desarrollo.

#### Sistema de Prioridades

Cada tipo de branch tiene una lista de prioridades para seleccionar la rama base:

```python
BRANCH_TYPES = {
    "feature": {
        "base_branch_priority": ["develop", "main"]
    },
    "fix": {
        "base_branch_priority": ["develop", "main"]
    },
    "hotfix": {
        "base_branch_priority": ["main", "master"]
    },
    "docs": {
        "base_branch_priority": ["develop", "main"]
    },
    "refactor": {
        "base_branch_priority": ["develop", "main"]
    },
    "test": {
        "base_branch_priority": ["develop", "main"]
    },
    "chore": {
        "base_branch_priority": ["develop", "main"]
    }
}
```

#### Lógica de Selección

1. **Verificar existencia**: La herramienta verifica si cada rama en la lista de prioridades existe
2. **Seleccionar primera disponible**: Se selecciona la primera rama que existe
3. **Fallback inteligente**: Si ninguna rama de la lista existe, se busca `main` o `master`
4. **Último recurso**: Si no se encuentra ninguna rama estándar, se usa la rama actual

#### Casos Especiales

**Hotfix siempre desde producción**:

```bash
# Hotfix siempre intenta main/master primero
branch-git-helper.py hotfix "fix-critico"
# Base: main (incluso si develop existe)
```

**Feature en proyecto sin develop**:

```bash
# Si no existe develop, usa main
branch-git-helper.py feature "nueva-feature"
# Base: main (fallback automático)
```

### Comandos y Sintaxis

#### Sintaxis Básica

```bash
# Formato general
branch-git-helper.py [tipo] "descripcion" [opciones]

# Tipos disponibles
branch-git-helper.py feature "descripcion"
branch-git-helper.py fix "descripcion"
branch-git-helper.py hotfix "descripcion"
branch-git-helper.py docs "descripcion"
branch-git-helper.py refactor "descripcion"
branch-git-helper.py test "descripcion"
branch-git-helper.py chore "descripcion"
```

#### Opciones Avanzadas

##### Control de Sincronización

**`--no-sync`: Omitir sincronización previa**

Por defecto, la herramienta sincroniza la rama base con el remoto antes de crear la nueva rama:

```bash
# Comportamiento normal (con sincronización)
branch-git-helper.py feature "nueva-api"
# 1. git pull origin develop  ← Sincroniza rama base
# 2. git checkout -b feature/nueva-api
# 3. git push -u origin feature/nueva-api

# Con --no-sync (omite sincronización)
branch-git-helper.py feature "nueva-api" --no-sync
# 1. (omite git pull)  ← No sincroniza
# 2. git checkout -b feature/nueva-api
# 3. git push -u origin feature/nueva-api
```

**Cuándo usar `--no-sync`**:

- **Trabajo offline**: Sin conexión a internet
- **Rama ya actualizada**: Sabes que tu rama base local está al día
- **Evitar conflictos**: Quieres crear la rama sin resolver conflictos de merge primero
- **Desarrollo rápido**: Iteraciones rápidas sin esperar sincronización

**`--no-push`: Omitir push automático**

Por defecto, la herramienta hace push automático y configura upstream:

```bash
# Comportamiento normal (con push automático)
branch-git-helper.py feature "nueva-api"
# 1. git pull origin develop
# 2. git checkout -b feature/nueva-api
# 3. git push -u origin feature/nueva-api  ← Push automático

# Con --no-push (omite push)
branch-git-helper.py feature "nueva-api" --no-push
# 1. git pull origin develop
# 2. git checkout -b feature/nueva-api
# 3. (omite git push)  ← No hace push
```

**Cuándo usar `--no-push`**:
- **Trabajo local primero**: Quieres hacer varios commits antes de subir
- **Sin conexión**: Trabajas offline
- **Experimentación**: Pruebas que pueden no llegar al remoto
- **Control manual**: Prefieres manejar el push manualmente

##### Control de Ubicación

**`-p, --repo-path`: Especificar repositorio**

Permite trabajar con repositorios en diferentes ubicaciones sin cambiar de directorio:

```bash
# Trabajar en repositorio específico
branch-git-helper.py -p /path/to/proyecto feature "nueva-funcionalidad"

# Trabajar en proyecto relativo
branch-git-helper.py --repo-path ../otro-proyecto fix "bug-critico"

# Múltiples proyectos desde un directorio
branch-git-helper.py -p ~/proyectos/frontend feature "ui-mejoras"
branch-git-helper.py -p ~/proyectos/backend feature "api-usuarios"
```

**Cuándo usar `--repo-path`**:
- **Múltiples proyectos**: Gestionar varios repositorios desde un lugar
- **Scripts automatizados**: Automatización que opera en diferentes repos
- **Workspace organizado**: Mantener estructura de directorios específica
- **CI/CD**: Pipelines que operan en múltiples repositorios

##### Combinación de Opciones

Las opciones se pueden combinar según las necesidades:

```bash
# Trabajo completamente local
branch-git-helper.py feature "experimento" --no-sync --no-push

# Repositorio específico sin push
branch-git-helper.py -p ../proyecto-cliente hotfix "fix-urgente" --no-push

# Múltiples escenarios
branch-git-helper.py -p ~/trabajo/proyecto-a feature "nueva-feature" --no-sync
branch-git-helper.py -p ~/personal/proyecto-b docs "actualizar-readme" --no-push
```

#### Comandos de Estado

```bash
# Mostrar estado del repositorio
branch-git-helper.py status

# Output ejemplo:
# 🎭 Branch Git Helper - Estado del Repositorio
# 📍 Repositorio: /home/user/mi-proyecto
# 🌿 Rama actual: feature/nueva-funcionalidad
# 📊 Estadísticas:
#    - Contribuidores: 3
#    - Commits totales: 245
#    - Remotos configurados: 1
#    - CI/CD detectado: No
```

### Ejemplos Prácticos

#### Proyecto Personal (Contexto LOCAL)

```bash
# Inicializar proyecto personal
mkdir mi-app
cd mi-app
git init
echo "# Mi App" > README.md
git add README.md
git commit -m "[BUILD] Initial commit"

# Crear feature branch
branch-git-helper.py feature "login-usuario"
# Crea: feature/login-usuario desde main
# No requiere upstream, validaciones permisivas

# Trabajar en la feature
echo "login code" > login.py
git add login.py
git commit -m "[FEATURE] Implementa login básico"

# La herramienta no hace push automático en LOCAL
# Push manual cuando esté listo
git push -u origin feature/login-usuario
```

#### Proyecto de Equipo (Contexto HYBRID)

```bash
# Clonar proyecto existente
git clone https://github.com/equipo/proyecto.git
cd proyecto

# Crear feature branch
branch-git-helper.py feature "api-usuarios"
# Crea: feature/api-usuarios desde develop
# Configura upstream automáticamente
# Hace push automático

# Trabajar en la feature
# ... desarrollo ...
git add .
git commit -m "[FEATURE] Añade endpoint usuarios"

# Push automático ya configurado
git push
```

#### Proyecto Empresarial (Contexto REMOTE)

```bash
# Clonar proyecto empresarial
git clone https://github.com/empresa/proyecto-critico.git
cd proyecto-critico

# Crear hotfix urgente
branch-git-helper.py hotfix "vulnerabilidad-seguridad"
# Crea: hotfix/vulnerabilidad-seguridad desde main
# Validaciones estrictas aplicadas
# Push automático con upstream

# Trabajar en el hotfix
# ... desarrollo urgente ...
git add .
git commit -m "[HOTFIX] Corrige vulnerabilidad XSS"

# Push automático configurado
git push

# Continuar con Git Integration Manager para PR automático
```

---

## Git Integration Manager - Orquestador de Workflows

### Introducción y Propósito

Git Integration Manager es el componente más avanzado y sofisticado del ecosistema Git Branch Tools. Su propósito principal es orquestar workflows completos de integración, automatizando procesos desde la creación de branches hasta el merge final, incluyendo la gestión de Pull Requests, validaciones pre-integración y configuración de branch protection rules.

Esta herramienta representa la evolución natural del flujo de trabajo de Git, eliminando las tareas repetitivas y propensas a errores que tradicionalmente requieren intervención manual. El Integration Manager no solo automatiza operaciones individuales, sino que las conecta en flujos de trabajo coherentes y adaptativos.

**¿Por qué necesitas un Integration Manager?**

El desarrollo moderno de software requiere workflows complejos que van mucho más allá de crear ramas y hacer commits.

**Automatización de Pull Requests**:

El sistema automatiza la creación y gestión de PRs mediante un proceso básico:

1. **Generación Automática**:

   - Detecta el tipo de branch (feature/hotfix/release)
   - Crea Pull Requests/Merge Requests con título y descripción estándar basados en el nombre de la rama
   - Usa formato: `[AUTO] Integrate {branch_name}` con timestamp de creación
   - Incluye información básica: rama, fecha de creación y origen del workflow

2. **Creación Simplificada**:

   - Título automático generado desde el nombre de la rama
   - Descripción básica con información de contexto
   - Configuración de rama base automática (develop por defecto)
   - Integración con APIs de plataforma cuando están disponibles

3. **Fallback Manual**:

   - Cuando las APIs no están disponibles, genera instrucciones manuales detalladas
   - Proporciona URLs directas para crear PRs manualmente
   - Incluye títulos y descripciones sugeridos
   - Ofrece comandos Git equivalentes para operaciones manuales

### Funcionalidades Principales

#### Orquestación Completa de Workflows

El Integration Manager automatiza workflows end-to-end completos:

**Workflow de Integración de Features:**

1. Validación pre-integración de la rama
2. Sincronización con rama base
3. Creación automática de Pull Request (si hay APIs disponibles)
4. Configuración básica de metadata del PR
5. Aplicación de formato estándar de título y descripción
6. Notificación de próximos pasos
7. Monitoreo manual del estado de CI/CD
8. Merge manual tras aprobaciones

**Workflow de Configuración Remota:**

1. Detección automática de plataforma Git
2. Análisis del contexto del proyecto
3. Aplicación de estrategias de protección apropiadas
4. Sincronización de reglas locales con remotas
5. Validación de configuraciones aplicadas

#### Gestión Inteligente de Branch Protection

El sistema implementa un enfoque estratégico para la gestión de branch protection:

**Estrategia LOCAL:**

- Sin branches protegidas remotas
- Configuración mínima local
- Máxima flexibilidad para desarrollo individual

**Estrategia HYBRID:**

- Protección de `main` y `develop`
- Configuración balanceada entre flexibilidad y control
- Ideal para equipos pequeños

**Estrategia REMOTE:**

- Protección completa de `main`, `master`, `develop`, `staging`, `release`
- Configuración empresarial estricta
- Cumplimiento de políticas corporativas

#### Detección Automática de Capacidades

El Integration Manager detecta automáticamente qué funcionalidades están disponibles:

**Detección de Tokens:**

- Verifica tokens disponibles en keyring
- Identifica plataformas Git configuradas
- Determina permisos de API disponibles

**Detección de Plataforma:**
- Analiza remotes Git para identificar plataforma
- Detecta servicios cloud vs on-premise
- Extrae información de repositorio (owner, name)

**Adaptación de Funcionalidades:**
- APIs completas cuando hay tokens válidos
- Fallback a operaciones locales sin tokens
- Degradación elegante de funcionalidades

#### Análisis de Salud del Repositorio

Sistema avanzado de métricas de salud:

**Métricas Analizadas:**

- Total de branches activas vs obsoletas
- Número de contribuidores activos
- Distribución temporal de commits
- Presencia de branches stale (>30 días sin actividad)
- Score de salud general (0-100)

**Acciones de Limpieza:**

- Identificación automática de branches para limpiar
- Validación de seguridad antes de eliminación
- Modo dry-run para revisar acciones
- Ejecución controlada con confirmación

### Sistema de Validación Híbrida

El Integration Manager implementa un sistema de validación híbrida que combina validaciones locales y remotas para asegurar la calidad del código y el cumplimiento de políticas.

#### Validación Local

**Pre-integración:**

- Verificación de estado de la rama (commits no pusheados, conflictos)
- Validación de formato de commits según convenciones
- Análisis de diferencias con rama base
- Verificación de tests locales (si están configurados)

**Validación de Contexto:**

- Verificación de que la rama es apropiada para integración
- Validación de naming conventions
- Verificación de branch base apropiada

#### Validación Remota

**APIs de Plataforma:**

- Verificación de estado de CI/CD remoto
- Validación de branch protection rules
- Verificación de permisos de usuario
- Estado de Pull Requests existentes

**Integración con Servicios:**

- GitHub: Status checks, required reviews, branch protection
- GitLab: Merge requests, pipelines, approval rules
- Gitea/Forgejo: Pull requests, branch protection
- Bitbucket: Pull requests, branch permissions

#### Fallback Graceful

Cuando las APIs no están disponibles, el sistema proporciona:

**Validación Local Extendida:**

- Análisis más profundo del estado local
- Sugerencias de acciones manuales
- Generación de comandos Git para ejecución manual
- Instrucciones paso a paso para workflows manuales

### Configuración Automática del Remoto

Una de las características más avanzadas del Integration Manager es su capacidad para configurar automáticamente branch protection rules en repositorios remotos, adaptándose a diferentes plataformas y contextos.

#### Detección de Plataforma Automática

El sistema detecta automáticamente la plataforma Git:

```python
# Detección desde remotes Git
git remote get-url origin
# → https://github.com/usuario/proyecto.git
# → Detecta: GitHub cloud

git remote get-url origin
# → https://gitlab.empresa.com/team/proyecto.git
# → Detecta: GitLab on-premise + host
```

**Plataformas Soportadas:**

- **GitHub**: Cloud (github.com)
- **GitLab**: Cloud (gitlab.com) y On-premise
- **Gitea**: On-premise
- **Forgejo**: Cloud y On-premise
- **Bitbucket**: Cloud y Server

#### Configuración Universal

El sistema utiliza un modelo de configuración universal que se adapta a las capacidades específicas de cada plataforma:

**Configuración Base:**

```json
{
  "require_reviews": true,
  "min_reviewers": 1,
  "dismiss_stale_reviews": true,
  "require_code_owners": false,
  "required_checks": [],
  "restrict_access": false,
  "enforce_admins": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

**Adaptación por Plataforma:**

- GitHub: Soporte completo de todas las características
- GitLab: Adaptación de teams a grupos
- Gitea: Code owners no disponible
- Bitbucket: Adaptación de configuraciones específicas

#### Estrategias Pre-definidas

**Estrategia LOCAL:**

```json
{
  "protected_branches": [],
  "require_reviews": false,
  "description": "Sin protección remota, máxima flexibilidad"
}
```

**Estrategia HYBRID:**

```json
{
  "protected_branches": ["main", "develop"],
  "require_reviews": true,
  "min_reviewers": 1,
  "required_checks": ["ci/tests"],
  "description": "Balance entre flexibilidad y control"
}
```

**Estrategia REMOTE:**

```json
{
  "protected_branches": ["main", "master", "develop", "staging", "release"],
  "require_reviews": true,
  "min_reviewers": 2,
  "dismiss_stale_reviews": true,
  "require_code_owners": true,
  "required_checks": ["ci/tests", "ci/security", "ci/quality"],
  "restrict_access": true,
  "enforce_admins": true,
  "description": "Máxima protección para entornos empresariales"
}
```

### Comandos y Sintaxis

#### Sintaxis Básica

```bash
# Formato general
git-integration-manager.py [acción] [argumentos] [opciones]

# Acciones principales
git-integration-manager.py integrate [branch-name]          # Integrar feature completa
git-integration-manager.py health-check                     # Analizar salud del repo
git-integration-manager.py cleanup                          # Limpiar branches obsoletas
git-integration-manager.py status                           # Estado del manager
git-integration-manager.py setup-remote-protection          # Configurar protección remota
git-integration-manager.py protection-status                # Estado de protección
git-integration-manager.py sync-protection-rules            # Sincronizar reglas
```

#### Comando Integrate - Integración Completa

**Propósito**: Orquestar la integración completa de una feature branch

```bash
# Integración básica
git-integration-manager.py integrate feature/nueva-api

# Con opciones avanzadas
git-integration-manager.py integrate feature/nueva-api --mode api --dry-run
git-integration-manager.py integrate hotfix/fix-critico --mode auto
git-integration-manager.py -p /path/to/project integrate feature/ui-improvements
```

**Flujo de Ejecución:**

1. Validación pre-integración de la rama

2. Sincronización con rama base

3. Creación de Pull Request (con APIs):

   - Detección automática de plataforma
   - Creación de PR con formato estándar
   - Configuración básica de título y descripción
   - URL de comparación generada automáticamente

4. **Configuración de Metadata:**

   - Título generado desde branch name con prefijo [AUTO]
   - Descripción básica con timestamp
   - Información del origen del workflow
   - Configuración de rama base (develop por defecto)

5. **Notificación Post-creación:**

   - Confirmación de PR creado exitosamente
   - URL del PR para acceso manual
   - Instrucciones para próximos pasos
   - Sugerencias para configuración manual adicional

**Opciones Específicas:**

- `--mode`: Nivel de automatización (dry-run, local, api, auto)
- `--dry-run`: Solo mostrar qué haría sin ejecutar
- `-p, --path`: Repositorio específico

#### Comando Health-Check - Análisis de Salud

**Propósito**: Analizar la salud general del repositorio

```bash
# Análisis básico
git-integration-manager.py health-check

# En repositorio específico
git-integration-manager.py -p ../proyecto-cliente health-check
```

**Métricas Reportadas:**

- Total de branches (activas vs obsoletas)
- Número de contribuidores únicos
- Branches stale (sin actividad >30 días)
- Score de salud general (0-100)

**Ejemplo de Salida:**

```bash
📊 Reporte de Salud del Repositorio
====================================
🌳 Total branches: 15
✅ Branches activas: 12
⚠️  Branches stale: 3
👥 Contribuidores: 5
📈 Score de salud: 85.2/100
```

#### Comando Cleanup - Limpieza de Repositorio

**Propósito**: Identificar y limpiar branches obsoletas

```bash
# Análisis de limpieza (dry-run por defecto)
git-integration-manager.py cleanup

# Ejecutar limpieza real
git-integration-manager.py cleanup --execute

# En repositorio específico
git-integration-manager.py -p ~/proyectos/backend cleanup --execute
```

**Criterios de Limpieza:**

- Branches mergeadas completamente
- Branches sin actividad >30 días
- Branches sin commits únicos
- Exclusión de branches protegidas

**Ejemplo de Salida:**

```bash
📋 Acciones de limpieza: 3
  • feature/old-experiment (mergeada, 45 días)
  • fix/temp-solution (mergeada, 60 días)
  • docs/outdated-guide (sin actividad, 90 días)

💡 Usar --execute para ejecutar las acciones
```

#### Comando Status - Estado del Manager

**Propósito**: Mostrar estado actual de capacidades y configuración

```bash
# Estado general
git-integration-manager.py status

# Estado en proyecto específico
git-integration-manager.py -p /path/to/project status
```

**Información Mostrada:**

- Contexto detectado (LOCAL/HYBRID/REMOTE)
- Nivel de capacidades disponibles
- Estado de APIs y tokens
- Configuración de Git CLI

**Ejemplo de Salida:**

```bash
📊 Estado del Integration Manager
===============================
📍 Contexto: HYBRID
⚡ Capacidades: enhanced
🐙 GitHub API: ✅
🦊 Git CLI: ✅
```

#### Comando Setup-Remote-Protection - Configuración de Protección

**Propósito**: Configurar branch protection rules en el repositorio remoto

```bash
# Aplicar estrategia específica
git-integration-manager.py setup-remote-protection --strategy hybrid

# Con preview (dry-run)
git-integration-manager.py setup-remote-protection --strategy remote --dry-run

# Especificar plataforma manualmente
git-integration-manager.py setup-remote-protection --strategy remote --platform gitlab-o --host gitlab.empresa.com
```

**Estrategias Disponibles:**

- `local`: Sin protección remota
- `hybrid`: Protección moderada (main, develop)
- `remote`: Protección completa (empresarial)

**Ejemplo de Salida:**

```bash
🎯 Aplicando estrategia 'hybrid' en github
📋 Configuración adaptada para github:
   Configuración:
   - Require reviews: 1 mínimo
   - Status checks: ci/tests
   - Acceso restringido habilitado

🔍 DRY RUN - No se aplicarán cambios reales
```

#### Comando Protection-Status - Estado de Protección

**Propósito**: Mostrar estado actual de branch protection

```bash
# Estado básico
git-integration-manager.py protection-status

# Con comparación local vs remoto
git-integration-manager.py protection-status --compare

# Salida en formato JSON
git-integration-manager.py protection-status --json

# Comparación en proyecto específico
git-integration-manager.py -p ../proyecto protection-status --compare
```

**Información Mostrada:**

- Plataforma detectada
- Branches protegidas remotamente
- Detalles de configuración por branch
- Comparación con configuración local (si se solicita)

**Ejemplo de Salida con Comparación:**

```bash
📊 Estado de Protección con Comparación
=====================================

🏠 Branches protegidas localmente:
   • main
   • develop

☁️  Branches protegidas remotamente:
   • main

🔍 Diferencias encontradas:
   ⚠️  Branches protegidas localmente pero no remotamente:
      • develop

🛡️  Detalles de Protección Remota:
   main:
      ✅ Status Checks: ci/tests habilitado
      ✅ PR Reviews: 1 reviewer(s) requerido(s)
         Dismiss stale: Sí
         Code owners: No
      🌐 Restricciones: Acceso abierto
      👑 Enforce Admins: Sí
```

#### Comando Sync-Protection-Rules - Sincronización de Reglas

**Propósito**: Sincronizar reglas de protección entre local y remoto

```bash
# Sincronizar local → remoto
git-integration-manager.py sync-protection-rules --direction local-to-remote

# Sincronizar remoto → local
git-integration-manager.py sync-protection-rules --direction remote-to-local

# Con preview
git-integration-manager.py sync-protection-rules --direction local-to-remote --dry-run
```

**Direcciones de Sincronización:**

- `local-to-remote`: Aplicar configuración local al repositorio remoto
- `remote-to-local`: Descargar configuración remota a archivos locales

### Workflows Automatizados

El Integration Manager proporciona workflows automatizados completos que conectan múltiples operaciones en flujos coherentes y eficientes.

#### Workflow de Feature Integration

**Flujo Completo Automatizado:**

```bash
# 1. Desarrollo completado en feature branch
git checkout feature/nueva-autenticacion
git push

# 2. Integración automática
git-integration-manager.py integrate feature/nueva-autenticacion --mode auto
```

**Pasos Ejecutados Automáticamente:**

1. **Validación Pre-integración:**

   - Verificar que la rama actual esté actualizada
   - Validar formato de commits
   - Comprobar ausencia de conflictos
   - Verificar estado de tests locales

2. **Sincronización:**

   - Fetch latest changes del remoto
   - Merge/rebase con rama base si es necesario
   - Push de cambios sincronizados

3. **Creación de Pull Request (con APIs):**

   - Detección automática de plataforma
   - Creación de PR con formato estándar
   - Configuración básica de título y descripción
   - URL de comparación generada automáticamente

4. **Configuración de Metadata:**

   - Título generado desde branch name con prefijo [AUTO]
   - Descripción básica con timestamp
   - Información del origen del workflow
   - Configuración de rama base (develop por defecto)

5. **Notificación Post-creación:**

   - Confirmación de PR creado exitosamente
   - URL del PR para acceso manual
   - Instrucciones para próximos pasos
   - Sugerencias para configuración manual adicional

**Ejemplo de Ejecución:**

```bash
$ git-integration-manager.py integrate feature/nueva-autenticacion --mode auto

🎭 Git Integration Manager iniciado
📍 Contexto detectado: HYBRID (equipo colaborativo)
⚡ Capacidades disponibles: enhanced (APIs + Git CLI)

🔍 VALIDACIÓN PRE-INTEGRACIÓN:
   ✅ Rama actual: feature/nueva-autenticacion
   ✅ Commits no pusheados: 0
   ✅ Estado de sincronización: actualizado
   ✅ Conflictos: ninguno detectado

📡 SINCRONIZACIÓN:
   git fetch origin develop... ✅
   Estado: rama base actualizada

🚀 CREACIÓN DE PULL REQUEST:
   🌐 Plataforma detectada: GitHub
   📝 Título: "[AUTO] Integrate feature/nueva-autenticacion"
   📋 Descripción: Automated integration via git-integration-manager
   📅 Timestamp: 2024-01-15T10:30:45
   🔗 URL generada: https://github.com/equipo/proyecto/compare/develop...feature/nueva-autenticacion

✅ Pull Request creado: https://github.com/equipo/proyecto/pull/123

🎉 INTEGRACIÓN COMPLETADA:
   📍 PR URL: https://github.com/equipo/proyecto/pull/123
   📋 Próximos pasos:
      1. Revisar y configurar reviewers manualmente
      2. Monitorear CI/CD: https://github.com/equipo/proyecto/actions
      3. Hacer merge manual tras aprobaciones
```

#### Workflow de Configuración Empresarial

**Configuración Automática para Entornos Empresariales:**

```bash
# Configuración completa con una sola línea
git-integration-manager.py setup-remote-protection --strategy remote
```

**Pasos Ejecutados:**

1. **Detección de Entorno:**

   - Análisis del repositorio (contribuidores, commits, CI/CD)
   - Detección de plataforma Git automática
   - Verificación de tokens y permisos

2. **Aplicación de Estrategia:**

   - Configuración de branches protegidas
   - Setup de required reviews
   - Configuración de status checks obligatorios
   - Establecimiento de restrictions

3. **Validación y Confirmación:**

   - Verificación de configuración aplicada
   - Comparación con políticas corporativas
   - Generación de reporte de compliance

**Ejemplo de Ejecución:**

```bash
$ git-integration-manager.py setup-remote-protection --strategy remote

🎯 Aplicando estrategia 'remote' en github
📊 Análisis del repositorio:
   - Contribuidores: 23 (equipo grande)
   - Commits: 2,847 (proyecto maduro)
   - CI/CD: Complejo detectado

📋 Configuración empresarial para github:
   Configuración:
   - Require reviews: 2 mínimo
   - Status checks: ci/tests, ci/security, ci/quality
   - Acceso restringido habilitado
   - Enforce admins habilitado

🛡️  APLICANDO PROTECCIÓN A BRANCHES:
   ✅ main: Protección empresarial aplicada
   ✅ master: Protección empresarial aplicada
   ✅ develop: Protección empresarial aplicada
   ✅ staging: Protección empresarial aplicada
   ✅ release: Protección empresarial aplicada

🎉 CONFIGURACIÓN COMPLETADA:
   🔒 5 branches protegidas configuradas
   ✅ Compliance empresarial establecido
   📊 Configuración validada contra políticas
```

#### Workflow de Limpieza Periódica

**Mantenimiento Automático del Repositorio:**

```bash
# Análisis y limpieza en un solo comando
git-integration-manager.py cleanup --execute
```

**Proceso Automatizado:**

1. **Análisis de Salud:**


   - Identificación de branches stale
   - Verificación de branches mergeadas
   - Análisis de actividad por contribuidor

2. **Limpieza Inteligente:**

   - Eliminación de branches mergeadas completamente
   - Limpieza de branches sin actividad reciente
   - Preservación de branches protegidas

3. **Reporte y Confirmación:**

   - Generación de reporte de acciones
   - Confirmación de branches eliminadas
   - Actualización de métricas de salud

### Integración con APIs

El Integration Manager está diseñado para aprovechar al máximo las APIs de las diferentes plataformas Git cuando están disponibles, pero funciona completamente sin ellas cuando es necesario.

#### Arquitectura de APIs Multi-plataforma

El sistema implementa una arquitectura modular que soporta múltiples plataformas:

**Factory Pattern para APIs:**

```python
class PlatformAPIFactory:
    @staticmethod
    def create_api(platform_info: PlatformInfo, token: str):
        if platform_info.service == "github":
            return GitHubAPI(token)
        elif platform_info.service == "gitlab":
            return GitLabAPI(token, platform_info.host)
        elif platform_info.service == "gitea":
            return GiteaAPI(token, platform_info.host)
        # ... más plataformas
```

**APIs Implementadas:**

1. **GitHub API (REST v4):**

   - Pull Requests: creación básica con título y descripción estándar
   - Branch Protection: configuración completa
   - Status Checks: verificación de CI/CD
   - Repositorio: información básica y metadatos

2. **GitLab API (REST v4):**

   - Merge Requests: creación básica con formato estándar
   - Push Rules: configuración de branches
   - Pipelines: estado de CI/CD
   - Proyectos: información básica y metadatos

3. **Gitea API (GitHub compatible):**

   - Pull Requests: funcionalidad básica de creación
   - Branch Protection: configuración básica
   - Repositorio: información básica

4. **Forgejo API (Gitea compatible):**

   - Funcionalidad equivalente a Gitea
   - Soporte para instancias cloud y on-premise
   - APIs básicas de Pull Requests

5. **Bitbucket API (REST v2):**

   - Pull Requests: creación básica
   - Branch Permissions: configuración de acceso
   - Repositorio: información básica

#### Gestión Inteligente de Tokens

**Integración con Git Tokens Manager:**

El Integration Manager se integra transparentemente con el sistema de tokens:

```python
# Detección automática de tokens
platform_info = GitPlatformDetector.detect_platform()
token = token_manager.get_platform_token(platform_info)

if token:
    # Funcionalidad completa con APIs
    api = PlatformAPIFactory.create_api(platform_info, token)
    result = api.create_pull_request(branch_info)
else:
    # Fallback graceful sin APIs
    result = create_manual_pr_instructions(platform_info, branch_info)
```

**Manejo de Errores de API:**

- **Token inválido**: Instrucciones para renovar token
- **Permisos insuficientes**: Sugerencias de permisos necesarios
- **Rate limiting**: Retry automático con backoff
- **API no disponible**: Fallback a operaciones manuales

#### Fallback Manual Elegante

Cuando las APIs no están disponibles, el sistema proporciona fallbacks elegantes:

**Generación de Instrucciones Manuales:**

```bash
$ git-integration-manager.py integrate feature/nueva-api
# (sin tokens configurados)

🎭 Git Integration Manager iniciado
📍 Contexto detectado: HYBRID
⚡ Capacidades disponibles: basic (solo Git CLI)

⚠️  APIs no disponibles - Modo manual activado

🔍 VALIDACIÓN LOCAL COMPLETADA:
   ✅ Rama: feature/nueva-api
   ✅ Estado: lista para integración
   ✅ Base: develop (actualizada)

📋 PASOS MANUALES RECOMENDADOS:

1. 🌐 Crear Pull Request manualmente:
   URL: https://github.com/usuario/proyecto/compare/develop...feature/nueva-api

2. 📝 Título sugerido:

   "Nueva API para gestión de usuarios"

3. 📋 Descripción sugerida:

   ```
   ## Descripción

   Implementa nueva API REST para gestión de usuarios con:

   - Endpoints CRUD completos
   - Autenticación JWT
   - Validación de datos

   ## Commits incluidos:

   - abc123f: [FEATURE] Añade endpoints de usuarios
   - def456a: [FEATURE] Implementa autenticación JWT
   - ghi789b: [TEST] Añade tests de integración

   ## Checklist
   - [x] Tests añadidos
   - [x] Documentación actualizada
   - [ ] Review de seguridad pendiente
   ```

4. 👥 Reviewers sugeridos:
   - @lead-developer (código)
   - @security-team (autenticación)

5. 🏷️  Labels recomendados:
   feature, api, authentication, needs-review

💡 Consejo: Configura un token con git-tokens.py para automatización completa
```

**Comandos Git Equivalentes:**

Para operaciones que no requieren APIs, el sistema genera los comandos Git equivalentes:

```bash
📋 COMANDOS EQUIVALENTES:
   git push origin feature/nueva-api
   git checkout develop
   git pull origin develop
   git merge feature/nueva-api
   git push origin develop
   git branch -d feature/nueva-api
```

Esta integración híbrida permite que el Integration Manager sea útil en cualquier contexto, desde proyectos personales hasta entornos empresariales complejos, adaptándose automáticamente a las capacidades disponibles.

---
