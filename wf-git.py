#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-04-30 09:16:03
# Version: 0.1.0
#
# wf-git.py - CLI tool to assist with the Git workflow defined in docs/guia-git-workflow.md
# -----------------------------------------------------------------------------
#
# Description: CLI tool to assist with the Git workflow defined in docs/guia-git-workflow.md

import argparse
import subprocess
import sys
import os
import re

# --- Configuration ---
# (Could be loaded from a .wf-git-config file later)
MAIN_BRANCH = "main"
DEVELOP_BRANCH = "develop"
STAGING_BRANCH = "staging"
REMOTE_NAME = "origin"
COMMIT_TAGS = [
    "[FEATURE]", "[IMPROVE]", "[FIX]", "[DOCS]", "[STYLE]",
    "[REFACTOR]", "[PERF]", "[TEST]", "[BUILD]", "[CI]", "[CHORE]"
]
# --- End Configuration ---

# --- Helper Functions ---

def run_git_command(command, check=True, capture_output=False, suppress_output=False, cwd=None):
    """Executes a Git command using subprocess."""
    try:
        env = os.environ.copy()
        # Ensure Git uses English for predictable output parsing if needed
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'

        kwargs = {
            'check': check,
            'shell': False,
            'text': True,
            'cwd': cwd,
            'env': env
        }
        if capture_output:
            kwargs['capture_output'] = True
        elif suppress_output:
            kwargs['stdout'] = subprocess.DEVNULL
            kwargs['stderr'] = subprocess.DEVNULL
        else:
            # Let the command print directly to stdout/stderr
            pass

        # print(f"DEBUG: Running command: {' '.join(command)}") # Uncomment for debugging
        process = subprocess.run(command, **kwargs)
        return process
    except subprocess.CalledProcessError as e:
        print(f"\nError executing command: {' '.join(e.cmd)}", file=sys.stderr)
        if e.stderr and not suppress_output:
            print(f"Git Error Output:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'git' command not found. Is Git installed and in your PATH?", file=sys.stderr)
        sys.exit(1)

def get_current_branch():
    """Gets the current Git branch name."""
    result = run_git_command(["git", "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True)
    return result.stdout.strip()

def confirm(prompt):
    """Gets user confirmation (y/n)."""
    while True:
        response = input(f"{prompt} (s/N): ").lower().strip()
        if response == 's':
            return True
        elif response == 'n' or response == '':
            return False
        print("Respuesta inválida. Por favor, introduce 's' o 'n'.")

def sanitize_branch_name(description):
    """Cleans a description string to be used in a branch name."""
    # Convert to lowercase
    name = description.lower()
    # Replace spaces and underscores with hyphens
    name = re.sub(r'[\s_]+', '-', name)
    # Remove invalid characters (allow letters, numbers, hyphens, slashes for prefixes)
    name = re.sub(r'[^a-z0-9-/]', '', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Collapse multiple hyphens
    name = re.sub(r'-+', '-', name)
    return name

def check_staging_area():
    """Checks if there are changes staged for commit."""
    result = run_git_command(["git", "diff", "--cached", "--quiet"], check=False) # Don't exit on error
    return result.returncode != 0 # 0 means no staged changes, 1 means staged changes

def check_upstream_exists(branch):
    """Checks if the branch has a remote upstream configured."""
    result = run_git_command(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", f"{branch}@{'{u'}"],
                              check=False, capture_output=True, suppress_output=True)
    return result.returncode == 0

# --- Command Implementations ---

def init_repo(args):
    print("Initializing new repository according to the workflow...")
    remote_url = args.url_remoto

    if os.path.exists(".git"):
        if not confirm("¡Advertencia! Ya existe un repositorio Git (.git) en este directorio. Continuar podría sobreescribir la configuración existente. ¿Continuar de todos modos?"):
            print("Operation cancelled.")
            sys.exit(1)
        else:
            print("Continuing with existing .git directory...")

    run_git_command(["git", "init"])
    print("Git repository initialized.")

    repo_name = os.path.basename(os.getcwd())
    readme_content = f"# {repo_name}\n"
    gitignore_content = ".env\nnode_modules/\n__pycache__/\ndist/\n*.log\n" # Basic template

    with open("README.md", "w") as f:
        f.write(readme_content)
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("Created README.md and .gitignore.")

    run_git_command(["git", "add", "."])
    run_git_command(["git", "commit", "-m", "[BUILD] Initial project setup"])
    # Verify default branch name (Git >= 2.28 defaults to main usually)
    default_branch = get_current_branch()
    if default_branch != MAIN_BRANCH:
         print(f"Warning: Default branch created is '{default_branch}', expected '{MAIN_BRANCH}'. Adjusting...")
         run_git_command(["git", "branch", "-M", MAIN_BRANCH])
         default_branch = MAIN_BRANCH

    print(f"Initial commit created on branch '{default_branch}'.")

    run_git_command(["git", "branch", DEVELOP_BRANCH, MAIN_BRANCH])
    run_git_command(["git", "branch", STAGING_BRANCH, DEVELOP_BRANCH])
    print(f"Branches '{DEVELOP_BRANCH}' and '{STAGING_BRANCH}' created locally.")

    run_git_command(["git", "remote", "add", REMOTE_NAME, remote_url])
    print(f"Remote '{REMOTE_NAME}' added with URL: {remote_url}")
    print("Verifying remote...")
    run_git_command(["git", "remote", "-v"])
    if not confirm("¿Es correcta la URL del remoto 'origin'?"):
        print("Please fix the remote URL manually using 'git remote set-url origin <correct_url>' and then push manually.")
        sys.exit(1)

    print(f"Pushing initial branches to {REMOTE_NAME}...")
    run_git_command(["git", "push", "-u", REMOTE_NAME, MAIN_BRANCH])
    run_git_command(["git", "push", "-u", REMOTE_NAME, DEVELOP_BRANCH])
    run_git_command(["git", "push", "-u", REMOTE_NAME, STAGING_BRANCH])

    print(f"\n¡Éxito! Repositorio Git inicializado. Ramas '{MAIN_BRANCH}', '{DEVELOP_BRANCH}', '{STAGING_BRANCH}' creadas y sincronizadas con '{REMOTE_NAME}'.")
    print(f"Ya puedes empezar a trabajar creando tareas con 'wf-git start'.")

def start_task(args):
    task_type = args.type
    description = args.description
    issue_num = getattr(args, 'issue', None) # Optional issue number for fix

    print(f"Starting new {task_type} task...")

    print(f"Switching to '{DEVELOP_BRANCH}' and updating...")
    run_git_command(["git", "checkout", DEVELOP_BRANCH])
    run_git_command(["git", "pull", REMOTE_NAME, DEVELOP_BRANCH])

    sanitized_desc = sanitize_branch_name(description)
    if task_type == 'fix' and issue_num:
        branch_name = f"{task_type}/{issue_num}-{sanitized_desc}"
    else:
         branch_name = f"{task_type}/{sanitized_desc}"

    print(f"Creating new branch '{branch_name}'...")
    run_git_command(["git", "checkout", "-b", branch_name])

    print(f"\n¡Éxito! Rama '{branch_name}' creada y lista para trabajar desde '{DEVELOP_BRANCH}' actualizado.")

def commit_changes(args):
    print("Preparing commit...")

    if not check_staging_area():
        print("No hay cambios añadidos al commit (usa 'git add ...' primero).")
        sys.exit(0)

    print("Select commit tag:")
    for i, tag in enumerate(COMMIT_TAGS):
        print(f"  {i+1}: {tag}")

    while True:
        try:
            tag_choice = int(input(f"Enter number (1-{len(COMMIT_TAGS)}): "))
            if 1 <= tag_choice <= len(COMMIT_TAGS):
                selected_tag = COMMIT_TAGS[tag_choice-1]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    issue_num_str = input("Número de Issue (opcional, presiona Enter para omitir): ").strip()
    if issue_num_str and not issue_num_str.isdigit():
        print("Warning: Issue number must be numeric. Ignoring.")
        issue_num_str = ""

    description = ""
    while not description:
        description = input("Descripción corta del commit (en presente): ").strip()
        if not description:
            print("La descripción no puede estar vacía.")

    commit_msg = f"{selected_tag} "
    if issue_num_str:
        commit_msg += f"(#{issue_num_str}) "
    commit_msg += description

    print(f"\nMensaje de commit a crear:\n\"{commit_msg}\"")
    if confirm("¿Confirmar?"):
        run_git_command(["git", "commit", "-m", commit_msg])
        print("Commit created successfully.")
    else:
        print("Commit cancelado.")


def push_changes(args):
    current_branch = get_current_branch()
    print(f"Pushing changes for branch '{current_branch}'...")

    protected_branches = [MAIN_BRANCH, DEVELOP_BRANCH, STAGING_BRANCH]
    if current_branch in protected_branches:
         print(f"Error: Este comando es para ramas de tarea (feature, fix, chore). No se puede usar en '{current_branch}'.")
         sys.exit(1)

    if not check_upstream_exists(current_branch):
         print(f"Configurando seguimiento remoto para '{current_branch}'...")
         run_git_command(["git", "push", "-u", REMOTE_NAME, current_branch])
    else:
         print(f"Empujando cambios de '{current_branch}' al remoto...")
         run_git_command(["git", "push"])

    print("Push completed.")

def finish_task(args):
    current_branch = get_current_branch()
    print(f"Finishing task for branch '{current_branch}'...")

    protected_branches = [MAIN_BRANCH, DEVELOP_BRANCH, STAGING_BRANCH]
    task_prefixes = ("feature/", "fix/", "chore/")
    if current_branch in protected_branches or not current_branch.startswith(task_prefixes):
         print(f"Error: Este comando es para ramas de tarea ({'/'.join(p for p in task_prefixes)}*). No se puede usar en '{current_branch}'.")
         sys.exit(1)

    if not confirm(f"¿Estás seguro de que el Pull Request para la rama '{current_branch}' ha sido **fusionado** exitosamente en '{DEVELOP_BRANCH}'?"):
         print("Operación de limpieza cancelada.")
         sys.exit(0)

    print(f"Cambiando a '{DEVELOP_BRANCH}' y actualizando...")
    run_git_command(["git", "checkout", DEVELOP_BRANCH])
    run_git_command(["git", "pull", REMOTE_NAME, DEVELOP_BRANCH])

    print(f"Borrando rama local '{current_branch}'...")
    # Use check=False for branch deletion, as it might fail if not fully merged (though PR implies it is)
    result = run_git_command(["git", "branch", "-d", current_branch], check=False)
    if result.returncode != 0:
        print(f"Warning: No se pudo borrar la rama local '{current_branch}'. ¿Quizás no está totalmente fusionada?")
        if confirm("¿Forzar el borrado local con -D? (¡CUIDADO!)"):
             run_git_command(["git", "branch", "-D", current_branch])
             print("Rama local forzada a borrar.")
        else:
             print("Rama local no borrada.")

    if confirm(f"¿Borrar también la rama '{current_branch}' del repositorio remoto ({REMOTE_NAME})?"):
         print(f"Borrando rama remota '{current_branch}'...")
         run_git_command(["git", "push", REMOTE_NAME, "--delete", current_branch])
         print("Rama remota borrada.")

    print("\nLimpieza completada.")


def release_prepare(args):
    print(f"Preparing '{STAGING_BRANCH}' for release...")

    prompt = (f"Esto creará o **reseteará** la rama '{STAGING_BRANCH}' para que sea idéntica "
              f"al estado actual de '{DEVELOP_BRANCH}' en el remoto '{REMOTE_NAME}'. ¿Continuar?")
    if not confirm(prompt):
        print("Preparación de release cancelada.")
        sys.exit(0)

    print(f"Actualizando '{DEVELOP_BRANCH}' local...")
    run_git_command(["git", "checkout", DEVELOP_BRANCH])
    run_git_command(["git", "pull", REMOTE_NAME, DEVELOP_BRANCH])

    print(f"Creando/reseteando '{STAGING_BRANCH}' desde '{DEVELOP_BRANCH}'...")
    run_git_command(["git", "checkout", "-B", STAGING_BRANCH, DEVELOP_BRANCH])

    print(f"Subiendo '{STAGING_BRANCH}' al remoto ({REMOTE_NAME})...")
    # Use --force-with-lease for safety
    run_git_command(["git", "push", "--force-with-lease", REMOTE_NAME, STAGING_BRANCH])

    print(f"\n¡Éxito! Rama '{STAGING_BRANCH}' creada/actualizada desde '{DEVELOP_BRANCH}' y subida al remoto.")
    print("Lista para pruebas pre-release.")

def _validate_version(version):
    if not re.match(r'^v\d+\.\d+\.\d+$', version):
        print(f"Error: Formato de versión inválido '{version}'. Debe ser vX.Y.Z (ej. v1.2.3).")
        sys.exit(1)

def _merge_main_to_develop():
     print(f"Sincronizando '{DEVELOP_BRANCH}' con '{MAIN_BRANCH}'...")
     run_git_command(["git", "checkout", DEVELOP_BRANCH])
     run_git_command(["git", "pull", REMOTE_NAME, DEVELOP_BRANCH])

     # Use --no-ff to keep merge commit history
     result = run_git_command(["git", "merge", "--no-ff", MAIN_BRANCH], check=False)

     if result.returncode != 0:
        # Merge conflict or other merge error
        print(f"\n¡ERROR! Conflicto de merge al intentar fusionar '{MAIN_BRANCH}' en '{DEVELOP_BRANCH}'.")
        print("Debes resolver los conflictos manualmente:")
        print("  1. Abre los archivos marcados por Git.")
        print("  2. Edítalos para dejar el código correcto.")
        print(f"  3. Ejecuta 'git add <archivos-resueltos>'.")
        print(f"  4. Ejecuta 'git commit' (Git propondrá un mensaje de merge).")
        print(f"  5. Finalmente, ejecuta 'git push {REMOTE_NAME} {DEVELOP_BRANCH}'.")
        print("El script terminará ahora.")
        sys.exit(1) # Exit, requires manual intervention

     print(f"Subiendo '{DEVELOP_BRANCH}' sincronizada al remoto...")
     run_git_command(["git", "push", REMOTE_NAME, DEVELOP_BRANCH])
     return True # Merge successful

def release_perform(args):
    version = args.version
    _validate_version(version)
    print(f"Performing release actions for version {version}...")

    prompt = ("¿Estás **ABSOLUTAMENTE SEGURO** de que:\n"
              f"  1. La rama '{STAGING_BRANCH}' ha sido completamente **probada y aprobada**.\n"
              f"  2. El Pull Request de '{STAGING_BRANCH}' a '{MAIN_BRANCH}' ya ha sido **fusionado en '{MAIN_BRANCH}'**.\n"
              "¿Proceder con el tageo y sincronización?")
    if not confirm(prompt):
        print("Operación de finalización de release cancelada.")
        sys.exit(0)

    print(f"Cambiando a '{MAIN_BRANCH}' y actualizando...")
    run_git_command(["git", "checkout", MAIN_BRANCH])
    run_git_command(["git", "pull", REMOTE_NAME, MAIN_BRANCH])

    print(f"Creando tag '{version}'...")
    # Check if tag exists locally first
    tag_exists_local = run_git_command(["git", "tag", "-l", version], capture_output=True, check=False).stdout.strip()
    if tag_exists_local:
         print(f"Warning: Tag '{version}' ya existe localmente. ¿Continuar (podría fallar al pushear)?")
         if not confirm("¿Continuar?"):
              print("Operation cancelled.")
              sys.exit(0)

    run_git_command(["git", "tag", version], check=False) # Let push handle remote tag conflict

    print(f"Subiendo '{MAIN_BRANCH}' y el nuevo tag al remoto...")
    run_git_command(["git", "push", REMOTE_NAME, MAIN_BRANCH, "--tags"])

    print(f"\n¡Release completada en '{MAIN_BRANCH}'! Versión '{version}' tageada y subida.")

    if _merge_main_to_develop():
        print(f"\n¡Éxito! Rama '{DEVELOP_BRANCH}' sincronizada con los cambios de la release '{version}' y subida al remoto.")

def hotfix_start(args):
    description = args.description
    print(f"Starting hotfix...")

    print(f"Switching to '{MAIN_BRANCH}' and updating...")
    run_git_command(["git", "checkout", MAIN_BRANCH])
    run_git_command(["git", "pull", REMOTE_NAME, MAIN_BRANCH])

    sanitized_desc = sanitize_branch_name(description)
    branch_name = f"hotfix/{sanitized_desc}"

    print(f"Creating hotfix branch '{branch_name}'...")
    run_git_command(["git", "checkout", "-b", branch_name])

    print(f"\n¡Rama de emergencia '{branch_name}' creada desde '{MAIN_BRANCH}'!")
    print("Realiza aquí los cambios mínimos necesarios y haz commit.")
    print(f"Luego usa 'wf-git hotfix finish <{version}>' (ej. v1.2.1).")


def hotfix_finish(args):
    version = args.version
    _validate_version(version)
    current_branch = get_current_branch()
    print(f"Finishing hotfix '{current_branch}' with version {version}...")

    if not current_branch.startswith("hotfix/"):
         print(f"Error: Este comando debe ejecutarse desde una rama 'hotfix/*', pero estás en '{current_branch}'.")
         sys.exit(1)

    prompt = ("¿Estás **ABSOLUTAMENTE SEGURO** de que:\n"
              f"  1. El arreglo en '{current_branch}' está **completo y probado urgentemente**.\n"
              f"  2. El Pull Request de '{current_branch}' a '{MAIN_BRANCH}' ya ha sido **fusionado en '{MAIN_BRANCH}'**.\n"
              "¿Proceder con el tageo y sincronización?")
    if not confirm(prompt):
        print("Operación de finalización de hotfix cancelada.")
        sys.exit(0)

    print(f"Cambiando a '{MAIN_BRANCH}' y actualizando...")
    run_git_command(["git", "checkout", MAIN_BRANCH])
    run_git_command(["git", "pull", REMOTE_NAME, MAIN_BRANCH])

    print(f"Creando tag de hotfix '{version}'...")
    tag_exists_local = run_git_command(["git", "tag", "-l", version], capture_output=True, check=False).stdout.strip()
    if tag_exists_local:
         print(f"Warning: Tag '{version}' ya existe localmente. ¿Continuar?")
         if not confirm("¿Continuar?"):
              print("Operation cancelled.")
              sys.exit(0)
    run_git_command(["git", "tag", version], check=False)


    print(f"Subiendo '{MAIN_BRANCH}' con el hotfix y el nuevo tag al remoto...")
    run_git_command(["git", "push", REMOTE_NAME, MAIN_BRANCH, "--tags"])

    print(f"\n¡Hotfix completado en '{MAIN_BRANCH}'! Versión '{version}' tageada y subida.")

    if _merge_main_to_develop():
        print(f"\n¡Éxito! Rama '{DEVELOP_BRANCH}' sincronizada con los cambios del hotfix '{version}' y subida.")

    # Clean up hotfix branch
    print(f"Limpiando rama de hotfix local '{current_branch}'...")
    # Checkout develop first before deleting current branch
    run_git_command(["git", "checkout", DEVELOP_BRANCH], suppress_output=True)
    result = run_git_command(["git", "branch", "-d", current_branch], check=False)
    if result.returncode != 0:
        print(f"Warning: No se pudo borrar la rama local '{current_branch}'. ¿Quizás no está totalmente fusionada?")
        if confirm("¿Forzar el borrado local con -D? (¡CUIDADO!)"):
             run_git_command(["git", "branch", "-D", current_branch])
             print("Rama local forzada a borrar.")
        else:
             print("Rama local no borrada.")


    if confirm(f"¿Borrar también la rama remota '{current_branch}'?"):
         print(f"Borrando rama remota '{current_branch}'...")
         run_git_command(["git", "push", REMOTE_NAME, "--delete", current_branch])
         print("Rama remota borrada.")

    print("\nLimpieza de Hotfix completada.")


# --- Argument Parser Setup ---

def main():
    parser = argparse.ArgumentParser(
        description="CLI Helper for the Git workflow defined in docs/guia-git-workflow.md",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # wf-git init-repo
    parser_init = subparsers.add_parser("init-repo", help="Initialize a new project repository following the workflow (Flujo 1).")
    parser_init.add_argument("url_remoto", help="URL of the empty remote repository (e.g., https://github.com/user/repo.git).")
    parser_init.set_defaults(func=init_repo)

    # wf-git start
    parser_start = subparsers.add_parser("start", help="Start a new feature, fix, or chore branch from develop (Flujo 2).")
    parser_start.add_argument("type", choices=["feature", "fix", "chore"], help="Type of task.")
    # Add optional argument for issue number, only relevant for 'fix' conceptually but argparse handles it broadly
    parser_start.add_argument("issue", nargs='?', type=int, help="Optional issue number (useful for 'fix' type).")
    parser_start.add_argument("description", help="Short description of the task (will be sanitized for branch name).")
    parser_start.set_defaults(func=start_task)

    # wf-git commit
    parser_commit = subparsers.add_parser("commit", help="Create a commit with a formatted message (Flujo 2). Assumes 'git add' was done.")
    parser_commit.set_defaults(func=commit_changes)

    # wf-git push
    parser_push = subparsers.add_parser("push", help="Push the current task branch to the remote (Flujo 2). Sets upstream if needed.")
    parser_push.set_defaults(func=push_changes)

    # wf-git finish
    parser_finish = subparsers.add_parser("finish", help="Clean up after a task branch PR has been merged to develop (Flujo 2).")
    parser_finish.set_defaults(func=finish_task)

    # wf-git release prepare
    parser_release_prep = subparsers.add_parser("release", help="Commands related to releases (Flujo 3).")
    release_subparsers = parser_release_prep.add_subparsers(dest="release_command", required=True)
    parser_release_prepare_cmd = release_subparsers.add_parser("prepare", help=f"Prepare '{STAGING_BRANCH}' by resetting it from '{DEVELOP_BRANCH}'.")
    parser_release_prepare_cmd.set_defaults(func=release_prepare)

    # wf-git release perform
    parser_release_perform_cmd = release_subparsers.add_parser("perform", help=f"Perform release: tag '{MAIN_BRANCH}' and merge back to '{DEVELOP_BRANCH}'. Assumes PR from '{STAGING_BRANCH}' to '{MAIN_BRANCH}' is merged.")
    parser_release_perform_cmd.add_argument("version", help="The version tag to create (e.g., v1.2.3).")
    parser_release_perform_cmd.set_defaults(func=release_perform)

    # wf-git hotfix start
    parser_hotfix = subparsers.add_parser("hotfix", help="Commands related to hotfixes (Flujo 4).")
    hotfix_subparsers = parser_hotfix.add_subparsers(dest="hotfix_command", required=True)
    parser_hotfix_start_cmd = hotfix_subparsers.add_parser("start", help=f"Start a new hotfix branch from '{MAIN_BRANCH}'.")
    parser_hotfix_start_cmd.add_argument("description", help="Short description of the urgent fix.")
    parser_hotfix_start_cmd.set_defaults(func=hotfix_start)

    # wf-git hotfix finish
    parser_hotfix_finish_cmd = hotfix_subparsers.add_parser("finish", help=f"Finish hotfix: tag '{MAIN_BRANCH}' and merge back to '{DEVELOP_BRANCH}'. Assumes PR from hotfix branch to '{MAIN_BRANCH}' is merged.")
    parser_hotfix_finish_cmd.add_argument("version", help="The hotfix version tag to create (e.g., v1.2.1).")
    parser_hotfix_finish_cmd.set_defaults(func=hotfix_finish)


    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main() 