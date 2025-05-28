# 📋 Archivo de Requisitos Python (`requirements.def`)

Archivo de definición para los requisitos básicos en entornos virtuales de Python.

## 📝 Descripción

Este archivo contiene una lista de paquetes Python esenciales que se instalan automáticamente en los entornos virtuales creados con `pymanager.sh`. Proporciona un conjunto de herramientas comunes para desarrollo y automatización.

## 📦 Paquetes incluidos

### 🛠️ Utilidades básicas y consola

| Paquete | Versión | Descripción |
|:--------|:--------|:------------|
| `colorama` | >=0.4.4 | Colores y formato en terminal para mejor visualización de salidas |
| `dnspython` | >=2.2.0 | Librería para consultas y manipulación de DNS |

### 🌐 Procesamiento HTML y web scraping

| Paquete | Versión | Descripción |
|:--------|:--------|:------------|
| `beautifulsoup4` | >=4.11.0 | Parser de HTML/XML para extracción de datos y web scraping |
| `html2text` | >=2020.1.16 | Conversión de HTML a texto plano para extracción de contenido |
| `requests` | >=2.27.0 | Cliente HTTP para hacer peticiones a APIs y sitios web |

### 📊 Análisis de datos

| Paquete | Versión | Descripción |
|:--------|:--------|:------------|
| `pandas` | >=1.5.0 | Análisis y manipulación de datos estructurados en DataFrames |
| `python-dateutil` | >=2.8.2 | Extensiones útiles para el módulo datetime de Python |

### 🗃️ Formatos de datos y configuración

| Paquete | Versión | Descripción |
|:--------|:--------|:------------|
| `pyyaml` | >=6.0 | Manejo de archivos YAML para configuración y almacenamiento de datos |

### 🖥️ Servidores web y APIs

| Paquete | Versión | Descripción |
|:--------|:--------|:------------|
| `uvicorn` | >=0.15.0 | Servidor ASGI de alto rendimiento (usado con FastAPI/Starlette) |

## 🔄 Uso del archivo

Este archivo sirve como base para la instalación de paquetes en entornos virtuales Python:

```bash
# Creación de entorno con requisitos por defecto
pymanager.sh create miproyecto ~/bin/config/requirements.def

# Instalación del entorno por defecto
pymanager.sh --install
```

## 📝 Formato

El archivo sigue el formato estándar de `requirements.txt` de pip:

- Una línea por paquete
- Comentarios precedidos por `#`
- Restricciones de versión mediante operadores (`>=`, `==`, etc.)
- Metadatos en comentarios al inicio del archivo

## ⚙️ Personalización

Para añadir paquetes adicionales, simplemente edite el archivo añadiendo nuevas líneas con el formato:

```
nombre_paquete>=versión  # Descripción opcional del paquete
```

## 🔄 Actualizaciones

El archivo se actualiza periódicamente para incluir nuevos paquetes útiles o actualizar las versiones mínimas requeridas de los existentes.
