# Contribuciones binTools

¡Gracias por considerar contribuir a nuestro proyecto! 
Mantenemos estándares estrictos para garantizar claridad, mantenibilidad y calidad en toda la base de código. 
Por favor, lee y sigue estas directrices cuidadosamente.

## Flujo de trabajo general

1. Haz un fork del repositorio.
2. Crea una nueva rama para tu funcionalidad:
   git checkout -b feature/tu-nombre-de-funcionalidad
3. Sigue los estándares de codificación detallados a continuación.
4. Realiza commits atómicos (cambios pequeños y lógicos).
5. Sube tu rama y abre un pull request.

## Estándares de Codificación

### Scripts Shell (.sh)
- Usa funciones modulares para toda la lógica reutilizable.
- Maneja errores correctamente usando códigos de salida (exit codes).
- Incluye cabeceras de licencia y versión en los scripts.
- Utiliza snake_case para nombres de variables y funciones.
- Documenta el propósito de cada función con comentarios y ejemplos de uso.

### Scripts Python (.py)
- Sigue estrictamente los estándares de codificación PEP-8.
- Agrega docstrings en todas las funciones, clases y módulos.
- Maneja excepciones adecuadamente con bloques try-except.
- Asegura que los scripts terminen con códigos de salida apropiados.

### Node.js (.js, .mjs, .cjs, package.json)
- Prefiere el uso de async/await en lugar de promesas encadenadas.
- Modula el código en servicios, rutas y middlewares.
- Documenta cualquier cambio realizado en package.json, especialmente en dependencias.

### TypeScript (.ts, .tsx)
- Utiliza interfaces y tipos estrictos en lugar de any.
- Aplica tipado estricto en funciones asíncronas.
- Refactoriza para mejorar mantenibilidad sin cambiar el comportamiento externo.

### Documentación (.md, .rst, .txt, /docs/)
- Actualiza o agrega documentación cuando cambien funcionalidades.
- Mantén los manuales, tutoriales y guías claros y actualizados.
- Utiliza un formato consistente para títulos y estructura.

## Guía para Mensajes de Commit

Todos los mensajes de commit deben seguir esta estructura:

Prefijos permitidos:
- [ADDED] para nuevas funcionalidades.
- [IMPROVED] para mejoras en funcionalidades existentes.
- [FIXED] para corrección de errores.
- [REFACTORED] para refactorización de código sin cambiar la funcionalidad.
- [DOCS] para cambios exclusivamente en la documentación (manuales, tutoriales, guías).
- [SOPS] para cambios relacionados con gestión de secretos.
- [INIT] para commits iniciales del proyecto.

Reglas de Formato:
- Usa modo imperativo en los títulos (ej. "Añadir", "Mejorar", "Corregir").
- Limita el título a un máximo de 72 caracteres.
- Si el commit incluye múltiples cambios importantes, agrega un cuerpo detallado usando viñetas.

Ejemplo:

[IMPROVED] Mejorar la validación de registros de usuario

- Añadida validación de correo electrónico basada en regex
- Mejorados los mensajes de error para campos faltantes
- Actualizadas las pruebas unitarias correspondientes

## Proceso de Revisión

- Todos los pull requests requieren al menos una revisión aprobada.
- Mantén títulos y descripciones claras y descriptivas en los pull requests.
- Pull requests grandes (más de 500 líneas) deben dividirse en PRs más pequeños y enfocados.

## Notas Adicionales

- Sincroniza tu rama regularmente con la rama principal (main).
- Realiza squash de commits si es necesario para mantener un historial limpio.
- Mantén un tono profesional en todos los comentarios y documentación.

¡Gracias por ayudarnos a construir herramientas de alta calidad! 
Mantengamos la claridad, consistencia y excelencia en todo momento.
