# 🛠️ Utilitarios Personales de Mauro Rosero P.

Colección de scripts y herramientas para automatizar tareas y mejorar la productividad.

## 🚀 Inicio Rápido

Para comenzar a usar estas utilidades:

```bash
# Configuración permanente (recomendado)
~/bin/binsetup.sh --persistent

# O solo para la sesión actual
source ~/bin/binsetup.sh
```

## 📋 Índice de Aplicaciones

### 💻 Bash Scripts

| Script | Actualización | Descripción |
|:-------|:-------------:|:------------|
| `binsetup.sh` | 2025-04-24 | ✨ Maneja `~/bin` en el PATH.<br>• Temporal: `source binsetup.sh`<br>• Desactivar: `source binsetup.sh --disable`<br>• Permanente: `./binsetup.sh --persistent`<br>• Remover: `./binsetup.sh --remove` |
| `hexroute` | 2025-03-19 | 🔄 Convierte IPv4 a formato hexadecimal para tablas de ruteo.<br>• Uso: `hexroute <dirección-ip>` |
| `packages.sh` | 2025-04-25 | 📦 Gestiona paquetes base en múltiples sistemas operativos.<br>• Instalar: `sudo packages.sh --install`<br>• Actualizar: `sudo packages.sh --update`<br>• Solo SOPS: `sudo packages.sh --install --sops` |
| `pymanager.sh` | 2025-05-26 | 🐍 Gestiona entornos virtuales de Python.<br>• Crear: `pymanager.sh create <nombre> [reqfile]`<br>• Instalar: `pymanager.sh --install`<br>• Actualizar: `pymanager.sh --update <nombre> [pkg]` |
| `videoset.sh` | 2025-04-24 | 🖥️ Configura resolución de pantalla 1600x900@60Hz.<br>• Uso básico: `videoset.sh`<br>• Auto-detección: `videoset.sh --auto` |

### 🐍 Python Scripts

| Script | Actualización | Descripción |
|:-------|:-------------:|:------------|
| `email_cleaner` | 2025-04-24 | 📧 Gestor de correos para categorización y limpieza automática.<br>• Categoriza emails por tema, remitente y fecha<br>• Genera reportes CSV de correos por categoría<br>• Función para eliminar correos automáticamente |
| `mcp_manager.py`| 2025-05-26 | 🖥️ Gestor de servidores MCP concurrentes.<br>• Configura servidores desde archivo YAML<br>• Asigna puertos automáticamente<br>• Ejecuta servidores node/python en paralelo |

### 📦 Binarios Ejecutables

| Binario | Actualización | Descripción |
|:--------|:-------------:|:------------|
| | | |

### 📚 Librerías

| Librería | Actualización | Descripción |
|:---------|:-------------:|:------------|
| | | |

### 🧰 Otros Recursos

| Recurso | Actualización | Descripción |
|:--------|:-------------:|:------------|
| | | |

## 📖 Documentación

Para información detallada sobre cada herramienta, consulte los documentos en la carpeta [`docs/`](docs/):

- [Documentación de binsetup.sh](docs/binsetup.md)
- [Documentación de hexroute](docs/hexroute.md)
- [Documentación de packages.sh](docs/packages.md)
- [Documentación de videoset.sh](docs/videoset.md)
- [Documentación de email_cleaner](docs/email_cleaner.md)
- [Documentación de mcp_manager.py](docs/mcp_manager.md)
- [Documentación de pymanager.sh](docs/pymanager.md)
- [Documentación de requirements.def](docs/requirements.md)

## 👥 Créditos

| Script | Autor | Colaboradores |
|:-------|:------|:--------------|
| `binsetup.sh` | Mauro Rosero P. | |
| `hexroute` | Karl McMurdo (2005-2015) | Mauro Rosero P. (adaptación) |
| `packages.sh` | Mauro Rosero P. | |
| `pymanager.sh` | Mauro Rosero P. | |
| `videoset.sh` | Mauro Rosero P. | |
| `email_cleaner` | Mauro Rosero P. | |
| `mcp_manager.py` | Mauro Rosero P. | |

## 📝 Notas

- ✅ Herramientas diseñadas para uso personal
- 🔄 Actualizaciones periódicas según necesidades
- 💡 Para sugerencias o problemas, contactar a Mauro Rosero P. <mauro.rosero@gmail.com>

