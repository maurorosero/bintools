#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-04-30 05:52:19
# Version: 0.1.0
#
# context-sync.py - Sincroniza archivos de contexto README del usuario entre un directorio `tmp` y una ubicación externa. También configura enlaces simbólicos.
# -----------------------------------------------------------------------------
#
import os
import sys
import re
import shutil
import subprocess
import argparse
from pathlib import Path

APP_NAME = "Sincronizador de Contexto para README (usuario)"
APP_VERSION = "1.2.5"
APP_AUTHOR = "Mauro Rosero Pérez (mauro.rosero@gmail.com)" 

# --- Configuración ---
# Directorio temporal dentro del workspace
TMP_DIR_NAME = "tmp"
# Patrón regex para buscar archivos de contexto en tmp (case-insensitive)
# Busca 'context', opcionalmente seguido de - o _, 'user', opcionalmente - o _, 'readme', extensión .md
CONTEXT_FILE_PATTERN = re.compile(r"context[-_ ]?user[-_ ]?readme\.md", re.IGNORECASE)
# Ruta externa de destino para la sincronización desde tmp
EXTERNAL_TARGET_CONTEXT_PATH = Path("~/.developer/contexts/user_readme.md").expanduser()
# --- Archivo destino en tmp para edición ---
TMP_EDIT_TARGET_FILENAME = "context_user_readme.md"
# --- NUEVO: Ruta de la plantilla de inicialización ---
INIT_TEMPLATE_PATH_REL = Path("config/context-readme-user.md")
# -----------------------------------------------------

# --- Configuración para la funcionalidad de setup (similar a setup-readme-context.sh) ---
# Archivo de configuración que PUEDE contener la ruta maestra
CONFIG_FILE_PATH = Path("~/bin/config/readme_user.context").expanduser() # <-- Nombre corregido
# Ruta maestra de fallback si el archivo de config no existe/es inválido
FALLBACK_MASTER_CONTEXT_PATH = Path("~/.config/contexts/readme/personal.md").expanduser()
# Ruta relativa dentro del repo para el enlace simbólico
RELATIVE_SYMLINK_PATH = Path(".github/readme-context-personal-global.md")
# --------------------

# --- Funciones Auxiliares ---

def print_info(message):
    print(f"\033[0;32mINFO:\033[0m {message}")

def print_warn(message):
    print(f"\033[1;33mWARN:\033[0m {message}")

def print_error(message, exit_code=1):
    print(f"\033[0;31mERROR:\033[0m {message}", file=sys.stderr)
    if exit_code is not None:
        sys.exit(exit_code)

def run_command(command, cwd=None):
    """Ejecuta un comando y retorna (stdout, stderr, returncode)."""
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd or Path.cwd(),
            encoding='utf-8'
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except FileNotFoundError:
        print_error(f"Comando '{command[0]}' no encontrado. Asegúrate de que esté en tu PATH.")
        return None, f"Comando '{command[0]}' no encontrado.", 1
    except Exception as e:
        print_error(f"Error inesperado ejecutando {' '.join(command)}: {e}")
        return None, str(e), 1

def is_git_repo(path):
    """Verifica si una ruta está dentro de un repositorio Git."""
    stdout, stderr, returncode = run_command(['git', 'rev-parse', '--is-inside-work-tree'], cwd=path)
    return returncode == 0 and stdout == 'true'

def get_git_root(path):
    """Obtiene la ruta raíz del repositorio Git."""
    stdout, stderr, returncode = run_command(['git', 'rev-parse', '--show-toplevel'], cwd=path)
    if returncode == 0:
        return Path(stdout)
    else:
        print_error(f"No se pudo determinar la raíz del repositorio Git desde '{path}'.\\nStderr: {stderr}")
        return None

def get_master_context_path_from_config():
    """Determina la ruta maestra leyendo config o usando fallback."""
    master_path = None
    config_path_used = False

    if CONFIG_FILE_PATH.is_file():
        print_info(f"Leyendo archivo de configuración: {CONFIG_FILE_PATH}")
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # --- MODIFICADO: Expandir ~ y $HOME --- 
                        path_str = line
                        home_dir = str(Path.home())
                        # Reemplazar ~ al inicio o exacto
                        if path_str.startswith("~/"):
                            path_str = home_dir + path_str[1:]
                        elif path_str == "~":
                            path_str = home_dir
                        # Reemplazar $HOME al inicio o exacto
                        if path_str.startswith("$HOME/"):
                            path_str = home_dir + path_str[5:] # Longitud de $HOME/
                        elif path_str == "$HOME":
                            path_str = home_dir
                        
                        potential_path = Path(path_str)
                        # ----------------------------------------
                        master_path = potential_path
                        config_path_used = True
                        print_info(f"Usando ruta maestra configurada: {master_path}")
                        break # Usar solo la primera línea válida
        except Exception as e:
            print_warn(f"No se pudo leer el archivo de configuración '{CONFIG_FILE_PATH}': {e}")

    if not config_path_used:
        master_path = FALLBACK_MASTER_CONTEXT_PATH
        print_info(f"Archivo de config no encontrado o inválido. Usando fallback: {master_path}")

    if not master_path:
         print_error("Error crítico: No se pudo determinar la ruta maestra del contexto.", None)
         # Intentar recuperarse con el fallback por si acaso
         master_path = FALLBACK_MASTER_CONTEXT_PATH
         print_warn(f"Intentando recuperarse con fallback: {master_path}")

    # --- NUEVO: Asegurar que el directorio padre exista --- 
    if master_path:
        master_dir = master_path.parent
        if not master_dir.is_dir():
            print_info(f"El directorio para el archivo maestro no existe: {master_dir}")
            print_info("Intentando crear directorios...")
            try:
                master_dir.mkdir(parents=True, exist_ok=True)
                print_info(f"Directorios creados exitosamente: {master_dir}")
            except Exception as e:
                print_error(f"No se pudieron crear los directorios necesarios '{master_dir}': {e}", None)
                print_error("Por favor, crea los directorios manualmente.", None)
                return None # No podemos continuar si no se puede crear el directorio
    # -----------------------------------------------------

    # Verificar existencia final del archivo
    if master_path and not master_path.is_file(): # Añadido check master_path aquí también
         print_error(f"El archivo maestro de contexto NO existe en la ruta determinada: {master_path}", None)
         print_error(f"Por favor, crea este archivo o corrige la ruta en '{CONFIG_FILE_PATH}' (si aplica).", None)
         # Nota: No lo creamos automáticamente, solo el directorio.
         # El archivo maestro debe ser creado manualmente o mediante el flujo tmp->externa.
         return None # No se puede continuar sin el archivo maestro

    if master_path: # Si todo fue bien
        print_info(f"Archivo maestro de contexto encontrado (o directorio listo): {master_path}")
        return master_path
    else:
        # Si llegamos aquí, es porque master_path era None inicialmente o la creación del dir falló
        print_error("No se pudo establecer una ruta maestra válida.", None)
        return None

def update_gitignore(gitignore_path, entry_to_add):
    """Añade una entrada a .gitignore si no existe, con comentarios.
    Retorna True si el archivo fue modificado, False en caso contrario.
    """
    entry_exists = False
    lines = []
    modified = False # <<< NUEVO: Flag para rastrear modificación

    if gitignore_path.is_file():
        try:
            lines = gitignore_path.read_text(encoding='utf-8').splitlines()
            for line in lines:
                if line.strip() == entry_to_add:
                    entry_exists = True
                    print_info(f"La ruta '{entry_to_add}' ya está en {gitignore_path.name}.")
                    break
        except Exception as e:
            print_warn(f"No se pudo leer {gitignore_path.name}: {e}. Se intentará añadir la entrada de todas formas.")
            lines = [] # Resetear lines para asegurar que se escriba

    if not entry_exists:
        print_info(f"Añadiendo '{entry_to_add}' a {gitignore_path.name}")
        try:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                if lines:
                     f.write("\n")
                f.write("\n# --- Contexto README (Auto-añadido por script) ---\n")
                f.write(f"# Enlace simbólico al contexto global de README personal (ignorar)\n")
                f.write(f"{entry_to_add}\n")
                f.write("# -------------------------------------------------\n\n")
            print_info(f"Entrada añadida a {gitignore_path.name}.")
            modified = True # <<< NUEVO: Marcar como modificado
        except Exception as e:
            print_error(f"No se pudo escribir en {gitignore_path.name}: {e}")
            # No marcamos modificado si falla la escritura
    
    return modified # <<< NUEVO: Retornar estado de modificación


# --- Funciones Principales ---

def sync_context_from_tmp(workspace_root):
    """Busca archivos de contexto en tmp/ y los copia a la ruta externa.
    Retorna la ruta del archivo fuente si se encontró y copió, sino None.
    """
    print_info("--- Iniciando Sincronización (tmp -> externa) ---")
    tmp_dir = workspace_root / TMP_DIR_NAME
    source_file_to_delete_later = None # Variable para guardar la ruta del archivo fuente

    if not tmp_dir.is_dir():
        print_info(f"Directorio '{TMP_DIR_NAME}/' no encontrado en el workspace. Nada que sincronizar.")
        return source_file_to_delete_later # Devuelve None

    found_files = []
    for item in tmp_dir.iterdir():
        if item.is_file() and CONTEXT_FILE_PATTERN.fullmatch(item.name):
            found_files.append(item)

    if not found_files:
        print_info(f"No se encontraron archivos ({CONTEXT_FILE_PATTERN.pattern}) en '{TMP_DIR_NAME}/'.")
        return source_file_to_delete_later # Devuelve None

    source_file = found_files[0] # Tomar el primero encontrado
    if len(found_files) > 1:
        print_warn(f"Se encontraron múltiples archivos de contexto en '{TMP_DIR_NAME}/': {[f.name for f in found_files]}")
        print_warn(f"Se sincronizará solo el primero: {source_file.name}")

    target_path = EXTERNAL_TARGET_CONTEXT_PATH
    target_dir = target_path.parent

    print_info(f"Archivo fuente encontrado: {source_file}")
    print_info(f"Ruta de destino externa: {target_path}")

    try:
        # Crear directorio de destino si no existe (ya estaba, pero asegurar)
        target_dir.mkdir(parents=True, exist_ok=True)
        # Copiar archivo (preserva metadatos como fecha de modificación)
        shutil.copy2(source_file, target_path)
        print_info(f"¡Éxito! Archivo copiado a {target_path}")
        # Guardar la ruta del archivo fuente para borrarla DESPUÉS si todo va bien
        source_file_to_delete_later = source_file

        # -- YA NO SE BORRA AQUÍ --
        # try:
        #     source_file.unlink()
        #     print_info(f"Archivo fuente '{source_file.name}' eliminado de '{TMP_DIR_NAME}/'.")
        # except Exception as e_unlink:
        #     print_warn(f"No se pudo eliminar el archivo fuente '{source_file.name}' de '{TMP_DIR_NAME}/': {e_unlink}")
        # -- YA NO SE BORRA AQUÍ --

    except Exception as e:
        # Si la copia falla, no intentamos borrar el original y no devolvemos la ruta
        print_error(f"No se pudo copiar '{source_file.name}' a '{target_path}': {e}")
        source_file_to_delete_later = None # Asegurar que no se borre si la copia falló

    print_info("--- Sincronización Finalizada ---")
    return source_file_to_delete_later # Devuelve la ruta del fuente o None

def setup_project_context_link(git_root):
    """Configura el enlace simbólico desde la ruta maestra al proyecto.
    Retorna una tupla: (setup_ok: bool, commit_needed: bool)
      - setup_ok: True si el proceso general fue exitoso (o no se requirió acción),
                  False si ocurrió un error crítico.
      - commit_needed: True si se creó el enlace o se modificó .gitignore.
    """
    print_info("--- Iniciando Configuración de Enlace Simbólico (externa -> proyecto) ---")
    setup_ok = False # Estado inicial
    commit_needed = False # <<< NUEVO: Flag para commit

    master_context_path = get_master_context_path_from_config()
    if not master_context_path:
        print_error("No se pudo determinar la ruta maestra del contexto. Abortando setup.", None)
        return False, commit_needed # Salir si no se pudo encontrar el archivo maestro

    target_symlink_path_abs = (git_root / RELATIVE_SYMLINK_PATH).resolve() # Resolve para normalizar
    target_symlink_path_rel = RELATIVE_SYMLINK_PATH # Usar relativa para gitignore
    target_dir = target_symlink_path_abs.parent
    gitignore_path = git_root / ".gitignore"

    print_info(f"Ruta maestra a enlazar: {master_context_path}")
    print_info(f"Ruta destino del enlace (relativa): {target_symlink_path_rel}")

    # 1. Verificar si el enlace ya existe y apunta correctamente
    link_already_ok = False
    if target_symlink_path_abs.exists():
        if target_symlink_path_abs.is_symlink():
            try:
                current_target = Path(os.readlink(target_symlink_path_abs)).resolve()
                expected_target = master_context_path.resolve()
                if current_target == expected_target:
                    print_info(f"El enlace simbólico ya existe y apunta correctamente a: {master_context_path}")
                    link_already_ok = True
                else:
                    print_warn(f"El enlace simbólico existe en '{target_symlink_path_rel}' pero apunta a '{current_target}' en lugar de '{expected_target}'.")
                    print_warn("Puedes borrarlo manualmente y re-ejecutar si quieres corregirlo.")
                    link_already_ok = True # Consideramos OK para no intentar crearlo, pero se dio warning.
            except Exception as e:
                 print_warn(f"No se pudo verificar el destino del enlace existente '{target_symlink_path_rel}': {e}")
                 link_already_ok = True # No podemos verificar, asumimos OK para no romper nada.
        else:
            print_warn(f"Ya existe un archivo o directorio (no un enlace) en: {target_symlink_path_rel}. No se creará el enlace.")
            link_already_ok = True # Ya existe algo, no sobreescribimos

    # 2. Crear directorio y enlace si no existe o no es válido
    link_created_now = False
    if not link_already_ok:
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            print_info(f"Creando enlace simbólico: {target_symlink_path_rel} -> {master_context_path}")
            os.symlink(master_context_path, target_symlink_path_abs, target_is_directory=False)
            print_info("Enlace simbólico creado.")
            link_created_now = True
            commit_needed = True # <<< NUEVO: Se creó enlace, se necesita commit
        except OSError as e:
            if os.name == 'nt' and isinstance(e, OSError) and e.winerror == 1314:
                 print_error(f"No se pudo crear el enlace simbólico. En Windows, esto puede requerir ejecutar el script como Administrador o habilitar el Modo Desarrollador.", None)
                 print_error(f"Intenta copiar el archivo manually: cp '{master_context_path}' '{target_symlink_path_abs}'", None)
            else:
                 print_error(f"No se pudo crear el enlace simbólico: {e}")
            return False, commit_needed # Error crítico
        except Exception as e:
            print_error(f"Error inesperado al crear enlace simbólico: {e}")
            return False, commit_needed # Error crítico

    # 3. Asegurar que esté en .gitignore (solo si el enlace existe o se creó ahora)
    gitignore_modified = False # <<< NUEVO: Flag para modificación de gitignore
    if link_already_ok or link_created_now:
        gitignore_entry_unix_path = str(target_symlink_path_rel).replace(os.sep, '/')
        gitignore_modified = update_gitignore(gitignore_path, gitignore_entry_unix_path) # <<< NUEVO: Capturar resultado
        if gitignore_modified:
             commit_needed = True # <<< NUEVO: Se modificó gitignore, se necesita commit
        setup_ok = True # Consideramos éxito si el enlace está o se creó y gitignore se actualizó/verificó
    else:
        # Si llegamos aquí, no existía y no se pudo crear
        setup_ok = False

    print_info("--- Configuración de Enlace Finalizada ---")
    return setup_ok, commit_needed # <<< NUEVO: Retornar ambos flags

# --- NUEVO: Banner ---
def print_banner():
    """Imprime un banner minimalista usando variables globales y separadores."""
    # Determina un ancho razonable (ej. 80 caracteres o basado en el contenido)
    # O simplemente dejamos que las líneas ocupen lo que necesiten
    separator = "-" * 60 # Línea separadora simple

    print(separator)
    print(f"{APP_NAME} - v{APP_VERSION}")
    print(f"Por: {APP_AUTHOR}")
    print(separator)
    print("") # Línea extra para separación
# -------------------

# --- NUEVA FUNCION: Preparar tmp para edición ---
def prepare_tmp_for_edit(workspace_root):
    """Copia el archivo maestro de contexto a tmp/ para su edición."""
    print_info(f"--- Iniciando Preparación de '{TMP_DIR_NAME}/' para Edición --- ")
    
    master_context_path = get_master_context_path_from_config()
    if not master_context_path:
        print_error("No se pudo determinar la ruta maestra del contexto. No se puede copiar a tmp.", exit_code=None)
        return # No salir del script, solo de esta función

    if not master_context_path.is_file():
        print_error(f"El archivo maestro '{master_context_path}' no existe. No se puede copiar a tmp.", exit_code=None)
        print_error("Por favor, créalo primero (ej. usando este script sin flags o manualmente).", exit_code=None)
        return
        
    tmp_dir = workspace_root / TMP_DIR_NAME
    tmp_target_path = tmp_dir / TMP_EDIT_TARGET_FILENAME

    try:
        # Asegurar que el directorio tmp exista
        tmp_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar el archivo maestro a tmp
        shutil.copy2(master_context_path, tmp_target_path)
        print_info(f"Archivo maestro copiado a: {tmp_target_path}")
        print_info(f"Ahora puedes editar '{tmp_target_path.relative_to(workspace_root)}' y luego ejecutar '{sys.argv[0]} --user' para sincronizar.")
        
    except Exception as e:
        print_error(f"No se pudo copiar el archivo maestro '{master_context_path}' a '{tmp_target_path}': {e}")

    print_info("--- Preparación para Edición Finalizada ---")
# ------------------------------------------------

# --- NUEVA FUNCION: Inicializar desde Plantilla ---
def initialize_user_context_from_template(workspace_root):
    """Copia una plantilla desde config/ al archivo maestro de contexto del usuario."""
    print_info("--- Iniciando Inicialización de Contexto de Usuario desde Plantilla ---")
    
    target_master_path = get_master_context_path_from_config()
    if not target_master_path:
        print_error("No se pudo determinar la ruta maestra del contexto. Abortando inicialización.", exit_code=None)
        return
        
    source_template_path = workspace_root / INIT_TEMPLATE_PATH_REL
    
    print_info(f"Buscando plantilla en: {source_template_path}")
    if not source_template_path.is_file():
        print_error(f"No se encontró la plantilla de inicialización en '{source_template_path}'.", exit_code=None)
        print_error(f"Por favor, asegúrate de que exista el archivo '{INIT_TEMPLATE_PATH_REL}' en tu workspace.", exit_code=None)
        return

    print_info(f"Archivo maestro de destino: {target_master_path}")
    
    proceed_with_copy = False
    if not target_master_path.is_file():
        print_info("El archivo maestro de destino no existe. Se procederá a crearlo desde la plantilla.")
        proceed_with_copy = True
    else:
        print_warn(f"¡Atención! El archivo maestro de destino '{target_master_path}' ya existe.")
        confirm = input("¿Deseas sobrescribirlo con la plantilla? (s/N): ")
        if confirm.lower() == 's':
            proceed_with_copy = True
            print_info("Confirmado. Se sobrescribirá el archivo existente.")
        else:
            print_info("Operación cancelada por el usuario. No se sobrescribirá el archivo.")

    if proceed_with_copy:
        try:
            # Asegurar que el directorio destino exista (ya lo hace get_master..., pero doble check)
            target_master_path.parent.mkdir(parents=True, exist_ok=True)
            # Copiar la plantilla al destino
            shutil.copy2(source_template_path, target_master_path)
            print_info(f"¡Éxito! Contexto de usuario inicializado/actualizado en '{target_master_path}' desde la plantilla.")
        except Exception as e:
            print_error(f"No se pudo copiar la plantilla '{source_template_path}' a '{target_master_path}': {e}")

    print_info("--- Inicialización desde Plantilla Finalizada ---")
# ---------------------------------------------------

# --- Ejecución Principal ---
if __name__ == "__main__":
    # --- Configuración de Argumentos (Actualizado) ---
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{APP_VERSION} - {APP_AUTHOR}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplos:\n"
               "  ./context-sync.py --user       (Sincroniza tmp->externa, configura enlace y commitea)\n"
               "  ./context-sync.py --user-edit  (Copia maestro a tmp para editar)\n"
               "  ./context-sync.py --user-init  (Inicializa maestro desde plantilla config/)"
    )
    # Argumento de versión (manejado automáticamente por argparse)
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {APP_VERSION}', # Muestra el nombre del script y la versión
        help="Muestra la versión del script y sale."
    )
    # Grupo para acciones mutuamente exclusivas (opcional pero bueno)
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '--user',
        action='store_true',
        help='Sincroniza tmp->externa, configura enlace en proyecto y hace commit si es necesario.'
    )
    action_group.add_argument(
        '--user-edit',
        action='store_true',
        help=f'Copia el contexto maestro a {TMP_DIR_NAME}/{TMP_EDIT_TARGET_FILENAME} para facilitar la edición.'
    )
    action_group.add_argument(
        '--user-init',
        action='store_true',
        help=f'Inicializa/sobrescribe el contexto maestro usando la plantilla {INIT_TEMPLATE_PATH_REL}.'
    )
    
    args = parser.parse_args()
    # ---------------------------------------

    print_banner()

    # --- Condicionar Ejecución (Actualizado) --- 
    workspace_path_main = Path.cwd()
    git_root_path_main = get_git_root(workspace_path_main) if is_git_repo(workspace_path_main) else None
    
    if args.user_edit:
        print_info("Ejecutando en modo --user-edit...")
        prepare_tmp_for_edit(workspace_path_main)

    elif args.user_init:
        print_info("Ejecutando en modo --user-init...")
        initialize_user_context_from_template(workspace_path_main)
        
    elif args.user:
        print_info("Ejecutando en modo --user...")
        current_dir = workspace_path_main 
        git_root_path = git_root_path_main
        is_valid_repo = git_root_path is not None

        if is_valid_repo:
             print_info(f"Detectado repositorio Git en: {git_root_path}")
        else:
            if not is_git_repo(current_dir):
                 print_warn("El directorio actual no parece ser un repositorio Git. La función de 'setup' no se ejecutará.")

        synced_source_file_path = sync_context_from_tmp(workspace_path_main)
        print("") 
        setup_step_succeeded = False
        commit_is_needed = False 
        if is_valid_repo:
            setup_step_succeeded, commit_is_needed = setup_project_context_link(git_root_path)
        else:
            print_info("Omitiendo configuración de enlace (no estamos en un repo Git válido).")
        
        if is_valid_repo and commit_is_needed:
            print_info("--- Realizando Commit Automático ---")
            gitignore_rel_path = Path(".gitignore").relative_to(git_root_path) if git_root_path == Path.cwd() else Path(".gitignore") 
            symlink_rel_path = RELATIVE_SYMLINK_PATH.relative_to(git_root_path) if git_root_path == Path.cwd() else RELATIVE_SYMLINK_PATH
            files_to_check = [str(gitignore_rel_path), str(symlink_rel_path)]
            print_info(f"Verificando estado de: {files_to_check}")
            stdout, stderr, retcode = run_command(['git', 'status', '--porcelain'] + files_to_check, cwd=git_root_path)
            if retcode == 0 and stdout:
                print_info("Cambios detectados por Git. Procediendo con add y commit...")
                _, stderr_add, retcode_add = run_command(['git', 'add'] + files_to_check, cwd=git_root_path)
                if retcode_add == 0:
                    print_info(f"Archivos añadidos al stage: {files_to_check}")
                    commit_msg = "chore: Configure README context link and/or gitignore [skip ci]"
                    _, stderr_commit, retcode_commit = run_command(['git', 'commit', '-m', commit_msg], cwd=git_root_path)
                    if retcode_commit == 0:
                        print_info(f"Commit realizado exitosamente: '{commit_msg}'")
                    else:
                        print_error(f"Falló el commit. Stderr: {stderr_commit}", None) 
                else:
                     print_error(f"Falló 'git add'. Stderr: {stderr_add}", None)
            elif retcode == 0 and not stdout:
                 print_info("No se detectaron cambios por Git en los archivos relevantes. No se requiere commit.")
            else:
                 print_error(f"Falló 'git status --porcelain'. Stderr: {stderr}", None)
        elif is_valid_repo and not commit_is_needed:
            print_info("No se realizaron cambios que requieran commit.")
        
        if synced_source_file_path:
            should_delete = not is_valid_repo or (is_valid_repo and setup_step_succeeded)
            if should_delete:
                print_info(f"--- Limpieza de {TMP_DIR_NAME} --- ")
                try:
                    synced_source_file_path.unlink()
                    print_info(f"Archivo fuente '{synced_source_file_path.name}' eliminado de '{TMP_DIR_NAME}/' exitosamente.")
                except Exception as e_unlink:
                    print_warn(f"No se pudo eliminar el archivo fuente '{synced_source_file_path.name}' de '{TMP_DIR_NAME}/': {e_unlink}")
            else:
                print_warn(f"El archivo fuente '{synced_source_file_path.name}' NO se eliminó de '{TMP_DIR_NAME}/' porque la configuración del enlace simbólico no se completó exitosamente.")
        print_info("Script completado para --user.")
    
    else: # Si no se pasó ninguna acción
        print("Modo de operación no especificado.")
        parser.print_help() 
        sys.exit(0) 