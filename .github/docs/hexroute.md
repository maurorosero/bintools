# 📚 Documentación: hexroute

[⬅️ Volver al Índice Principal](/home/mrosero/bin/README.md)

## Descripción

`hexroute` es un script bash que convierte direcciones IPv4 a formato hexadecimal, lo cual es útil para configuración de tablas de ruteo en sistemas Linux.

## Características

- Convierte direcciones IPv4 a formato hexadecimal
- Valida formato y rango de direcciones IP
- Proporciona ejemplos de uso con comandos `ip rule` e `ip route`
- Facilita la creación de políticas de ruteo avanzadas

## Sintaxis

```bash
hexroute <dirección-ip>
```

## Ejemplos de Uso

### Conversión Básica

```bash
$ hexroute 192.168.1.1
IP: 192.168.1.1
Hex: 0xC0A80101

Para uso en ip rule:
ip rule add from 192.168.1.1/32 table 200 prio 200
ip rule add to 192.168.1.1/32 table 200 prio 200

Para uso en ip route:
ip route add default via [gateway] dev [interface] table 200
```

### Configuración de Ruteo Basada en Origen

Este ejemplo muestra cómo utilizar la salida de `hexroute` para configurar reglas de enrutamiento basadas en origen:

```bash
# Convertir la IP a formato hexadecimal
$ hexroute 10.0.0.5

# Utilizar la información proporcionada para crear reglas de ruteo
$ ip rule add from 10.0.0.5/32 table 100 prio 100
$ ip route add default via 192.168.1.1 dev eth0 table 100
```

## Casos de Uso Comunes

- Configuración de políticas de ruteo avanzadas
- Ruteo basado en dirección IP de origen o destino
- Configuración de múltiples proveedores de Internet (Multi-homing)
- Segregación de tráfico para VPNs o redes específicas

## Notas Técnicas

- El script valida que la dirección IP tenga el formato correcto (cuatro octetos separados por puntos)
- Verifica que cada octeto esté dentro del rango válido (0-255)
- No soporta direcciones IPv6