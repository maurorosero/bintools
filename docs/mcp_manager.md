# Documentación de `mcp_manager.py`

**Gestor de servidores MCP concurrentes.**

Este script permite gestionar múltiples servidores (Node.js, Python) definidos en un archivo de configuración YAML, ejecutándolos en paralelo y asignando puertos automáticamente.

## Uso

```bash
python mcp_manager.py [archivo_config.yaml]
```

- Si no se especifica un archivo, buscará `mcp_config.yaml` en el directorio actual.

## Configuración (YAML)

El archivo YAML debe seguir la siguiente estructura:

```yaml
servers:
  - name: server_1
    type: node # o python
    path: /ruta/a/server_1/app.js # o script.py
    # port: 8001 # Opcional, si no se especifica, se asigna automáticamente
    # env: # Opcional, variables de entorno
    #   VAR1: valor1
  - name: server_2
    type: python
    path: /ruta/a/server_2/main.py
    # ...
```

## Funcionalidades

- Lectura de configuración desde archivo YAML.
- Asignación automática de puertos si no se especifican.
- Ejecución concurrente de los servidores definidos.
- Manejo de variables de entorno por servidor.
- Registro de logs básico.

*(Esta documentación es un placeholder. Necesita ser expandida con más detalles sobre la implementación y opciones avanzadas.)*
