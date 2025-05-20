#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MICURSOR - Un script para ayudar a instalar y desinstalar Cursor AI.

Copyright (C) 2025 MAURO ROSERO PÉREZ
License: GPLv3

File: micursor.py
Version: 0.1.0
Author: Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant: Cursor AI (https://cursor.com)
Created: 2025-05-19 20:56:28

This file is managed by template_manager.py.
Any changes to this header will be overwritten on the next fix.
"""

# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# Description: Un script para ayudar a instalar y desinstalar Cursor AI.

"""
Este script tiene como objetivo automatizar partes del proceso de instalación
y desinstalación de Cursor AI en sistemas Linux, y proporcionar guía
para macOS y Windows.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import json
import urllib.request
from pathlib import Path
import re
import time
import tempfile

# --- Constantes Globales ---
APP_NAME = "Instalación y Configuración de Cursor IDE"
VERSION = "0.1.0"
AUTHOR = "Mauro Rosero Pérez"
BANNER_WIDTH = 70

# Intentaremos obtener esta dinámicamente o usaremos la más genérica si no.
# CURSOR_RELEASES_API_URL = "https://api.github.com/repos/getcursor/cursor/releases/latest" # Comentado, ya que no se usa por ahora
CURSOR_DOWNLOAD_PAGE_URL = "https://cursor.com/download"
CURSOR_WEBSITE_URL = "https://cursor.com"

# Ubicaciones comunes (pueden necesitar ajustes o confirmación)
LINUX_INSTALL_DIR_BASE = Path.home() / ".local" / "share"
LINUX_BIN_DIR = Path.home() / ".local" / "bin"
LINUX_APPS_DIR = Path.home() / ".local" / "share" / "applications"
LINUX_ICONS_DIR_BASE = Path.home() / ".local" / "share" / "icons" / "hicolor"
MACOS_INSTALL_DIR = Path("/Applications")
MACOS_CONFIG_DIR = Path.home() / "Library" / "Application Support" / "Cursor"
WINDOWS_INSTALL_DIR_PROGRAMFILES = Path(os.getenv("ProgramFiles", r"C:\Program Files")) / "Cursor"
WINDOWS_INSTALL_DIR_LOCALAPPDATA = Path(os.getenv("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")) / "Programs" / "Cursor" if os.getenv("LOCALAPPDATA") else None
WINDOWS_CONFIG_DIR_ROAMING = Path(os.getenv("APPDATA", r"C:\Users\Default\AppData\Roaming")) / "Cursor" if os.getenv("APPDATA") else None
WINDOWS_CONFIG_DIR_LOCAL = Path(os.getenv("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")) / "Cursor" if os.getenv("LOCALAPPDATA") else None

# URL del README de la comunidad para buscar enlaces de descarga
COMMUNITY_README_URL = "https://raw.githubusercontent.com/oslook/cursor-ai-downloads/main/README.md"
CACHE_DIR = Path.home() / ".cache" / "micursor"
README_CACHE_FILE = CACHE_DIR / "README.md"
CACHE_EXPIRY_SECONDS = 3600 # 1 hora

def show_banner():
    """Limpia la pantalla y muestra el banner de la aplicación."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * BANNER_WIDTH)
    title_line = f"{APP_NAME} - Versión {VERSION}"
    author_line = f"Autor: {AUTHOR}"
    slogan_line = "Utilidad para la gestión de Cursor AI"

    print(f"{title_line:^{BANNER_WIDTH}}")
    print(f"{author_line:^{BANNER_WIDTH}}")
    print(f"{slogan_line:^{BANNER_WIDTH}}")
    print("=" * BANNER_WIDTH)
    print() # Línea vacía después del banner

def ensure_cache_dir():
    """Asegura que el directorio de caché exista."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_readme_content():
    """Obtiene el contenido del README.md, usando caché si es posible."""
    ensure_cache_dir()
    
    if README_CACHE_FILE.exists():
        try:
            # Verificar la antigüedad del caché
            if (time.time() - README_CACHE_FILE.stat().st_mtime) < CACHE_EXPIRY_SECONDS:
                print_debug("Usando README.md cacheado.")
                return README_CACHE_FILE.read_text(encoding="utf-8")
        except Exception as e:
            print_debug(f"Error al leer o verificar el caché del README: {e}. Se descargará de nuevo.")

    print_debug(f"Descargando README.md desde {COMMUNITY_README_URL}...")
    try:
        with urllib.request.urlopen(COMMUNITY_README_URL) as response:
            if response.status == 200:
                content = response.read().decode("utf-8")
                try:
                    README_CACHE_FILE.write_text(content, encoding="utf-8")
                    print_debug(f"README.md cacheado en {README_CACHE_FILE}")
                except Exception as e:
                    print_debug(f"Error al escribir el caché del README: {e}")
                return content
            else:
                print_error(f"Error al descargar el README: Código de estado {response.status}")
                return None
    except urllib.error.URLError as e:
        print_error(f"Error de URL al descargar el README: {e.reason}")
        return None
    except Exception as e:
        print_error(f"Error inesperado al descargar el README: {e}")
        return None

def get_os_arch_label_for_community_readme():
    """Determina la etiqueta de SO y arquitectura para el README de la comunidad (oslook)."""
    os_type = platform.system().lower()
    arch = platform.machine().lower()

    if os_type == "linux":
        if "aarch64" in arch or "arm64" in arch:
            return "linux-arm64"
        elif "x86_64" in arch or "amd64" in arch:
            return "linux-x64"
    elif os_type == "darwin": # macOS
        if "aarch64" in arch or "arm64" in arch:
            return "darwin-arm64"
        elif "x86_64" in arch or "amd64" in arch:
            return "darwin-x64"
    # Windows no está explícitamente en la tabla de ese README, se maneja por separado.
    
    print_warning(f"Combinación SO/arquitectura no soportada directamente por el parseo del README de la comunidad: {os_type}-{arch}")
    return None

def get_latest_download_url():
    """
    Obtiene la URL de descarga más reciente para el SO y arquitectura actuales
    parseando el README.md de https://github.com/oslook/cursor-ai-downloads.
    """
    os_label = get_os_arch_label_for_community_readme()
    if not os_label:
        return None

    readme_content = get_readme_content()
    if not readme_content:
        return None

    print_debug(f"Buscando URL para la etiqueta: {os_label}")

    lines = readme_content.splitlines()
    header_found = False
    
    # Expresiones regulares corregidas (raw strings r"\\"")
    # Pipe literal es \\\\| , corchetes literales son \\\\[ y \\\\]], paréntesis literales son \\\\( y \\\\)
    data_row_pattern_linux = re.compile(r"^\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|$")
    data_row_pattern_macos = re.compile(r"^\|([^|]+)\|([^|]+)\|([^|]+)\|$")
    # Corrected regex for separator lines (NO SPACE between main groups):
    # One segment: ([:]?[-]+[:]?) means optional colon, 1+ hyphens, optional colon.
    # The line: optional leading pipe, ONE segment, then ZERO OR MORE (separator, segment), optional trailing pipe.
    separator_line_pattern = re.compile(r"^\s*\|?\s*[:\-]{3,}\s*(\|\s*[:\-]{3,}\s*)*\|?\s*$")
    data_row_pattern = None
    if "darwin" in os_label:
        data_row_pattern = data_row_pattern_macos
    elif "linux" in os_label:
        data_row_pattern = data_row_pattern_linux
    else:
        print_debug("Parseo del README de la comunidad no aplicable directamente para este SO/arquitectura (Windows u otro).")
        return None

    for line in lines:
        stripped_line = line.strip()
        if not header_found:
            if "Linux Installer" in stripped_line or "Universal (macOS)" in stripped_line:
                print_debug(f"Encabezado de tabla encontrado en línea: {stripped_line}")
                header_found = True
            continue
        
        if separator_line_pattern.match(stripped_line) or stripped_line == "":
            print_debug(f"Línea separadora o vacía ignorada: {stripped_line}")
            continue

        # If we reach here, header_found is true, and it's not a separator/empty line.
        # This MUST be the first data line we are interested in.
        # data_row_pattern should be valid if os_label was successfully determined.
        
        print_debug(f"Procesando primera línea de datos candidata: '{stripped_line}'")
        match = data_row_pattern.match(stripped_line)
        
        if match:
            # Para Linux, la columna con los enlaces es la quinta.
            # Para macOS, es la tercera (según el patrón data_row_pattern_macos).
            target_group_index = 0
            if "linux" in os_label:
                target_group_index = 5
            elif "darwin" in os_label: # macOS
                target_group_index = 3
            else: # Debería haberse manejado antes, pero por seguridad
                print_error("Error interno: etiqueta de SO no reconocida para determinar el índice del grupo de captura.")
                return None

            if match.re.groups < target_group_index:
                 print_error(f"Error interno: El patrón regex ({match.re.pattern}) no tiene suficientes grupos de captura ({match.re.groups}) para el índice esperado ({target_group_index}).")
                 return None

            column_content_match = match.group(target_group_index)
            if column_content_match is None:
                print_debug(f"El grupo de captura ({target_group_index}) para la columna de enlaces es None. Línea: '{stripped_line}'. Regex: {data_row_pattern.pattern}")
                print_error(f"Falla crítica: El patrón de fila de datos coincidió, pero el grupo de captura ({target_group_index}) para la columna de enlaces estaba vacío.")
                return None
            
            column_content = column_content_match.strip()
            print_debug(f"Contenido de columna (columna de enlaces) extraído: '{column_content}'")
            
            # os_label is like "linux-x64" or "darwin-arm64"
            # El contenido es HTML, no Markdown. Buscamos <a href="URL">os_label_escaped</a>
            # Ejemplo: <a href="https://...AppImage">linux-x64</a>
            # re.escape(os_label) asegura que si os_label tiene caracteres especiales de regex (como '-'), se traten literalmente.
            link_pattern_str = r'<a\s+href="([^"]+)"[^>]*>\s*' + re.escape(os_label) + r'\s*</a>'
            link_match = re.search(link_pattern_str, column_content)
            
            if link_match:
                url = link_match.group(1).strip() # Extract the URL
                print_debug(f"URL específica para '{os_label}' encontrada: {url}")
                return url # Success!
            else:
                # Row matched, column extracted, but the specific link for our OS wasn't found in that column.
                print_debug(f"La columna de enlaces ('{column_content}') fue parseada, pero el enlace específico para '{os_label}' (patrón: {link_pattern_str}) no se encontró en ella.")
                print_error(f"No se encontró el enlace para '{os_label}' en la primera fila de datos relevante del README.")
                return None # Failure, as we only process the first data row.
        else:
            # This line (first after header/separator) did not match the data_row_pattern.
            print_debug(f"La línea '{stripped_line}' no coincide con el patrón de fila de datos esperado ('{data_row_pattern.pattern}') después del encabezado y separadores.")
            print_error("La primera línea candidata a ser de datos no coincidió con el formato esperado.")
            return None # Failure, structure problem with the first data row.
        # After processing this one candidate line (and returning), the loop effectively stops for this call.
        # The 'continue' statements above ensure we find this *first* candidate line.
        # If this line was processed and didn't return a URL, it returned None (error).

    print_error("No se encontró la tabla o la fila de datos esperada en el README después de iterar todas las líneas.")
    return None

def install_linux():
    """Instala Cursor AI en Linux."""
    print_info(f"Iniciando la instalación de {APP_NAME} para Linux...")

    # No necesitamos verificar si el SO es Linux aquí, ya que esta función solo se llama si es Linux.
    # Crear directorios necesarios
    LINUX_INSTALL_DIR_BASE.mkdir(parents=True, exist_ok=True)
    LINUX_BIN_DIR.mkdir(parents=True, exist_ok=True)
    LINUX_APPS_DIR.mkdir(parents=True, exist_ok=True)
    # Crear directorios de iconos base si no existen
    for size in ["16x16", "32x32", "48x48", "64x64", "128x128", "256x256", "512x512", "scalable"]:
        (LINUX_ICONS_DIR_BASE / size / "apps").mkdir(parents=True, exist_ok=True)

    # 1. Obtener la URL de descarga
    download_url = get_latest_download_url()
    if not download_url:
        print_error("No se pudo obtener la URL de descarga automáticamente. "
                    f"Por favor, visita {CURSOR_DOWNLOAD_PAGE_URL}")
        print_error("Abortando instalación.")
        return

    print_info(f"URL de descarga obtenida: {download_url}")
    
    file_name = download_url.split("/")[-1]
    temp_download_path = Path(shutil.get_unpack_formats()[0][0]) / file_name # Usa un dir temporal estándar
    # Corregido: shutil.get_unpack_formats()[0][0] no es un directorio, usar tempfile
    temp_dir = tempfile.mkdtemp(prefix="micursor-")
    temp_download_path = Path(temp_dir) / file_name


    # 2. Descargar el archivo
    try:
        print_info(f"Descargando {file_name}...")
        with urllib.request.urlopen(download_url) as response, open(temp_download_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print_success("Descarga completada.")
    except Exception as e:
        print_error(f"Error durante la descarga: {e}")
        if Path(temp_dir).exists(): shutil.rmtree(temp_dir)
        return

    # 3. Instalar (asumiendo AppImage por ahora, basado en la lógica del README)
    if file_name.lower().endswith(".appimage"):
        install_path = LINUX_BIN_DIR / "cursor" # Nombre genérico del ejecutable
        
        print_info(f"Preparando instalación de {file_name}...")
        try:
            # Usar capture_output para evitar que pkill imprima a la consola
            # Usar check=False para no fallar si no hay procesos o pkill no está.
            # El argumento -f busca en toda la línea de comandos, no solo el nombre del proceso.
            pkill_result = subprocess.run(["pkill", "-f", "cursor"], check=False, capture_output=True, text=True)
            if pkill_result.returncode == 0:
                print_debug("Señal de terminación enviada a procesos de Cursor.")
            elif pkill_result.returncode == 1: # Código de salida 1 de pkill: no se encontraron procesos
                print_debug("No se encontraron instancias de Cursor en ejecución.")
            else: # Otro error de pkill
                print_warning(f"Comando pkill finalizó con código {pkill_result.returncode}. Salida STDERR: {pkill_result.stderr.strip()}")

            print_debug("Esperando 2 segundos para que los procesos se cierren...")
            time.sleep(2)
        except FileNotFoundError:
            print_warning("Comando 'pkill' no encontrado. Omitiendo cierre de procesos de Cursor.")
        except Exception as sub_e:
            print_warning(f"Error inesperado al intentar cerrar procesos de Cursor: {sub_e}")

        if install_path.exists():
            print_debug(f"El archivo de destino {install_path} existe. Intentando eliminarlo...")
            try:
                install_path.unlink()
                print_debug(f"Archivo {install_path} eliminado exitosamente.")
            except OSError as ose:
                print_warning(f"No se pudo eliminar {install_path} (podría estar aún en uso): {ose}. Se intentará mover de todas formas.")
            except Exception as ex_unlink:
                 print_warning(f"Error inesperado al eliminar {install_path}: {ex_unlink}. Se intentará mover de todas formas.")
        
        # Mover y renombrar el AppImage
        try:
            print_info(f"Instalando {file_name} en {install_path}...")
            shutil.move(str(temp_download_path), str(install_path))
            os.chmod(install_path, 0o755) # Hacerlo ejecutable
            print_success(f"{APP_NAME} AppImage instalado en {install_path}")
        except Exception as e:
            print_error(f"Error al mover/renombrar el AppImage: {e}")
            if Path(temp_dir).exists(): shutil.rmtree(temp_dir)
            return

        # 4. Crear entrada .desktop (opcional, pero bueno para la integración)
        create_linux_desktop_entry(install_path)
        
        print_info(f"Puedes ejecutar {APP_NAME} escribiendo 'cursor' en tu terminal o buscándolo en tu menú de aplicaciones.")

    elif file_name.lower().endswith(".tar.gz") or file_name.lower().endswith(".zip"):
        # Lógica para extraer y mover si es un tar.gz o zip
        # Esto requeriría encontrar el ejecutable dentro del archivo descomprimido.
        print_info(f"Descargado {file_name}. La instalación de archivos comprimidos aún no está implementada en este script.")
        print_info("Por favor, descomprime manualmente y mueve el ejecutable a tu PATH.")
        # Limpiar
        if Path(temp_dir).exists(): shutil.rmtree(temp_dir)
        return # Salir si no es AppImage por ahora

    else:
        print_warning(f"Formato de archivo no reconocido o no manejado: {file_name}")
        print_info("Por favor, maneja la instalación manualmente.")
        if Path(temp_dir).exists(): shutil.rmtree(temp_dir)
        return

    # Limpieza final del directorio temporal
    if Path(temp_dir).exists():
        shutil.rmtree(temp_dir)
    
    print_success(f"{APP_NAME} para Linux instalado correctamente.")

def remove_linux():
    """Desinstala Cursor AI de Linux."""
    print_info(f"Iniciando la desinstalación de {APP_NAME} para Linux...")
    
    install_dir_app = LINUX_INSTALL_DIR_BASE / "Cursor"
    executable_path = LINUX_BIN_DIR / "cursor"
    desktop_file_path = LINUX_APPS_DIR / "cursor.desktop"

    removed_something = False
    print_info("Eliminando componentes de Cursor AI...")
    try:
        if executable_path.is_symlink() or executable_path.exists(): # Chequeo extra por si no es symlink
            print_debug(f"Eliminando enlace simbólico/ejecutable: {executable_path}")
            executable_path.unlink(missing_ok=True)
            removed_something = True
        
        if desktop_file_path.exists():
            print_debug(f"Eliminando archivo .desktop: {desktop_file_path}")
            desktop_file_path.unlink(missing_ok=True)
            removed_something = True

        # El AppImage/archivos de la app están en install_dir_app
        # El script original `cursor-install.sh remove` elimina ~/.local/share/cursor-temp
        # y el AppImage específico. Aquí seremos un poco más amplios con el directorio
        # que creamos.
        if install_dir_app.exists():
            print_debug(f"Eliminando directorio de instalación: {install_dir_app}")
            # Preguntar antes de eliminar un directorio recursivamente podría ser más seguro
            # confirm = input(f"¿Está seguro de que desea eliminar {install_dir_app} y todo su contenido? (s/N): ")
            # if confirm.lower() == 's':
            #     shutil.rmtree(install_dir_app)
            #     print(f"Directorio {install_dir_app} eliminado.")
            #     removed_something = True
            # else:
            #     print(f"Eliminación de {install_dir_app} cancelada por el usuario.")
            # Por ahora, para automatización, eliminamos directamente.
            shutil.rmtree(install_dir_app) # ¡CUIDADO! Esto elimina recursivamente.
            print_debug(f"Directorio {install_dir_app} eliminado.")
            removed_something = True
        
        # Limpiar también archivos de configuración si es necesario, similar a macOS/Windows.
        # Cursor podría almacenar configuraciones en ~/.config/Cursor o similar.
        # Esto no estaba en el script `cursor-install.sh` original.
        # Path.home() / ".config" / "Cursor"
        # Por ahora, nos enfocamos en lo que instaló el script.
        
        if removed_something:
            print_success(f"{APP_NAME} desinstalado de Linux.")
            print_info(f"Actualizando base de datos de menús...")
            try:
                subprocess.run(["update-desktop-database", str(LINUX_APPS_DIR)], check=True, capture_output=True)
                print_debug("Base de datos de menús actualizada.")
            except FileNotFoundError:
                print_warning("`update-desktop-database` no encontrado. Puede que necesites ejecutarlo manualmente.")
            except subprocess.CalledProcessError as e:
                print_warning(f"Falló la actualización de la base de datos de menús: {e.stderr.decode().strip()}")
        else:
            print_info(f"No se encontraron componentes de {APP_NAME} para eliminar en las rutas esperadas.")

    except Exception as e:
        print_error(f"Error durante la desinstalación en Linux: {e}")

def install_macos():
    """Proporciona instrucciones para instalar Cursor AI en macOS."""
    print(f"Instalación de {APP_NAME} para macOS:")
    print("1. Ve a la página de descargas oficial: https://cursor.com/download")
    print("2. Descarga el archivo .dmg para macOS.")
    print("3. Abre el archivo .dmg descargado.")
    print(f"4. Arrastra el icono de '{APP_NAME}' (o similar) a tu carpeta de Aplicaciones ('{MACOS_INSTALL_DIR}').")
    print("5. Puedes expulsar el .dmg después de la instalación.")
    print(f"{APP_NAME} debería estar ahora disponible en tu Launchpad y carpeta de Aplicaciones.")

def remove_macos():
    """Proporciona instrucciones para desinstalar Cursor AI de macOS."""
    print(f"Desinstalación de {APP_NAME} para macOS:")
    print(f"1. Cierra {APP_NAME} si se está ejecutando.")
    print(f"2. Ve a tu carpeta de Aplicaciones ('{MACOS_INSTALL_DIR}').")
    print(f"3. Arrastra el icono de '{APP_NAME}' a la Papelera.")
    print("4. Vacía la Papelera para completar la desinstalación.")
    print("\nOpcional: Para eliminar archivos de configuración y caché:")
    print(f" - Elimina el directorio: {MACOS_CONFIG_DIR}")
    print(f"   (Puedes acceder a él desde Finder > Ir > Ir a la carpeta... y pegando la ruta)")
    # Podría haber otros directorios en ~/Library/Caches, ~/Library/Preferences, etc.

def install_windows():
    """Proporciona instrucciones para instalar Cursor AI en Windows."""
    print(f"Instalación de {APP_NAME} para Windows:")
    print("1. Ve a la página de descargas oficial: https://cursor.com/download")
    print("2. Descarga el archivo instalador .exe para Windows.")
    print("3. Ejecuta el archivo .exe descargado.")
    print("4. Sigue las instrucciones del asistente de instalación.")
    print(f"{APP_NAME} debería estar ahora disponible en tu Menú de Inicio.")

def remove_windows():
    """Proporciona instrucciones para desinstalar Cursor AI de Windows."""
    print(f"Desinstalación de {APP_NAME} para Windows:")
    print("1. Cierra {APP_NAME} si se está ejecutando.")
    print("2. Abre 'Configuración' > 'Aplicaciones' > 'Aplicaciones y características'.")
    print("   (O busca 'Agregar o quitar programas' en el Menú de Inicio).")
    print(f"3. Busca '{APP_NAME}' en la lista de aplicaciones instaladas.")
    print("4. Selecciónalo y haz clic en 'Desinstalar'. Sigue las instrucciones.")
    print("\nOpcional: Para eliminar archivos de configuración y caché:")
    if WINDOWS_CONFIG_DIR_ROAMING and WINDOWS_CONFIG_DIR_ROAMING.exists():
        print(f" - Considera eliminar el directorio: {WINDOWS_CONFIG_DIR_ROAMING}")
    if WINDOWS_CONFIG_DIR_LOCAL and WINDOWS_CONFIG_DIR_LOCAL.exists():
        print(f" - Considera eliminar el directorio: {WINDOWS_CONFIG_DIR_LOCAL}")
    print(f"   (Puedes acceder a estas rutas pegándolas en la barra de direcciones del Explorador de Archivos, ej. %APPDATA%\\Cursor)")

def create_linux_desktop_entry(executable_path: Path):
    print_info(f"Intentando crear entrada .desktop para {executable_path}...")
    # La ruta ejecutable debe estar entre comillas si puede contener espacios
    exec_command = f'"{executable_path}" --no-sandbox %U' # Usar comillas simples para el f-string externo
    
    # Usar f-string con triples comillas. Asegurarse que las comillas internas no interfieran.
    # Si se necesitan comillas dentro del contenido del .desktop, usar un tipo diferente
    # o escaparlas si es necesario, aunque para este contenido no parece ser el caso.
    desktop_file_content = f'''[Desktop Entry]
Name={APP_NAME}
Comment=Code editor with AI capabilities
Exec={exec_command}
Icon=cursor
Terminal=false
Type=Application
Categories=Development;IDE;TextEditor;
Keywords=Text;Editor;Development;IDE;AI;
StartupWMClass=Cursor
''' # Fin de la f-string triple comilla

    # Usar el LINUX_APPS_DIR definido globalmente
    desktop_file_path = LINUX_APPS_DIR / "micursor-cursor.desktop" # Nombre consistente
    try:
        desktop_file_path.write_text(desktop_file_content, encoding="utf-8")
        if shutil.which("update-desktop-database"):
            # Asegurar que LINUX_APPS_DIR es un string para subprocess
            subprocess.run(["update-desktop-database", str(LINUX_APPS_DIR)], check=False)
        print_success(f"Entrada .desktop creada en {desktop_file_path}")
        print_info("Puede que necesites reiniciar tu sesión o actualizar el menú de aplicaciones.")
    except Exception as e:
        print_error(f"No se pudo crear la entrada .desktop: {e}")

def config_mdc():
    """Configura los archivos de reglas de Cursor."""
    print("\n🔄 Configurando reglas MDC para Cursor...\n")
    
    # Obtener la ruta del script actual
    script_dir = Path(__file__).parent
    config_dir = script_dir / "config"
    
    # Verificar que existe el directorio config
    if not config_dir.exists():
        print("❌ No se encontró el directorio de configuración")
        return False
    
    # Usar el directorio actual como ruta del proyecto por defecto
    project_dir = Path.cwd()
    cursor_rules_dir = project_dir / ".cursor" / "rules"
    cursor_rules_dir.mkdir(parents=True, exist_ok=True)
    
    # Copiar archivos *.mdc.def a .cursor/rules
    mdc_files = list(config_dir.glob("*.mdc.def"))
    if not mdc_files:
        print("❌ No se encontraron archivos .mdc.def en el directorio de configuración")
        return False
    
    print("📁 Copiando archivos de reglas...")
    for mdc_file in mdc_files:
        target_file = cursor_rules_dir / mdc_file.stem.replace(".def", "")
        try:
            shutil.copy2(mdc_file, target_file)
            print(f"  ✓ {mdc_file.name} → {target_file.name}")
        except Exception as e:
            print(f"  ✗ Error al copiar {mdc_file.name}: {e}")
            return False
    
    # Copiar .cursorrules.def a .cursorrules en la raíz del proyecto
    cursorrules_def = config_dir / ".cursorrules.def"
    if not cursorrules_def.exists():
        print("❌ No se encontró el archivo .cursorrules.def")
        return False
    
    target_cursorrules = project_dir / ".cursorrules"
    try:
        shutil.copy2(cursorrules_def, target_cursorrules)
        print(f"  ✓ .cursorrules.def → .cursorrules")
    except Exception as e:
        print(f"  ✗ Error al copiar .cursorrules.def: {e}")
        return False
    
    # Leer y mostrar el contenido de cursor_identity.def
    identity_file = config_dir / "cursor_identity.def"
    if not identity_file.exists():
        print("❌ No se encontró el archivo cursor_identity.def")
        return False
    
    try:
        identity_content = identity_file.read_text(encoding="utf-8")
        print("\n📋 Configuración de identidad de Cursor:")
        print("─" * 80)
        for line in identity_content.splitlines():
            print(line)
        print("─" * 80)
        
        print("\n📝 Pasos para configurar:")
        print("  1. Abre Cursor Settings (File/Preferences/Cursor Settings)")
        print("  2. En Rules/User Rules, pega el contenido anterior")
        print("  3. Guarda los cambios")
    except Exception as e:
        print(f"❌ Error al leer cursor_identity.def: {e}")
        return False
    
    print("\n✨ Configuración completada exitosamente\n")
    return True

def main():
    show_banner() # Llamada al banner al inicio

    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} (Versión {VERSION}) - {AUTHOR}\\nUtilidad para instalar o desinstalar Cursor AI.",
        epilog=f"Ejemplos de uso:\\n  python micursor.py --install    (Para instalar {APP_NAME})\\n  python micursor.py --remove     (Para desinstalar {APP_NAME})\\n  python micursor.py --config-mdc (Para configurar reglas MDC)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.title = "Acciones requeridas (elegir una)"
    action_group.add_argument("--install", action="store_true", help=f"Realiza la instalación de {APP_NAME} en el sistema.\\nPara Linux, intentará una instalación automatizada.\\nPara macOS y Windows, proporcionará instrucciones detalladas.")
    action_group.add_argument("--remove", action="store_true", help=f"Realiza la desinstalación de {APP_NAME} del sistema.\\nPara Linux, intentará una desinstalación automatizada de los componentes instalados por este script.\\nPara macOS y Windows, proporcionará instrucciones detalladas.")
    action_group.add_argument("--config-mdc", action="store_true", help="Configura los archivos de reglas MDC para Cursor.")

    if len(sys.argv) == 1: # Si no se pasan argumentos, muestra la ayuda y sale.
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()

    system = platform.system()

    if args.install:
        if system == "Linux":
            install_linux()
        elif system == "Darwin": # macOS
            install_macos()
        elif system == "Windows":
            install_windows()
        else:
            print_error(f"Sistema operativo '{system}' no soportado directamente por este script para instalación automática.")
            print_info(f"Por favor, visita {CURSOR_DOWNLOAD_PAGE_URL} para instrucciones manuales.")
    
    elif args.remove:
        if system == "Linux":
            remove_linux()
        elif system == "Darwin":
            remove_macos()
        elif system == "Windows":
            remove_windows()
        else:
            print_error(f"Sistema operativo '{system}' no soportado directamente por este script para desinstalación automática.")
            print_info("Por favor, consulta la documentación de tu sistema o de Cursor para desinstalación manual.")
            sys.exit(1)
    
    elif args.config_mdc:
        if not config_mdc():
            sys.exit(1)

if __name__ == "__main__":
    # Definiciones placeholder para las funciones de impresión si no existen en el contexto completo
    # Esto es solo para que el extracto sea ejecutable aisladamente.
    # En el script real, estas funciones ya deberían estar definidas.
    DEBUG_ENABLED = os.getenv("MICURSOR_DEBUG") == "1"

    def print_debug(message: str):
        if DEBUG_ENABLED:
            print(f"[DEBUG] {message}")

    def print_info(message: str):
        print(f"[INFO] {message}")

    def print_warning(message: str):
        print(f"[WARNING] {message}")

    def print_error(message: str):
        print(f"[ERROR] {message}")
    
    def print_success(message: str):
        print(f"[SUCCESS] {message}")

    main()