# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🚀 Added

#### Core Infrastructure
- **Commit Management System**: Semantic commit format configuration with commitlint integration
- **Template Management System**: Comprehensive system for managing project templates and configurations
- **Security Token Management**: Secure token handling with libsecret/libsecret-tools integration and keyring migration
- **Multi-Platform API Support**: Complete APIs for GitLab, Gitea, Forgejo, Atlassian, and Bitbucket platforms

#### Git Branch Tools Ecosystem
- **Branch Workflow Validator**: Integrated pre-commit validation system for branch workflows
- **Multi-Project Support**: Enhanced Git Branch Tools with support for multiple project configurations
- **Branch State Management**: Complete implementation of branch states (WIP, MERGED, DELETED) with aliases
- **Remote Synchronization**: Upstream push as default with `--no-remote` flag option

#### CI/CD & Quality Management
- **CICDManager**: Automated CI/CD configuration management with multi-language detection
- **QualityManager Integration**: Comprehensive code quality management system
- **Metrics & Badges System**: Adaptive metrics workflows for all supported platforms (#45)
- **Critical CI/CD Validations**: Enhanced validation system for CI/CD configurations

#### Documentation & File Management
- **Document Generation (docgen)**: Complete documentation generation system with configuration support
- **File Header Validation**: Automated validation and updating of file headers with metadata
- **Version Analysis System**:
  - Per-file and repository-wide version analysis
  - Global version management with `.project/version` support
  - Group analysis with glob patterns support
  - Recursive search with `--depth` parameter
- **License Management**: Automated installation and replacement of established licenses

### ⚡ Changed

#### Configuration & Structure Reorganization
- **Commitlint Configuration**: Enhanced templates, package.json setup, and dynamic tag reading
- **Hook System Reorganization**:
  - Moved commitlint files to `.githooks/`
  - Organized pre-commit hooks by functional groups
  - Relocated configuration files to `scaffold/` directory
- **Template System Improvements**: Simplified template manager with better format handling
- **Dynamic Configuration Generation**: Jinja2-based `.pre-commit-config.yaml` generation

#### Development Tools Enhancement
- **Cursor Integration**:
  - Minimalist MDC configuration display
  - Reorganized cursor configuration structure
  - Comprehensive coding style rules for Bash, JavaScript, Python, and TypeScript
  - Dynamic Cursor-commitlint integration
- **Git Branch Tools Manual**: Complete rewrite with real functionalities, end-to-end workflows, and troubleshooting guides
- **Code Quality Improvements**: Automatic lint corrections and enhanced validation systems

#### Security & Token Management
- **Enhanced git-tokens.py**: Optional user handling, graceful interruption management, and modular Spanish CLI
- **GPG Verification**: Centralized GPG verification in branch-workflow-validator
- **Branch Protection**: Improved management of branch protections and configurations

#### Version Management
- **Semantic Versioning Enhancement**:
  - REFACTOR now increments MINOR version in groups
  - Only RELEASE increments MAJOR version
  - Two-phase calculation for `--update-all`
  - Individual file version updates in headers

### ⚠️ Deprecated
- **Legacy File Cleanup**: Removed obsolete backup files and legacy systems

### 🐛 Fixed

#### Core System Fixes
- **Permission & Security**: Corrected execution permissions and eliminated false positives in secret detection
- **Commitlint Wrapper**: Fixed dynamic tag reading and semantic configuration updates
- **Validator Configuration**: Resolved `always_run: true` configuration issues
- **QualityManager**: Refactored for independent configuration and improved portability with relative paths

#### Branch Management Fixes
- **Context Detection**: Updated logic to match branch-git-helper behavior
- **Branch Protection**: Enhanced robustness in protection and configuration management
- **Status Display**: Fixed KeyError in 'show_status' by properly returning dynamic repository data

#### File Header Management
- **Header Validation**: Complete fix for Bash, Python, and JavaScript header detection
- **Modification Date Updates**: Resolved automatic date updating across all supported file types
- **Sed-based Updates**: Fixed file corruption issues during modification date updates

#### Version Analysis
- **Update Logic**: Corrected `--update-all` to process files individually
- **Recursive Search**: Extended `--depth` for automatic recursive search in specific files

### 💥 Breaking Changes
- **Branch State Management**: Complete redesign of branch state handling (MERGED/WIP) with new commands: `--delete`, `--replace`, and git aliases
- **State Command Implementation**: New comprehensive branch state management system that may affect existing workflows

---

## [v0.0.2] - 2025-06-18

### 🚀 Added

#### Infrastructure Foundation
- **Semantic Commit System**: Initial commitlint configuration with semantic formatting
- **Template Management**: Basic system for managing project templates
- **Security Integration**: Added libsecret and libsecret-tools for secure token management
- **Python Libraries**: Essential dependencies for secure token handling and multi-platform API support

#### Git Tools Implementation
- **Branch Workflow Validator**: Pre-commit hook integration for branch validation
- **Git Branch Tools Ecosystem**: Complete implementation of branch management tools
- **Multi-Project Support**: Enhanced tools to handle multiple project configurations
- **Token Management**: Improved git-tokens.py with optional user handling

#### Platform Integration
- **Multi-Platform APIs**: Complete implementation for GitLab, Gitea, Forgejo, and Bitbucket
- **Quality Management**: QualityManager integration for code quality assurance
- **CI/CD Management**: CICDManager implementation with multi-language detection
- **Configuration Reorganization**: Restructured existing CI/CD configurations

#### Documentation & Analysis Tools
- **Document Generation**: Core docgen scripts implementation
- **Header Validation**: File metadata validation with automatic date updates
- **Version Analysis**:
  - Per-file and repository-wide version analysis
  - Global version writing to `.project/version`
  - Pattern-based group analysis support
- **License Management**: Script for installing and replacing established licenses

### ⚡ Changed

#### Configuration Management
- **Commitlint Setup**: Added templates, package.json, and wrapper scripts
- **Pre-commit Updates**: Enhanced templates and script configurations
- **CI Flow Configuration**: Comprehensive commit flow and hook setup (multiple iterations)
- **Cursor Integration**: Installation functionality and improved MDC visualization

#### System Reorganization
- **File Structure**: Major reorganization of commitlint and configuration files
- **Hook Organization**: Grouped pre-commit hooks by functionality
- **Template System**: Improved Bash header formatting and template management
- **Security Migration**: Restructured git-tokens.py with keyring migration

#### Documentation Enhancement
- **Git Branch Tools Manual**: Complete documentation with real functionalities
- **Workflow Documentation**: Added end-to-end workflows and practical use cases
- **Quality Documentation**: Updated documentation and quality configuration

#### Development Improvements
- **Coding Standards**: Established MDC rules for multiple languages
- **Dynamic Generation**: Jinja2-based configuration generation
- **Lint Corrections**: Automatic formatting corrections application
- **Branch Management**: Intelligent system with automatic context detection

### ⚠️ Deprecated
- **Legacy Cleanup**: Removed obsolete backup and legacy files

### 🐛 Fixed

#### Core Functionality
- **Permissions**: Corrected execution permissions and secret detection false positives
- **Commitlint**: Fixed dynamic tag reading and semantic configuration
- **Validation**: Resolved validator configuration issues
- **Quality Management**: Improved portability and configuration independence

#### Branch & Context Management
- **Context Detection**: Aligned logic with branch-git-helper
- **Branch Protection**: Enhanced robustness in protection management
- **Status Display**: Fixed KeyError issues in repository data retrieval

#### File Management
- **Header Processing**: Fixed validation for Bash, Python, and JavaScript
- **Date Updates**: Resolved automatic modification date updating
- **File Integrity**: Fixed corruption issues during updates using sed

#### Version Control
- **Update Logic**: Corrected individual file processing in `--update-all`
- **Recursive Search**: Enhanced depth handling for specific file searches

### 💥 Breaking Changes
- **Branch State System**: Introduced new branch state management (MERGED/WIP) with `--delete`, `--replace` commands and git aliases
- **State Management**: Complete implementation of branch state handling that changes existing workflow patterns

---

### 📊 Release Statistics
- **Total Commits**: 130
- **Breaking Changes**: Yes - Major workflow changes in branch management
- **Security Updates**: Enhanced token management and secure storage
- **Deprecations**: Legacy file cleanup and system modernization
