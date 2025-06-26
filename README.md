# Braintools - Suite Integral de Herramientas DevOps y Automatización

## 📖 Descripción

**BRAINTOOLS** es una suite completa de herramientas de línea de comandos, scripts de automatización y utilidades DevOps diseñada para revolucionar los flujos de trabajo de desarrollo moderno. Esta colección centraliza herramientas esenciales que abarcan desde la gestión avanzada de proyectos Git hasta la automatización de pipelines CI/CD, proporcionando una experiencia unificada para desarrolladores, administradores de sistemas, equipos DevOps y profesionales de la productividad.

El proyecto combina scripts Python inteligentes, utilidades de shell optimizadas, plantillas de configuración reutilizables y herramientas de documentación automática, todo integrado en un ecosistema cohesivo que acelera el desarrollo y reduce la fricción operacional.

## 🎯 Propósito

Este proyecto proporciona una solución integral para la gestión y automatización de procesos empresariales, diseñada para optimizar flujos de trabajo y mejorar la eficiencia operacional.

**Objetivos principales:**

- **Automatización inteligente**: Reducir tareas manuales repetitivas mediante procesos automatizados
- **Centralización de datos**: Unificar información dispersa en una plataforma cohesiva
- **Mejora de productividad**: Facilitar la colaboración y acelerar la toma de decisiones
- **Escalabilidad**: Adaptarse al crecimiento y evolución de las necesidades organizacionales

La plataforma está construida con tecnologías modernas y siguiendo las mejores prácticas de desarrollo, garantizando robustez, seguridad y mantenibilidad a largo plazo.

## 👥 Público Objetivo

- Desarrolladores de software
- Líderes técnicos
- Equipos de DevOps
- Contribuidores de proyectos open source

## 🌟 ¿Por qué elegir Braintools?

**Braintools** no es solo otra colección de scripts - es un ecosistema completo diseñado para transformar tu flujo de trabajo de desarrollo. Con herramientas inteligentes, automatización avanzada y una arquitectura extensible, Braintools te permite enfocarte en lo que realmente importa: crear software excepcional.

### ✨ Características

- Herramientas multiplataforma
- Automatización de tareas
- Configuración flexible

### 🎯 Beneficios Clave
- **Productividad 10x** - Automatiza tareas repetitivas
- **Calidad Consistente** - Standards y validaciones automáticas
- **Escalabilidad** - Crece con tu equipo y proyectos
- **Flexibilidad** - Configurable para cualquier stack tecnológico
- **Comunidad** - Soporte activo y mejoras continuas

### 💡 Solución

Combina análisis estático de código con IA para realizar diferentes tareas recurrentes y de automatización.

## 📁 Estructura del Proyecto


```
📁 Estructura del Proyecto

🌳 bin/
   ├── 🔄 ci/
       ├── ⚙️ config/
           └── ⚙️ metric-definitions.yml
       └── 🔧 scripts/
           └── 🐍 metrics_manager.py
   ├── ⚙️ config/
       ├── ⚙️ mcp_servers.yaml
       ├── 📦 requirements.def
   ├── 📚 docs/
       ├── ⚙️ config/
           ├── 📁 analysis/
               ├── ⚙️ default.yaml
               ├── ⚙️ project_description.yaml
               ├── ⚙️ contributing.yaml
               ├── ⚙️ git_branch_tools.yaml
               └── ⚙️ changelog.yaml
           ├── 📁 prompts/
           ├── 📁 toc/
           └── ⚙️ model.yaml
       ├── 📝 binsetup.md
       ├── 📝 changelog-generation.md
       ├── 📝 email_cleaner.md
       ├── 📝 git-branch-tools-guide.md
       ├── 📝 guia-git-workflow.md
       ├── 📝 guia-seleccion-modelos-cursor.md
       ├── 📝 hexroute.md
       ├── 📝 metodologia-ci-cd-estandarizada.md
       ├── 📝 packages.md
       ├── 📝 pymanager.md
       ├── 📝 requirements.md
       ├── 📝 sops.md
       └── 📝 videoset.md
   ├── 💡 ideas/
       └── 📝 persistencia_contexto_asistente.md
   ├── 🏗️ scaffold/
       ├── 🔄 ci/
           ├── 📁 bitbucket-pipelines/
               └── ⚙️ bitbucket-pipelines.yml
           └── 📁 ci-projects/
       ├── 🔧 commit-format/
       ├── 🔧 cursor/
           └── 📁 rules/
       ├── 📜 licenses/
           ├── 📝 academic.md
           ├── 📝 afl-3-0.md
           ├── 📝 agpl-3-0.md
           ├── 📝 apache-2-0.md
           ├── 📝 artistic-2-0.md
           ├── 📝 beta.md
           ├── 📝 boost-1-0.md
           ├── 📝 bsd-2-clause.md
           ├── 📝 bsd-3-clause.md
           ├── 📝 bsd-4-clause.md
           ├── 📝 business.md
           ├── 📝 cc0-1-0.md
           ├── 📝 cddl-1-0.md
           ├── 📝 commercial.md
           ├── 📝 confidential.md
           ├── 📝 cpl-1-0.md
           ├── 📝 custom.md
           ├── 📝 ecl-2-0.md
           ├── 📝 enterprise.md
           ├── 📝 epl-1-0.md
           ├── 📝 epl-2-0.md
           ├── 📝 eupl-1-1.md
           ├── 📝 eupl-1-2.md
           ├── 📝 evaluation.md
           ├── 📝 gpl-2-0.md
           ├── 📝 gpl-3-0.md
           ├── 📝 internal.md
           ├── 📝 isc.md
           ├── 📝 lgpl-2-1.md
           ├── 📝 lgpl-3-0.md
           ├── 📝 limited.md
           ├── 📝 mit.md
           ├── 📝 mpl-2-0.md
           ├── 📝 ncsa.md
           ├── 📝 non-profit.md
           ├── 📝 professional.md
           ├── 📝 proprietary.md
           ├── 📝 restricted.md
           ├── 📝 trial.md
           ├── 📝 unlicense.md
           ├── 📝 wtfpl.md
           └── 📝 zlib.md
       ├── 📁 mo/
       ├── 📁 pr/
       └── 📁 ws/
           └── 📁 brain/
   ├── 🔧 scripts/
       ├── 🔄 ci/
           ├── 🐍 calculate_next_version.py
           └── 🐍 update_file_versions.py
       ├── 📁 pre_commit_checks/
           └── 🐍 check_commit_msg.py
       └── 🐍 project_description_analyzer.py
   ├── 📋 tmp/
   ├── 🔧 .cursor/
       ├── ⚙️ rules/
```

### 📋 Descripción de Directorios

- **🔧 scripts/** Scripts de automatización y utilidades
- **⚙️ config/** Archivos de configuración y settings
- **📋 tmp/** Archivos temporales
- **📁 .githooks/** Hooks de Git y configuraciones de commit
- **📚 docs/** Documentación del proyecto, guías y manuales
- **💡 ideas/** Ideas y conceptos del proyecto
- **🔄 ci/** Configuración de CI/CD y pipelines
- **🏗️ scaffold/** Plantillas y estructuras base
- **📁 .project/** Configuración y metadatos del proyecto
- **🔧 .cursor/** Configuración del editor Cursor IDE

### 📄 Archivos Principales

- **🐍 *.py** Scripts y módulos Python
- **🟨 *.js** Archivos JavaScript
- **🔷 *.ts** Archivos TypeScript
- **📋 *.json** Configuraciones y metadatos
- **⚙️ *.yml/*.yaml** Configuraciones de servicios
- **📝 *.md** Documentación en Markdown
- **🐚 *.sh** Scripts de shell y bash
- **📄 *.txt** Archivos de texto y documentación
- **📋 *.toml** Configuraciones en formato TOML
- **⚙️ *.ini/*.cfg** Archivos de configuración
- **🌐 *.html** Archivos HTML
- **🎨 *.css** Hojas de estilo CSS
- **🟢 *.vue** Componentes Vue.js
- **🟠 *.svelte** Componentes Svelte
- **🦀 *.rs** Código Rust
- **🔵 *.go** Código Go
- **☕ *.java** Código Java
- **🟣 *.kt** Código Kotlin
- **🍎 *.swift** Código Swift
- **🔵 *.c/*.cpp** Código C/C++
- **🟣 *.php** Código PHP
- **💎 *.rb** Código Ruby
- **🗄️ *.sql** Consultas y esquemas SQL
- **🐳 Dockerfile** Configuración de contenedores Docker
- **📖 README** Documentación principal del proyecto
- **📜 LICENSE** Licencia del proyecto
- **📋 CHANGELOG** Registro de cambios del proyecto
- **🤝 CONTRIBUTING** Guía de contribución al proyecto

## 📊 Estado del Proyecto

Activo y en desarrollo continuo con nuevas funcionalidades.

## 📚 Documentación

### 📋 Guías Locales Disponibles

| Documento | Descripción | Ubicación |
|-----------|-------------|-----------|
| **Instalación** | Pasos detallados para instalar Braintools | [`docs/installation.md`](docs/installation.md) |
| **Git Branch Tools** | Como gestionar el desarrollo de tus proyectos | [`docs/git-branch-tools-guide.md`](docs/git-branch-tools-guide.md) |
| **Documents Generator** | Como generar documentación de tu proyecto | [`docs/docgen.md`](docs/docgen.md/) |
| **Vídeo Set for Linux** | Como configurar la resolución de vídeo | [`docs/videoset.md`](docs/videoset.md/) |
| **HEXROUTE** | Convierte rutas legibles por humanos a información de rutas estáticas dhcpd | [`docs/hexroute.md`](docs/hexroute.md/) |
| **Más utilitarios** | Guías de uso de otros utilitarios de Braintools | [`docs/more_braintools.md`](docs/more_braintools.md/) |
| **Guía de Contribución** | Cómo contribuir al proyecto | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| **Changelog** | Historial de cambios y versiones | [`CHANGELOG.md`](CHANGELOG.md) |

## 🔗 Enlaces Relacionados

- [Documentación oficial](https://github.com/maurorosero/braintools/docs)
- [Issues](https://github.com/maurorosero/braintools/issues)

## 📄 Licencia y Legal

Este proyecto está licenciado bajo **GNU General Public License v3.0** - consulta [LICENSE.md](LICENSE.md) para detalles completos.

### Derechos y Responsabilidades
- ✅ Uso comercial permitido
- ✅ Modificación y distribución permitidas
- ✅ Uso privado permitido
- ❗ Debe incluir licencia y copyright
- ❗ Cambios deben ser documentados

## 🤝 Contribución

¡Te invitamos a contribuir a **Braintools**!

Para conocer todas las formas de colaborar, desde reportar bugs hasta desarrollar nuevas funcionalidades, consulta nuestra guía completa en **[CONTRIBUTING.md](CONTRIBUTING.md)**.

Cada contribución, por pequeña que sea, ayuda a hacer de Braintools una herramienta más potente y útil para toda la comunidad DevOps.

## 👥 Equipo y Reconocimientos

### Autor Principal
- **Mauro Rosero**
- Arquitecto y Desarrollador Principal
- [@mrosero](https://github.com/mrosero)

### Contribuidores
- Ver [CONTRIBUTORS.md](CONTRIBUTORS.md) para lista completa

### Agradecimientos Especiales
- Comunidad de desarrolladores DevOps
- Mantenedores de proyectos de código abierto
- Beta testers y usuarios early adopters
- Contribuidores de documentación y traducciones

---

**¡Únete a la revolución DevOps con Braintools!** 🚀

---
