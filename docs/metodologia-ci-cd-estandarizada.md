# Guía de Implementación: Metodología CI/CD Estandarizada para Proyectos

## 1. Introducción

Esta guía describe una metodología estandarizada para la Integración Continua (CI) y el Despliegue Continuo (CD). El objetivo es establecer un flujo de trabajo robusto, automatizado, consistente y adaptable que asegure la calidad del software desde el desarrollo de características hasta su despliegue en producción, independientemente de la plataforma de CI/CD específica utilizada (ej. GitHub Actions, GitLab CI/CD, Jenkins, Azure DevOps, etc.).

Esta metodología se basa en una capa inicial de validaciones locales mediante **Pre-Commit Hooks**, seguida por un conjunto de pipelines (o workflows) interconectados que controlan el ciclo de vida del código una vez enviado al repositorio. Se aplican validaciones progresivas, permitiendo la personalización específica para cada proyecto dentro de un marco común.

## 2. Principios Fundamentales

La metodología se sustenta en los siguientes principios, aplicables universalmente:

*   **Calidad Progresiva:** Las validaciones se introducen en etapas tempranas y se vuelven más exhaustivas a medida que el código avanza hacia producción.
*   **Separación de Intereses:** Cada pipeline (o workflow) tiene un propósito claro y definido, enfocándose en una etapa específica del ciclo de vida del desarrollo.
*   **Automatización Extensiva:** Minimizar la intervención manual para reducir errores, acelerar los ciclos de entrega y asegurar la repetibilidad.
*   **Feedback Rápido y Continuo:** Los desarrolladores reciben información sobre la calidad e impacto de su código lo antes posible.
*   **Confianza en los Releases:** Cada release se basa en código que ha superado múltiples etapas de validación automatizada.
*   **Adaptabilidad Controlada:** Se proporciona una estructura base estandarizada, pero cada proyecto tiene la flexibilidad de adaptar los detalles de implementación a su plataforma y necesidades.
*   **Resultados Claros y Accionables:** Los pipelines y sus componentes (jobs/stages) deben culminar en estados o variables lógicas claras que determinen el éxito y condicionen los pasos subsiguientes.

## 0. Pre-Commit Hooks: Validación Local Inmediata (Capa 0)

Antes de que el código sea enviado al repositorio y procesado por los pipelines de CI/CD, se establece una capa de validación local mediante hooks de pre-commit. Estos hooks se ejecutan automáticamente en la máquina del desarrollador antes de cada `git commit`.

*   **Propósito**:
    *   Proporcionar feedback instantáneo al desarrollador.
    *   Corregir automáticamente problemas de formato y estilo.
    *   Prevenir commits con errores obvios, secretos accidentales o violaciones de estándares básicos.
    *   Asegurar que el código que llega al repositorio ya tiene un nivel mínimo de calidad y consistencia.
*   **Tareas Típicas**:
    *   **Formateo de Código Automático**: (ej. Prettier, Black)
    *   **Linting Básico y Rápido**: (ej. ESLint, Flake8 con reglas rápidas)
    *   **Chequeo de Formato del Mensaje de Commit**: (ej. commitlint)
    *   **Detección de Archivos Grandes o Conflictos de Fusión No Resueltos**.
    *   **Chequeos básicos de seguridad**: (ej. detección de claves privadas).
*   **Puntos Clave**:
    *   **Extremadamente Rápidos**: No deben añadir latencia significativa al proceso de commit.
    *   **Locales**: Se ejecutan en el entorno del desarrollador.
    *   **Complementarios a CI**: Actúan como el primer filtro; no reemplazan las validaciones más exhaustivas en los pipelines de CI.
*   **Implementación**: Generalmente mediante un framework como `pre-commit` y un archivo de configuración (ej. `.pre-commit-config.yaml`) en el proyecto.

## 3. Visión General de los Pipelines/Workflows (Post-Commit)

Una vez que el código ha pasado los pre-commit hooks locales y es enviado al repositorio (mediante `git push`), la metodología se articula a través de **seis** pipelines (o workflows) principales, cada uno con un rol específico y activado por eventos definidos en el sistema de control de versiones (SCM):

1.  **CI de Rama de Trabajo (Push a Ramas de Trabajo)**: Proporciona feedback rápido al desarrollador con validaciones ligeras en cada push a su rama de característica o corrección.
2.  **Validación de Ramas de Trabajo (PR/MR a `develop`)**: Asegura la calidad del código de las ramas de características/correcciones *antes* de su integración a la rama `develop`.
3.  **Integración y QA en `develop` (Push/Merge a `develop`)**: Valida el estado integrado de la rama `develop`, construye artefactos para entornos de QA y, opcionalmente, realiza despliegues a dichos entornos.
4.  **Validación Pre-Release y Documentación (PR/MR a `main`)**: Realiza las pruebas finales y validaciones críticas (incluyendo la documentación) antes de que el código se fusione a la rama `main` y quede elegible para un release.
5.  **Generación de Release (Push de Tags `v*`)**: Automatiza la creación de un release oficial, incluyendo el versionado, la construcción de artefactos finales y su publicación (ej. en el SCM o un registro de artefactos).
6.  **Despliegue Continuo (Evento de Nuevo Release Publicado)**: Despliega los artefactos de un release publicado a los entornos de producción o staging finales.

## 4. Detalle de Cada Pipeline/Workflow (Post-Commit)

A continuación, se describe la estructura, propósito y componentes clave de cada pipeline. Estos se ejecutan sobre código que ya ha sido filtrado por los pre-commit hooks.

### 4.1. Pipeline 0: CI de Rama de Trabajo (Push a Ramas de Trabajo)

*   **Configuración Base Sugerida**: (ej. `ci-branch-push.yml`, sección en `.gitlab-ci.yml` con `rules` para ramas que no sean `main`/`develop`)
*   **Trigger Principal**: Push a cualquier rama de trabajo (ej. `feature/*`, `bugfix/*`, `hotfix/*`, excluyendo `develop` y `main`).
*   **Propósito**: Proporcionar feedback inmediato al desarrollador sobre la calidad básica de su código (ya pre-validado localmente) antes de la creación de una Solicitud de Fusión (PR/MR).
*   **Jobs/Stages Clave (Ligeros y Rápidos)**:
    *   `lint_code_branch`: Ejecuta linters (puede ser el mismo conjunto o un superconjunto de los pre-commit linters).
    *   `quick_unit_tests`: Ejecuta un subconjunto de tests unitarios rápidos.
    *   `basic_build_check` (si aplica): Verifica que el código compila o se construye sin errores básicos.
*   **Puntos Clave**:
    *   **Feedback Temprano Post-Push**: Es crucial que este pipeline sea muy rápido.
    *   **No Bloqueante (Generalmente)**: Su fallo alerta al desarrollador.
    *   Complementa los pre-commit hooks, verificando en un entorno de CI limpio.

### 4.2. Pipeline 1: Validación de Ramas de Trabajo (PR/MR a `develop`)

*   **Configuración Base Sugerida**: (ej. `ci-pr-to-develop.yml` para GitHub Actions, `.gitlab-ci.yml` sección `merge_request_pipelines` para GitLab)
*   **Trigger Principal**: Solicitud de Fusión (Pull Request, Merge Request) con rama base `develop`.
*   **Propósito**: Validar la calidad e integridad del código de una rama de característica/corrección antes de su fusión a `develop`.
*   **Jobs/Stages Clave**:
    *   `lint_feature_branch`: Ejecuta análisis estático de código (linters) sobre los cambios introducidos. (Puede ser más exhaustivo que en el Pipeline 0).
    *   `test_feature_branch`: Ejecuta tests unitarios y de integración básicos, enfocados en los cambios.
*   **Puntos Clave**:
    *   La protección de la rama `develop` (o configuración equivalente en el SCM/CI) debe configurarse para requerir que los jobs/stages de este pipeline concluyan exitosamente antes de permitir la fusión.
    *   El resultado de estos jobs (éxito/fallo) actúa como la variable lógica principal que condiciona la fusión.

### 4.3. Pipeline 2: Integración y QA en `develop` (Push/Merge a `develop`)

*   **Configuración Base Sugerida**: (ej. `ci-push-to-develop.yml`, `.gitlab-ci.yml` sección `branches: develop`)
*   **Trigger Principal**: Push o Fusión a la rama `develop`.
*   **Propósito**: Validar el estado integrado de `develop`, construir artefactos para QA, y opcionalmente, desplegar a un entorno de QA.
*   **Jobs/Stages Clave**:
    *   `lint_develop`: Ejecuta linters sobre el estado completo de `develop`.
    *   `test_develop_integration`: Ejecuta un conjunto más amplio de tests de integración en `develop`.
    *   `build_dev_qa_artifacts`: (Depende de `test_develop_integration`) Construye artefactos de desarrollo/QA y los publica en un almacenamiento de artefactos accesible.
    *   `deploy_to_qa` (Opcional): (Depende de `build_dev_qa_artifacts` o `test_develop_integration`) Despliega `develop` a un entorno de QA.
*   **Puntos Clave**: Este pipeline asegura que `develop` se mantenga consistentemente en un estado estable y probado.

### 4.4. Pipeline 3: Validación Pre-Release y Documentación (PR/MR a `main`)

*   **Configuración Base Sugerida**: (ej. `ci-pr-to-main.yml`, `.gitlab-ci.yml` sección `merge_request_pipelines` para `main`)
*   **Trigger Principal**: Solicitud de Fusión (Pull Request, Merge Request) con rama base `main`.
*   **Propósito**: Realizar las validaciones finales, incluyendo la conformidad de la documentación, antes de que el código se fusione a `main`.
*   **Jobs/Stages Clave**:
    *   `final_tests_on_pr`: Ejecuta un conjunto final y exhaustivo de tests sobre el código propuesto.
    *   `validate_documentation`:
        *   Lee la configuración del proyecto (ej. `require_component_docs` desde un archivo de metadatos como `.project/project_meta.toml`).
        *   Si es requerida, ejecuta los scripts de validación de documentación (ej. Niveles 0, 1, 2, uso de `docs_map.json`).
        *   Debe culminar en un estado claro (éxito/fallo).
*   **Puntos Clave**:
    *   La protección de la rama `main` debe configurarse para requerir que los jobs `final_tests_on_pr` y `validate_documentation` concluyan exitosamente.
    *   El resultado de `validate_documentation` es una variable lógica crítica.

### 4.5. Pipeline 4: Generación de Release (Push de Tags)

*   **Configuración Base Sugerida**: (ej. `ci-release.yml`, `.gitlab-ci.yml` sección `tags`)
*   **Trigger Principal**: Push de un tag Git que siga el patrón de versionado del proyecto.
*   **Propósito**: Automatizar la creación de un release oficial, incluyendo construcción de artefactos finales y su publicación.
*   **Jobs/Stages Clave**:
    *   `build_and_publish_release`:
        *   Realiza el checkout del código del tag.
        *   Construye los artefactos finales para el release.
        *   Determina si es un pre-release o estable.
        *   Publica el release (ej. en el SCM, como GitLab Releases, o un registro de artefactos como Nexus/Artifactory) y adjunta los artefactos.
*   **Puntos Clave**: Se asume que los tags solo se crean sobre commits de `main` que han pasado el Pipeline 3.

### 4.6. Pipeline 5: Despliegue Continuo (CD) (Evento de Nuevo Release Publicado)

*   **Configuración Base Sugerida**: (ej. `ci-deploy.yml`, `.gitlab-ci.yml` con trigger en la API de release o similar)
*   **Trigger Principal**: Evento que indica un nuevo release ha sido publicado formalmente (ej. API de la plataforma de CI/CD, webhook desde el registro de artefactos).
*   **Propósito**: Automatizar el despliegue de los artefactos de un release a los entornos de destino.
*   **Jobs/Stages Clave**:
    *   `deploy_to_environment`: (Puede haber múltiples para diferentes entornos)
        *   Descarga los artefactos del release.
        *   Ejecuta los scripts de despliegue al entorno.
*   **Puntos Clave**:
    *   Gestión segura de credenciales de despliegue.
    *   Uso de mecanismos de control de entornos si la plataforma de CI/CD los ofrece.

## 5. Mecanismos de Enlace y Condicionamiento Estratégico (Conceptos Universales)

La interconexión y el flujo lógico entre pipelines y sus jobs/stages se gestionan mediante mecanismos que, aunque con sintaxis variable, son conceptualmente comunes en la mayoría de las plataformas de CI/CD:

*   **Dependencias de Jobs/Stages**: Define el orden de ejecución. El "éxito" del job/stage anterior es la variable lógica implícita.
*   **Paso de Artefactos/Variables entre Jobs/Stages**: Permiten a un job/stage exponer explícitamente "variables lógicas" o datos. Otros pueden acceder a estos para tomar decisiones.
*   **Condicionales de Ejecución**: Permiten ejecutar jobs/stages o pasos solo si una condición es verdadera, basándose en resultados implícitos, artefactos/variables explícitas, o contexto del evento.
*   **Resultados de Jobs/Stages como Prerrequisitos**: El resultado final de un job/stage (éxito/fallo) actúa como un prerrequisito para acciones críticas (ej. fusión de ramas, despliegues).
*   **Disparadores de Pipelines (Triggers)**: Definen las condiciones iniciales para la activación de un pipeline, basados en eventos del SCM.

Cada job/stage debe definir claramente su criterio de "éxito" y exponer resultados significativos.

## 6. Implementación Genérica y Adaptabilidad del Proyecto

Se proporciona una "librería base" de plantillas conceptuales o archivos de configuración de ejemplo para cada pipeline/workflow.

*   **Proceso de "Instalación"**: Al configurar un proyecto, estas plantillas se adaptan y se implementan en la sintaxis de la plataforma de CI/CD elegida.
*   **Personalización Específica del Proyecto**:
    *   **Flexibilidad Total**: Una vez implementados, estos archivos de configuración **pertenecen y son gestionados por el proyecto**.
    *   Los equipos adaptarán los scripts y comandos, y podrán añadir, eliminar o modificar jobs/stages y pasos.
*   **Scripts Reutilizables**: Se pueden ofrecer scripts agnósticos a la plataforma para lógicas complejas.
*   **Configuración del Proyecto (Archivo de Metadatos)**: Flags como `require_component_docs` y, potencialmente, flags para habilitar/deshabilitar ciertos grupos de pre-commit hooks o pipelines, en un archivo como `.project/project_meta.toml` permiten controlar comportamientos.
*   **Herramienta de Asistencia (Opcional)**: Herramientas internas (`promanager.py`) podrían ayudar a generar la configuración inicial para pre-commit hooks y para la plataforma CI/CD seleccionada.

## 7. Pasos para la Adopción en un Proyecto

1.  **Definir Ramas Principales y de Trabajo**: Establecer `develop`, `main` y patrones para ramas de trabajo (ej. `feature/*`).
2.  **Inicializar Configuración del Proyecto**: Configurar el archivo de metadatos del proyecto.
3.  **Configurar Pre-Commit Hooks**:
    *   Añadir un archivo de configuración de pre-commit (ej. `.pre-commit-config.yaml`) con los hooks recomendados (formateo, linting básico, mensaje de commit).
    *   Instruir a los desarrolladores sobre cómo instalar y usar los hooks (`pre-commit install`).
4.  **"Traducir" e Instalar Pipelines Base**: Adaptar las plantillas conceptuales (incluyendo la del Pipeline 0) a la sintaxis de la plataforma de CI/CD del proyecto y configurarlas.
5.  **Personalizar Pipelines**: Adaptar cada configuración de pipeline a las necesidades específicas del proyecto.
6.  **Implementar/Adaptar Scripts de Soporte**: Desarrollar o adaptar scripts externos.
7.  **Configurar Protección de Ramas y Disparadores**: Implementar las reglas en el SCM y la plataforma de CI/CD para todos los pipelines relevantes.
8.  **Probar el Flujo Completo**: Ejecutar un ciclo completo (commit local con pre-commit hooks -> push a rama feature -> PR develop -> PR main -> tag -> release -> deploy) para validar.
9.  **Iterar y Refinar**: Tratar las configuraciones de pre-commit y CI/CD como código, iterando y mejorándolas continuamente.

## 8. Conclusión

Esta metodología CI/CD estandarizada, comenzando con validaciones locales mediante Pre-Commit Hooks y continuando con una serie de pipelines de CI/CD, proporciona un marco exhaustivo y adaptable para el desarrollo de software. Al definir claramente cada capa de validación y sus responsabilidades, los equipos pueden lograr un alto grado de automatización y confianza en sus entregas. La clave reside en la correcta implementación de los "puntos de control lógicos" en cada etapa, desde el commit local hasta el despliegue final.
