# Guía de Uso: `git-tokens.py` - Gestor Seguro de Tokens Git

<!-- PARSEABLE_METADATA_START
purpose: Proporcionar una guía de usuario completa para la herramienta git-tokens.py, incluyendo instalación, configuración, uso de comandos y solución de problemas.
technology: Python, SOPS, GPG, Bash
status: Development
PARSEABLE_METADATA_END -->

<!-- CURRENT_VERSION_PLACEHOLDER -->

<!-- TOC -->
<!-- Generaremos una tabla de contenidos aquí más adelante si es necesario. -->

## 1. Introducción

`git-tokens.py` es una herramienta de línea de comandos diseñada para ayudarte a gestionar de forma segura tus tokens de acceso personal (PATs) y otras credenciales para interactuar con diversos servidores Git (como GitHub, GitLab, Gitea, etc.). Utiliza [SOPS (Secrets OPerationS)](https://github.com/getsops/sops) para encriptar los tokens, asegurando que no se almacenen en texto plano en tu sistema de archivos.

El objetivo principal es proporcionar una manera conveniente y segura de almacenar y recuperar tokens para su uso en scripts, herramientas de línea de comandos o cualquier situación donde necesites autenticarte con un servidor Git mediante un token.

## 2. Requisitos Previos

Antes de utilizar `git-tokens.py`, asegúrate de tener lo siguiente:

*   **Python 3.x**: El script está escrito en Python 3.
*   **SOPS**: La herramienta SOPS debe estar instalada y accesible en el `PATH` de tu sistema. Consulta la [documentación oficial de SOPS](https://github.com/getsops/sops/blob/master/README.md) o la guía `docs/sops.md` de este proyecto para la instalación.
*   **GnuPG (GPG)**: Debes tener GPG instalado y una clave PGP personal generada y configurada. `git-tokens.py` (a través de SOPS) utilizará esta clave PGP para encriptar y desencriptar tus tokens. Necesitarás la huella digital (fingerprint) de tu clave PGP para la configuración de SOPS.

## 3. Instalación

1.  Asegúrate de que el script `git-tokens.py` (ubicado, por ejemplo, en `scripts/python/git-tokens.py` dentro de este repositorio) sea ejecutable:
    ```bash
    chmod +x scripts/python/git-tokens.py
    ```
2.  Para mayor comodidad, puedes añadir el directorio `scripts/python/` a tu `PATH` o crear un enlace simbólico del script a un directorio que ya esté en tu `PATH` (ej. `~/.local/bin/`).
    ```bash
    # Ejemplo de enlace simbólico
    # ln -s /ruta/completa/a/scripts/python/git-tokens.py ~/.local/bin/git-tokens
    ```
    (Asegúrate de que `~/.local/bin` esté en tu `PATH`).

## 4. Configuración Inicial

### 4.1. Configuración de SOPS (`.sops.yaml`)

Para que SOPS pueda encriptar y desencriptar los archivos de token, necesita un archivo de configuración llamado `.sops.yaml`. Este archivo le dice a SOPS qué claves utilizar para qué archivos.

*   **Ubicación del `.sops.yaml`**: Este archivo debe colocarse en el directorio donde se almacenarán tus tokens encriptados (ver sección 4.2) o en un directorio padre. Una práctica común es tener un `.sops.yaml` global en `~/.config/sops/rules.yaml` o específico para el proyecto. Para `git-tokens.py`, el `.sops.yaml` relevante es el que afecta al directorio de almacenamiento de tokens.
*   **Contenido**: Debes crear una regla que especifique tu huella PGP para los archivos de token. Puedes usar la plantilla `config/sops_rules.def` de este proyecto como base. La variable `${git_fingerprint}` en la plantilla debe ser reemplazada por tu huella PGP real.

    **Ejemplo de `.sops.yaml` para los archivos de token:**
    ```yaml
    creation_rules:
      - path_regex: '.*token_.*\.git\.sops\.yaml$'
        pgp: 'TU_FINGERPRINT_PGP_REAL_AQUI' # Reemplaza esto con tu huella PGP
    ```
    Asegúrate de que la `path_regex` coincida con los nombres de archivo que `git-tokens.py` utilizará (ver Sección 6).

### 4.2. Directorio de Almacenamiento de Tokens

`git-tokens.py` almacena los archivos de token encriptados en una ubicación específica:

1.  Primero, la herramienta intenta leer una ruta desde el archivo `~/bin/sops/devspath.def`.
2.  Si este archivo no existe, no es accesible o no contiene una ruta válida, `git-tokens.py` utiliza la ubicación por defecto: `~/.sops/`.

Asegúrate de que este directorio exista y que tengas permisos de escritura en él. Es recomendable que el archivo `.sops.yaml` descrito anteriormente se aplique a este directorio.

## 5. Uso de Comandos

La sintaxis general para usar la herramienta es:

```bash
git-tokens.py [OPCIÓN] [ARGUMENTO_POSICIONAL_SI_APLICA]
```

A continuación, se describen las acciones disponibles:

### 5.1. Añadir un Nuevo Token

Esta es la acción por defecto cuando se ejecuta el script sin opciones que modifiquen su comportamiento (como `--remove` o `--version`).

```bash
git-tokens.py
```

Al ejecutarlo de esta manera, `git-tokens.py` te solicitará interactivamente la siguiente información:

1.  **Selección del proveedor Git**: Se muestra un menú numerado con los proveedores disponibles (GitHub, GitLab, Gitea, etc.) y una opción para cancelar.
2.  **Token secreto**: El token de acceso personal o credencial que quieres almacenar.
3.  **URL del servidor Git** (si el proveedor lo requiere): La URL base completa del servidor Git.

Una vez proporcionada la información, `git-tokens.py`:
1.  Codifica el token secreto en Base64.
2.  Crea un archivo YAML temporal con la URL del servidor y el token codificado.
3.  Utiliza SOPS (y tu clave PGP configurada en `.sops.yaml`) para encriptar este archivo YAML.
4.  Guarda el archivo encriptado en el directorio de almacenamiento configurado (ver Sección 4.2) con el nombre `token_<identificador>.git.sops.yaml`.

**Ejemplo de Interacción:**
```
$ git-tokens.py
Seleccione el servicio Git para su token (o '0' para cancelar):
  0. Cancelar / Salir
  1. github - GitHub
  2. gitlab - GitLab
  3. gitea - Gitea
Seleccione una opción (número): 1
Token para GitHub (github)
Ingrese su token para github (o Enter vacío para cancelar): ****************************************
Token 'github' añadido y encriptado exitosamente.
```

### 5.2. Eliminar un Token (`--remove`)

Este comando elimina permanentemente un archivo de token encriptado.

```bash
git-tokens.py --remove <identificador_token>
```

*   `<identificador_token>`: El nombre único del token que deseas eliminar (el mismo que usaste al añadirlo, e.g., `github`).

`git-tokens.py` te pedirá confirmación antes de eliminar el archivo `token_<identificador_token>.git.sops.yaml` del sistema de archivos. Si el token no existe, mostrará una lista de los tokens disponibles.

**Ejemplo:**
```
$ git-tokens.py --remove github
¿Está seguro de que desea eliminar el archivo de token /home/usuario/.sops/token_github.git.sops.yaml? (s/N): s
Archivo de token /home/usuario/.sops/token_github.git.sops.yaml eliminado exitosamente.
```

### 5.3. Mostrar la Versión del Script (`--version`)

Esta opción muestra la versión actual de `git-tokens.py` y luego sale.

```bash
git-tokens.py --version
```

### 5.4. Mostrar Ayuda (`-h` o `--help`)

Estas opciones muestran el mensaje de ayuda del script, listando las opciones disponibles, y luego sale.

```bash
git-tokens.py -h
```
o
```bash
git-tokens.py --help
```

## 6. Estructura y Formato de los Archivos de Token

Como referencia, los archivos de token gestionados por `git-tokens.py` tienen el siguiente formato:

```yaml
git_url: <URL_del_servidor_Git>
token: <token_codificado_en_Base64>
```

Por ejemplo:

```yaml
git_url: https://github.com
token: Z2hwX2ludGVybmFsX3Rva2VuCg==
```

Estos archivos se encriptan utilizando SOPS y se almacenan en el directorio de almacenamiento de tokens configurado (ver Sección 4.2) con el nombre `token_<identificador>.git.sops.yaml`.

## 7. Casos de Uso Comunes

### 7.1. Configuración Inicial de un Nuevo Proyecto

Cuando comienzas a trabajar en un nuevo proyecto que requiere autenticación con múltiples servidores Git:

```bash
# Añadir token para GitHub
$ git-tokens.py
Seleccione el servicio Git para su token (o '0' para cancelar):
  0. Cancelar / Salir
  1. github - GitHub
  2. gitlab - GitLab
  3. gitea - Gitea
Seleccione una opción (número): 1
Token para GitHub (github)
Ingrese su token para github (o Enter vacío para cancelar): ****************************************

# Añadir token para GitLab
$ git-tokens.py
Seleccione el servicio Git para su token (o '0' para cancelar):
  0. Cancelar / Salir
  1. github - GitHub
  2. gitlab - GitLab
  3. gitea - Gitea
Seleccione una opción (número): 2
Token para GitLab (gitlab)
Ingrese su token para gitlab (o Enter vacío para cancelar): ****************************************
Indique la URL del servidor Git (ej: https://git.example.com): https://gitlab.corporacion.com
```

### 7.2. Gestión de Tokens

Para eliminar un token que ya no necesitas:

```bash
$ git-tokens.py --remove github
¿Está seguro de que desea eliminar el archivo de token /home/usuario/.sops/token_github.git.sops.yaml? (s/N): s
Archivo de token /home/usuario/.sops/token_github.git.sops.yaml eliminado exitosamente.
```

## 8. Contribución

Si deseas contribuir a este proyecto, por favor sigue las pautas de contribución en `CONTRIBUTING.md`.

## 9. Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles.

## 10. Créditos

*   Este proyecto fue creado y mantenido por [Tu Nombre].
*   Agradecimientos especiales a [Nombre de la persona o organización] por su contribución al proyecto.

## 11. Contacto

Si tienes preguntas o sugerencias, no dudes en contactarme a través de [tu dirección de correo electrónico].

## 12. Recursos Adicionales

*   [Repositorio de GitHub del proyecto](https://github.com/tu_usuario/git-tokens)
*   [Documentación de SOPS](https://github.com/getsops/sops/blob/master/README.md)
*   [Documentación de GnuPG](https://www.gnupg.org/documentation/)