# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-04-30 05:43:12
# Version: 0.1.1
#
# header_manage.py - Description placeholder
# -----------------------------------------------------------------------------
#
import sys
import os
import re
import ast
import argparse
import configparser
from datetime import datetime

HEADER_CONFIG_FILE = '.headerconfig'
IGNORE_FILE = '.headerignore'
HEADER_PLACEHOLDER = '__INITIAL_VERSION__'
MAX_LINES_TO_CHECK = 20 # Check this many lines for existing header

# --- Configuration Loading ---

def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(HEADER_CONFIG_FILE):
        print(f"Error: Configuration file '{HEADER_CONFIG_FILE}' not found.")
        sys.exit(1)
    config.read(HEADER_CONFIG_FILE)
    try:
        defaults = config['HeaderDefaults']
        return {
            'holder': defaults['CopyrightHolder'],
            'license': defaults['LicenseName'],
            'author': defaults['DefaultAuthor'],
            'initial_version': defaults['InitialVersion']
        }
    except KeyError as e:
        print(f"Error: Missing key {e} in '{HEADER_CONFIG_FILE}' under [HeaderDefaults].")
        sys.exit(1)

# --- Ignore File Handling ---

def load_ignore_patterns():
    if not os.path.exists(IGNORE_FILE):
        return set()
    try:
        with open(IGNORE_FILE, 'r') as f:
            patterns = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        return patterns
    except IOError as e:
        print(f"Warning: Could not read ignore file '{IGNORE_FILE}': {e}")
        return set()

def is_ignored(filepath, ignore_patterns):
    # Simple check: exact match or directory prefix match for now
    # Could be extended with glob patterns if needed
    if filepath in ignore_patterns:
        return True
    for pattern in ignore_patterns:
        if pattern.endswith('/') and filepath.startswith(pattern):
            return True
        # Basic glob-like check for directory contents
        if pattern.endswith('/*') and os.path.dirname(filepath) == pattern[:-2]:
             return True
    return False

# --- Header Generation and Parsing ---

def get_comment_prefix(filepath):
    _, ext = os.path.splitext(filepath)
    if ext in ['.py', '.sh']:
        return '#'
    elif ext in ['.ts', '.js']:
        return '//'
    else:
        return None # Unsupported file type

def generate_header_lines(config, comment_prefix, filename, description):
    year = datetime.now().year
    # Include time in the created timestamp
    created_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    return [
        f"{comment_prefix} -----------------------------------------------------------------------------",
        f"{comment_prefix} Copyright (c) {year}, {config['holder']}",
        f"{comment_prefix} License: {config['license']}",
        f"{comment_prefix} Author: {config['author']}",
        # Use the new timestamp variable
        f"{comment_prefix} Created: {created_timestamp}", 
        f"{comment_prefix} Version: {HEADER_PLACEHOLDER}", # Placeholder added here
        f"{comment_prefix}",
        # Use the passed description variable
        f"{comment_prefix} {os.path.basename(filename)} - {description}", 
        f"{comment_prefix} -----------------------------------------------------------------------------",
        f"{comment_prefix}" # Add an empty comment line for spacing maybe?
    ]

def get_version_regex(comment_prefix):
    # Regex to find 'Version: X.Y.Z' preceded by the correct comment
    # Allows optional space after colon
    # Captures the version string X.Y.Z
    escaped_prefix = re.escape(comment_prefix)
    return re.compile(rf"^{escaped_prefix}\s*Version:\s*(\d+\.\d+\.\d+)$")

def increment_patch_version(version_string):
    parts = version_string.split('.')
    if len(parts) != 3:
        return None # Invalid format
    try:
        major, minor, patch = map(int, parts)
        patch += 1
        return f"{major}.{minor}.{patch}"
    except ValueError:
        return None # Non-integer parts

# --- File Processing Logic ---

def process_file(filepath, config, ignore_patterns):
    if is_ignored(filepath, ignore_patterns):
        print(f"Ignoring file: {filepath}")
        return False # Indicate no changes needed

    comment_prefix = get_comment_prefix(filepath)
    if not comment_prefix:
        print(f"Skipping unsupported file type: {filepath}")
        return False

    version_regex = get_version_regex(comment_prefix)
    placeholder_line = f"{comment_prefix} Version: {HEADER_PLACEHOLDER}"
    initial_version_line = f"{comment_prefix} Version: {config['initial_version']}"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return False # Treat as error, no changes

    original_lines = list(lines) # Keep a copy
    modified = False
    version_found = False
    placeholder_found = False
    header_exists = False # Crude check

    # Check first few lines for existing header structure (simple check)
    if len(lines) >= 5:
         # Check if first line starts with comment prefix or shebang
        first_line_check = lines[0].strip().startswith(comment_prefix) or lines[0].startswith('#!')
         # Check if some known header line exists within first MAX_LINES_TO_CHECK
        header_pattern_check = any(l.strip().startswith(f"{comment_prefix} Copyright (c)") for l in lines[:MAX_LINES_TO_CHECK])
        header_exists = first_line_check and header_pattern_check


    new_lines = []
    line_index_to_replace = -1

    for i, line in enumerate(lines):
        # 1. Check for placeholder
        if line.strip() == placeholder_line.strip():
            new_lines.append(initial_version_line + '\n')
            placeholder_found = True
            modified = True
            version_found = True # Consider placeholder as a version indicator
            print(f"Setting initial version in {filepath}")
            continue # Move to next line

        # 2. Check for existing version
        match = version_regex.match(line.strip())
        if match:
            # --- TEMPORARILY DISABLED VERSION INCREMENT ---
            # current_version = match.group(1)
            # new_version = increment_patch_version(current_version)
            # if new_version:
            #     new_lines.append(f"{comment_prefix} Version: {new_version}\n")
            #     modified = True
            #     version_found = True
            #     print(f"Incrementing version in {filepath} to {new_version}")
            # else:
            #     print(f"Warning: Could not increment invalid version '{current_version}' in {filepath}")
            #     new_lines.append(line) # Keep original invalid line
            # --- END TEMPORARY DISABLE ---
            # Just keep the existing version line for now
            new_lines.append(line)
            version_found = True # Still mark version as found
            continue # Move to next line

        new_lines.append(line)

    # 3. If no version/placeholder found, check if we need to add a header
    if not version_found:
        if not header_exists or not lines: # If no header structure OR empty file
            print(f"Adding standard header to {filepath}")
            
            # --- Extract Description Logic ---
            description = "Description placeholder" # Default
            file_extension = os.path.splitext(filepath)[1]

            if file_extension == '.py':
                try:
                    # Re-read the full file content for parsing
                    with open(filepath, 'r', encoding='utf-8') as f_content:
                        file_content = f_content.read()
                    
                    # Avoid parsing if file is empty or just has shebang
                    if file_content.strip() and not (file_content.startswith('#!') and not '\n' in file_content.strip()):
                        tree = ast.parse(file_content)
                        docstring = ast.get_docstring(tree, clean=True)
                        if docstring:
                            first_line = docstring.split('\n', 1)[0].strip()
                            if first_line:
                                description = first_line
                                print(f"  Found description: \"{description}\"")
                except SyntaxError:
                    print(f"  Warning: Could not parse Python file {filepath} to extract docstring (Syntax Error).")
                except Exception as e:
                    print(f"  Warning: Error extracting docstring from {filepath}: {e}")
            # --- End Extract Description ---

            # Basic check for shebang to keep it at the top
            shebang_line = None
            content_start_index = 0
            if lines and lines[0].startswith("#!"):
                shebang_line = lines[0]
                content_start_index = 1

            # Generate header using the determined description
            header_template = generate_header_lines(config, comment_prefix, filepath, description)
            # Replace version placeholder in template immediately
            header_template = [initial_version_line if l.strip() == placeholder_line.strip() else l for l in header_template]

            final_lines = []
            if shebang_line:
                final_lines.append(shebang_line)
            final_lines.extend([l + '\n' for l in header_template])
            final_lines.extend(lines[content_start_index:]) # Add original content after header
            new_lines = final_lines
            modified = True
        else:
            # Header seems to exist but no standard version line found. FAIL.
            print(f"Error: File '{filepath}' has a non-standard header or is missing the '{comment_prefix} Version: X.Y.Z' line.")
            print("Please fix the header manually according to the project standard.")
            sys.exit(1) # Fail the commit


    # Write changes if modified
    if modified:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True # Indicate changes were made
        except Exception as e:
            print(f"Error writing changes to {filepath}: {e}")
            # Attempt to restore original content (best effort)
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(original_lines)
            except Exception as restore_e:
                 print(f"CRITICAL: Failed to restore original content for {filepath}: {restore_e}")
            return False # Error occurred
    else:
        return False # No changes needed

# --- Main Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check and update file headers.')
    parser.add_argument('filenames', nargs='*', help='Files to process.')
    args = parser.parse_args()

    if not args.filenames:
        print("No filenames provided.")
        sys.exit(0)

    config = load_config()
    ignore_patterns = load_ignore_patterns()
    made_changes = False

    for filename in args.filenames:
        if os.path.isfile(filename):
            if process_file(filename, config, ignore_patterns):
                made_changes = True
        else:
            print(f"Skipping non-file: {filename}")

    # If changes were made, pre-commit requires exit code 1 to indicate
    # that files need to be re-staged. But we only want to fail hard
    # if there was a real error (handled by sys.exit(1) within process_file).
    # For successful modifications, exit 0, but pre-commit will still likely
    # stop the commit because the files changed. The user just needs to `git add`.
    # We could exit(1) here if `made_changes` is True, which forces the user
    # to re-add, but exiting 0 is slightly less aggressive. Let's stick with 0 for now.
    sys.exit(0) 