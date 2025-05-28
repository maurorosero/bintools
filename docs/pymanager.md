# pymanager.sh - Guía Detallada para la Gestión de Entornos Virtuales Python

<!-- PARSEABLE_METADATA_START
purpose: Guía completa para entender y utilizar pymanager.sh para la gestión de entornos virtuales Python, desde conceptos básicos hasta uso avanzado, con una estructura jerárquica detallada.
technology: Bash Script, Python, venv
status: Development
PARSEABLE_METADATA_END -->

<!-- CURRENT_VERSION_PLACEHOLDER -->

## Tabla de Contenidos

1.  [Parte 1: Fundamentos de los Entornos Virtuales en Python](#parte-1-fundamentos-de-los-entornos-virtuales-en-python)
    *   [Sección 1.1: ¿Qué es un Entorno Virtual?](#sección-11-qué-es-un-entorno-virtual)
    *   [Sección 1.2: La Importancia Crítica de los Entornos Virtuales](#sección-12-la-importancia-crítica-de-los-entornos-virtuales)
        *   [Subsección 1.2.1: Aislamiento de Proyectos y Dependencias](#subsección-121-aislamiento-de-proyectos-y-dependencias)
        *   [Subsección 1.2.2: Resolución Efectiva de Conflictos de Versiones](#subsección-122-resolución-efectiva-de-conflictos-de-versiones)
        *   [Subsección 1.2.3: Garantía de Reproducibilidad de Proyectos](#subsección-123-garantía-de-reproducibilidad-de-proyectos)
        *   [Subsección 1.2.4: Mantenimiento de un Intérprete Global de Python Limpio](#subsección-124-mantenimiento-de-un-intérprete-global-de-python-limpio)
    *   [Sección 1.3: El Problema Resuelto: Un Escenario Práctico](#sección-13-el-problema-resuelto-un-escenario-práctico)
2.  [Parte 2: Introducción al Gestor de Entornos `pymanager.sh`](#parte-2-introducción-al-gestor-de-entornos-pymanagersh)
    *   [Sección 2.1: ¿Qué es `pymanager.sh`?](#sección-21-qué-es-pymanagersh)
    *   [Sección 2.2: Ventajas Clave de Utilizar `pymanager.sh`](#sección-22-ventajas-clave-de-utilizar-pymanagersh)
        *   [Subsección 2.2.1: Sintaxis Simplificada y Unificada](#subsección-221-sintaxis-simplificada-y-unificada)
        *   [Subsección 2.2.2: Gestión Diferenciada de Entornos](#subsección-222-gestión-diferenciada-de-entornos)
        *   [Subsección 2.2.3: Integración Opcional con `gum`](#subsección-223-integración-opcional-con-gum)
        *   [Subsección 2.2.4: Logging Detallado de Operaciones](#subsección-224-logging-detallado-de-operaciones)
        *   [Subsección 2.2.5: Configuración de Alias Útiles](#subsección-225-configuración-de-alias-útiles)
        *   [Subsección 2.2.6: Selección Inteligente de la Versión de Python](#subsección-226-selección-inteligente-de-la-versión-de-python)
3.  [Parte 3: Primeros Pasos con `pymanager.sh`](#parte-3-primeros-pasos-con-pymanagersh)
    *   [Sección 3.1: Requisitos Previos para la Instalación](#sección-31-requisitos-previos-para-la-instalación)
    *   [Sección 3.2: Instalación y Acceso al Script `pymanager.sh`](#sección-32-instalación-y-acceso-al-script-pymanagersh)
        *   [Subsección 3.2.1: Obtención y Permisos del Script](#subsección-321-obtención-y-permisos-del-script)
        *   [Subsección 3.2.2: Configuración del Acceso al Script](#subsección-322-configuración-del-acceso-al-script)
    *   [Sección 3.3: Estructura de Directorios Utilizada por `pymanager.sh`](#sección-33-estructura-de-directorios-utilizada-por-pymanagersh)
4.  [Parte 4: Guía Detallada de Comandos de `pymanager.sh`](#parte-4-guía-detallada-de-comandos-de-pymanagersh)
    *   [Sección 4.0: Consideraciones Generales sobre los Comandos](#sección-40-consideraciones-generales-sobre-los-comandos)
    *   [Sección 4.1: Creación de Entornos Virtuales Locales (Comando: `--create`)](#sección-41-creación-de-entornos-virtuales-locales-comando---create)
        *   [Subsección 4.1.1: Propósito y Funcionalidad Principal](#subsección-411-propósito-y-funcionalidad-principal)
        *   [Subsección 4.1.2: Sintaxis Detallada](#subsección-412-sintaxis-detallada)
        *   [Subsección 4.1.3: Comportamiento Clave del Comando `--create`](#subsección-413-comportamiento-clave-del-comando---create)
        *   [Subsección 4.1.4: Escenarios de Uso y Ejemplos del Comando `--create`](#subsección-414-escenarios-de-uso-y-ejemplos-del-comando---create)
        *   [Subsección 4.1.5: Consideraciones sobre la Selección de Versión de Python](#subsección-415-consideraciones-sobre-la-selección-de-versión-de-python)
    *   [Sección 4.2: Activación de Entornos Virtuales (Comandos: `--set local` y alias `pyglobalset`)](#sección-42-activación-de-entornos-virtuales-comandos---set-local-y-alias-pyglobalset)
        *   [Subsección 4.2.1: Propósito y Mecanismo de Activación](#subsección-421-propósito-y-mecanismo-de-activación)
        *   [Subsección 4.2.2: Activación de Entornos Locales (`--set local`)](#subsección-422-activación-de-entornos-locales---set-local)
        *   [Subsección 4.2.3: Activación del Entorno Global por Defecto (Alias `pyglobalset`)](#subsección-423-activación-del-entorno-global-por-defecto-alias-pyglobalset)
        *   [Subsección 4.2.4: Identificación de un Entorno Activo](#subsección-424-identificación-de-un-entorno-activo)
    *   [Sección 4.3: Listado de Paquetes e Información de Entorno (Comando: `--list`)](#sección-43-listado-de-paquetes-e-información-de-entorno-comando---list)
        *   [Subsección 4.3.1: Propósito y Funcionalidad](#subsección-431-propósito-y-funcionalidad)
        *   [Subsección 4.3.2: Sintaxis del Comando `--list`](#subsección-432-sintaxis-del-comando---list)
        *   [Subsección 4.3.3: Comportamiento Detallado](#subsección-433-comportamiento-detallado)
    *   [Sección 4.4: Instalación de Paquetes (Comandos: `--package-local`, `--install`, `--package-global`)](#sección-44-instalación-de-paquetes-comandos---package-local---install---package-global)
        *   [Subsección 4.4.1: Instalación en Entornos Locales EXISTENTES (Comando: `--package-local`)](#subsección-441-instalación-en-entornos-locales-existentes-comando---package-local)
        *   [Subsección 4.4.2: Instalación en Entorno Global con Requisitos POR DEFECTO DEL SCRIPT (Comando: `--install`)](#subsección-442-instalación-en-entorno-global-con-requisitos-por-defecto-del-script-comando---install)
        *   [Subsección 4.4.3: Instalación en Entorno Global con Paquetes o Requisitos ESPECÍFICOS (Comando: `--package-global`)](#subsección-443-instalación-en-entorno-global-con-paquetes-o-requisitos-específicos-comando---package-global)
    *   [Sección 4.5: Eliminación de Entornos Virtuales (Comandos: `--remove-local`, `--remove-global`)](#sección-45-eliminación-de-entornos-virtuales-comandos---remove-local---remove-global)
        *   [Subsección 4.5.1: Eliminación de Entornos Locales (Comando: `--remove-local`)](#subsección-451-eliminación-de-entornos-locales-comando---remove-local)
        *   [Subsección 4.5.2: Eliminación del Entorno Global por Defecto (Comando: `--remove-global`)](#subsección-452-eliminación-del-entorno-global-por-defecto-comando---remove-global)
    *   [Sección 4.6: Gestión del Alias Global para Activación Rápida (Comandos: `--set global`, `--unset global`)](#sección-46-gestión-del-alias-global-para-activación-rápida-comandos---set-global---unset-global)
        *   [Subsección 4.6.1: Configuración del Alias (Comando: `--set global`)](#subsección-461-configuración-del-alias-comando---set-global)
        *   [Subsección 4.6.2: Eliminación del Alias (Comando: `--unset global`)](#subsección-462-eliminación-del-alias-comando---unset-global)
    *   [Sección 4.8: Ayuda y Versión del Script (Comandos: `--help`, `--version`)](#sección-48-ayuda-y-versión-del-script-comandos---help---version)
        *   [Subsección 4.8.1: Obtención de Ayuda Detallada (Comando: `--help`)](#subsección-481-obtención-de-ayuda-detallada-comando---help)
        *   [Subsección 4.8.2: Visualización de la Versión del Script (Comando: `--version`)](#subsección-482-visualización-de-la-versión-del-script-comando---version)
5.  [Parte 5: Flujos de Trabajo y Escenarios Prácticos con `pymanager.sh`](#parte-5-flujos-de-trabajo-y-escenarios-prácticos-con-pymanagersh)
    *   [Escenario 5.1: Configuración de un Nuevo Proyecto de Desarrollo Python](#escenario-51-configuración-de-un-nuevo-proyecto-de-desarrollo-python)
        *   [Subsección 5.1.1: Creación del Directorio y Navegación](#subsección-511-creación-del-directorio-y-navegación)
        *   [Subsección 5.1.2: Creación del Entorno Virtual Local](#subsección-512-creación-del-entorno-virtual-local)
        *   [Subsección 5.1.3: Activación del Entorno Local](#subsección-513-activación-del-entorno-local)
        *   [Subsección 5.1.4: Instalación de Dependencias del Proyecto](#subsección-514-instalación-de-dependencias-del-proyecto)
        *   [Subsección 5.1.5: Generación del Archivo `requirements.txt`](#subsección-515-generación-del-archivo-requirementstxt)
        *   [Subsección 5.1.6: Desarrollo y Desactivación](#subsección-516-desarrollo-y-desactivación)
    *   [Escenario 5.2: Gestión de Herramientas Python de Uso Frecuente (Entorno Global)](#escenario-52-gestión-de-herramientas-python-de-uso-frecuente-entorno-global)
        *   [Subsección 5.2.1: Instalación de Herramientas en el Entorno Global](#subsección-521-instalación-de-herramientas-en-el-entorno-global)
        *   [Subsección 5.2.2: Configuración del Alias `pyglobalset`](#subsección-522-configuración-del-alias-pyglobalset)
        *   [Subsección 5.2.3: Uso de las Herramientas Globales](#subsección-523-uso-de-las-herramientas-globales)
    *   [Escenario 5.3: Experimentación Rápida con una Librería (Usando un Entorno Local Temporal)](#escenario-53-experimentación-rápida-con-una-librería-usando-un-entorno-local-temporal)
        *   [Subsección 5.3.1: Creación del Entorno Temporal
Primero, crea un directorio temporal para tu experimento y navega hacia él:
```bash
mkdir ~/experimento_nueva_lib && cd ~/experimento_nueva_lib
```
Dentro de este directorio, crea un entorno local específico para esta prueba:
```bash
pymanager.sh --create prueba_lib
# Esto creará el entorno en ./venv/prueba_lib/
```

Este bloque asegura que el comando `mkdir ~/experimento_nueva_lib && cd ~/experimento_nueva_lib` esté correctamente formateado como un bloque de código Bash.

Lamento los inconvenientes que está causando la herramienta de edición. Una vez que hayas realizado este cambio manualmente, el formato debería ser correcto.
        *   [Subsección 5.3.2: Activación del Entorno Temporal](#subsección-532-activación-del-entorno-temporal)
        *   [Subsección 5.3.3: Instalación y Prueba de la Librería](#subsección-533-instalación-y-prueba-de-la-librería)
        *   [Subsección 5.3.4: Desactivación](#subsección-534-desactivación)
        *   [Subsección 5.3.5: Limpieza del Entorno Temporal](#subsección-535-limpieza-del-entorno-temporal)
6.  [Parte 6: Características Adicionales y Consejos Útiles](#parte-6-características-adicionales-y-consejos-útiles)
    *   [Sección 6.1: Integración Opcional con `gum`](#sección-61-integración-opcional-con-gum)
    *   [Sección 6.2: Utilidad del Archivo de Logging](#sección-62-utilidad-del-archivo-de-logging)
7.  [Parte 7: Contribución al Proyecto](#parte-7-contribución-al-proyecto)
8.  [Parte 8: Licencia de Uso](#parte-8-licencia-de-uso)

## Parte 1: Fundamentos de los Entornos Virtuales en Python

### Sección 1.1: ¿Qué es un Entorno Virtual?
Imagina que estás construyendo diferentes sets de LEGO. Cada set tiene sus propias piezas específicas y un manual de instrucciones. Un entorno virtual en Python es conceptualmente similar: actúa como una caja separada y aislada para cada uno de tus proyectos de Python. Dentro de esta "caja" (el entorno virtual), puedes instalar versiones específicas de "piezas" (que en Python son librerías o paquetes) que tu proyecto necesita. Crucialmente, estas instalaciones no afectan a otros proyectos ni a la configuración global de Python en tu sistema.

### Sección 1.2: La Importancia Crítica de los Entornos Virtuales
El uso de entornos virtuales no es meramente una buena práctica; es un pilar fundamental para el desarrollo en Python de forma organizada, reproducible y libre de problemas. A continuación, se detallan las razones principales de su imprescindibilidad.

#### Subsección 1.2.1: Aislamiento de Proyectos y Dependencias
Cada proyecto de Python puede tener su propio conjunto completamente aislado de dependencias. Por ejemplo, el "Proyecto A" podría requerir la versión 1.0 de una librería específica, mientras que el "Proyecto B" necesita la versión 2.0 de esa misma librería. Sin entornos virtuales, gestionar estas situaciones conflictivas sería extremadamente complicado, llevando a menudo a errores difíciles de diagnosticar.

#### Subsección 1.2.2: Resolución Efectiva de Conflictos de Versiones
Los entornos virtuales son la principal herramienta para evitar el temido "infierno de las dependencias". Este problema surge cuando la instalación de una librería para un proyecto modifica (actualiza o degrada) una dependencia compartida, rompiendo inadvertidamente la funcionalidad de otro proyecto que dependía de una versión diferente.

#### Subsección 1.2.3: Garantía de Reproducibilidad de Proyectos
Con los entornos virtuales, puedes definir con precisión qué versiones de qué paquetes necesita tu proyecto. Esta definición se plasma comúnmente en un archivo denominado `requirements.txt`. Dicho archivo permite que cualquier otra persona (o tú mismo, trabajando en una máquina diferente o en un momento futuro) pueda recrear exactamente el mismo entorno de ejecución, asegurando que el proyecto se comporte de manera consistente.

#### Subsección 1.2.4: Mantenimiento de un Intérprete Global de Python Limpio
Al utilizar entornos virtuales, evitas la acumulación innecesaria de paquetes en tu instalación principal (global) de Python. Muchos de estos paquetes podrían ser específicos de un solo proyecto. Mantener limpio el intérprete global no solo es una cuestión de organización, sino que también reduce la probabilidad de conflictos inesperados a nivel del sistema.

### Sección 1.3: El Problema Resuelto: Un Escenario Práctico
Para ilustrar concretamente la utilidad de los entornos virtuales, consideremos un escenario común. Supongamos que estás trabajando en dos proyectos diferentes:

1.  **`viejo_proyecto_web`**: Un proyecto antiguo que depende de `Flask==1.1.2` y `Requests==2.20.0`.
2.  **`nuevo_proyecto_api`**: Un desarrollo más reciente que requiere las últimas funcionalidades de `Flask==2.0.1` y `Requests==2.25.1`.

Si intentaras instalar estos paquetes directamente en tu Python global (es decir, sin usar entornos virtuales), te enfrentarías a serios problemas. Si instalas primero las dependencias de `viejo_proyecto_web` y luego las de `nuevo_proyecto_api`, las versiones de Flask y Requests se actualizarán para satisfacer a `nuevo_proyecto_api`. Como resultado, `viejo_proyecto_web` podría dejar de funcionar correctamente, ya que sus dependencias habrían cambiado. Intentar mantener una única versión global de cada paquete que satisfaga a ambos proyectos sería, en este caso, imposible.

La solución elegante y robusta es el uso de entornos virtuales:

*   Se crea un entorno virtual dedicado para `viejo_proyecto_web`. Dentro de este entorno, se instalan `Flask==1.1.2` y `Requests==2.20.0`.

*   Se crea un segundo entorno virtual, completamente independiente, para `nuevo_proyecto_api`. Dentro de él, se instalan `Flask==2.0.1` y `Requests==2.25.1`.

De esta manera, ambos proyectos pueden coexistir armoniosamente en la misma máquina, cada uno con sus propias dependencias perfectamente aisladas y sin interferencias.

## Parte 2: Introducción al Gestor de Entornos `pymanager.sh`

### Sección 2.1: ¿Qué es `pymanager.sh`?
`pymanager.sh` es un script de utilidad, escrito en Bash, cuyo propósito es simplificar y agilizar significativamente la gestión de entornos virtuales de Python. Funciona como una capa de abstracción amigable y potente sobre las herramientas estándar que Python provee para la gestión de entornos (principalmente el módulo `venv`). Al ofrecer comandos más intuitivos y funcionalidades adicionales, `pymanager.sh` busca hacer la vida del desarrollador Python más fácil y productiva. Puedes considerarlo tu asistente personal para manejar tus diversos entornos virtuales de manera eficiente.

### Sección 2.2: Ventajas Clave de Utilizar `pymanager.sh`
Si bien es totalmente posible gestionar entornos virtuales utilizando directamente los comandos nativos de Python, como `python -m venv nombre_entorno` seguido de `source nombre_entorno/bin/activate`, el script `pymanager.sh` introduce una serie de ventajas que justifican su uso:

#### Subsección 2.2.1: Sintaxis Simplificada y Unificada
`pymanager.sh` proporciona comandos más cortos, consistentes y fáciles de recordar para las operaciones más comunes, como la creación, activación, listado y eliminación de entornos.

#### Subsección 2.2.2: Gestión Diferenciada de Entornos
El script distingue claramente entre entornos locales (específicos del proyecto) y un entorno global por defecto.

*   **Entornos Locales (`./.venv/`):** El comando `pymanager.sh --create [<nombre_env>] [--python <ver>]` está diseñado para generar entornos virtuales directamente en un subdirectorio `./.venv/` dentro del directorio actual del proyecto. Esto es ideal para aislar las dependencias de proyectos individuales.

*   **Entorno Global por Defecto (`~/.venv/default`):** El script facilita la creación y gestión de un entorno "global por defecto", ubicado en `~/.venv/default`. Este entorno es perfecto para instalar herramientas de interfaz de línea de comandos (CLI) escritas en Python que se utilizan frecuentemente en diversos proyectos (ej. linters, formateadores). Comandos como `pymanager.sh --install` y `pymanager.sh --package-global` interactúan con este entorno global.

#### Subsección 2.2.3: Integración Opcional con `gum`
Si tienes instalada la herramienta `gum` (que permite crear menús interactivos y otros elementos de UI en la terminal), `pymanager.sh` puede utilizarla para ofrecer una experiencia de usuario más rica y visual en ciertos comandos, como el listado o la eliminación de entornos.

#### Subsección 2.2.4: Logging Detallado de Operaciones
Todas las acciones importantes realizadas por `pymanager.sh` se registran en un archivo de log (`~/.logs/pymanager.log`). Este registro puede ser invaluable para diagnosticar problemas o para entender exactamente qué operaciones realizó el script.

#### Subsección 2.2.5: Configuración de Alias Útiles
`pymanager.sh` puede ayudarte a configurar un alias en el archivo de inicio de tu shell (ej. `.bashrc`), como `pyglobalset` (mediante `pymanager.sh --set global`), para activar rápidamente el entorno global por defecto.

#### Subsección 2.2.6: Selección Inteligente de la Versión de Python
Al crear un nuevo entorno, el script intenta utilizar la versión más adecuada y moderna de Python disponible en tu sistema, aunque también permite especificar una versión concreta si es necesario.

## Parte 3: Primeros Pasos con `pymanager.sh`

### Sección 3.1: Requisitos Previos para la Instalación
Antes de utilizar `pymanager.sh`, asegúrate de que tu sistema cumple con los siguientes requisitos:

*   **Shell Bash:** El script está escrito en Bash, por lo que necesitas un entorno de shell compatible con Bash. Esto es estándar en la mayoría de las distribuciones de Linux y en macOS.

*   **Python 3 y el módulo `venv`:** `pymanager.sh` depende fundamentalmente de que Python 3 esté instalado en tu sistema. Además, el módulo `venv`, que se utiliza para crear los entornos virtuales, debe estar disponible (generalmente viene incluido con las instalaciones estándar de Python 3). El script realiza una verificación de estos prerrequisitos al inicio de su ejecución.

*   **`gum` (Opcional, para experiencia mejorada):** Como se mencionó, la herramienta `gum` puede mejorar la interfaz de usuario de `pymanager.sh` con menús interactivos. Si `gum` no está instalado, `pymanager.sh` seguirá funcionando correctamente, pero utilizará una interfaz de línea de comandos básica. Puedes instalar `gum` siguiendo las instrucciones de su repositorio oficial si deseas esta funcionalidad.

### Sección 3.2: Instalación y Acceso al Script `pymanager.sh`
Para instalar y empezar a usar `pymanager.sh`, sigue estos pasos:

#### Subsección 3.2.1: Obtención y Permisos del Script
Primero, necesitas descargar o copiar el archivo `pymanager.sh` a tu sistema. Una vez que tengas el archivo, debes otorgarle permisos de ejecución. Abre tu terminal y ejecuta:
```bash
chmod +x pymanager.sh
```

#### Subsección 3.2.2: Configuración del Acceso al Script
Tienes dos opciones principales para hacer que el script sea fácilmente accesible desde cualquier ubicación en tu terminal:

*   **Opción A (Recomendada): Colócalo en un directorio de tu `PATH`:** La forma más conveniente es mover el archivo `pymanager.sh` a un directorio que esté incluido en la variable de entorno `PATH` de tu sistema. Directorios comunes para esto son `~/.local/bin` (para scripts de usuario) o `/usr/local/bin` (para scripts a nivel de sistema). Si el directorio `~/.local/bin` no existe, puedes crearlo.
    ```bash
    mkdir -p ~/.local/bin
    mv pymanager.sh ~/.local/bin/
    ```
    Asegúrate de que el directorio elegido (ej. `~/.local/bin`) esté efectivamente en tu `PATH`. Puedes verificarlo con `echo $PATH`. Si no está, deberás añadirlo a la configuración de tu shell (ej. `~/.bashrc` o `~/.zshrc`) añadiendo una línea como: `export PATH="$HOME/.local/bin:$PATH"`. No olvides recargar la configuración de tu shell después (ej. `source ~/.bashrc`).

*   **Opción B: Llama al script usando su ruta completa:** Si prefieres no añadirlo al `PATH`, siempre puedes ejecutar el script especificando su ruta relativa (ej. `./pymanager.sh` si estás en el mismo directorio que el script) o su ruta absoluta (ej. `/ruta/completa/a/pymanager.sh`).

### Sección 3.3: Estructura de Directorios Utilizada por `pymanager.sh`
`pymanager.sh` utiliza y puede crear algunos directorios y archivos clave en tu sistema para su funcionamiento:

*   **`~/.venv/default/`**: Este es el directorio donde `pymanager.sh` almacena el entorno virtual que considera "global por defecto". Los comandos `--install` y `--package-global` operan principalmente sobre este entorno.

*   **`~/.logs/`**: En este directorio se guardan los archivos de registro generados por el script.
    *   **`~/.logs/pymanager.log`**: Este es el archivo de log principal donde `pymanager.sh` registra los detalles de sus operaciones. Es el primer lugar donde debes mirar si encuentras algún problema.

*   **`./.venv/`**: Este directorio se crea dentro del directorio de tu proyecto actual cuando utilizas el comando `pymanager.sh --create [<nombre_env>]`. Funciona como el directorio base para todos los entornos locales de ese proyecto. Cada entorno local específico residirá en un subdirectorio dentro de `./.venv/` (ej. `./.venv/default` o `./.venv/mi_entorno_especifico`).

## Parte 4: Guía Detallada de Comandos de `pymanager.sh`

### Sección 4.0: Consideraciones Generales sobre los Comandos
La mayoría de los comandos de `pymanager.sh` siguen una sintaxis básica de `pymanager.sh <comando> [argumentos...]`. Para obtener la lista completa y oficial de todos los comandos, sus opciones y una breve descripción de cada uno, el recurso fundamental es la ayuda integrada del propio script. Puedes acceder a ella ejecutando:

```bash
pymanager.sh --help
```

Para verificar la versión del script `pymanager.sh` que estás utilizando, ejecuta:
```bash
pymanager.sh --version
```

### Sección 4.1: Creación de Entornos Virtuales Locales (Comando: `--create`)

#### Subsección 4.1.1: Propósito y Funcionalidad Principal
El comando `--create` se utiliza para generar nuevos entornos virtuales de Python. Es importante destacar que, según la información de la ayuda del script, este comando está diseñado para crear entornos **locales**, los cuales se alojarán dentro de un directorio `.venv/` en el directorio de trabajo actual.

#### Subsección 4.1.2: Sintaxis Detallada
La sintaxis para este comando, extraída de la ayuda del script, es la siguiente:

```bash
pymanager.sh --create [<nombre_env>] [--python <ver>]
```

##### Argumento Opcional `<nombre_env>`
Este argumento permite especificar un nombre para el subdirectorio del entorno que se creará dentro de `./.venv/`. Si omites este argumento, el script utilizará `default` como nombre para el subdirectorio del entorno (resultando en `./.venv/default/`). Si proporcionas un nombre, por ejemplo `mi_entorno`, el entorno se creará en `./.venv/mi_entorno/`.

##### Opción Opcional `--python <ver>`
Esta opción te permite indicar una versión específica de Python que deseas utilizar para el nuevo entorno (por ejemplo, `--python 3.10`). El script intentará localizar un ejecutable de Python correspondiente a esa versión en tu sistema (ej. `python3.10`).

#### Subsección 4.1.3: Comportamiento Clave del Comando `--create`

*   **Creación Local Exclusiva:** Este comando siempre crea los entornos virtuales en un subdirectorio dentro de `./.venv/` en el directorio actual.

*   **Sin Instalación de Paquetes Inicial:** Por defecto, el comando `--create` no instala ningún paquete en el entorno recién creado. El entorno se crea limpio.

*   **Manejo de Entornos Existentes:** Si intentas crear un entorno local que ya existe (por ejemplo, si `./.venv/default` ya está presente y ejecutas `pymanager.sh --create`), el script te preguntará si deseas reinstalarlo, ofreciendo la opción de cancelar la operación.

#### Subsección 4.1.4: Escenarios de Uso y Ejemplos del Comando `--create`

##### Creación de un Entorno Local con Nombre `default`
Esta es la forma más común y sencilla de crear un entorno local para un proyecto, utilizando el nombre predeterminado `default`.

```bash
# Primero, navega al directorio raíz de tu proyecto
cd /ruta/a/mi_proyecto

# Ejecuta el comando para crear el entorno en ./.venv/default
pymanager.sh --create
```

Como resultado, se creará un nuevo entorno virtual en la ruta `/ruta/a/mi_proyecto/.venv/default/`. El script seleccionará automáticamente la versión de Python más adecuada que encuentre disponible en tu sistema para este nuevo entorno.

##### Creación de un Entorno Local con un Nombre Específico
Si necesitas una mayor organización dentro de tus proyectos o gestionas múltiples configuraciones, puedes asignar un nombre específico a tu entorno local.

```bash
# Asegúrate de estar en el directorio de tu proyecto
cd /ruta/a/mi_proyecto

# Crea un entorno local con un nombre personalizado, ej. 'mi_entorno_dev'
pymanager.sh --create mi_entorno_dev
```

Esto resultará en la creación de un entorno en `/ruta/a/mi_proyecto/.venv/mi_entorno_dev/`.

##### Creación de un Entorno Local Especificando la Versión de Python
Si tu proyecto requiere una versión particular de Python, puedes indicarlo durante la creación del entorno.

```bash
# En el directorio de tu proyecto
cd /ruta/a/mi_proyecto

# Ejemplo 1: Crear ./.venv/default usando python3.11 (si existe python3.11)
pymanager.sh --create --python 3.11

# Ejemplo 2: Crear ./.venv/mi_entorno_py310 usando python3.10 (si existe python3.10)
pymanager.sh --create mi_entorno_py310 --python 3.10
```

#### Subsección 4.1.5: Consideraciones sobre la Selección de Versión de Python
Si no especificas una versión de Python mediante la opción `--python <ver>`, `pymanager.sh` implementa una lógica para buscar automáticamente la versión de Python más adecuada y reciente disponible en tu sistema. Generalmente, prioriza versiones numéricas específicas (como 3.12, 3.11, 3.10, 3.9) antes de recurrir a un ejecutable genérico como `python3`. Los detalles exactos de la versión seleccionada y el ejecutable utilizado se pueden consultar en el archivo de log del script (`~/.logs/pymanager.log`).

### Sección 4.2: Activación de Entornos Virtuales (Comandos: `--set local` y alias `pyglobalset`)

#### Subsección 4.2.1: Propósito y Mecanismo de Activación
Activar un entorno virtual significa configurar tu sesión de shell actual para que utilice el intérprete de Python y los paquetes instalados dentro de ese entorno específico. Es crucial entender que un script de shell como `pymanager.sh` no puede modificar directamente el entorno del shell que lo invocó para "activar" un entorno. En lugar de ello, `pymanager.sh` te proporciona los comandos exactos que tú debes ejecutar manualmente en tu terminal para lograr la activación.

#### Subsección 4.2.2: Activación de Entornos Locales (`--set local`)
Para los entornos locales (aquellos creados con `--create` dentro de `./.venv/`), el comando `pymanager.sh --set local [<nombre_env_local>]` es el encargado de mostrarte las instrucciones de activación.

##### Sintaxis del Comando `--set local`
La sintaxis, según la ayuda del script, es:

```bash
pymanager.sh --set local [<nombre_env_local>]
```
El argumento `[<nombre_env_local>]` es opcional. Corresponde al nombre del subdirectorio del entorno dentro de `./.venv/` (por ejemplo, `default` o `mi_entorno_dev`). Si lo omites y existe más de un entorno local en el directorio actual, `pymanager.sh` podría presentar un menú interactivo (si `gum` está disponible) para que selecciones el entorno deseado.

##### Ejemplo de Uso de `--set local`
Supongamos que estás en el directorio de tu proyecto `/ruta/a/mi_proyecto`, que contiene un entorno en `./.venv/default/`.

```bash
# Para obtener los comandos de activación para ./.venv/default:
pymanager.sh --set local default

# Si 'default' es el único entorno o si quieres usar el menú de selección (con gum):
# pymanager.sh --set local
```
El script mostrará una salida similar a esta:

```
Info: Para activar el entorno local 'default':
  source "/ruta/a/mi_proyecto/.venv/default/bin/activate"
Info: Para desactivarlo:
  deactivate
```
Deberás copiar y pegar el comando `source "/ruta/a/mi_proyecto/.venv/default/bin/activate"` en tu terminal y ejecutarlo.

#### Subsección 4.2.3: Activación del Entorno Global por Defecto (Alias `pyglobalset`)
Para el entorno global por defecto (`~/.venv/default/`), `pymanager.sh` ofrece la conveniencia de un alias de shell llamado `pyglobalset`. Este alias se configura mediante el comando `pymanager.sh --set global` (detallado en la Sección 4.6). Una vez que el alias está configurado y tu shell ha recargado su configuración, activar el entorno global es tan simple como:

```bash
pyglobalset
```
Para desactivar este o cualquier otro entorno virtual activo, el comando estándar es:

```bash
deactivate
```

#### Subsección 4.2.4: Identificación de un Entorno Activo
Una vez que has ejecutado correctamente el comando `source .../activate`, el prompt de tu terminal generalmente cambiará. A menudo, incluirá el nombre del entorno activo entre paréntesis al principio del prompt (por ejemplo, `(default) tu_usuario@tu_maquina:~$`), indicándote visualmente que el entorno virtual está activo.

### Sección 4.3: Listado de Paquetes e Información de Entorno (Comando: `--list`)

#### Subsección 4.3.1: Propósito y Funcionalidad
El comando `--list` se utiliza para obtener información sobre un entorno virtual seleccionado, incluyendo una lista de los paquetes Python instalados en él y la versión de Python que utiliza dicho entorno.

#### Subsección 4.3.2: Sintaxis del Comando `--list`
La sintaxis, según la ayuda del script, es sencilla:

```bash
pymanager.sh --list
```

#### Subsección 4.3.3: Comportamiento Detallado
La descripción en la ayuda del script indica: "Lista paquetes y versión de Python del entorno seleccionado. (Menú interactivo si hay múltiples entornos locales/global)."

Esto implica que el comportamiento del comando puede variar ligeramente dependiendo del contexto:
*   Si te encuentras dentro de un directorio de proyecto que contiene un entorno local (ej. `./.venv/default/`), o si has estado interactuando principalmente con el entorno global (`~/.venv/default/`), el comando `--list` probablemente intentará mostrar información sobre el entorno más relevante o "activo" contextualmente.
*   Si existe ambigüedad (por ejemplo, si hay múltiples entornos locales en el directorio actual y no hay un contexto claro, o si se consideran tanto entornos locales como el global), `pymanager.sh` puede presentar un menú interactivo para que selecciones el entorno del cual deseas ver la información. Esta funcionalidad interactiva depende de la disponibilidad de `gum`.

### Sección 4.4: Instalación de Paquetes (Comandos: `--package-local`, `--install`, `--package-global`)
`pymanager.sh` proporciona tres comandos distintos para la instalación de paquetes, cada uno con un propósito y un entorno destino específicos.

#### Subsección 4.4.1: Instalación en Entornos Locales EXISTENTES (Comando: `--package-local`)

##### Propósito de `--package-local`
Este comando está diseñado para instalar paquetes Python dentro de un entorno virtual **local que ya ha sido creado previamente** con `pymanager.sh --create`. El entorno destino debe residir en un subdirectorio de `./.venv/`.

##### Sintaxis de `--package-local`
La sintaxis, según la ayuda del script, es:

```bash
pymanager.sh --package-local [<nombre_env_local>] [<paquete_o_archivo_reqs>]
```

###### Argumento Opcional `<nombre_env_local>`
Este argumento especifica el nombre del subdirectorio del entorno local (dentro de `./.venv/`) en el cual se instalarán los paquetes. Si se omite, el script asume que el destino es el entorno local llamado `default` (es decir, `./.venv/default/`).

###### Argumento Opcional `<paquete_o_archivo_reqs>`
Este argumento puede ser:
*   El nombre de un solo paquete (ej. `flask`).
*   Una cadena con múltiples nombres de paquetes, entre comillas (ej. `"flask requests"`).
*   La ruta a un archivo de requisitos (ej. `requirements.txt` o `./project_requirements.txt`).
Si este argumento se omite, el script intentará utilizar un archivo llamado `requirements.txt` ubicado en el directorio actual.

##### Consideración Importante para `--package-local`
Es crucial recordar que **el entorno local especificado debe existir antes de intentar instalar paquetes en él**. Si el entorno no ha sido creado, debes usar `pymanager.sh --create [<nombre_env_local>]` primero.

##### Ejemplos de Uso de `--package-local`
Asegúrate de estar en el directorio raíz de tu proyecto.

```bash
# Ejemplo 1: Instalar 'flask' y 'requests' en el entorno local ./.venv/default/
pymanager.sh --package-local default "flask requests"

# Ejemplo 2: Instalar paquetes desde ./requirements.txt en ./.venv/default/
# (asume que default es el entorno y requirements.txt es el archivo si se omiten los argumentos)
pymanager.sh --package-local

# Ejemplo 3: Instalar paquetes en un entorno local nombrado, ej. ./.venv/mi_entorno_dev/,
# desde un archivo de requisitos específico para él, ej. requirements_dev.txt
pymanager.sh --package-local mi_entorno_dev requirements_dev.txt
```

#### Subsección 4.4.2: Instalación en Entorno Global con Requisitos POR DEFECTO DEL SCRIPT (Comando: `--install`)

##### Propósito de `--install`
El comando `pymanager.sh --install` tiene un doble propósito:
1.  Crea el entorno virtual global por defecto, ubicado en `~/.venv/default/`, si este no existe ya.
2.  Una vez asegurada la existencia del entorno global por defecto, instala en él un conjunto de paquetes definidos en un archivo de requisitos específico, cuya ruta está preconfigurada dentro del propio script `pymanager.sh` (referenciada internamente como `DEFAULT_ENV_REQUIREMENTS_PATH`). Este comando es útil para configurar rápidamente el entorno global con un conjunto base de herramientas predefinidas por el autor del script.

##### Sintaxis de `--install`
La sintaxis es directa, ya que no toma argumentos adicionales para la selección de paquetes:

```bash
pymanager.sh --install
```

#### Subsección 4.4.3: Instalación en Entorno Global con Paquetes o Requisitos ESPECÍFICOS (Comando: `--package-global`)

##### Propósito de `--package-global`
Este comando también opera sobre el entorno global por defecto (`~/.venv/default/`), creándolo si no existe. Sin embargo, a diferencia de `--install`, `pymanager.sh --package-global` te permite especificar qué paquetes o qué archivo de requisitos particular deseas instalar en este entorno global.

##### Sintaxis de `--package-global`
La sintaxis es:

```bash
pymanager.sh --package-global <paquete_o_archivo_reqs>
```
El argumento `<paquete_o_archivo_reqs>` es obligatorio y puede ser el nombre de uno o más paquetes (entre comillas si son varios) o la ruta a un archivo de requisitos.

##### Ejemplos de Uso de `--package-global`

```bash
# Ejemplo 1: Instalar las herramientas 'ansible-lint' y 'ruff' en ~/.venv/default/
pymanager.sh --package-global "ansible-lint ruff"

# Ejemplo 2: Instalar paquetes en ~/.venv/default/ desde un archivo de requisitos personalizado
pymanager.sh --package-global ~/.mis_herramientas_globales.txt
```

### Sección 4.5: Eliminación de Entornos Virtuales (Comandos: `--remove-local`, `--remove-global`)
Estos comandos se utilizan para eliminar entornos virtuales que ya no son necesarios. Es fundamental ejercer precaución, ya que esta acción es destructiva y borrará permanentemente el entorno y todos los paquetes que contenía.

#### Subsección 4.5.1: Eliminación de Entornos Locales (Comando: `--remove-local`)

##### Propósito y Sintaxis de `--remove-local`
El comando `pymanager.sh --remove-local` está diseñado para eliminar entornos virtuales locales, es decir, aquellos ubicados dentro del directorio `./.venv/` del proyecto actual.
Sintaxis:

```bash
pymanager.sh --remove-local
```

##### Comportamiento de `--remove-local`
Al ejecutar este comando, `pymanager.sh` buscará los entornos existentes en `./.venv/*`.
*   Si `gum` está disponible, presentará un menú interactivo que te permitirá seleccionar uno, varios o todos los entornos locales detectados para su eliminación.
*   Independientemente de `gum`, el script solicitará confirmación antes de proceder con la eliminación.

#### Subsección 4.5.2: Eliminación del Entorno Global por Defecto (Comando: `--remove-global`)

##### Propósito y Sintaxis de `--remove-global`
El comando `pymanager.sh --remove-global` se utiliza específicamente para eliminar el entorno virtual global por defecto, que reside en `~/.venv/default/`.
Sintaxis:

```bash
pymanager.sh --remove-global
```

##### Comportamiento de `--remove-global`
Este comando intentará eliminar el directorio `~/.venv/default/`. Siempre solicitará confirmación antes de llevar a cabo la eliminación para prevenir borrados accidentales.

### Sección 4.6: Gestión del Alias Global para Activación Rápida (Comandos: `--set global`, `--unset global`)
`pymanager.sh` ofrece una funcionalidad para configurar un alias de shell, llamado `pyglobalset`, que facilita la activación rápida del entorno global por defecto (`~/.venv/default/`).

#### Subsección 4.6.1: Configuración del Alias (Comando: `--set global`)

##### Propósito y Funcionamiento de `--set global`
El comando `pymanager.sh --set global` realiza las siguientes acciones, según la ayuda del script:
1.  Añade la definición del alias `pyglobalset` a tu archivo de configuración de shell `~/.bashrc`. Este alias está configurado para ejecutar el comando `source $HOME/.venv/default/bin/activate`.
2.  Para que esta configuración funcione, el entorno global por defecto (`~/.venv/default/`) debe existir. Si no existe, deberás crearlo primero, por ejemplo, instalando algún paquete con `pymanager.sh --package-global mi_paquete_inicial` o usando `pymanager.sh --install`.

##### Uso de `--set global`
Para configurar el alias, ejecuta:

```bash
pymanager.sh --set global
```
Inmediatamente después de ejecutar este comando, y para que el alias esté disponible en tu sesión de terminal actual, necesitas recargar la configuración de tu shell:

```bash
source ~/.bashrc
```
En futuras sesiones de terminal, el alias ya estará disponible automáticamente. Una vez configurado, puedes activar el entorno global por defecto simplemente escribiendo `pyglobalset` y desactivarlo con `deactivate`.

#### Subsección 4.6.2: Eliminación del Alias (Comando: `--unset global`)

##### Propósito y Funcionamiento de `--unset global`
El comando `pymanager.sh --unset global` revierte la acción de `--set global`. Específicamente, elimina el bloque de definición del alias `pyglobalset` (identificado por marcadores especiales) de tu archivo `~/.bashrc`.

##### Uso de `--unset global`
Para eliminar el alias, ejecuta:

```bash
pymanager.sh --unset global
```
Al igual que con la configuración, después de eliminar el alias, debes recargar la configuración de tu shell para que el cambio surta efecto en la sesión actual:
```bash
source ~/.bashrc
```

### Sección 4.8: Ayuda y Versión del Script (Comandos: `--help`, `--version`)

#### Subsección 4.8.1: Obtención de Ayuda Detallada (Comando: `--help`)
El comando `pymanager.sh --help` (o su forma abreviada `-h`) es tu principal recurso para entender todas las capacidades del script. Muestra un mensaje de ayuda detallado que lista todos los comandos disponibles, sus respectivas opciones y una breve descripción de su funcionalidad.

#### Subsección 4.8.2: Visualización de la Versión del Script (Comando: `--version`)
Para conocer la versión específica del script `pymanager.sh` que estás utilizando, ejecuta `pymanager.sh --version`. Esta información es útil para el seguimiento de cambios, para reportar problemas o para asegurarte de que estás utilizando la versión más actualizada.

## Parte 5: Flujos de Trabajo y Escenarios Prácticos con `pymanager.sh`

### Escenario 5.1: Configuración de un Nuevo Proyecto de Desarrollo Python

#### Subsección 5.1.1: Creación del Directorio y Navegación
Primero, crea el directorio para tu nuevo proyecto y navega hacia él:

```bash
mkdir mi_nuevo_proyecto && cd mi_nuevo_proyecto
```

#### Subsección 5.1.2: Creación del Entorno Virtual Local
Dentro del directorio de tu proyecto, crea un entorno virtual local. Para usar el nombre `default` (resultando en `./.venv/default/`):

```bash
pymanager.sh --create
```
Si prefieres un nombre específico para el entorno local, por ejemplo `mi_proyecto_env` (resultando en `./.venv/mi_proyecto_env/`):

```bash
pymanager.sh --create mi_proyecto_env
```
Es una buena práctica añadir el directorio `.venv/` a tu archivo `.gitignore` para evitar que los archivos del entorno virtual se incluyan en tu repositorio Git.

#### Subsección 5.1.3: Activación del Entorno Local
Para activar el entorno local recién creado, primero obtén las instrucciones de activación usando `pymanager.sh --set local`.
Si tu entorno se llama `default`:

```bash
pymanager.sh --set local default
```
Si le diste un nombre, como `mi_proyecto_env`:

```bash
pymanager.sh --set local mi_proyecto_env
```
El script te mostrará el comando `source .../activate` específico para tu entorno. Cópialo y ejecútalo en tu terminal. Por ejemplo:

```bash
source ./.venv/default/bin/activate
```
Tu prompt debería cambiar.

#### Subsección 5.1.4: Instalación de Dependencias del Proyecto
Con el entorno local activado, puedes instalar las dependencias de tu proyecto.

*   **Opción A (Recomendada - usando `pip` directamente):** Esta es la forma más común una vez que el entorno está activo.

    ```bash
    pip install flask requests "sqlalchemy<2.0"  # Ejemplo de instalación de paquetes específicos
    # Si tienes un archivo de requisitos (ej. requirements.txt):
    pip install -r requirements.txt
    ```

*   **Opción B (Usando `pymanager.sh --package-local`):** Este comando es útil si necesitas instalar paquetes en un entorno local existente *sin tenerlo activado* en tu shell actual.

    ```bash
    # Para instalar 'flask' y 'requests' en el entorno local ./.venv/default/:
    pymanager.sh --package-local default "flask requests"

    # Para instalar desde un archivo 'requirements.txt' en el entorno local ./.venv/mi_proyecto_env/:
    pymanager.sh --package-local mi_proyecto_env requirements.txt

    # Si quieres instalar desde './requirements.txt' en './.venv/default/'
    # (omitiendo el nombre del entorno y el nombre del paquete/archivo):
    pymanager.sh --package-local
    ```

#### Subsección 5.1.5: Generación del Archivo `requirements.txt`
Si instalaste paquetes manualmente usando `pip` (Opción A), es crucial generar un archivo `requirements.txt` para asegurar la reproducibilidad de tu proyecto. Con el entorno aún activo:
```bash
pip freeze > requirements.txt
```
Este archivo listará todos los paquetes y sus versiones exactas en tu entorno. Asegúrate de incluir `requirements.txt` en tu control de versiones (Git).

#### Subsección 5.1.6: Desarrollo y Desactivación
Ahora puedes proceder con el desarrollo de tu aplicación. Todos los comandos `python` y `pip` que ejecutes utilizarán el intérprete y los paquetes del entorno activado.
Cuando termines tu sesión de trabajo, desactiva el entorno:

```bash
deactivate
```

### Escenario 5.2: Gestión de Herramientas Python de Uso Frecuente (Entorno Global)
Utiliza el entorno global por defecto (`~/.venv/default/`) para herramientas CLI como linters, formateadores, etc., para no tener que instalarlas en cada proyecto.

#### Subsección 5.2.1: Instalación de Herramientas en el Entorno Global
Utiliza `pymanager.sh --package-global` para instalar tus herramientas. Este comando también creará el directorio `~/.venv/default/` si aún no existe.

```bash
pymanager.sh --package-global "black ruff flake8 httpie"
```
O si prefieres instalar desde un archivo de requisitos personalizado:

```bash
pymanager.sh --package-global ~/.mis_herramientas_globales.txt
```
Recuerda que el comando `pymanager.sh --install` también opera sobre este entorno global, pero instala un conjunto de requisitos predefinidos por el propio script `pymanager.sh`.

#### Subsección 5.2.2: Configuración del Alias `pyglobalset`
Para acceder fácilmente a estas herramientas globales, configura el alias `pyglobalset`. Esto solo necesitas hacerlo una vez:

```bash
pymanager.sh --set global
source ~/.bashrc  # Recarga la configuración de tu shell
```

#### Subsección 5.2.3: Uso de las Herramientas Globales
Con el alias configurado, tu flujo de trabajo para usar estas herramientas es:
1.  Activa el entorno global: `pyglobalset`
2.  Ejecuta tus herramientas (ej. `black mi_archivo.py`, `ruff .`, `httpie GET google.com`).
3.  Desactiva el entorno cuando hayas terminado: `deactivate`

### Escenario 5.3: Experimentación Rápida con una Librería (Usando un Entorno Local Temporal)
A veces, solo quieres probar una nueva librería o una pieza de código sin afectar tus proyectos principales o tu entorno global.

#### Subsección 5.3.1: Creación del Entorno Temporal
Primero, crea un directorio temporal para tu experimento y navega hacia él:

```bash
mkdir ~/experimento_nueva_lib && cd ~/experimento_nueva_lib
```
Dentro de este directorio, crea un entorno local específico para esta prueba:

```bash
pymanager.sh --create prueba_lib
# Esto creará el entorno en ./venv/prueba_lib/
```

#### Subsección 5.3.2: Activación del Entorno Temporal
Obtén y ejecuta el comando de activación para `prueba_lib`:

```bash
pymanager.sh --set local prueba_lib
```
Copia y ejecuta el comando `source ./.venv/prueba_lib/bin/activate` que te muestra el script.

#### Subsección 5.3.3: Instalación y Prueba de la Librería

Con el entorno `prueba_lib` activo, instala la librería que deseas probar usando `pip`:

```bash
pip install super_nueva_libreria_experimental
```
Luego, puedes abrir un intérprete de Python y experimentar:

```python
>>> import super_nueva_libreria_experimental
>>> # ... aquí tu código de prueba ...
>>> exit()
```

## Parte 6: Características Adicionales y Consejos Útiles

### Sección 6.1: Integración Opcional con `gum`
Como se ha mencionado a lo largo de esta guía, si tienes la utilidad `gum` instalada en tu sistema, `pymanager.sh` la detectará y la utilizará para enriquecer la experiencia del usuario en varias operaciones. Esto incluye:

*   **Menús de Selección Interactivos:** Para comandos como `--list` (si hay ambigüedad sobre qué entorno listar), `--remove-local` (para elegir qué entornos específicos liminar de `./.venv/*`), y `--set local` (si no se especifica un nombre de entorno local y existen múltiples), `gum` puede presentar un menú navegable para facilitar la selección.

*   **Diálogos de Confirmación Mejorados:** Para acciones destructivas como --remove-global` o `--remove-local`, `gum` puede usarse para mostrar diálogos de confirmación más visuales y claros antes de proceder.

La integración con `gum` busca hacer la gestión de entornos no solo más eficiente sino también más agradable visualmente y, en algunos casos, más segura al requerir interacciones de confirmación explícitas.

### Sección 6.2: Utilidad del Archivo de Logging
`pymanager.sh` mantiene un registro de sus operaciones principales en el archivo `~/.logs/pymanager.log`. Este archivo de log es un recurso valioso en varias situaciones:

*   **Diagnóstico de Problemas:** Si un comando no funciona como esperas, o si encuentras un error, el archivo de log a menudo contendrá mensajes detallados que pueden ayudarte a ti o al desarrollador del script a entender la causa del problema.

*   **Auditoría de Acciones:** Si necesitas verificar qué comandos exactos ejecutó el script (por ejemplo, qué versión específica de Python se seleccionó para crear un entorno, o los detalles de una instalación de paquetes), el log proporciona este rastro.

*   **Comprensión del Funcionamiento Interno:** Para usuarios avanzados interesados en cómo opera el script internamente, el log puede ofrecer pistas sobre la lógica de ejecución.

Se recomienda revisar este archivo si necesitas profundizar en el comportamiento del script.

## Parte 7: Contribución al Proyecto
Este script `pymanager.sh` se describe como un proyecto personal. Sin embargo, si tienes sugerencias para mejorarlo, encuentras errores, o deseas contribuir de alguna manera, es probable que el repositorio del proyecto (si es público) contenga un archivo `CONTRIBUTING.md` o directrices similares. Dicho archivo detallaría el proceso para proponer cambios, reportar problemas y el formato esperado para los mensajes de commit, el cual es una parte importante de muchos flujos de trabajo de desarrollo colaborativo.

## Parte 8: Licencia de Uso
El script `pymanager.sh` se distribuye bajo los términos de una licencia específica. Para conocer los detalles completos sobre tus derechos y responsabilidades al usar, modificar o distribuir el script, debes consultar el archivo `LICENSE` que debería acompañar al script o estar presente en su repositorio fuente.
