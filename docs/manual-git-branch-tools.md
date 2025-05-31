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

2. [Componentes y Estructura](#componentes-y-estructura)
   - [Arquitectura del Ecosistema](#arquitectura-del-ecosistema)
   - [Diagrama de Componentes](#diagrama-de-componentes)
   - [Flujo de Datos entre Herramientas](#flujo-de-datos-entre-herramientas)
   - [Detección Automática de Contexto](#detección-automática-de-contexto)
   - [Niveles de Capacidades](#niveles-de-capacidades)
   - [Contextos Soportados](#contextos-soportados)
   - [Impacto en el Comportamiento](#impacto-en-el-comportamiento)
   - [Ejemplo de Adaptación](#ejemplo-de-adaptación)

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
   - [Introducción y Propósito](#introducción-y-propósito-1)
   - [Tipos de Branch Soportados](#tipos-de-branch-soportados)
   - [Detección Automática de Contexto](#detección-automática-de-contexto-1)
   - [Prioridades de Branch Base](#prioridades-de-branch-base)
   - [Comandos y Sintaxis](#comandos-y-sintaxis-1)
   - [Git Aliases - Shortcuts para Uso Diario](#git-aliases---shortcuts-para-uso-diario)
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

El ecosistema proporciona **automatización inteligente** de operaciones Git comunes, transformando tareas repetitivas en procesos fluidos y eficientes. Desde la creación automática de ramas siguiendo convenciones de nombres hasta la gestión inteligente de merges y rebases, las herramientas anticipan las necesidades del desarrollador. Incluyen resolución automática de conflictos simples, sugerencias contextuales para mejores prácticas, y comandos compuestos que encapsulan flujos de trabajo completos, reduciendo significativamente la fricción en el desarrollo diario.

La **validación contextual** es un pilar fundamental que previene errores antes de que ocurran. El sistema implementa verificaciones proactivas de políticas de ramas, detecta tempranamente conflictos potenciales, y valida mensajes de commit según convenciones establecidas. Además, realiza comprobaciones de permisos y estados de ramas, junto con una auditoría continua de cambios sensibles en archivos críticos, asegurando la integridad y calidad del código en todo momento.

El ecosistema destaca por su capacidad de **adaptación automática** al tamaño y complejidad del proyecto. Mediante la detección inteligente del contexto (LOCAL/HYBRID/REMOTE), ajusta dinámicamente sus reglas y validaciones según el entorno. Este sistema escalable optimiza su comportamiento basándose en la criticidad de las operaciones, patrones de uso observados, y los recursos disponibles, proporcionando una experiencia óptima en cualquier escenario.

La **integración nativa** con plataformas Git como GitHub y GitLab es profunda y completa. El sistema mantiene una sincronización bidireccional de estados, gestiona automáticamente Pull Requests, y se integra perfectamente con sistemas de CI/CD. Además, proporciona soporte completo para APIs de plataformas populares, webhooks y eventos de plataforma, facilitando una experiencia de desarrollo cohesiva y moderna.

Un aspecto crucial del ecosistema es su sistema de **fallbacks elegantes** cuando las funcionalidades avanzadas no están disponibles. Implementa una degradación gradual de características según el contexto, manteniendo siempre la funcionalidad core en modo offline. El sistema ofrece alternativas locales para operaciones remotas, implementa un caché inteligente de estados y configuraciones, y proporciona recuperación automática cuando se restaura la conectividad, asegurando la continuidad del trabajo en cualquier situación.

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

**Evolución natural del workflow:**

El ecosistema evoluciona naturalmente con el crecimiento del proyecto, adaptándose a las necesidades cambiantes del equipo. **Para un desarrollador individual**, las herramientas actúan como un mentor silencioso, sugiriendo mejores prácticas y guiando hacia patrones de trabajo óptimos sin imponer restricciones. Este enfoque educativo permite a los desarrolladores aprender y adoptar buenos hábitos de forma orgánica, mientras mantienen la flexibilidad necesaria para la experimentación y el aprendizaje.

**A medida que el proyecto crece y se incorporan más desarrolladores**, el sistema se vuelve más estructurado, aplicando automáticamente convenciones básicas de nombrado y flujos de trabajo para mantener la consistencia en equipos pequeños. En esta fase, las herramientas comienzan a implementar validaciones más estrictas, asegurando que todos los miembros del equipo sigan las mismas prácticas y mantengan un código base coherente. La automatización de tareas repetitivas se vuelve más prominente, liberando a los desarrolladores para enfocarse en la creación de valor.

**Finalmente, cuando el proyecto alcanza el nivel organizacional**, las herramientas se transforman en guardianes robustos de la calidad, implementando y haciendo cumplir políticas corporativas estrictas. En este nivel, el sistema garantiza compliance regulatorio, auditoría completa de cambios, y trazabilidad en cada operación Git. Las integraciones con sistemas empresariales se vuelven críticas, permitiendo una gestión eficiente de permisos, aprobaciones y flujos de trabajo complejos de CI/CD.

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

El número de contribuidores es uno de los factores más importantes para determinar el contexto del proyecto. Este valor se obtiene analizando el historial de commits del repositorio y contando las direcciones de email únicas que han realizado commits.

Este factor es crucial porque:

1. Define el nivel de coordinación necesario
2. Indica la complejidad de la gestión del proyecto
3. Determina qué tipo de reglas y validaciones son apropiadas

El sistema utiliza este valor como uno de los principales indicadores para decidir entre los contextos LOCAL, HYBRID y REMOTE.

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

El número total de commits en el repositorio es un indicador importante de la madurez y estabilidad del proyecto. Este factor ayuda a determinar qué nivel de validación y control es apropiado.

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

La configuración de remotos determina el contexto del proyecto al indicar si el código está siendo compartido y colaborado a través de un repositorio centralizado (como GitHub, GitLab o Bitbucket) o si es un proyecto puramente local. Esto afecta directamente las reglas de validación que se aplicarán.

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

**¿Qué calcula?**

El sistema analiza los archivos de configuración de CI/CD (Integración Continua/Despliegue Continuo) para determinar qué procesos de desarrollo están automatizados, desde la ejecución de pruebas hasta el despliegue en producción.

**¿Para qué sirve?**

Este factor ayuda a determinar el nivel de automatización y madurez del proyecto, permitiendo aplicar las validaciones y controles apropiados según la infraestructura de CI/CD existente.

**¿Qué hace con esa información?**

El sistema utiliza esta información para:
- Ajustar las reglas de validación según el nivel de automatización
- Determinar si se requieren validaciones adicionales manuales
- Configurar los hooks de Git apropiados para el nivel de CI/CD
- Adaptar los workflows de desarrollo al contexto de automatización del proyecto

**¿Qué detecta?**

El sistema analiza la presencia de archivos y directorios de configuración de sistemas de CI/CD populares:

**Tipos de configuración:**

- **Sin CI/CD**: Proyecto manual o en etapas tempranas
- **CI básico**: Tests automatizados
- **CI/CD completo**: Pipeline completo de integración y despliegue
- **CI/CD empresarial**: Múltiples entornos, gates de calidad, etc.


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

El sistema analiza la estructura de branches del repositorio para determinar el flujo de trabajo de desarrollo implementado. Esta información es crucial para aplicar las validaciones y controles apropiados según el modelo de branching utilizado.

**¿Para qué sirve?**

Este factor ayuda a:
- Identificar el modelo de branching (Git Flow, GitHub Flow, etc.)
- Determinar el nivel de madurez del proceso de desarrollo
- Ajustar las validaciones según la estructura de branches
- Configurar protecciones específicas por tipo de rama

**¿Qué hace con esa información?**

El sistema utiliza esta información para:
- Adaptar las reglas de validación al modelo de branching
- Configurar protecciones específicas por rama
- Ajustar los mensajes y warnings según el contexto
- Determinar qué operaciones están permitidas en cada rama

**¿Qué detecta?**

El sistema analiza la presencia y uso de ramas especiales que indican diferentes niveles de madurez en el proceso de desarrollo:

**Tipos de estructura:**

- **Simple**: Solo main/master
- **Git Flow**: develop + feature branches
- **GitHub Flow**: main + feature branches
- **Enterprise**: múltiples ramas de integración y release

**¿Por qué es crítico?**

La estructura de branches indica:
- Nivel de formalidad del proceso
- Complejidad del proyecto
- Necesidad de controles específicos
- Madurez del equipo de desarrollo


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

### Git Aliases - Shortcuts para Uso Diario

Una de las características más útiles del Branch Git Helper es su sistema de aliases persistentes que transforman comandos largos en shortcuts simples y memorables. Los aliases se integran directamente con Git, permitiendo usar comandos como `git new-feature` en lugar de `branch-git-helper.py feature`.

#### ¿Por qué usar Git Aliases?

**Productividad Diaria**: Los aliases reducen significativamente la fricción en el uso diario. En lugar de escribir `branch-git-helper.py feature "nueva-funcionalidad"`, simplemente escribes `git new-feature "nueva-funcionalidad"`.

**Integración Natural**: Los aliases se integran perfectamente con el flujo de trabajo de Git existente. Funcionan desde cualquier directorio y se sienten como comandos nativos de Git.

**Consistencia de Equipo**: Una vez instalados, todos los miembros del equipo pueden usar los mismos shortcuts, creando un vocabulario común y reduciendo la curva de aprendizaje.

**Flexibilidad Multi-proyecto**: Los aliases incluyen variantes para trabajar con múltiples proyectos desde un solo lugar, ideal para desarrolladores que manejan varios repositorios.

#### Instalación de Aliases

```bash
# Instalar todos los aliases persistentes
branch-git-helper.py install-aliases

# Verificar que los aliases están instalados
git config --global --get-regexp alias.new-

# Desinstalar aliases si es necesario
branch-git-helper.py uninstall-aliases
```

**Proceso de Instalación:**

1. **Backup Automático**: Se crea automáticamente un backup de tu `.gitconfig` en `~/.gitconfig.backup`
2. **Instalación Global**: Los aliases se instalan globalmente, disponibles en todos tus repositorios
3. **Verificación**: El sistema verifica que cada alias se instale correctamente
4. **Confirmación**: Muestra un resumen de todos los aliases instalados

#### Aliases para Proyecto Actual

Estos aliases funcionan en el directorio actual donde ejecutas el comando:

```bash
# Aliases básicos para tipos de branch
git new-feature "descripción"      # Crear feature branch
git new-fix "descripción"          # Crear fix branch
git new-hotfix "descripción"       # Crear hotfix branch
git new-docs "descripción"         # Crear docs branch
git new-refactor "descripción"     # Crear refactor branch
git new-test "descripción"         # Crear test branch
git new-chore "descripción"        # Crear chore branch

# Comando de estado
git branch-status                  # Estado del repositorio actual
```

**Ejemplos de uso:**

```bash
# En lugar de: branch-git-helper.py feature "nueva-autenticacion"
git new-feature "nueva-autenticacion"

# En lugar de: branch-git-helper.py hotfix "vulnerabilidad-critica"
git new-hotfix "vulnerabilidad-critica"

# En lugar de: branch-git-helper.py status
git branch-status
```

#### Aliases para Proyectos Específicos

Estos aliases permiten trabajar con repositorios en diferentes ubicaciones sin cambiar de directorio:

```bash
# Aliases multi-proyecto
git new-feature-in /path/to/project "descripción"    # Feature en proyecto específico
git new-fix-in ../mi-proyecto "descripción"          # Fix en proyecto relativo
git branch-status-in /path/to/project                # Estado de proyecto específico
```

**Casos de uso prácticos:**

```bash
# Gestionar múltiples proyectos desde un workspace
git new-feature-in ~/proyectos/frontend "ui-mejoras"
git new-feature-in ~/proyectos/backend "api-usuarios"
git new-fix-in ../proyecto-cliente "bug-critico"

# Verificar estado de múltiples proyectos
git branch-status-in ~/trabajo/proyecto-a
git branch-status-in ~/trabajo/proyecto-b
git branch-status-in ~/personal/mi-app
```

#### Configuración Técnica de Aliases

Los aliases se configuran usando el sistema de configuración global de Git:

**Estructura de los aliases:**

```bash
# Alias básico (ejemplo interno)
git config --global alias.new-feature '!python /path/to/branch-git-helper.py feature'

# Alias multi-proyecto (ejemplo interno)
git config --global alias.new-feature-in '!f() { python /path/to/branch-git-helper.py -p "$1" feature "$2"; }; f'
```

**Características técnicas:**

- **Rutas Absolutas**: Los aliases usan rutas absolutas al script, funcionando desde cualquier directorio
- **Funciones Shell**: Los aliases multi-proyecto usan funciones shell para manejar múltiples parámetros
- **Configuración Global**: Se almacenan en `~/.gitconfig` para disponibilidad universal
- **Compatibilidad**: Funcionan en bash, zsh, fish y otros shells compatibles

#### Verificación y Troubleshooting

**Verificar aliases instalados:**

```bash
# Listar todos los aliases del Branch Helper
git config --global --get-regexp alias.new-
git config --global --get-regexp alias.branch-status

# Probar un alias específico
git new-feature --help
```

**Problemas comunes y soluciones:**

**Error: "command not found"**
```bash
# Verificar que el script existe en la ruta configurada
which branch-git-helper.py

# Reinstalar aliases si la ruta cambió
branch-git-helper.py install-aliases
```

**Error: "permission denied"**
```bash
# Verificar permisos del script
ls -la $(which branch-git-helper.py)

# Hacer ejecutable si es necesario
chmod +x $(which branch-git-helper.py)
```

**Aliases no funcionan en nuevo terminal**
```bash
# Verificar que están en configuración global
git config --global --list | grep alias.new-

# Recargar configuración de shell
source ~/.bashrc  # o ~/.zshrc según tu shell
```

#### Integración con IDEs y Editores

Los aliases también funcionan desde terminales integrados en IDEs:

**VS Code:**
```bash
# Terminal integrado de VS Code
git new-feature "nueva-funcionalidad"
```

**JetBrains IDEs (IntelliJ, PyCharm, etc.):**
```bash
# Terminal integrado
git new-hotfix "fix-urgente"
```

**Vim/Neovim:**
```bash
# Desde terminal en vim
:terminal git new-feature "mejora-editor"
```

#### Personalización Avanzada

**Crear aliases personalizados adicionales:**

```bash
# Alias personalizado para workflow específico
git config --global alias.quick-feature '!f() { git new-feature "$1" && git commit --allow-empty -m "[FEATURE] Start $1"; }; f'

# Usar el alias personalizado
git quick-feature "nueva-idea"
```

**Combinar con otros comandos Git:**

```bash
# Workflow completo en un alias
git config --global alias.feature-complete '!f() { git new-feature "$1" && git push && echo "Feature $1 ready for development"; }; f'
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

# Crear feature branch (usando alias)
git new-feature "login-usuario"
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

# Crear feature branch (usando alias)
git new-feature "api-usuarios"
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

# Crear hotfix urgente (usando alias)
git new-hotfix "vulnerabilidad-seguridad"
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

#### Ejemplos con Aliases Multi-proyecto

```bash
# Gestionar múltiples proyectos desde un workspace central
cd ~/workspace

# Crear features en diferentes proyectos sin cambiar directorio
git new-feature-in ./frontend "nueva-ui"
git new-feature-in ./backend "api-mejorada"
git new-feature-in ../cliente/proyecto "funcionalidad-especial"

# Verificar estado de múltiples proyectos
git branch-status-in ./frontend
git branch-status-in ./backend
git branch-status-in ../cliente/proyecto

# Crear diferentes tipos de branches en proyectos específicos
git new-fix-in ./frontend "corregir-responsive"
git new-docs-in ./backend "actualizar-api-docs"
git new-test-in ./shared-lib "unit-tests-utils"
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

## Branch Workflow Validator - Validación Contextual

### Introducción y Propósito

Branch Workflow Validator es el sistema de validación contextual del ecosistema Git Branch Tools, diseñado para verificar operaciones Git antes de ejecutarlas y prevenir errores comunes en el flujo de trabajo. Su propósito principal es actuar como una red de seguridad inteligente que se adapta automáticamente al contexto del proyecto.

El validador funciona como un guardian contextual que analiza cada operación Git (commits, pushes, merges, creación/eliminación de branches) y aplica diferentes niveles de validación según el entorno detectado. Esto significa que las mismas operaciones pueden ser permisivas en proyectos personales pero estrictas en entornos empresariales.

**¿Por qué implementar un Workflow Validator?**

El Workflow Validator es esencial para mantener la integridad y calidad del código en cualquier proyecto Git, independientemente de su escala. Actúa como un sistema de control preventivo que:

- Intercepta operaciones potencialmente problemáticas antes de que afecten el repositorio
- Guía a los desarrolladores hacia mejores prácticas de Git
- Asegura consistencia en el flujo de trabajo del equipo
- Se adapta automáticamente según el contexto del proyecto

**Prevención Proactiva de Errores**: El validador intercepta operaciones problemáticas antes de que causen daño, como pushes directos a ramas protegidas, nombres de ramas incorrectos, o operaciones sin upstream tracking configurado.

**Educación Contextual**: En contextos permisivos, el validador actúa como mentor, sugiriendo mejores prácticas sin bloquear el trabajo. En contextos estrictos, enforza políticas corporativas sin excepciones.

**Consistencia de Equipo**: Asegura que todos los miembros del equipo sigan las mismas reglas y convenciones, independientemente de su nivel de experiencia con Git.

**Adaptación Automática**: El validador evoluciona con el proyecto, desde validaciones educativas en proyectos personales hasta compliance empresarial en entornos corporativos.

### Niveles de Validación

El validador implementa tres niveles de validación que se adaptan automáticamente al contexto detectado:

#### Nivel PERMISSIVE (Contexto LOCAL)

**Características:**

- Solo muestra warnings educativos
- No bloquea ninguna operación
- Enfoque en enseñar mejores prácticas
- Máxima flexibilidad para experimentación

**Configuración:**

```json
{
  "level": "permissive",
  "protected_branches": ["main", "master"],
  "require_upstream": false,
  "require_pr": false,
  "allow_direct_push_to_main": true,
  "enforce_branch_naming": false,
  "require_linear_history": false
}
```

**Ejemplo de salida:**

```bash
$ branch-workflow-validator.py push --target-branch main

🔍 Resultados de Validación
  ℹ️  Contexto detectado: LOCAL (nivel: permissive)
  ⚠️  Nombre de rama 'experimental-feature' no sigue convenciones recomendadas
  ℹ️  Push directo a 'main' permitido en contexto LOCAL
  ⚠️  Considera usar formato: feature/descripcion para mejor organización

✅ Todas las validaciones pasaron exitosamente
```

#### Nivel MODERATE (Contexto HYBRID)

**Características:**

- Combina warnings con algunos bloqueos críticos
- Balance entre flexibilidad y control
- Ideal para equipos pequeños en crecimiento
- Enforza convenciones importantes pero no obsesivamente

**Configuración:**

```json
{
  "level": "moderate",
  "protected_branches": ["main", "master", "develop"],
  "require_upstream": true,
  "require_pr": false,
  "allow_direct_push_to_main": false,
  "enforce_branch_naming": true,
  "require_linear_history": false
}
```

**Ejemplo de salida:**

```bash
$ branch-workflow-validator.py push --target-branch main

🔍 Resultados de Validación
  ℹ️  Contexto detectado: HYBRID (nivel: moderate)
  ✅ Nombre válido para rama feature: feature/nueva-funcionalidad
  ❌ Push directo a rama protegida 'main' no permitido. Usar Pull Request.
  ⚠️  Se requiere Pull Request para cambios en 'main'

❌ 1 error(es) encontrado(s)
```

#### Nivel STRICT (Contexto REMOTE)

**Características:**

- Validación estricta con cero tolerancia
- Bloquea operaciones que no cumplan políticas
- Compliance empresarial completo
- Auditoría y trazabilidad obligatoria

**Configuración:**

```json
{
  "level": "strict",
  "protected_branches": ["main", "master", "develop", "staging", "release"],
  "require_upstream": true,
  "require_pr": true,
  "allow_direct_push_to_main": false,
  "enforce_branch_naming": true,
  "require_linear_history": true
}
```

**Ejemplo de salida:**

```bash
$ branch-workflow-validator.py commit

🔍 Resultados de Validación
  ℹ️  Contexto detectado: REMOTE (nivel: strict)
  ✅ Nombre válido para rama feature: feature/microservicio-pagos
  ✅ Rama 'feature/microservicio-pagos' creada correctamente desde 'develop'
  ✅ No hay conflictos de merge pendientes

✅ Todas las validaciones pasaron exitosamente
```

### Reglas de Validación

El validador de ramas implementa un conjunto de reglas que varían según el contexto de ejecución (LOCAL, HYBRID, REMOTE) y el nivel de validación (relaxed, moderate, strict). Estas reglas aseguran la integridad del flujo de trabajo Git y previenen operaciones potencialmente peligrosas.

#### Validación de Nombres de Rama

El validador enforza convenciones de naming según patrones predefinidos:

**Patrones Soportados:**

- `feature/descripcion-clara`: Nuevas funcionalidades
- `fix/descripcion-del-problema`: Correcciones de bugs
- `hotfix/descripcion-urgente`: Correcciones críticas
- `docs/tema-documentacion`: Cambios de documentación
- `refactor/area-refactorizada`: Refactorización de código
- `test/area-testing`: Añadir o mejorar tests
- `chore/tarea-mantenimiento`: Tareas de mantenimiento
- `release/v1.0.0`: Ramas de release con versionado

**Ramas Principales Válidas:**

- `main`, `master`, `develop`, `staging`

**Ejemplos de validación:**

```bash
# ✅ Nombres válidos
feature/nueva-autenticacion
fix/error-calculo-iva
hotfix/vulnerabilidad-critica
docs/api-reference
refactor/estructura-modulos
test/unit-tests-auth
chore/actualizar-dependencias
release/v2.1.0

# ❌ Nombres inválidos (en contexto strict)
nueva-feature              # Falta prefijo de tipo
feature-nueva              # Formato incorrecto
experimental               # No sigue convención
temp-fix                   # Formato incorrecto
```

#### Validación de Ramas Protegidas

El validador previene operaciones peligrosas en ramas protegidas:

**Operaciones Validadas:**

- **Push directo**: Bloquea push directo a ramas protegidas en contextos moderate/strict
- **Eliminación**: Previene eliminación accidental de ramas críticas
- **Merge directo**: Enforza uso de Pull Requests cuando corresponde

**Ejemplo de configuración por contexto:**

```python
# LOCAL: Solo main/master protegidas, push directo permitido
"protected_branches": ["main", "master"]
"allow_direct_push_to_main": true

# HYBRID: Añade develop, push directo bloqueado
"protected_branches": ["main", "master", "develop"]
"allow_direct_push_to_main": false

# REMOTE: Protección completa
"protected_branches": ["main", "master", "develop", "staging", "release"]
"allow_direct_push_to_main": false
```

#### Validación de Upstream Tracking

El validador verifica configuración de upstream para asegurar sincronización:

**Verificaciones:**

- Rama actual tiene upstream configurado
- Upstream apunta al remoto correcto
- No hay configuraciones huérfanas

**Comportamiento por contexto:**

```bash
# LOCAL: Opcional (solo warning)
⚠️  Rama 'feature/nueva-api' no tiene upstream tracking. Usar: git push -u origin feature/nueva-api

# HYBRID/REMOTE: Obligatorio (error)
❌ Rama 'feature/nueva-api' no tiene upstream tracking. Usar: git push -u origin feature/nueva-api
```

#### Validación de Rama Base

El validador verifica que las ramas se hayan creado desde la rama base correcta:

**Reglas por tipo de rama:**

- `hotfix/*`: Debe crearse desde `main` o `master`
- `feature/*`, `fix/*`, `docs/*`, `refactor/*`, `test/*`, `chore/*`: Desde `develop` o `main`
- `release/*`: Desde `develop`

**Verificación técnica:**

```bash
# El validador usa git merge-base para verificar el ancestro
git merge-base --is-ancestor develop feature/nueva-api
# Si retorna 0, la rama se creó correctamente desde develop
```

#### Validación de Conflictos de Merge

El validador detecta conflictos pendientes antes de operaciones críticas:

**Detección:**

```bash
# Busca archivos con conflictos no resueltos
git diff --name-only --diff-filter=U
```

**Bloqueo:**

```bash
❌ Conflictos de merge detectados en: src/auth.py, config/settings.py
```

#### Validación de Requerimiento de Pull Request

En contextos estrictos, el validador enforza uso de Pull Requests:

**Criterios:**

- Operaciones en ramas protegidas requieren PR
- Push directo bloqueado en contexto strict
- Warnings en contexto moderate

### Integración con Git Hooks

El validador está diseñado para integrarse seamlessly con Git hooks para validación automática:

#### Pre-Commit Hook

El hook pre-commit se ejecuta automáticamente antes de cada commit para validar que los cambios cumplan con las reglas del workflow. Este hook actúa como primera línea de defensa, verificando el formato del mensaje de commit, la rama base y otros criterios antes de permitir que el commit se complete.

**Contenido del hook:**

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Ejecutar validación de commit
python3 .githooks/branch-workflow-validator.py commit

# Si falla, bloquear commit
if [ $? -ne 0 ]; then
    echo "❌ Commit bloqueado por validaciones fallidas"
    exit 1
fi
```

#### Pre-Push Hook

El hook pre-push se ejecuta automáticamente antes de cada push para validar que la operación cumpla con las reglas del workflow. Este hook actúa como segunda línea de defensa, verificando que el push sea permitido según el contexto de la rama destino y las políticas establecidas.

**Contenido del hook:**

```bash
#!/bin/bash
# .git/hooks/pre-push

# Obtener información del push
while read local_ref local_sha remote_ref remote_sha; do
    # Extraer nombre de rama remota
    remote_branch=$(echo $remote_ref | sed 's/refs\/heads\///')

    # Validar push
    python3 .githooks/branch-workflow-validator.py push --target-branch $remote_branch

    if [ $? -ne 0 ]; then
        echo "❌ Push bloqueado por validaciones fallidas"
        exit 1
    fi
done

exit 0
```

#### Configuración de Hooks

El ecosistema utiliza el framework **pre-commit** para gestionar los hooks de Git. La configuración está centralizada en `.pre-commit-config.yaml` que ya incluye la integración con el Branch Workflow Validator.

**Configuración con Pre-commit Framework:**

1. **Verificar pre-commit** (braintools ya maneja la instalación):

   ```bash
   # Verificar que pre-commit esté instalado
   pre-commit --version
   ```

2. **Instalar hooks en el repositorio**:
   ```bash
   # Si usas braintools, la configuración es automática

   # Si no usas braintools, instalar manualmente:
   # pre-commit install
   # pre-commit install --hook-type commit-msg
   # pre-commit install --hook-type pre-push
   ```

3. **Verificar instalación**:
   ```bash
   # Verificar que los hooks estén instalados
   ls -la .git/hooks/

   # Probar hooks manualmente
   pre-commit run --all-files

   # Probar el validador específico
   .githooks/branch-workflow-validator.py status
   ```

**Configuración incluida automáticamente en `.pre-commit-config.yaml`:**

```yaml
# Branch Workflow Commit Validation
- repo: local
  hooks:
    - id: branch-workflow-commit
      name: branch-workflow-commit-validator
      entry: .githooks/branch-workflow-validator.py commit
      language: system
      stages: [pre-commit]
      pass_filenames: false
      always_run: true
      verbose: true

# Branch Workflow Push Validation
- repo: local
  hooks:
    - id: branch-workflow-push
      name: branch-workflow-push-validator
      entry: .githooks/branch-workflow-validator.py push
      language: system
      stages: [pre-push]
      pass_filenames: false
      always_run: true
      verbose: true
```

**Ejecución manual para pruebas:**
```bash
# Ejecutar todos los hooks
pre-commit run --all-files

# Ejecutar solo el validador de workflow
pre-commit run branch-workflow-commit
pre-commit run branch-workflow-push

# Ejecutar directamente el validador
.githooks/branch-workflow-validator.py commit
.githooks/branch-workflow-validator.py push --target-branch main
```

---

## Workflows Completos End-to-End

Esta sección demuestra cómo todas las herramientas del ecosistema Git Branch Tools trabajan juntas para crear workflows completos y eficientes. Los ejemplos muestran flujos de trabajo reales desde la concepción de una idea hasta su implementación en producción, adaptándose automáticamente al contexto del proyecto.

### Workflow de Feature Development

El workflow de desarrollo de features es el más común en cualquier proyecto de software. Este flujo demuestra cómo crear, desarrollar, validar e integrar una nueva funcionalidad usando todo el ecosistema.

#### Fase 1: Planificación y Configuración

**Configuración inicial del entorno:**

```bash
# 1. Verificar estado del ecosistema
git-integration-manager.py status
branch-git-helper.py status
git-tokens.py get github-integration

# 2. Asegurar configuración de tokens (si es necesario)
git-tokens.py set github-integration

# 3. Verificar protecciones remotas
git-integration-manager.py protection-status
```

**Análisis del contexto del proyecto:**

```bash
# El sistema detecta automáticamente:
# - Contexto: HYBRID (equipo de 4 desarrolladores)
# - Estructura: develop + feature branches
# - CI/CD: GitHub Actions básico
# - Protecciones: main y develop protegidas
```

#### Fase 2: Creación de Feature Branch

**Creación inteligente de la rama:**

```bash
# Usar alias para máxima eficiencia
git new-feature "sistema-notificaciones-push"

# El sistema ejecuta automáticamente:
# 1. Detecta contexto HYBRID
# 2. Selecciona 'develop' como rama base
# 3. Sincroniza con remoto: git pull origin develop
# 4. Crea rama: feature/sistema-notificaciones-push
# 5. Configura upstream: git push -u origin feature/sistema-notificaciones-push
# 6. Aplica validaciones moderadas
```

**Salida del sistema:**

```bash
🎭 Contexto detectado: HYBRID (equipo colaborativo)
📊 Análisis del repositorio:
   - Contribuidores: 4 (equipo pequeño)
   - Commits: 234 (proyecto establecido)
   - Remotos: 1 (origin configurado)
   - CI/CD: Básico detectado (.github/workflows)

⚖️ Modo balanceado: Productividad con orden

🔍 Validando formato de branch... ✅
📡 Sincronizando con remoto...
   git fetch origin develop... ✅
   git pull origin develop... ✅ (ya actualizado)

📍 Rama base seleccionada: develop
✅ Rama creada: feature/sistema-notificaciones-push
🔄 Cambiado a feature/sistema-notificaciones-push
📤 Configurando upstream tracking...
   git push -u origin feature/sistema-notificaciones-push... ✅

🎉 ¡Branch lista para colaboración!
```

#### Fase 3: Desarrollo Iterativo

**Desarrollo con validación continua:**

```bash
# Desarrollo iterativo con commits validados
echo "notification service" > src/notifications.py
git add src/notifications.py
git commit -m "[FEATURE] Añade servicio base de notificaciones"

# El Branch Workflow Validator se ejecuta automáticamente:
# - Valida formato de commit ✅
# - Verifica rama apropiada ✅
# - Confirma ausencia de conflictos ✅

# Continuar desarrollo
echo "push notification logic" >> src/notifications.py
git add src/notifications.py
git commit -m "[FEATURE] Implementa lógica de push notifications"

# Añadir tests
echo "notification tests" > tests/test_notifications.py
git add tests/test_notifications.py
git commit -m "[TEST] Añade tests para sistema de notificaciones"

# Push automático (upstream ya configurado)
git push
```

**Validación continua en acción:**

```bash
# Cada commit es validado automáticamente
🔍 Resultados de Validación
  ℹ️ Contexto detectado: HYBRID (nivel: moderate)
  ✅ Nombre válido para rama feature: feature/sistema-notificaciones-push
  ✅ Formato de commit válido: [FEATURE] Implementa lógica de push notifications
  ✅ Rama creada correctamente desde 'develop'
  ✅ No hay conflictos de merge pendientes

✅ Todas las validaciones pasaron exitosamente
```

#### Fase 4: Integración y Pull Request

**Integración automática con el ecosistema:**

```bash
# Integración completa usando Integration Manager
git-integration-manager.py integrate feature/sistema-notificaciones-push --mode auto
```

**Proceso de integración automática:**

```bash
🎭 Git Integration Manager iniciado
📍 Contexto detectado: HYBRID (equipo colaborativo)
⚡ Capacidades disponibles: enhanced (APIs + Git CLI)

🔍 VALIDACIÓN PRE-INTEGRACIÓN:
   ✅ Rama actual: feature/sistema-notificaciones-push
   ✅ Commits no pusheados: 0
   ✅ Estado de sincronización: actualizado
   ✅ Conflictos: ninguno detectado
   ✅ Tests locales: pasando (si están configurados)

📡 SINCRONIZACIÓN:
   git fetch origin develop... ✅
   Estado: rama base actualizada

🚀 CREACIÓN DE PULL REQUEST:
   🌐 Plataforma detectada: GitHub
   📝 Título: "[AUTO] Integrate feature/sistema-notificaciones-push"
   📋 Descripción:
   ```
   ## Sistema de Notificaciones Push

   ### Descripción
   Implementa sistema completo de notificaciones push con:
   - Servicio base de notificaciones
   - Lógica de push notifications
   - Tests unitarios completos

   ### Commits incluidos:
   - abc123f: [FEATURE] Añade servicio base de notificaciones
   - def456a: [FEATURE] Implementa lógica de push notifications
   - ghi789b: [TEST] Añade tests para sistema de notificaciones

   ### Checklist
   - [x] Tests añadidos
   - [x] Funcionalidad implementada
   - [ ] Review de código pendiente
   - [ ] Documentación actualizada
   ```

✅ Pull Request creado: https://github.com/equipo/proyecto/pull/42

🎉 INTEGRACIÓN COMPLETADA:
   📍 PR URL: https://github.com/equipo/proyecto/pull/42
   📋 Próximos pasos:
      1. Revisar y configurar reviewers manualmente
      2. Monitorear CI/CD: https://github.com/equipo/proyecto/actions
      3. Hacer merge manual tras aprobaciones
```

#### Fase 5: Review y Merge

**Proceso de review colaborativo:**

```bash
# El equipo revisa el PR creado automáticamente
# - CI/CD se ejecuta automáticamente
# - Tests pasan ✅
# - Code review por compañeros
# - Aprobación del PR

# Merge manual tras aprobaciones
# (El ecosistema puede automatizar esto en contextos REMOTE)
```

#### Fase 6: Limpieza Post-merge

**Limpieza automática del repositorio:**

```bash
# Después del merge, limpiar branches obsoletas
git-integration-manager.py cleanup --execute

📋 Acciones de limpieza: 1
  • feature/sistema-notificaciones-push (mergeada, 0 días)

✅ Limpieza completada:
   🗑️ 1 rama eliminada
   📊 Repositorio optimizado
```

### Workflow de Hotfix

Los hotfixes requieren un flujo especial para correcciones urgentes en producción. Este workflow demuestra la gestión de emergencias con máxima eficiencia y seguridad.

#### Situación: Vulnerabilidad Crítica Detectada

**Detección y respuesta inmediata:**

```bash
# Situación: Vulnerabilidad de seguridad detectada en producción
# Necesidad: Fix inmediato sin esperar el ciclo normal de desarrollo

# 1. Verificar estado actual
git branch-status
# Rama actual: feature/nueva-funcionalidad (en desarrollo)

# 2. Crear hotfix inmediatamente
git new-hotfix "vulnerabilidad-auth-bypass"
```

**Creación automática de hotfix:**

```bash
🎭 Contexto detectado: HYBRID (equipo colaborativo)
📊 Análisis del repositorio: [datos del proyecto]

🚨 MODO HOTFIX ACTIVADO - Prioridad máxima

🔍 Validando contexto de emergencia... ✅
📡 Sincronizando con producción...
   git fetch origin main... ✅
   git pull origin main... ✅

📍 Rama base seleccionada: main (producción)
✅ Rama creada: hotfix/vulnerabilidad-auth-bypass
🔄 Cambiado a hotfix/vulnerabilidad-auth-bypass
📤 Configurando upstream tracking...
   git push -u origin hotfix/vulnerabilidad-auth-bypass... ✅

🚨 ¡Hotfix listo para desarrollo urgente!
⏰ Tiempo total: 15 segundos
```

#### Desarrollo del Fix

**Implementación rápida y segura:**

```bash
# Implementar fix de seguridad
echo "security fix implementation" > src/auth/security_patch.py
git add src/auth/security_patch.py
git commit -m "[HOTFIX] Corrige vulnerabilidad de bypass en autenticación"

# Añadir test de seguridad
echo "security test" > tests/test_security_patch.py
git add tests/test_security_patch.py
git commit -m "[TEST] Añade test para fix de vulnerabilidad"

# Push inmediato
git push
```

#### Integración Urgente

**Fast-track para producción:**

```bash
# Integración urgente con validaciones estrictas
git-integration-manager.py integrate hotfix/vulnerabilidad-auth-bypass --mode auto
```

**Proceso acelerado:**

```bash
🚨 MODO HOTFIX DETECTADO - Fast-track activado

🔍 VALIDACIÓN CRÍTICA:
   ✅ Hotfix desde main: correcto
   ✅ Commits de seguridad: validados
   ✅ Tests de seguridad: incluidos
   ✅ Sin conflictos: confirmado

🚀 CREACIÓN DE PR URGENTE:
   🌐 Plataforma: GitHub
   📝 Título: "[HOTFIX] Vulnerabilidad auth bypass - URGENTE"
   🏷️ Labels: hotfix, security, urgent
   👥 Reviewers: @security-team, @lead-developer

✅ PR urgente creado: https://github.com/equipo/proyecto/pull/43

⚡ NOTIFICACIONES ENVIADAS:
   📧 Email a security-team
   💬 Slack #security-alerts
   📱 SMS a on-call engineer

🎯 PRÓXIMOS PASOS CRÍTICOS:
   1. Review inmediato por security team
   2. Merge tras aprobación de seguridad
   3. Deploy automático a staging
   4. Deploy manual a producción tras validación
```

### Workflow de Release

El workflow de release coordina la preparación, validación y despliegue de nuevas versiones. Este proceso es crítico para mantener la calidad y estabilidad del software.

#### Preparación de Release

**Inicialización del proceso de release:**

```bash
# Preparar release v2.1.0
git new-chore "preparar-release-v2.1.0"

# Análisis de cambios desde último release
git-integration-manager.py health-check
```

**Análisis de salud pre-release:**

```bash
📊 Reporte de Salud del Repositorio - Pre-Release
====================================
🌳 Total branches: 12
✅ Branches activas: 8
✅ Branches mergeadas: 4
⚠️ Branches stale: 0
👥 Contribuidores activos: 4
📈 Score de salud: 92.5/100

📋 ANÁLISIS DE RELEASE:
   ✅ Todas las features mergeadas en develop
   ✅ No hay branches stale
   ✅ CI/CD pasando en develop
   ✅ Tests de integración: 98% coverage

🎯 RECOMENDACIÓN: Repositorio listo para release
```

#### Creación de Release Branch

**Branch de release con validaciones especiales:**

```bash
# Crear branch de release desde develop
branch-git-helper.py -p . release "v2.1.0" --no-sync

# El sistema aplica validaciones especiales para releases:
# - Verifica que develop esté estable
# - Confirma que todas las features estén mergeadas
# - Valida que no hay work-in-progress
```

#### Preparación y Validación

**Proceso completo de preparación:**

```bash
# En la rama release/v2.1.0

# 1. Actualizar versiones
echo "2.1.0" > VERSION
git add VERSION
git commit -m "[RELEASE] Bump version to 2.1.0"

# 2. Generar changelog
echo "## v2.1.0 - $(date +%Y-%m-%d)" > CHANGELOG_NEW.md
echo "- Sistema de notificaciones push" >> CHANGELOG_NEW.md
echo "- Mejoras de seguridad" >> CHANGELOG_NEW.md
cat CHANGELOG.md >> CHANGELOG_NEW.md
mv CHANGELOG_NEW.md CHANGELOG.md
git add CHANGELOG.md
git commit -m "[RELEASE] Actualiza changelog para v2.1.0"

# 3. Ejecutar tests completos
git push
# CI/CD ejecuta suite completa de tests

# 4. Validación de release
branch-workflow-validator.py release --target-branch release/v2.1.0
```

#### Integración de Release

**Merge a main y develop:**

```bash
# Integrar release a main (producción)
git-integration-manager.py integrate release/v2.1.0 --target main --mode auto

# El sistema crea automáticamente:
# 1. PR de release/v2.1.0 → main
# 2. PR de release/v2.1.0 → develop (back-merge)
# 3. Tag de versión v2.1.0
# 4. Release notes automáticas
```

### Workflow Empresarial Completo

En entornos empresariales, los workflows son más complejos e incluyen múltiples etapas de validación, aprobaciones y compliance. Este ejemplo muestra un workflow completo para una empresa con políticas estrictas.

#### Contexto Empresarial

**Configuración inicial del entorno empresarial:**

```bash
# Proyecto empresarial detectado automáticamente:
# - 23 contribuidores
# - 2,847 commits
# - CI/CD complejo
# - Múltiples entornos (dev, staging, prod)
# - Compliance SOX requerido

# Verificar configuración empresarial
git-integration-manager.py status
```

**Estado del entorno empresarial:**

```bash
📊 Estado del Integration Manager - Entorno Empresarial
===============================
📍 Contexto: REMOTE (empresarial)
⚡ Capacidades: enterprise (APIs + Compliance + Auditoría)
🐙 GitHub Enterprise: ✅
🔒 Compliance SOX: ✅
🛡️ Security scanning: ✅
📋 Audit logging: ✅
```

#### Configuración de Protecciones Empresariales

**Aplicar políticas corporativas:**

```bash
# Configurar protecciones empresariales completas
git-integration-manager.py setup-remote-protection --strategy remote --dry-run
```

**Configuración empresarial aplicada:**

```bash
🎯 Aplicando estrategia 'remote' en github-enterprise
📊 Análisis del repositorio:
   - Contribuidores: 23 (equipo grande)
   - Commits: 2,847 (proyecto maduro)
   - Compliance: SOX requerido

📋 Configuración empresarial para github-enterprise:
   Configuración:
   - Require reviews: 2 mínimo (1 de arquitecto)
   - Status checks: ci/tests, ci/security, ci/compliance, ci/performance
   - Acceso restringido: Solo miembros autorizados
   - Enforce admins: Sí (sin excepciones)
   - Audit logging: Completo
   - Compliance checks: SOX, GDPR

🛡️ APLICANDO PROTECCIÓN EMPRESARIAL:
   ✅ main: Protección máxima + compliance
   ✅ master: Protección máxima + compliance
   ✅ develop: Protección alta + reviews
   ✅ staging: Protección media + tests
   ✅ release: Protección alta + compliance

🎉 CONFIGURACIÓN EMPRESARIAL COMPLETADA:
   🔒 5 branches con protección empresarial
   ✅ Compliance SOX establecido
   📊 Auditoría completa activada
   🛡️ Security scanning obligatorio
```

#### Desarrollo con Compliance

**Feature development con auditoría completa:**

```bash
# Crear feature con validaciones empresariales
git new-feature "microservicio-facturacion"
```

**Validaciones empresariales en acción:**

```bash
🎭 Contexto detectado: REMOTE (validación estricta)
📊 Análisis del repositorio: [datos empresariales]

🔒 Modo compliance: Políticas corporativas activadas

🔍 VALIDACIONES CORPORATIVAS:
   ✅ Formato de branch: Cumple estándares empresariales
   ✅ Usuario autorizado: Permisos verificados en AD
   ✅ Rama base: develop (política corporativa)
   ✅ Naming convention: Aprobado por arquitectura
   ✅ Compliance check: SOX requirements met

📡 Sincronización empresarial...
   git fetch origin develop... ✅
   git fetch upstream develop... ✅ (si existe)
   git pull origin develop... ✅

📍 Rama base: develop (política corporativa)
✅ Rama creada: feature/microservicio-facturacion
🔄 Cambiado a feature/microservicio-facturacion
📤 Configurando tracking completo...
   git push -u origin feature/microservicio-facturacion... ✅
🔗 Upstream tracking configurado (obligatorio para auditoría)

🏢 CONFIGURACIÓN EMPRESARIAL APLICADA:
   ✓ Trazabilidad completa habilitada
   ✓ Integración con sistemas corporativos
   ✓ Compliance con políticas de seguridad
   ✓ Auditoría automática configurada
   ✓ Logging de actividad activado

📋 WORKFLOW CORPORATIVO ACTIVADO:
   1. Desarrolla siguiendo estándares corporativos
   2. Commits con formato obligatorio: [TIPO] TICKET-123: Descripción
   3. Push automático con validaciones de seguridad
   4. PR automático con plantilla corporativa
   5. Revisión obligatoria de 2+ arquitectos
   6. CI/CD completo (tests, security, performance, compliance)
   7. Approval de DevOps + Security requerido
   8. Merge automático tras compliance total
```

#### Integración Empresarial Completa

**Proceso de integración con todas las validaciones:**

```bash
# Desarrollo completado, iniciar integración empresarial
git-integration-manager.py integrate feature/microservicio-facturacion --mode enterprise
```

**Flujo empresarial completo:**

```bash
🏢 Git Integration Manager - Modo Empresarial
📍 Contexto: REMOTE (compliance estricto)
⚡ Capacidades: enterprise (APIs + Compliance + Auditoría)

🔍 VALIDACIÓN PRE-INTEGRACIÓN EMPRESARIAL:
   ✅ Rama: feature/microservicio-facturacion
   ✅ Commits: Formato corporativo validado
   ✅ Security scan: Sin vulnerabilidades
   ✅ Compliance: SOX requirements met
   ✅ Performance: Benchmarks pasados
   ✅ Architecture review: Aprobado
   ✅ Legal review: Compliance GDPR

📡 SINCRONIZACIÓN EMPRESARIAL:
   git fetch origin develop... ✅
   git fetch upstream develop... ✅
   Merge conflicts: Ninguno detectado

🚀 CREACIÓN DE PR EMPRESARIAL:
   🌐 Plataforma: GitHub Enterprise
   📝 Título: "[ENTERPRISE] Microservicio de Facturación - TICKET-1234"
   📋 Descripción: Plantilla corporativa aplicada
   👥 Reviewers automáticos:
      - @architecture-team (obligatorio)
      - @security-team (obligatorio)
      - @devops-team (obligatorio)
      - @compliance-officer (obligatorio)
   🏷️ Labels: enterprise, microservice, billing, compliance
   📊 Métricas: Performance impact, security score, compliance rating

✅ PR empresarial creado: https://github-enterprise.com/company/project/pull/156

🔒 CONFIGURACIÓN DE COMPLIANCE:
   📋 Branch protection: Máxima seguridad
   🛡️ Required checks: 12 validaciones obligatorias
   👥 Required reviewers: 4 mínimo (diferentes equipos)
   ⏰ Review timeout: 48 horas máximo
   📊 Compliance tracking: Activado
   🔍 Audit trail: Completo

🎯 PRÓXIMOS PASOS EMPRESARIALES:
   1. Architecture review (SLA: 24h)
   2. Security assessment (SLA: 12h)
   3. Performance validation (SLA: 6h)
   4. Compliance verification (SLA: 24h)
   5. DevOps approval (SLA: 12h)
   6. Automated merge tras todas las aprobaciones
   7. Deployment automático a staging
   8. Validation en staging environment
   9. Approval para producción
   10. Deployment controlado a producción

📧 NOTIFICACIONES ENVIADAS:
   - Stakeholders notificados
   - Compliance team alertado
   - Architecture board informado
   - Security team en CC
```

#### Monitoreo y Auditoría

**Seguimiento completo del proceso:**

```bash
# Monitorear estado del PR empresarial
git-integration-manager.py status --pr 156

📊 Estado del PR Empresarial #156
================================
🏢 Proyecto: company/project
📝 Título: [ENTERPRISE] Microservicio de Facturación
⏰ Creado: hace 2 horas
👤 Autor: developer@company.com

🔍 ESTADO DE VALIDACIONES:
   ✅ CI/CD Pipeline: Pasado (12/12 checks)
   ✅ Security Scan: Sin vulnerabilidades
   ✅ Performance Test: Dentro de SLA
   ⏳ Architecture Review: En progreso (18h restantes)
   ⏳ Compliance Check: Pendiente (22h restantes)
   ❌ DevOps Approval: Pendiente

👥 ESTADO DE REVIEWS:
   ✅ @senior-architect: Aprobado
   ⏳ @security-lead: Review en progreso
   ❌ @devops-manager: Pendiente
   ❌ @compliance-officer: Pendiente

📊 MÉTRICAS DE COMPLIANCE:
   🛡️ Security Score: 98/100
   ⚡ Performance Impact: +2ms (aceptable)
   📋 Compliance Rating: SOX compliant
   🔍 Code Quality: A+ (SonarQube)

⏰ TIEMPO ESTIMADO PARA MERGE: 18-24 horas
```

Este conjunto de workflows demuestra cómo el ecosistema Git Branch Tools se adapta y escala desde proyectos simples hasta entornos empresariales complejos, manteniendo siempre la eficiencia y asegurando el cumplimiento de políticas y estándares de calidad.

---
