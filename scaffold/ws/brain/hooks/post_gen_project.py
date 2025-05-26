#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Este script se ejecuta después de que cookiecutter genere el proyecto.
Su propósito es realizar tareas de post-procesamiento como:
- Instalar dependencias de commitlint si se seleccionó
"""

import sys
import subprocess
from pathlib import Path
import os
import shutil

def init_git(workspace_dir: Path) -> bool:
    """
    Inicializa el repositorio git y configura el branch por defecto.
    El branch por defecto se lee de config/branch.def.
    Si no se encuentra el archivo, se usa 'develop' como valor por defecto.
    """
    try:
        # Leer el branch por defecto
        branch_def_file = workspace_dir / "config" / "branch.def"
        if branch_def_file.exists():
            default_branch = branch_def_file.read_text().strip()
            if not default_branch:
                print("Advertencia: El archivo de configuración de branch está vacío, usando 'develop'")
                default_branch = "develop"
        else:
            print("Advertencia: No se encontró el archivo de configuración de branch, usando 'develop'")
            default_branch = "develop"
            
        # Inicializar git
        subprocess.run(
            ["git", "init"],
            cwd=str(workspace_dir),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Crear el branch por defecto
        subprocess.run(
            ["git", "checkout", "-b", default_branch],
            cwd=str(workspace_dir),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"Repositorio git inicializado con branch por defecto: {default_branch}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error al inicializar git: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"Error inesperado al inicializar git: {e}")
        return False

def setup_pre_commit(workspace_dir: Path) -> bool:
    """
    Instala y configura pre-commit hooks.
    """
    try:
        # Verificar si hay un venv activo
        if not os.environ.get("VIRTUAL_ENV"):
            print("Error: No hay un entorno virtual activo.")
            return False
            
        # Verificar si pre-commit ya está instalado
        try:
            subprocess.run(["pre-commit", "--version"], 
                         check=True, 
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
            print("pre-commit ya está instalado en el entorno virtual")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Instalar pre-commit en el venv activo
            print("Instalando pre-commit en el entorno virtual...")
            subprocess.run(["pip", "install", "pre-commit"], check=True)
        
        # Instalar los hooks
        subprocess.run(
            ["pre-commit", "install", "--hook-type", "commit-msg"],
            cwd=str(workspace_dir),
            check=True
        )
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar pre-commit hooks: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado al configurar pre-commit: {e}")
        return False

def install_commitlint_deps(workspace_dir: Path) -> bool:
    """
    Instala las dependencias de commitlint si se seleccionó.
    """
    try:
        # Verificar que existan los archivos necesarios
        required_files = [
            workspace_dir / ".pre-commit-config.yaml"
        ]
        
        missing_files = [f for f in required_files if not f.exists()]
        if missing_files:
            print("Error: Faltan archivos necesarios para commitlint:")
            for f in missing_files:
                print(f"  - {f}")
            return False
            
        # Si no existe package.json, inicializar npm
        if not (workspace_dir / "package.json").exists():
            print("Inicializando npm...")
            subprocess.run(
                ["npm", "init", "-y"],
                cwd=str(workspace_dir),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
        # Instalar dependencias
        print("Instalando dependencias de commitlint...")
        subprocess.run(
            ["npm", "install", "--save-dev", "@commitlint/cli", "@commitlint/config-conventional"],
            cwd=str(workspace_dir),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar dependencias de commitlint: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"Error inesperado al instalar dependencias de commitlint: {e}")
        return False

def remove_commitlint_files(workspace_dir: Path) -> bool:
    """
    Elimina los archivos relacionados con commitlint.
    """
    try:
        files_to_remove = [
            workspace_dir / ".dithooks/commitlint.config.js",
            workspace_dir / ".githooks/commitlint-wrapper.py",
            workspace_dir / ".pre-commit-config.yaml",
        ]
        
        for file in files_to_remove:
            if file.exists():
                file.unlink()
                print(f"Archivo eliminado: {file}")
                
        return True
    except Exception as e:
        print(f"Error al eliminar archivos de commitlint: {e}")
        return False

def get_template_dir() -> Path | None:
    """
    Obtiene la ruta del template buscando el directorio de licencias.
    Primero busca en $HOME/bin/scaffold/licenses, luego busca recursivamente
    cualquier directorio scaffold/licenses dentro de $HOME.
    Retorna la ruta del template (scaffold/ws/brain) si encuentra el directorio de licencias.
    Retorna None si no se puede determinar.
    """
    try:
        # Obtener $HOME
        home = Path.home()
        
        # Intentar primero en $HOME/bin/scaffold
        bin_scaffold = home / "bin" / "scaffold"
        if bin_scaffold.exists():
            return home / "bin" / "scaffold" / "ws" / "brain"
            
        # Si no está en bin, buscar recursivamente en $HOME
        for scaffold_dir in home.rglob("scaffold"):
            if scaffold_dir.is_dir():
                template_dir = scaffold_dir.parent / "ws" / "brain"
                if template_dir.exists():
                    return template_dir
                    
        return None
        
    except Exception as e:
        print(f"Error al buscar el directorio scaffolding: {e}")
        return None

def copy_commitlint_config(workspace_dir: Path, commit_format: str) -> bool:
    """
    Copia el archivo de configuración de commitlint según el formato seleccionado.
    """
    try:
        # Obtener la ruta del template
        template_dir = get_template_dir()
        if template_dir is None:
            print("Error: No se pudo encontrar el directorio scaffold")
            return False
            
        # Construir el nombre del archivo usando el formato seleccionado
        source_file = template_dir.parent.parent / "commit-format" / f"commitlint.config.{commit_format.lower()}.js.def"
            
        if not source_file.exists():
            print(f"Error: No se encontró el archivo de configuración: {source_file}")
            return False
            
        # Asegurar que existe el directorio .prehooks
        prehooks_dir = workspace_dir / ".prehooks"
        prehooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar el archivo al directorio del proyecto
        target_file = workspace_dir / ".prehooks" / "commitlint.config.js"
        shutil.copy2(source_file, target_file)
        print(f"Archivo de configuración copiado: {target_file}")
        return True
        
    except Exception as e:
        print(f"Error al copiar el archivo de configuración: {e}")
        return False

def copy_license(workspace_dir: Path, license_type: str) -> bool:
    """
    Copia la licencia seleccionada al directorio del proyecto.
    Si license_type es 'no', no hace nada.
    Si la licencia tiene metadata en formato YAML:
    - Si requires_ai_generation es false, elimina la metadata y copia como LICENSE.md
    - Si requires_ai_generation es true, copia la licencia completa a config/license.def
    """
    if license_type.lower() == "no":
        return True
        
    try:
        # Obtener la ruta del template
        template_dir = get_template_dir()
        if template_dir is None:
            print("Error: No se pudo encontrar el directorio scaffold")
            return False
            
        # Construir rutas - subir hasta la raíz del scaffold
        source_license = template_dir.parent.parent / "licenses" / f"{license_type.lower()}.md"
        target_license = workspace_dir / "LICENSE.md"
        target_license_def = workspace_dir / "config" / "license.def"
        
        if not source_license.exists():
            print(f"Error: No se encontró la licencia: {source_license}")
            return False
            
        # Leer el contenido del archivo
        content = source_license.read_text()
        
        # Verificar si tiene metadata en formato YAML
        if content.startswith("---\n"):
            # Encontrar el final de la metadata
            metadata_end = content.find("\n---\n", 4)  # Buscar después del primer ---
            if metadata_end != -1:
                metadata = content[4:metadata_end]  # Excluir los --- iniciales
                
                # Verificar requires_ai_generation
                if "requires_ai_generation: true" in metadata.lower():
                    # Copiar la licencia completa a config/license.def
                    target_license_def.parent.mkdir(parents=True, exist_ok=True)
                    target_license_def.write_text(content)
                    print(f"Licencia copiada a: {target_license_def}")
                    return True
                elif "requires_ai_generation: false" in metadata.lower():
                    # Eliminar toda la metadata incluyendo los ---
                    content = content[metadata_end + 5:].lstrip()  # +5 para incluir el \n---\n
        
        # Escribir el contenido al archivo destino
        target_license.write_text(content)
        print(f"Licencia copiada: {target_license}")
        return True
        
    except Exception as e:
        print(f"Error al copiar la licencia: {e}")
        return False

def setup_cursor_config(workspace_dir: Path, cursor_config: str) -> bool:
    """
    Configura la estructura de directorios para Cursor.
    Si cursor_config es "no", no hace nada.
    Tipos de configuración:
    - "base": Copia base_*.mdc -> *.mdc
    - "brain": Copia base_*.mdc y brain_*.mdc -> *.mdc
    - "base-custom": Copia base_*.mdc -> *.mdc y custom_*.mdc
    - "brain-custom": Copia base_*.mdc y brain_*.mdc -> *.mdc y custom_*.mdc
    - "custom": Copia custom_*.mdc
    
    También crea el directorio .vscode en la raíz del proyecto si cursor_config no es "no".
    """
    try:
        # Crear la estructura de directorios
        cursor_rules_dir = workspace_dir / ".cursor" / "rules"
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)
        
        if cursor_config.lower() == "no":
            return True
            
        # Crear directorio .vscode
        vscode_dir = workspace_dir / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directorio .vscode creado: {vscode_dir}")
            
        # Obtener la ruta del template
        template_dir = get_template_dir()
        if template_dir is None:
            print("Error: No se pudo encontrar el directorio scaffold")
            return False
            
        # Construir ruta a los archivos de reglas
        rules_dir = template_dir.parent.parent / "cursor" / "rules"
        if not rules_dir.exists():
            print(f"Error: No se encontró el directorio de reglas: {rules_dir}")
            return False
            
        # Determinar qué archivos copiar según el tipo de configuración
        patterns_to_copy = []
        if cursor_config.lower() in ["base", "brain", "base-custom", "brain-custom"]:
            patterns_to_copy.append("base_*.mdc")
        if cursor_config.lower() in ["brain", "brain-custom"]:
            patterns_to_copy.append("brain_*.mdc")
        if cursor_config.lower() in ["base-custom", "brain-custom", "custom"]:
            patterns_to_copy.append("custom_*.mdc")
            
        if not patterns_to_copy:
            print(f"Error: Tipo de configuración de Cursor no válido: {cursor_config}")
            return False
            
        # Copiar los archivos según los patrones
        print(f"Copiando reglas de Cursor ({cursor_config})...")
        files_copied = False
        for pattern in patterns_to_copy:
            files = list(rules_dir.glob(pattern))
            if not files:
                print(f"Advertencia: No se encontraron archivos {pattern}")
                continue
                
            for file in files:
                # Remover el prefijo solo para base_ y brain_, mantener custom_
                if file.name.startswith(("base_", "brain_")):
                    new_name = file.name.split("_", 1)[1]
                else:
                    new_name = file.name
                    
                target_file = cursor_rules_dir / new_name
                shutil.copy2(file, target_file)
                print(f"  ✓ {new_name}")
                files_copied = True
                
        if not files_copied:
            print("Error: No se copió ningún archivo de reglas")
            return False
                
        print(f"Directorio de reglas de Cursor creado: {cursor_rules_dir}")
        return True
        
    except Exception as e:
        print(f"Error al configurar directorios de Cursor: {e}")
        return False

def main():
    """
    Función principal que ejecuta las tareas post-generación.
    """
    # Obtener las variables de cookiecutter
    workspace_slug = "{{ cookiecutter.workspace_slug }}"
    commit_format = "{{ cookiecutter.commit_format }}"
    license_type = "{{ cookiecutter.license }}"
    cursor_config = "{{ cookiecutter.cursor_config }}"
    
    # Obtener el directorio del proyecto
    workspace_dir = Path.cwd()
    
    if not workspace_dir.exists():
        print(f"Error: No se encontró el directorio del proyecto: {workspace_dir}")
        sys.exit(1)
    
    # Inicializar git primero
    if not init_git(workspace_dir):
        print("Error: No se pudo inicializar git")
        sys.exit(1)
    
    # Ejecutar tareas post-generación
    success = True
    
    # Copiar la licencia si se seleccionó una
    if not copy_license(workspace_dir, license_type):
        success = False
    
    # Configurar Cursor si se seleccionó
    if cursor_config.lower() != "no":
        if not setup_cursor_config(workspace_dir, cursor_config):
            success = False
    
    if commit_format.lower() == "no":
        # Eliminar archivos de commitlint si no se seleccionó formato
        if not remove_commitlint_files(workspace_dir):
            success = False
    else:
        # Verificar solo el archivo de pre-commit
        if not (workspace_dir / ".pre-commit-config.yaml").exists():
            print("Error: No se encontró el archivo .pre-commit-config.yaml")
            print("Esto puede indicar que cookiecutter no copió correctamente los archivos")
            success = False
        else:
            # Primero copiar el archivo de configuración de commitlint
            if not copy_commitlint_config(workspace_dir, commit_format):
                success = False
            else:
                # Luego instalar dependencias y configurar pre-commit
                if not install_commitlint_deps(workspace_dir):
                    success = False
                elif not setup_pre_commit(workspace_dir):
                    success = False
    
    # Si alguna tarea falla, terminar con error
    if not success:
        print("\nError: No se pudo completar la configuración del proyecto")
        print("Verifica que cookiecutter haya copiado correctamente los archivos del template")
        sys.exit(1)
        
    print("\n¡Proyecto generado exitosamente!")
    print(f"Directorio: {workspace_dir}")
    if license_type.lower() != "no":
        print("Licencia copiada")
    if cursor_config.lower() != "no":
        print(f"Configuración de Cursor creada ({cursor_config})")
    if commit_format.lower() == "no":
        print("Archivos de commitlint eliminados")
    else:
        print("Dependencias de commitlint instaladas")
        print("Hooks de pre-commit configurados")

if __name__ == "__main__":
    main() 