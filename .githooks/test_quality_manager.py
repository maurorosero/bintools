#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para el QualityManager.
Permite probar la funcionalidad del QualityManager de forma interactiva.
"""

import sys
import os
from pathlib import Path
from quality_manager import QualityManager, QualityLevel

def get_workspace_root() -> Path:
    """Obtiene la ruta raíz del workspace."""
    current_dir = Path.cwd()
    # Si estamos en .githooks, subimos un nivel
    if current_dir.name == '.githooks':
        return current_dir.parent
    return current_dir

def print_menu():
    """Muestra el menú de opciones."""
    print("\n🔧 Quality Manager - Menú de Prueba")
    print("--------------------------------")
    print("1. Listar formatos disponibles")
    print("2. Ver configuración actual")
    print("3. Aplicar nivel minimal")
    print("4. Aplicar nivel standard")
    print("5. Aplicar nivel enterprise")
    print("6. Aplicar formato específico")
    print("0. Salir")
    print("--------------------------------")

def apply_level(manager: QualityManager, level: str):
    """Aplica un nivel de calidad."""
    try:
        result = manager.apply_configuration(level)
        print(f"\n✅ Nivel {result['level']} aplicado correctamente")
        print(f"   - Formato de commit: {result['commit_format']}")
    except ValueError as e:
        print(f"\n❌ Error al aplicar nivel {level}: {e}")

def apply_format(manager: QualityManager):
    """Aplica un formato de commit específico."""
    formats = manager.list_available_formats()
    print("\n📋 Formatos Disponibles:")
    for i, (name, info) in enumerate(formats.items(), 1):
        print(f"{i}. {name}: {info['description']}")

    try:
        choice = int(input("\nSeleccione un formato (número): "))
        if 1 <= choice <= len(formats):
            format_name = list(formats.keys())[choice - 1]
            level = input("Nivel a aplicar (minimal/standard/enterprise): ")
            result = manager.apply_configuration(level, format_name)
            print(f"\n✅ Nivel {result['level']} aplicado correctamente")
            print(f"   - Formato de commit: {result['commit_format']}")
        else:
            print("\n❌ Opción no válida")
    except ValueError as e:
        print(f"\n❌ Error: {e}")

def main():
    """Función principal."""
    try:
        # Asegurarnos de que estamos en el directorio correcto
        workspace_root = get_workspace_root()
        os.chdir(workspace_root)

        manager = QualityManager(workspace_root)

        while True:
            print_menu()
            choice = input("\nSeleccione una opción: ")

            if choice == "1":
                print("\n📋 Formatos de Commit Disponibles")
                print("--------------------------------")
                for name, info in manager.list_available_formats().items():
                    print(f"{name}: {info['description']}")

            elif choice == "2":
                print("\n📊 Estado Actual")
                print("---------------")
                config = manager.get_current_configuration()
                if config['status'] == 'active':
                    print(f"Nivel: {config['level']}")
                    print(f"Formato de commit: {config['commit_format']}")
                else:
                    print("No hay configuración activa")

            elif choice == "3":
                apply_level(manager, "minimal")

            elif choice == "4":
                apply_level(manager, "standard")

            elif choice == "5":
                apply_level(manager, "enterprise")

            elif choice == "6":
                apply_format(manager)

            elif choice == "0":
                print("\n👋 ¡Hasta luego!")
                sys.exit(0)

            else:
                print("\n❌ Opción no válida")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
