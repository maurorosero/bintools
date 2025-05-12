#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-11 14:20:08
# Version: 0.1.0
#
# wfwdevs.py - Description placeholder
# -----------------------------------------------------------------------------
#
# -*- coding: utf-8 -*-

# wfwdevs.py - Script para gestionar flujos de trabajo de desarrollo Git.

import argparse
import subprocess
from pathlib import Path
import sys # Para sys.exit
import re
import os

"""
wfwdevs.py - Script para gestionar flujos de trabajo de desarrollo Git.

Este script proporciona herramientas para automatizar tareas comunes del flujo de
trabajo de desarrollo basado en Git, como la creación estandarizada de ramas
de trabajo (features, fixes, hotfixes) asegurando la sincronización
adecuada con las ramas principales (develop, main).
"""

# --- Opcional: Colorama y Questionary ---
try:
    from colorama import Fore, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
    colorama_init(autoreset=True)
except ImportError:
    COLORAMA_AVAILABLE = False
    class DummyColorama: # type: ignore
        def __getattr__(self, name): return ""
    Fore = Style = DummyColorama() # type: ignore

try:
    import questionary
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
# ------------------------------------------

# --- Definiciones de Ramas y Tipos ---
DEVELOP_BRANCH = "develop"
MAIN_BRANCH = "main" # O tu rama principal de producción/release
REMOTE_DEFAULT = "origin"

BRANCH_TYPES_CONFIG = {
    "feature": {"description": "Nuevas características"},
    "fix": {"description": "Correcciones de errores"},
    "docs": {"description": "Documentación"},
    "style": {"description": "Cambios de formato, sin impacto en código"},
    "refactor": {"description": "Refactorización de código sin cambiar comportamiento"},
    "perf": {"description": "Mejoras de rendimiento"},
    "test": {"description": "Añadir o mejorar tests"},
    "chore": {"description": "Mantenimiento, tareas de build, etc."},
    "hotfix": {"description": "Correcciones urgentes en producción"},
}
# ---------------------------------------

def run_git_command(command: list[str], cwd: Path = Path("."), check: bool = True, suppress_output: bool = False) -> tuple[bool, str, str]:
    """
    Ejecuta un comando de Git y devuelve el éxito, stdout y stderr.
    """
    try:
        process = subprocess.run(
            command,
            cwd=str(cwd),
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        # La impresión de salida se manejará por la función que llama, si es necesario.
        return True, process.stdout.strip(), process.stderr.strip()
    except subprocess.CalledProcessError as e:
        # El error se propaga y la función que llama decide qué imprimir.
        return False, e.stdout.strip(), e.stderr.strip()
    except Exception as e_gen:
        return False, "", str(e_gen)

def clean_branch_name_suffix(suffix: str) -> str:
    """Limpia el sufijo del nombre de la rama."""
    s = suffix.lower()
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'[^a-z0-9\-_/]', '', s) # Permitir alfanuméricos, guiones, underscores, y slashes
    s = re.sub(r'[-_]{2,}', '-', s)      # Reemplazar múltiples delimitadores con uno solo
    s = s.strip('-_/')                  # Quitar delimitadores al principio o final
    return s

def check_if_main_is_ahead(repo_path: Path, remote_name: str, main_branch_name: str, develop_branch_name: str) -> bool:
    """Verifica si la rama main remota tiene commits que develop (local) no tiene."""
    print(f"{Fore.CYAN}Verificando si '{remote_name}/{main_branch_name}' tiene cambios para '{develop_branch_name}'...{Style.RESET_ALL}")
    
    # Asegurar que las referencias remotas están actualizadas para una comparación precisa
    run_git_command(["git", "fetch", remote_name, main_branch_name], cwd=repo_path, suppress_output=True)
    # No es estrictamente necesario fetchear develop aquí si vamos a compararlo con su estado local actual.
    # run_git_command(["git", "fetch", remote_name, develop_branch_name], cwd=repo_path, suppress_output=True)

    # Contar commits en remote/main_branch_name que no están en develop_branch_name (local)
    # Este comando lista los commits que son ancestros de remote/main y no son ancestros de develop.
    success, out, _ = run_git_command(
        ["git", "rev-list", "--count", f"{develop_branch_name}..{remote_name}/{main_branch_name}"],
        cwd=repo_path,
        check=True, # Este comando debería funcionar si las ramas existen.
        suppress_output=True
    )
    
    if success and out.strip().isdigit():
        commits_ahead = int(out.strip())
        if commits_ahead > 0:
            print(f"{Fore.YELLOW}'{remote_name}/{main_branch_name}' tiene {commits_ahead} commit(s) que '{develop_branch_name}' (local) no posee. Se requiere merge.{Style.RESET_ALL}")
            return True
    
    print(f"{Fore.GREEN}'{develop_branch_name}' (local) ya está actualizada con (o por delante de) '{remote_name}/{main_branch_name}'.{Style.RESET_ALL}")
    return False

def sync_target_from_source_branch(
    target_branch: str,
    source_branch: str,
    remote_name: str,
    repo_path: Path,
    commit_msg_prefix: str = "[WFWDEVS]"
) -> bool:
    """
    Sincroniza la target_branch con la source_branch del remoto.
    Incluye checkout, pull, merge (si es necesario) y push de la target_branch.
    Devuelve True si todo es exitoso, False si hay algún fallo.
    """
    print(f"\n{Fore.BLUE}--- Iniciando sincronización de '{target_branch}' desde '{remote_name}/{source_branch}' ---{Style.RESET_ALL}")

    # Guardar rama original para poder volver
    current_branch_success, original_branch_on_sync_start, _ = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path, suppress_output=True)

    # 1. Checkout target_branch (si no estamos ya en ella)
    if not current_branch_success or original_branch_on_sync_start != target_branch:
        print(f"{Fore.CYAN}Cambiando a '{target_branch}'...{Style.RESET_ALL}")
        success_co_target, _, err_co_target = run_git_command(["git", "checkout", target_branch], cwd=repo_path)
        if not success_co_target:
            print(f"{Fore.RED}Error al cambiar a '{target_branch}': {err_co_target}{Style.RESET_ALL}")
            return False
    else:
        print(f"{Fore.CYAN}Ya se encuentra en la rama '{target_branch}'.{Style.RESET_ALL}")

    # 2. Pull target_branch (actualizar desde su propio remoto)
    print(f"{Fore.CYAN}Actualizando '{target_branch}' desde '{remote_name}/{target_branch}'...{Style.RESET_ALL}")
    success_pull_target, out_pull_target, err_pull_target = run_git_command(["git", "pull", remote_name, target_branch], cwd=repo_path)
    if not success_pull_target:
        print(f"{Fore.RED}Error al actualizar '{target_branch}' desde el remoto: {err_pull_target}{Style.RESET_ALL}")
        if QUESTIONARY_AVAILABLE:
            if not questionary.confirm(f"Falló 'git pull {remote_name} {target_branch}'. ¿Continuar con el merge de '{source_branch}' de todas formas?", default=False).ask():
                if current_branch_success and original_branch_on_sync_start != target_branch : run_git_command(["git", "checkout", original_branch_on_sync_start], cwd=repo_path, suppress_output=True)
                return False
        else: # No interactivo, asumir que no se debe continuar si el pull falla.
            print(f"{Fore.YELLOW}Operación abortada debido a fallo en 'git pull'.{Style.RESET_ALL}")
            if current_branch_success and original_branch_on_sync_start != target_branch : run_git_command(["git", "checkout", original_branch_on_sync_start], cwd=repo_path, suppress_output=True)
            return False
    elif "Already up to date" not in out_pull_target and "Ya está actualizado" not in out_pull_target and out_pull_target:
        print(out_pull_target) # Mostrar salida del pull si hubo cambios

    # 3. Verificar si source_branch (main) está por delante y necesita ser mergeada en target_branch (develop)
    should_merge_source = check_if_main_is_ahead(repo_path, remote_name, source_branch, target_branch)

    if should_merge_source:
        commit_message = f"{commit_msg_prefix} Auto-sync: Merge {remote_name}/{source_branch} into {target_branch}"
        print(f"{Fore.CYAN}Fusionando '{remote_name}/{source_branch}' en '{target_branch}'...{Style.RESET_ALL}")
        merge_cmd = ["git", "merge", f"{remote_name}/{source_branch}", "--no-ff", "--no-edit", "-m", commit_message]
        success_merge, out_merge, err_merge = run_git_command(merge_cmd, cwd=repo_path, check=False) # check=False para manejar conflictos

        if not success_merge:
            if "conflict" in out_merge.lower() or "conflict" in err_merge.lower():
                print(f"{Fore.RED}¡CONFLICTO! Se encontraron conflictos al fusionar '{source_branch}' en '{target_branch}'.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Por favor, resuelva los conflictos en '{target_branch}' manualmente.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Error al fusionar '{source_branch}' en '{target_branch}'. Detalles: {err_merge or out_merge}{Style.RESET_ALL}")
            if current_branch_success and original_branch_on_sync_start != target_branch : run_git_command(["git", "checkout", original_branch_on_sync_start], cwd=repo_path, suppress_output=True)
            return False

        # "Already up to date" no debería ocurrir aquí si should_merge_source fue True y rev-list funcionó bien.
        # Pero si el merge no hizo nada (ej. main fue mergeado y luego revertido en develop de alguna forma), out_merge podría decirlo.
        if "Already up to date." in out_merge or "Already up-to-date." in out_merge :
             print(f"{Fore.GREEN}'{target_branch}' ya estaba actualizada con '{remote_name}/{source_branch}'. (Mensaje de merge).{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Merge de '{source_branch}' en '{target_branch}' completado.{Style.RESET_ALL}")
            if out_merge: print(out_merge) # Mostrar salida del merge si la hubo
    # else: No se necesita merge, check_if_main_is_ahead ya imprimió el mensaje.

    # 4. Push target_branch
    # Solo hacer push si hubo un merge exitoso o si el pull inicial de target_branch tuvo cambios.
    # O, más simple, siempre intentar push si llegamos aquí sin errores, Git dirá si no hay nada que pushear.
    print(f"{Fore.CYAN}Empujando '{target_branch}' a '{remote_name}'...{Style.RESET_ALL}")
    success_push, out_push, err_push = run_git_command(["git", "push", remote_name, target_branch], cwd=repo_path)
    if not success_push:
        print(f"{Fore.RED}Error al empujar '{target_branch}': {err_push}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}El merge (si ocurrió) se completó localmente, pero el push falló. Intenta el push manual.{Style.RESET_ALL}")
        return False # Push falló. El usuario está en target_branch para arreglarlo.
    
    if "Everything up-to-date" in out_push or "Todo actualizado" in out_push:
        print(f"{Fore.GREEN}'{target_branch}' en el remoto ya estaba actualizada.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Push de '{target_branch}' completado.{Style.RESET_ALL}")


    print(f"{Fore.GREEN}Sincronización de '{target_branch}' desde '{source_branch}' finalizada.{Style.RESET_ALL}")
    
    # Volver a la rama original ANTES de la sincronización, si es diferente de target_branch y el proceso fue exitoso
    if current_branch_success and original_branch_on_sync_start != target_branch:
        print(f"\n{Fore.CYAN}Volviendo a la rama original '{original_branch_on_sync_start}'...{Style.RESET_ALL}")
        run_git_command(["git", "checkout", original_branch_on_sync_start], cwd=repo_path, suppress_output=True)
    return True


def handle_new_task(args: argparse.Namespace):
    """Manejador para --task new"""
    print(f"{Fore.MAGENTA}--- Iniciando Nueva Tarea de Desarrollo ---{Style.RESET_ALL}")
    
    repo_path = args.path.resolve()
    if not (repo_path / ".git").is_dir() and not (repo_path / ".git").is_file(): # .git puede ser un archivo en worktrees
        print(f"{Fore.RED}Error: La ruta '{repo_path}' no parece ser un repositorio Git válido.{Style.RESET_ALL}")
        sys.exit(1)

    branch_type = args.type.lower()
    branch_name_suffix_raw = args.name
    branch_name_suffix = clean_branch_name_suffix(branch_name_suffix_raw)

    if not branch_name_suffix:
        print(f"{Fore.RED}Error: El nombre de la rama '{branch_name_suffix_raw}' resultó en un sufijo vacío o inválido tras la limpieza.{Style.RESET_ALL}")
        sys.exit(1)

    if branch_type not in BRANCH_TYPES_CONFIG:
        print(f"{Fore.RED}Error: Tipo de rama '{branch_type}' no es válido. Tipos permitidos: {', '.join(BRANCH_TYPES_CONFIG.keys())}{Style.RESET_ALL}")
        sys.exit(1)
        
    full_new_branch_name = f"{branch_type}/{branch_name_suffix}"
    print(f"Nombre completo de la nueva rama: {Fore.YELLOW}{full_new_branch_name}{Style.RESET_ALL}")

    # Guardar rama actual al inicio del script para poder volver al final si es necesario
    script_initial_branch_success, script_initial_branch, _ = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path, suppress_output=True)

    # --- Sincronización de develop desde main (si no es hotfix) ---
    base_for_new_task = DEVELOP_BRANCH
    if branch_type == "hotfix":
        base_for_new_task = MAIN_BRANCH
        print(f"\n{Fore.CYAN}Preparando para crear hotfix desde '{MAIN_BRANCH}'. No se sincronizará '{DEVELOP_BRANCH}' con '{MAIN_BRANCH}' en este paso.{Style.RESET_ALL}")
    else: # Para feature, fix, etc.
        print(f"\n{Fore.BLUE}Paso 1: Asegurar que la rama base de desarrollo '{DEVELOP_BRANCH}' esté sincronizada con '{MAIN_BRANCH}'{Style.RESET_ALL}")
        if not sync_target_from_source_branch(
            target_branch=DEVELOP_BRANCH,
            source_branch=MAIN_BRANCH,
            remote_name=args.remote,
            repo_path=repo_path,
            commit_msg_prefix="[WFWDEVS]"
        ):
            print(f"\n{Fore.RED}Fallo Crítico: No se pudo sincronizar '{DEVELOP_BRANCH}' desde '{MAIN_BRANCH}'.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Por favor, revisa los mensajes de error anteriores y resuelve los problemas antes de crear una nueva tarea.{Style.RESET_ALL}")
            if script_initial_branch_success : run_git_command(["git", "checkout", script_initial_branch], cwd=repo_path, suppress_output=True) # Intentar volver a la rama original
            sys.exit(1)
        # sync_target_from_source_branch debería dejar develop como la rama activa o volver a la original.
        # Nos aseguraremos de estar en develop (o la base_for_new_task) antes de crear la nueva rama.
        print(f"{Fore.GREEN}Rama '{DEVELOP_BRANCH}' sincronizada y/o verificada con '{MAIN_BRANCH}' exitosamente.{Style.RESET_ALL}")


    # --- Creación de la nueva rama de trabajo ---
    print(f"\n{Fore.BLUE}Paso 2: Creación de la nueva rama '{full_new_branch_name}' desde '{base_for_new_task}'{Style.RESET_ALL}")

    # Asegurarse de estar en la base_for_new_task ANTES de crear la nueva rama
    current_branch_before_new_task_success, current_branch_name_before_new_task, _ = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path, suppress_output=True)
    if not current_branch_before_new_task_success or current_branch_name_before_new_task != base_for_new_task:
        print(f"{Fore.CYAN}Cambiando a la rama base '{base_for_new_task}' para crear la rama de trabajo...{Style.RESET_ALL}")
        success_co_base, _, err_co_base = run_git_command(["git", "checkout", base_for_new_task], cwd=repo_path)
        if not success_co_base:
            print(f"{Fore.RED}Error crítico al cambiar a '{base_for_new_task}': {err_co_base}{Style.RESET_ALL}")
            if script_initial_branch_success : run_git_command(["git", "checkout", script_initial_branch], cwd=repo_path, suppress_output=True)
            sys.exit(1)
    
    # Pull final en la rama base (especialmente importante para hotfix que no pasó por sync_target_from_source_branch)
    print(f"{Fore.CYAN}Asegurando la última versión de '{base_for_new_task}' desde el remoto ('{args.remote}')...{Style.RESET_ALL}")
    success_pull_base, out_pull_base, err_pull_base = run_git_command(["git", "pull", args.remote, base_for_new_task], cwd=repo_path)
    if not success_pull_base:
        print(f"{Fore.RED}Error al actualizar '{base_for_new_task}' local desde el remoto: {err_pull_base}{Style.RESET_ALL}")
        # Preguntar si continuar es una opción, o abortar.
        if QUESTIONARY_AVAILABLE:
            if not questionary.confirm(f"No se pudo hacer 'git pull' en '{base_for_new_task}'. ¿Continuar creando la rama de todas formas?", default=False).ask():
                if script_initial_branch_success : run_git_command(["git", "checkout", script_initial_branch], cwd=repo_path, suppress_output=True)
                sys.exit(1)
        else:
            print(f"{Fore.YELLOW}Continuando a pesar del fallo en 'git pull' de '{base_for_new_task}'.{Style.RESET_ALL}")
            
    elif "Already up to date" not in out_pull_base and "Ya está actualizado" not in out_pull_base and out_pull_base:
        print(out_pull_base) # Mostrar salida si hubo cambios


    # Crear la nueva rama
    print(f"{Fore.CYAN}Intentando crear la rama '{full_new_branch_name}'...{Style.RESET_ALL}")
    success_create, out_create, err_create = run_git_command(["git", "checkout", "-b", full_new_branch_name], cwd=repo_path)
    if not success_create:
        if "already exists" in err_create.lower() or "ya existe" in err_create.lower():
            print(f"{Fore.YELLOW}Advertencia: La rama '{full_new_branch_name}' ya existe.{Style.RESET_ALL}")
            perform_checkout_existing = True
            if QUESTIONARY_AVAILABLE:
                perform_checkout_existing = questionary.confirm(f"¿Desea cambiar a la rama existente '{full_new_branch_name}'?", default=True).ask()
            
            if perform_checkout_existing:
                success_co_exist, _, err_co_exist = run_git_command(["git", "checkout", full_new_branch_name], cwd=repo_path)
                if not success_co_exist:
                     print(f"{Fore.RED}Error al intentar cambiar a la rama existente '{full_new_branch_name}': {err_co_exist}{Style.RESET_ALL}")
                     if script_initial_branch_success : run_git_command(["git", "checkout", script_initial_branch], cwd=repo_path, suppress_output=True)
                     sys.exit(1)
                print(f"{Fore.GREEN}Cambiado exitosamente a la rama existente '{full_new_branch_name}'.{Style.RESET_ALL}")
            else: # Usuario no quiso cambiar
                print(f"{Fore.YELLOW}Operación cancelada por el usuario. No se cambió de rama.{Style.RESET_ALL}")
                if script_initial_branch_success and script_initial_branch != full_new_branch_name : # Solo si no es la misma y se pudo obtener
                    run_git_command(["git", "checkout", script_initial_branch], cwd=repo_path, suppress_output=True)
                sys.exit(0)
        else: # Otro error al crear la rama
            print(f"{Fore.RED}Error crítico al crear la rama '{full_new_branch_name}': {err_create or out_create}{Style.RESET_ALL}")
            if script_initial_branch_success : run_git_command(["git", "checkout", script_initial_branch], cwd=repo_path, suppress_output=True)
            sys.exit(1)
    else: # Creación exitosa
        print(f"{Fore.GREEN}Rama '{full_new_branch_name}' creada y seleccionada exitosamente.{Style.RESET_ALL}")

    # Push opcional de la nueva rama
    if not args.no_push: # Hacer push si --no-push NO está presente
        print(f"\n{Fore.BLUE}Paso 3: Empujando nueva rama '{full_new_branch_name}' al remoto '{args.remote}'{Style.RESET_ALL}")
        success_push_new, _, err_push_new = run_git_command(["git", "push", "-u", args.remote, full_new_branch_name], cwd=repo_path)
        if not success_push_new:
            print(f"{Fore.RED}Error al empujar la rama '{full_new_branch_name}' al remoto: {err_push_new}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}La rama se creó localmente. Puede intentar el push manual: git push -u {args.remote} {full_new_branch_name}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Rama '{full_new_branch_name}' empujada al remoto y upstream configurado exitosamente.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}La nueva rama '{full_new_branch_name}' no se ha empujado al remoto (opción --no-push).{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Cuando esté listo, puede empujarla con: git push -u {args.remote} {full_new_branch_name}{Style.RESET_ALL}")

    print(f"\n{Fore.MAGENTA}--- ¡Listo! Ya puede empezar a trabajar en la rama '{full_new_branch_name}' ---{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="wfwdevs.py - Herramienta para automatizar flujos de trabajo de desarrollo Git.",
        formatter_class=argparse.RawTextHelpFormatter # Para mejor visualización de choices en help
    )
    parser.add_argument('-p', '--path', type=Path, default=Path("."),
                        help='Ruta al directorio raíz del repositorio Git (default: directorio actual)')
    parser.add_argument('--remote', default=REMOTE_DEFAULT,
                        help=f'Nombre del remoto Git (default: {REMOTE_DEFAULT})')

    # Grupo de tareas principales
    task_subparsers = parser.add_subparsers(dest='task', title='Tareas disponibles',
                                            description='Seleccione una tarea a realizar.',
                                            required=True, metavar='TASK')

    # --- Subcomando para --task new ---
    new_task_parser = task_subparsers.add_parser(
        'new',
        help='Inicia una nueva tarea de desarrollo (crea una nueva rama de trabajo).',
        description='Crea una nueva rama de trabajo (feature, fix, etc.) asegurando que \'develop\' (o la rama base) esté sincronizada con \'main\'.'
    )
    new_task_parser.add_argument('--type', required=True, choices=list(BRANCH_TYPES_CONFIG.keys()),
                                 help='Tipo de rama/tarea a crear (ej: feature, fix, hotfix).')
    new_task_parser.add_argument('--name', required=True,
                                 help='Nombre descriptivo para la tarea/rama (sin el prefijo, ej: mi-nueva-interfaz).')
    new_task_parser.add_argument('--no-push', action='store_false', dest='push', default=True,
                                 help='Evita empujar la nueva rama creada al repositorio remoto automáticamente.')
    new_task_parser.set_defaults(func=handle_new_task)
    # --- Fin Subcomando new ---
    
    # Aquí se podrían añadir más subparsers para otras tareas en el futuro:
    # ej. integrate_task_parser = task_subparsers.add_parser('integrate', help='Integra la rama actual en develop/main.')
    # ej. cleanup_task_parser = task_subparsers.add_parser('cleanup', help='Limpia ramas fusionadas.')

    args = parser.parse_args()

    # Validar que la ruta del repositorio (path) exista y sea un directorio
    if not args.path.is_dir():
        print(f"{Fore.RED}Error: La ruta especificada para el repositorio '{args.path}' no es un directorio válido.{Style.RESET_ALL}")
        sys.exit(1)
        
    # El script espera ser ejecutado desde cualquier lugar, y las operaciones Git
    # se realizan en `args.path` usando el argumento `cwd` de `run_git_command`.
    # No es necesario cambiar el directorio global del script con os.chdir().

    if hasattr(args, 'func'):
        args.func(args) # Llama a la función manejadora asociada con el subcomando (ej. handle_new_task)
    else:
        # Esto no debería ocurrir si 'required=True' está en add_subparsers y no hay un comando por defecto.
        parser.print_help() 
        sys.exit(1)

if __name__ == "__main__":
    # Pequeño banner o mensaje de inicio (opcional)
    # if COLORAMA_AVAILABLE:
    #     if os.name == 'posix': print("c", end="") # Limpia la terminal en POSIX
    #     elif os.name == 'nt': os.system('cls')      # Limpia la terminal en Windows
    # print(f"{Fore.CYAN}--- wfwdevs.py - Asistente de Flujo de Trabajo Git ---{Style.RESET_ALL}\n")
    
    main() 