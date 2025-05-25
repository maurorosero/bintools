# hooks/pre_prompt.py

import json
import subprocess
from pathlib import Path

config_path = Path("cookiecutter.json")

# Leer el JSON original
data = json.loads(config_path.read_text())

def get_git_config_value(key, fallback):
    try:
        return subprocess.check_output(
            ["git", "config", "--global", key],
            text=True
        ).strip() or fallback
    except subprocess.CalledProcessError:
        return fallback

# Valores por defecto si git no los tiene
default_name = "Jane Doe"
default_email = "jane.doe@example.com"

# Obtener desde git o usar fallback
data["author_name"] = get_git_config_value("user.name", default_name)
data["author_email"] = get_git_config_value("user.email", default_email)

# Guardar el archivo actualizado
config_path.write_text(json.dumps(data, indent=4))
