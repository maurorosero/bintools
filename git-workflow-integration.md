# Git Workflow Integration - Branch Workflow Validator

## 🔄 Integración del Branch Workflow Validator en el Flujo Git

### 📊 Matriz de Integración por Contexto

| Punto de Integración | LOCAL | HYBRID | REMOTE | Propósito |
|---------------------|--------|---------|---------|-----------|
| **pre-commit**      | ❌     | ⚠️      | ✅      | Validar naming, conflicts |
| **pre-push**        | ⚠️     | ✅      | ✅      | Proteger ramas, upstream |
| **CI/CD Pipeline**  | ❌     | ❌      | ✅      | Validación remota |
| **PR Checks**       | ❌     | ❌      | ✅      | Validación de merge |

### 🎯 Configuración por Contexto

#### **LOCAL Context** (Solo advertencias)
```bash
# Integración mínima - solo pre-push con warnings
.git/hooks/pre-push:
  python branch-workflow-validator.py push || echo "Warning: Validation failed but allowing push"
```

#### **HYBRID Context** (Validación moderada)
```bash
# pre-commit: warnings
.git/hooks/pre-commit:
  python branch-workflow-validator.py commit || echo "Warning logged"

# pre-push: bloqueo en ramas protegidas
.git/hooks/pre-push:
  python branch-workflow-validator.py push --target-branch $target
```

#### **REMOTE Context** (Validación estricta)
```bash
# pre-commit: bloqueo estricto
.git/hooks/pre-commit:
  python branch-workflow-validator.py commit

# pre-push: bloqueo estricto
.git/hooks/pre-push:
  python branch-workflow-validator.py push --target-branch $target

# CI/CD: validación adicional
.github/workflows/validate.yml:
  python branch-workflow-validator.py push --strict
```

## 🛠️ Implementación Práctica

### 1. **Integración con pre-commit framework**

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: branch-validator-commit
        name: Branch Workflow Validator (Commit)
        entry: python branch-workflow-validator.py commit
        language: system
        stages: [commit]
        pass_filenames: false
        
      - id: branch-validator-push
        name: Branch Workflow Validator (Push)
        entry: python branch-workflow-validator.py push
        language: system
        stages: [push]
        pass_filenames: false
```

### 2. **Integración con GitHub Actions**

`.github/workflows/branch-validation.yml`:
```yaml
name: Branch Workflow Validation

on:
  push:
    branches: ['**']
  pull_request:
    branches: [main, develop]

jobs:
  validate-workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install colorama
          
      - name: Validate Branch Workflow
        run: |
          if [ "${{ github.event_name }}" == "pull_request" ]; then
            python branch-workflow-validator.py merge --target-branch ${{ github.base_ref }}
          else
            python branch-workflow-validator.py push --target-branch ${{ github.ref_name }}
          fi
```

### 3. **Integración con GitLab CI**

`.gitlab-ci.yml`:
```yaml
validate-workflow:
  stage: validate
  image: python:3.11-slim
  before_script:
    - pip install colorama
  script:
    - |
      if [ "$CI_PIPELINE_SOURCE" == "merge_request_event" ]; then
        python branch-workflow-validator.py merge --target-branch $CI_MERGE_REQUEST_TARGET_BRANCH_NAME
      else
        python branch-workflow-validator.py push --target-branch $CI_COMMIT_REF_NAME
      fi
  rules:
    - if: $CI_PIPELINE_SOURCE == "push"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### 4. **Hook Scripts Personalizados**

#### `install-git-hooks.py`:
```python
#!/usr/bin/env python3
"""Instalar hooks de Git automáticamente según contexto detectado."""

import os
import stat
from pathlib import Path

def install_hooks():
    # Detectar contexto usando el validador
    result = subprocess.run([
        "python", "branch-workflow-validator.py", "status"
    ], capture_output=True, text=True)
    
    if "REMOTE" in result.stdout:
        install_strict_hooks()
    elif "HYBRID" in result.stdout:
        install_moderate_hooks()
    else:
        install_permissive_hooks()

def install_strict_hooks():
    # Pre-commit estricto
    pre_commit = """#!/bin/bash
python branch-workflow-validator.py commit
exit $?
"""
    
    # Pre-push estricto
    pre_push = """#!/bin/bash
target_branch=$(git rev-parse --abbrev-ref @{u} 2>/dev/null | cut -d'/' -f2)
python branch-workflow-validator.py push --target-branch "$target_branch"
exit $?
"""
    
    write_hook("pre-commit", pre_commit)
    write_hook("pre-push", pre_push)

def write_hook(hook_name, content):
    hook_path = Path(".git/hooks") / hook_name
    hook_path.write_text(content)
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
```

## 🚦 Flujo de Validación Completo

### **Desarrollador Local**:
1. `git add files` → ✅ Sin validación
2. `git commit` → 🔍 **pre-commit validation**
3. `git push` → 🔍 **pre-push validation**

### **CI/CD Pipeline**:
1. Push/PR trigger → 🔍 **CI validation**
2. Branch rules check → 🔍 **PR validation**
3. Merge validation → 🔍 **merge validation**

### **Flujo de Escalación**:
```
LOCAL     →  Warnings only
   ↓
HYBRID    →  Moderate blocking  
   ↓
REMOTE    →  Strict blocking + CI
```

## 📋 Comandos de Instalación

### **Instalación Automática**:
```bash
# Detectar contexto e instalar hooks apropiados
python branch-workflow-validator.py install-hooks

# Instalar en pre-commit framework
pre-commit install
pre-commit install --hook-type pre-push

# Verificar instalación
python branch-workflow-validator.py status
```

### **Instalación Manual por Contexto**:
```bash
# LOCAL (permisivo)
echo 'python branch-workflow-validator.py push || true' > .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# HYBRID (moderado)
echo 'python branch-workflow-validator.py commit || true' > .git/hooks/pre-commit
echo 'python branch-workflow-validator.py push' > .git/hooks/pre-push
chmod +x .git/hooks/pre-*

# REMOTE (estricto)
echo 'python branch-workflow-validator.py commit' > .git/hooks/pre-commit
echo 'python branch-workflow-validator.py push' > .git/hooks/pre-push
chmod +x .git/hooks/pre-*
```

## 🔧 Configuración Avanzada

### **Override Temporal**:
```bash
# Saltarse validación una vez
git commit --no-verify
git push --no-verify

# Forzar validación estricta
python branch-workflow-validator.py commit --strict
```

### **Configuración por Proyecto**:
```bash
# .git/config
[branchvalidator]
    level = strict
    enforce-naming = true
    require-pr = true
```

## 📊 Monitoreo y Métricas

### **Logs de Validación**:
```bash
# Ver historial de validaciones
git log --grep="validation"

# Estadísticas de bloqueos
grep "validation failed" .git/logs/refs/heads/*
```

### **Dashboard de Compliance**:
- Porcentaje de commits validados
- Bloqueos por tipo de validación
- Adopción por contexto de proyecto 