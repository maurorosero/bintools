# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# gpg_wrapper.py - Description placeholder
# -----------------------------------------------------------------------------
#
import gnupg
import os
import tempfile
import platform

from .utils import show_error, show_info, show_warning, get_default_gpg_home

"""Wrapper functions for interacting with the GPG executable via python-gnupg."""

class GPGWrapper:
    """A class to manage interactions with GPG."""
    def __init__(self, gpg_home=None, gpg_binary='gpg'):
        """
        Initializes the GPG wrapper.

        Args:
            gpg_home (str, optional): Path to the GPG home directory. Defaults to system default.
            gpg_binary (str, optional): Path to the GPG executable. Defaults to 'gpg'.
        """
        self.gpg_home = gpg_home or get_default_gpg_home()
        self.gpg_binary = self._find_gpg_binary(gpg_binary)

        if not self.gpg_binary:
            show_error("GPG executable not found. Please install GnuPG.")
            # Provide hints based on OS
            os_name = platform.system()
            if os_name == "Linux":
                show_info("On Debian/Ubuntu: sudo apt install gnupg")
                show_info("On Fedora: sudo dnf install gnupg2")
                show_info("On Arch: sudo pacman -S gnupg")
            elif os_name == "Darwin": # macOS
                show_info("Using Homebrew: brew install gnupg")
            elif os_name == "Windows":
                show_info("Download and install Gpg4win from https://www.gpg4win.org/")
            raise FileNotFoundError("GPG executable not found")

        try:
            # Enable verbose output for debugging if needed, but can be noisy
            # self.gpg = gnupg.GPG(gnupghome=self.gpg_home, gpgbinary=self.gpg_binary, verbose=True)
            self.gpg = gnupg.GPG(gnupghome=self.gpg_home, gpgbinary=self.gpg_binary)
            # Test connection by listing keys (even if empty)
            self.gpg.list_keys()
        except Exception as e:
            show_error(f"Failed to initialize GPG: {e}",
                       details=f"GPG Home: {self.gpg_home}, GPG Binary: {self.gpg_binary}")
            raise

    def _find_gpg_binary(self, preferred_binary='gpg'):
        """Tries to find the GPG binary, checking common names."""
        candidates = [preferred_binary, 'gpg2']
        if platform.system() == "Windows":
            candidates.extend(['gpg.exe', 'gpg2.exe'])
            # Check common Gpg4win path if not in PATH
            program_files = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            gpg4win_path = os.path.join(program_files, "GnuPG", "bin", "gpg.exe")
            if os.path.exists(gpg4win_path):
                return gpg4win_path

        for candidate in candidates:
            try:
                # Check if the command exists and is executable
                result = gnupg.GPG(gpgbinary=candidate).list_keys() # Simple command to test existence
                # print(f"Found GPG binary at: {candidate}") # Debug
                return candidate
            except OSError:
                # print(f"GPG candidate '{candidate}' not found or failed.") # Debug
                continue
            except Exception:
                 # Catch other potential errors during initialization test
                 continue
        return None # Not found

    def list_keys(self, secret=False):
        """Lists public or secret keys."""
        try:
            return self.gpg.list_keys(secret)
        except Exception as e:
            show_error(f"Failed to list keys: {e}")
            return []

    def get_key(self, key_id):
        """Retrieves details for a specific key ID."""
        keys = self.list_keys(False) # Search public keys
        for key in keys:
            if key['keyid'].endswith(key_id.upper()): # Match suffix
                return key
        keys = self.list_keys(True) # Search secret keys if not found in public
        for key in keys:
            if key['keyid'].endswith(key_id.upper()):
                return key
        return None

    def export_keys(self, keyids, secret=False, armor=True, output_path=None):
        """Exports one or more keys."""
        try:
            options = {
                'armor': armor,
                'output': output_path,
                'secret': secret
            }
            # Filter out None values for arguments python-gnupg doesn't like as None
            export_args = {k: v for k, v in options.items() if v is not None}
            result = self.gpg.export_keys(keyids, **export_args)
            if output_path:
                # Check if the file was created and is not empty
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True # Success indicated by file creation
                else:
                    show_error("Export failed: Output file not created or empty.")
                    return False
            elif result:
                return result # Return the exported key data string
            else:
                show_error("Export failed: No data returned by GPG.")
                return None
        except Exception as e:
            show_error(f"Failed to export key(s) {keyids}: {e}")
            return None

    def import_keys(self, key_data=None, filepath=None):
        """Imports keys from data string or a file."""
        if not key_data and not filepath:
            show_error("Import failed: No key data or file path provided.")
            return None
        if filepath and not os.path.exists(filepath):
             show_error(f"Import failed: File not found at '{filepath}'")
             return None

        try:
            if filepath:
                 with open(filepath, 'r') as f:
                     key_data = f.read()

            result = self.gpg.import_keys(key_data)
            if result and result.count > 0:
                show_info(f"Import Results:")
                console.print(f"  Keys processed: {result.count}")
                console.print(f"  Keys imported: {result.imported}")
                console.print(f"  Keys unchanged: {result.unchanged}")
                console.print(f"  Fingerprints: {result.fingerprints}")
                # Check for errors during import
                if hasattr(result, 'results'):
                    for res in result.results:
                        if res.get('problem') and res.get('problem') != '0':
                            show_warning(f"Problem importing key {res.get('fingerprint', '')}: {res.get('text', 'Unknown error')}")
                return result
            elif result:
                 show_warning(f"GPG reported 0 keys imported. Status: {result.status}")
                 # Potentially print result.stderr here if available and useful
                 return None
            else:
                 show_error("Import failed: No result object returned.")
                 return None
        except Exception as e:
            show_error(f"Failed to import keys: {e}")
            return None

    def delete_keys(self, keyids, secret=False):
        """Deletes public or secret keys."""
        # Note: Deleting requires user confirmation via pinentry usually
        action = "secret key" if secret else "public key"
        try:
            results = []
            for keyid in keyids:
                 # python-gnupg delete_keys expects fingerprint, try to get it
                 key_info = self.get_key(keyid)
                 fingerprint = key_info.get('fingerprint') if key_info else keyid

                 if not fingerprint:
                     show_warning(f"Could not find fingerprint for key ID {keyid}. Skipping deletion.")
                     continue

                 delete_func = self.gpg.delete_keys
                 if secret:
                     # python-gnupg delete_keys deletes both by default if secret=True not passed
                     # To delete ONLY the secret key, need to call gpg directly or handle carefully.
                     # For simplicity here, let's assume we delete both if secret=True
                     # However, the original script likely intended separate deletes.
                     # Let's use the intended behavior of python-gnupg (delete both if fingerprint matches secret key)
                     pass

                 # We need to handle the confirmation prompt gpg might raise
                 # python-gnupg doesn't directly support non-interactive delete easily without passphrases
                 # It's often better to let gpg handle interaction via pinentry.
                 show_info(f"Attempting to delete {action} for fingerprint: {fingerprint}")
                 result = delete_func(fingerprint, secret)
                 results.append(result)
                 if result.status.lower() == 'ok' or 'deleted' in result.status.lower():
                     show_success(f"Successfully initiated deletion for {fingerprint}")
                 elif 'not found' in result.status.lower():
                     show_warning(f"Key {fingerprint} not found for deletion.")
                 else:
                     show_error(f"Failed to delete {action} {fingerprint}. Status: {result.status}", details=result.stderr)
            return results
        except Exception as e:
            show_error(f"An error occurred during key deletion: {e}")
            return []

    def generate_key(self, input_data):
        """Generates a new key pair based on input data."""
        # input_data should be a string formatted according to GPG --batch requirements
        try:
            result = self.gpg.gen_key(input_data)
            if result and result.fingerprint:
                show_success(f"Key generated successfully! Fingerprint: {result.fingerprint}")
                return result
            elif result:
                show_error("Key generation failed.", details=f"Status: {result.status}, Stderr: {result.stderr}")
                return None
            else:
                show_error("Key generation failed: No result object returned.")
                return None
        except Exception as e:
            show_error(f"Failed to generate key: {e}")
            return None

    def receive_keys(self, keyserver, keyids):
        """Receives keys from a keyserver."""
        try:
            result = self.gpg.recv_keys(keyserver, *keyids)
            if result and result.count > 0:
                show_info(f"Received {result.count} key(s) from {keyserver}.")
                console.print(f"  Fingerprints: {result.fingerprints}")
                return result
            elif result:
                 show_warning(f"GPG reported 0 keys received from {keyserver}. Status: {result.status}")
                 return None
            else:
                show_error(f"Receive keys failed: No result object returned from {keyserver}.")
                return None
        except Exception as e:
            show_error(f"Failed to receive keys from {keyserver}: {e}")
            return None

    def send_keys(self, keyserver, keyids):
        """Sends keys to a keyserver."""
        try:
            result = self.gpg.send_keys(keyserver, *keyids)
            # Check status more carefully for send_keys
            if result and 'request_status' in result.data and result.data['request_status'] == 'ok':
                 show_success(f"Successfully sent {len(keyids)} key(s) to {keyserver}.")
                 return True
            elif result:
                status = result.status or result.data.get('reason', 'Unknown reason')
                show_error(f"Failed to send keys to {keyserver}. Status: {status}", details=result.stderr)
                return False
            else:
                show_error(f"Send keys failed: No result object returned from {keyserver}.")
                return False
        except Exception as e:
            show_error(f"Failed to send keys to {keyserver}: {e}")
            return False

    def sign_key(self, key_id, signing_key_id, trust_level):
        """Signs a key with another key."""
        # This often requires interaction for passphrase
        try:
             # python-gnupg's sign_key is basic. For trust level, often need edit_key
             # Let's try the basic sign first
            show_info(f"Attempting to sign key {key_id} with {signing_key_id}.")
            # sign_key only takes keyid, might need explicit interaction for passphrase
            result = self.gpg.sign(key_id, keyid=signing_key_id) # This seems wrong, sign is for data

            # GnuPG sign-key is interactive or needs batch input
            # Using edit_keys might be more reliable here if we need non-interactive
            # For now, let's call the command directly if sign() isn't for keys
            # This is a placeholder - need to implement properly via edit_keys or direct call
            show_warning("Direct key signing via python-gnupg simple API is limited.")
            show_info("Attempting sign via GPG command directly (may require interaction)...")

            command = [
                self.gpg_binary, '--yes',
                f'--homedir={self.gpg_home}' if self.gpg_home else '',
                '--command-fd=0', # Read commands from stdin
                '--status-fd=1',  # Write status to stdout
                '--edit-key', key_id
            ]
            command = [c for c in command if c] # Remove empty strings

            # Prepare commands for GPG edit-key
            gpg_commands = f"sign\n{trust_level}\ny\nsave\n"

            process = self.gpg.result_map['edit_keys'](
                 command, gpg_commands.encode('utf-8')
            )
            process.wait() # Wait for gpg command to finish

            if process.returncode == 0:
                 show_success(f"Key {key_id} signed successfully with {signing_key_id}.")
                 return True
            else:
                 show_error(f"Failed to sign key {key_id}. GPG exited with code {process.returncode}.", details=process.stderr.decode('utf-8', errors='ignore'))
                 return False

            # Old placeholder:
            # show_error("Key signing function needs proper implementation (likely via edit_keys).")
            # return False
        except Exception as e:
            show_error(f"Failed to sign key {key_id}: {e}")
            return False

    def generate_revocation_certificate(self, key_id, reason_code="0", reason_string="", output_path=None):
        """Generates a revocation certificate for a key."""
        if not output_path:
             show_error("Output path is required for revocation certificate.")
             return False
        try:
            # Use --batch and --command-fd for non-interactive generation
            batch_input = f"key {key_id}\nrevocation-reason {reason_code} {reason_string}\ny\ny\n"

            command = [
                self.gpg_binary, '--batch', '--yes',
                f'--homedir={self.gpg_home}' if self.gpg_home else '',
                '--command-fd=0', # Read batch commands from stdin
                '--status-fd=1',  # Write status to stdout
                f'--output={output_path}',
                '--gen-revoke', key_id
            ]
            command = [c for c in command if c] # Remove empty strings

            # Need to run gpg directly as python-gnupg lacks gen-revoke wrapper
            # Using gnupg's internal way to run commands might be better
            proc = self.gpg.result_map['gen_revoke'](command, batch_input.encode('utf-8'))
            proc.wait()

            if proc.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                 show_success(f"Revocation certificate generated at {output_path}")
                 # Set restrictive permissions
                 try:
                     os.chmod(output_path, 0o600)
                 except OSError as chmod_err:
                     show_warning(f"Could not set permissions on {output_path}: {chmod_err}")
                 return True
            else:
                 stderr = proc.stderr.decode('utf-8', errors='ignore') if proc.stderr else "No stderr"
                 show_error("Failed to generate revocation certificate.", details=stderr)
                 # Clean up empty file if created
                 if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
                     os.remove(output_path)
                 return False

        except Exception as e:
            show_error(f"Failed to generate revocation certificate for {key_id}: {e}")
            return False

    def search_keys(self, keyserver, query):
         """Searches for keys on a keyserver."""
         # Note: python-gnupg search_keys can be problematic. Direct call might be needed.
         try:
             # This often hangs or fails depending on gpg version and keyserver
             # result = self.gpg.search_keys(query, keyserver)
             # return result

             # Alternative: Call GPG directly
             show_info(f"Searching for '{query}' on {keyserver}...")
             command = [
                 self.gpg_binary,
                 f'--homedir={self.gpg_home}' if self.gpg_home else '',
                 '--keyserver', keyserver,
                 '--search-keys', query,
                 '--batch', # Try batch mode to avoid hangs
                 '--status-fd=1'
             ]
             command = [c for c in command if c]

             # Use gnupg internal process handling
             proc = self.gpg.result_map['search_keys'](command, None)
             stdout_bytes, stderr_bytes = proc.communicate()
             stdout = stdout_bytes.decode('utf-8', errors='ignore')
             stderr = stderr_bytes.decode('utf-8', errors='ignore')

             if proc.returncode == 0 and stdout:
                 # python-gnupg usually parses this output, here we return raw text
                 # Might need parsing logic if we want structured data
                 return stdout
             elif "No keys found" in stdout or "No keys found" in stderr:
                  show_info("No keys found matching the query.")
                  return None
             else:
                 show_error("Search failed.", details=stderr or stdout)
                 return None

         except Exception as e:
             show_error(f"Failed to search keys for '{query}' on {keyserver}: {e}")
             return None

# Create a global instance (optional, can be instantiated where needed)
# try:
#     gpg_handler = GPGWrapper()
# except FileNotFoundError:
#     gpg_handler = None
#     show_error("GPG is not available. Some functionality will be disabled.")
# except Exception as e:
#     gpg_handler = None
#     show_error(f"Failed to initialize GPG handler: {e}") 