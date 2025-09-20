# Guía de Contribución de Documentación - bintools

> **📖 [← Volver al README principal](../README.md)**

## 📖 Introducción

Esta guía te ayuda a contribuir con documentación al proyecto bintools de forma efectiva y consistente.

## 🎯 Tipos de Contribuciones

### 📝 Documentación de Herramientas

- **Nuevas guías**: Crear `docs/[herramienta].md` para herramientas sin documentar
- **Mejoras**: Expandir secciones existentes, agregar ejemplos, mejorar claridad
- **Troubleshooting**: Agregar problemas comunes y soluciones

### 📚 Documentación del Proyecto

- **README.md**: Mejorar estructura, agregar secciones, mejorar navegación
- **Guías de instalación**: Mejorar instrucciones para diferentes sistemas
- **Casos de uso**: Agregar ejemplos prácticos y casos reales

### 🌐 Traducciones

- **Documentación en otros idiomas**: Mantener consistencia con la versión en español
- **Localización**: Adaptar ejemplos y referencias culturales

## 🔧 Estilo y Formato

### Estructura Estándar

```markdown
# Título de la Guía

> **📖 [← Volver al README principal](../README.md)**

## 📖 Introducción
## 🚀 Instalación/Uso
## 📝 Ejemplos
## 🚨 Solución de Problemas
## 📞 Soporte

---

**📖 [← Volver al README principal](../README.md)**
```

### Convenciones

- **Emojis en títulos**: Para navegación visual
- **Enlaces de retorno**: Siempre al README principal
- **Ejemplos funcionales**: Código probado y funcional
- **Estructura consistente**: Misma organización en todas las guías

## 🚀 Proceso de Contribución

### 1. Identificación

- **Audit**: Identificar gaps, inconsistencias, información obsoleta
- **Feedback**: Recopilar problemas comunes de usuarios
- **Priorización**: Qué documentación es más crítica

### 2. Desarrollo

- **Crear/Editar**: Seguir el formato estándar
- **Validar**: Verificar que la información es correcta
- **Probar**: Ejecutar ejemplos y comandos

### 3. Integración

- **Enlaces**: Agregar referencias desde README.md
- **Navegación**: Asegurar enlaces bidireccionales
- **Consistencia**: Mantener el estilo del proyecto

### 4. Pull Request

- **Descripción clara**: Explicar qué se agregó/mejoró
- **Ejemplos**: Incluir antes/después si es relevante
- **Validación**: Confirmar que no hay errores de linting

## ✅ Checklist de Calidad

### Contenido

- [ ] Información actualizada y precisa
- [ ] Ejemplos de código funcionales
- [ ] Sección de troubleshooting incluida
- [ ] Enlaces de retorno al README

### Formato

- [ ] Estructura estándar seguida
- [ ] Emojis en títulos para navegación
- [ ] Sin errores de linting
- [ ] Consistencia con otras guías

### Navegación

- [ ] Enlaces bidireccionales funcionando
- [ ] Referencias desde README.md actualizadas
- [ ] Enlaces internos verificados

## 🎯 Prioridades

### Alta Prioridad

1. **Documentación faltante**: Herramientas sin guías específicas
2. **Mejoras críticas**: Secciones confusas o incompletas
3. **Troubleshooting**: Expandir solución de problemas comunes
4. **Ejemplos prácticos**: Casos de uso reales

### Media Prioridad

1. **Traducciones**: Documentación en otros idiomas
2. **Tutoriales avanzados**: Guías para usuarios experimentados
3. **Integración**: Cómo usar bintools con otras herramientas
4. **Mejores prácticas**: Recomendaciones de uso

## 🔍 Herramientas Útiles

### Para Validación

```bash
# Verificar sintaxis Markdown
markdownlint docs/documentation-guide.md

# Verificar enlaces
grep -r "\[.*\](" docs/ | grep -v "http"

# Verificar estructura
grep -r "^## " docs/
```

### Para Desarrollo

- **Editor recomendado**: VS Code con extensión Markdown
- **Preview**: Usar preview integrado para verificar formato
- **Git**: Usar `git diff` para revisar cambios

## 📞 Soporte

Si tienes dudas sobre documentación:

1. **Revisar ejemplos**: Consulta documentación existente como referencia
2. **Verificar formato**: Usa `markdownlint` para validar sintaxis
3. **Probar ejemplos**: Ejecuta comandos y códigos antes de documentar
4. **Abrir Issue**: [GitHub Issues](https://github.com/maurorosero/bintools/issues) para dudas específicas

---

**📖 [← Volver al README principal](../README.md)**
