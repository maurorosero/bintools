# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v14.6.0] - 2025-06-18

### Added
- 🎉 **Automated Documentation Generation**: Auto-generation of CONTRIBUTING.md using hooks analyzer and CI/CD pipeline integration
- 📋 **Enhanced Project Templates**: Comprehensive template system for project scaffolding and configuration management

### Fixed
- 🐛 **Version Management**: Improved consistency in tag usage and proper version distribution in CHANGELOG generation
- 🔧 **CI/CD Pipeline**: Fixed automated release workflow and version tagging issues

## [v14.5.0] - 2025-06-18

### Added
- 🎯 **Commit Standards & Quality Control**
  - Semantic commit format configuration with commitlint integration
  - Advanced template management system for project scaffolding
  - Branch workflow validator with pre-commit hook integration
  - Comprehensive Git Branch Tools ecosystem with multi-project support

- 🔐 **Security & Token Management**
  - Secure token management with libsecret and libsecret-tools
  - Multi-platform API support for GitLab, Gitea, Forgejo, and Atlassian
  - Enhanced git-tokens.py with optional user handling and graceful interruption management

- 🚀 **CI/CD & Integration Management**
  - Complete CI/CD configuration manager with multi-language detection
  - Quality manager integration with independent configuration system
  - Automated metrics and badges system for all supported platforms
  - Branch state synchronization and protection management

- 📚 **Documentation & Code Generation**
  - Advanced docgen system with configuration management
  - File header validation and automatic metadata updates
  - Comprehensive versioning system with repository-wide analysis
  - Automated changelog generation with AI-powered improvements

- 📄 **License & Legal Compliance**
  - Automated license installation and replacement system
  - Support for established licenses with official texts
  - AI-generated license options with proper attribution

### Changed
- ⚡ **Development Workflow Improvements**
  - Streamlined commitlint configuration with dynamic tag reading
  - Enhanced pre-commit hook organization by functional groups
  - Improved template system with Jinja2 integration for dynamic generation
  - Comprehensive manual and documentation updates for Git Branch Tools

- 🔧 **Code Quality & Standards**
  - Automated code formatting and linting corrections
  - Enhanced cursor-mdc rules for bash, JavaScript, Python, and TypeScript
  - Improved docstring standards following Google/PEP-257 conventions
  - Dynamic Cursor integration with commitlint for better developer experience

- 🏗️ **Project Structure & Organization**
  - Reorganized configuration files in scaffold/ directory structure
  - Consolidated hooks and CI/CD configurations
  - Improved file header management with automatic date updates
  - Enhanced project metadata handling and version control

- 📊 **Monitoring & Analytics**
  - Advanced branch state management with WIP/MERGED/DELETED states
  - Improved repository metrics and contributor tracking
  - Enhanced quality validation and protection mechanisms

### Deprecated
- ⚠️ **Legacy System Cleanup**: Removed outdated legacy files and backup systems in favor of new standardized approach

### Fixed
- 🐛 **Critical Bug Fixes**
  - Resolved execution permissions and false positive secret detection issues
  - Fixed commitlint wrapper for dynamic tag reading and semantic configuration
  - Corrected KeyError in branch status display when accessing context information
  - Improved header validation for bash, Python, and JavaScript files

- 🔧 **System Reliability**
  - Enhanced branch protection and configuration management robustness
  - Fixed file modification date updates across multiple file types
  - Improved recursive file processing in versioning system
  - Corrected GPG verification centralization in branch workflow validator

### Security
- 🔒 **Enhanced Security Measures**: Implemented comprehensive secret management with keyring integration and multi-service CLI support

### Breaking Changes
- ❌ **Branch State Management**: Complete overhaul of branch state handling with new commands for MERGED/WIP/DELETED states, including --delete, --replace options and git aliases
- ❌ **Workflow Integration**: New upstream push defaults with --no-remote flag option for better remote repository management

## [v0.0.2] - 2025-05-13

### Changed
- ⚡ **CI/CD Enhancement**: Introduced specialized workflow for ci/* branches with updated development guides and tooling

## [v0.0.1] - 2025-05-13

### Added
- 🎉 **Core Project Foundation**
  - Initial project setup with comprehensive script collection and documentation
  - Python environment management system (pymanager.sh) with virtual environment handling
  - Git workflow management tools (wfwdevs.py) with automated stash and sync capabilities
  - Email cleaning utilities and package management scripts

- 🛠️ **Development Tools & Utilities**
  - Context synchronization system for project state management
  - Comprehensive package management with support for Snap packages
  - GitHub repository creation automation (gh-newrepos.py)
  - MCP (Model Context Protocol) server management system

- 📋 **Project Management & Documentation**
  - Complete project scaffolding with promanager.py
  - Automated header management and description extraction
  - Git workflow guides and best practices documentation
  - Contribution guidelines and issue/PR templates

### Changed
- ⚡ **System Improvements**
  - Enhanced email_cleaner.py with complete refactoring for better performance
  - Improved packages.sh with colored UI and better package handling
  - Advanced pymanager.sh with global/local environment management and alias support
  - Comprehensive .gitignore and project structure optimization

- 🔧 **Workflow Enhancements**
  - Automated release workflow configuration
  - Pre-commit hooks integration for code quality
  - Commitlint implementation for standardized commit messages
  - UTF-8 encoding standardization across all scripts

### Fixed
- 🐛 **Critical Fixes**
  - Resolved pip package extraction logic in pymanager.sh
  - Fixed log file location handling for non-superuser scenarios
  - Corrected optional push logic in wfwdevs.py workflow tasks
  - Improved virtual environment tracking and .gitignore management

### Breaking Changes
- ❌ **Environment Management Overhaul**: Complete restructuring of Python environment management with new --remove-global and --remove-local interactive commands
- ❌ **Project Structure Changes**: Significant reorganization of project files and removal of deprecated context-sync.py in favor of integrated solutions

---

## Migration Notes

### Upgrading to v14.5.0+
- **Action Required**: Update your pre-commit configuration to use the new hook structure
- **Breaking**: Branch state commands have changed - update your scripts accordingly
- **Recommended**: Review new CI/CD configuration options and update your workflows

### Upgrading from v0.0.x
- **Action Required**: Python environment management commands have changed significantly
- **Breaking**: Several legacy scripts have been removed or consolidated
- **Recommended**: Review new project structure and update your local configurations

For detailed migration instructions and troubleshooting, please refer to our [Migration Guide](docs/MIGRATION.md).
