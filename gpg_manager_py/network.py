# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# network.py - Description placeholder
# -----------------------------------------------------------------------------
#
import requests
from .utils import show_error, show_info, show_warning
from .tui import SpinnerContext

"""Network related functions, like downloading keys from URLs."""

def download_key_from_url(url):
    """Downloads key data from a given URL."""
    show_info(f"Attempting to download key from: {url}")
    try:
        with SpinnerContext(f"Downloading key from {url[:50]}..."):
            response = requests.get(url, timeout=15) # Add a timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        content_type = response.headers.get('content-type', '').lower()
        key_data = response.text

        # Basic check if it looks like a PGP key
        if "BEGIN PGP" not in key_data:
            show_warning("Downloaded content doesn't look like a PGP key.")
            show_info(f"Content type: {content_type}")
            show_info(f"Content preview:\n{key_data[:200]}...")
            # Optionally ask user if they want to proceed anyway
            return None

        show_info("Download successful.")
        return key_data

    except requests.exceptions.RequestException as e:
        show_error(f"Failed to download key from URL: {e}")
        return None
    except Exception as e:
        show_error(f"An unexpected error occurred during download: {e}")
        return None 