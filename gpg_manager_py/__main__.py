# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# __main__.py - Description placeholder
# -----------------------------------------------------------------------------
#
import sys
import argparse
from .gpg_wrapper import GPGWrapper
from .core import main_menu, APP_NAME, APP_VERSION
from .utils import show_error, confirm_continue

"""Main entry point for the GPG Manager application."""

def main():
    parser = argparse.ArgumentParser(
        prog='gpg_manager_py',
        description=f'{APP_NAME} v{APP_VERSION} - Interactive GPG Key Management Tool',
        epilog="Run without arguments for interactive menu."
    )
    # Add arguments if needed in the future (e.g., --gpg-home, --batch-mode)
    # parser.add_argument('--version', action='version', version=f'%(prog)s {APP_VERSION}')

    args = parser.parse_args()

    try:
        # Initialize GPG Wrapper
        gpg_handler = GPGWrapper()

        # Start the main menu
        main_menu(gpg_handler)

    except FileNotFoundError as e:
        # Error finding GPG handled in GPGWrapper init
        # show_error(f"Initialization failed: {e}")
        confirm_continue("Press Enter to exit.")
        sys.exit(1)
    except ImportError as e:
         show_error(f"Initialization failed due to missing dependency: {e}")
         print("Please ensure all required packages are installed:")
         print("  pip install -r requirements.txt")
         confirm_continue("Press Enter to exit.")
         sys.exit(1)
    except Exception as e:
        show_error(f"An unexpected critical error occurred: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for unexpected errors
        confirm_continue("Press Enter to exit.")
        sys.exit(1)

if __name__ == "__main__":
    main() 