# Generador de Documentación con Claude 3.7

<!-- PARSEABLE_METADATA_START
purpose: Generador de documentación automatizado usando la API de Anthropic Claude 3.7
technology: Python, Anthropic API, YAML, Click
status: Development
PARSEABLE_METADATA_END -->

<!-- CURRENT_VERSION_PLACEHOLDER -->

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generador de documentación automatizado que utiliza la API de Anthropic Claude 3.7 para crear documentación de alta calidad para proyectos de software. Permite generar READMEs, guías de usuario y documentación de API de manera consistente y personalizable.

## Características

- 🎯 Generación de documentación basada en plantillas predefinidas
- 📝 Soporte para múltiples tipos de documentación (README, guías de usuario, API docs)
- 🔧 Configuración flexible de modelos y parámetros
- 🔐 Gestión segura de tokens de API
- 📚 Estructura de tabla de contenidos personalizable
- 🎨 Prompts del sistema y contextos configurables
- 🛠️ Interfaz de línea de comandos intuitiva

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/docgen.git
cd docgen
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura tu token de API de Anthropic:
```bash
python docgen.py config-token
```

## Uso

### Configuración del Modelo

Puedes configurar los parámetros del modelo para diferentes tipos de documentación:

```bash
# Configurar modelo por defecto
python docgen.py config-model --model claude-3-sonnet-20240229 --max-tokens 4000 --temperature 0.7

# Configurar modelo específico para READMEs
python docgen.py config-model --doc-type readme --model claude-3-sonnet-20240229 --max-tokens 4000 --temperature 0.7
```

### Generación de Documentación

Para generar documentación:

```bash
python docgen.py generate \
    --output docs/README.md \
    --toc-type readme \
    --context cli_tool \
    --custom-instructions "Incluir ejemplos específicos para Linux"
```

Puedes generar múltiples documentos en una sola ejecución:

```bash
python docgen.py generate \
    --output docs/README.md \
    --output docs/USER_GUIDE.md \
    --toc-type readme \
    --context cli_tool
```

## Estructura del Proyecto

```
.
├── docgen.py              # Script principal
├── requirements.txt       # Dependencias del proyecto
└── docs/
    └── config/
        ├── model.yaml     # Configuración de modelos
        ├── prompts/
        │   ├── system/    # Prompts del sistema
        │   └── contexts/  # Contextos de documentación
        └── toc/
            ├── base/      # Tablas de contenidos base
            └── custom/    # Tablas de contenidos personalizadas
```

## Configuración

### Modelo

El archivo `docs/config/model.yaml` permite configurar los parámetros del modelo para diferentes tipos de documentación:

```yaml
default:
  model: claude-3-sonnet-20240229
  max_tokens: 4000
  temperature: 0.7

document_types:
  readme:
    model: claude-3-sonnet-20240229
    max_tokens: 4000
    temperature: 0.7
  user_guide:
    model: claude-3-sonnet-20240229
    max_tokens: 8000
    temperature: 0.5
  api_docs:
    model: claude-3-sonnet-20240229
    max_tokens: 6000
    temperature: 0.3
```

### Prompts

Los prompts del sistema y contextos se definen en archivos YAML bajo `docs/config/prompts/`:

- `system/`: Contiene los prompts base para cada tipo de documentación
- `contexts/`: Define contextos específicos (ej: cli_tool, library)

### Tablas de Contenidos

Las estructuras de las tablas de contenidos se definen en archivos YAML bajo `docs/config/toc/`:

- `base/`: Contiene las estructuras base para cada tipo de documentación
- `custom/`: Permite definir estructuras personalizadas

## Contribución

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## Contacto

Tu Nombre - [@tu_twitter](https://twitter.com/tu_twitter)

Link del Proyecto: [https://github.com/tu-usuario/docgen](https://github.com/tu-usuario/docgen)
