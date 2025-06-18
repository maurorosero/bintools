# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v14.5.0] - 2025-06-18

### 🎉 Added

#### Development Tools & Quality Assurance
- **Semantic Commit System**: Configured semantic format for commitlint with dynamic tag reading and professional templates
- **Pre-commit Hooks Integration**: Comprehensive pre-commit hook system with Branch Workflow Validator and organized hook groups
- **Git Branch Tools Ecosystem**: Complete multi-project support system for branch management with intelligent context detection
- **Quality Management System**: Integrated QualityManager with independent configuration and CI/CD pipeline enhancements
- **Multi-language CI/CD Detection**: Enhanced CI/CD integrator with automatic language detection and critical validations

#### Security & Token Management
- **Secure Token Management**: Added libsecret and libsecret-tools dependencies for secure token handling
- **Multi-platform API Support**: Complete APIs for GitLab, Gitea, Forgejo, Bitbucket, and Atlassian platforms
- **Enhanced Authentication**: Improved git-tokens.py with optional user parameters and graceful interruption handling

#### Documentation & Code Generation
- **Documentation Generation System**: Comprehensive docgen system with main scripts and configuration management
- **File Header Management**: Automated header validation and metadata management with @check-header integration
- **Version Analysis Tools**: File-by-file versioning analysis with repository-wide support and automatic version updates
- **Changelog Automation**: Advanced changelog generation with AI-powered improvements and release automation

#### Template & Configuration Management
- **Template Management System**: Professional template system for project scaffolding and configuration
- **License Management**: Automated license installation with established licenses and AI-generated license prompts
- **Dynamic Configuration**: Jinja2-based .pre-commit-config.yaml generation with intelligent template processing

### ⚡ Changed

#### Infrastructure & Workflow Improvements
- **Commitlint Enhancement**: Updated wrapper scripts, configuration templates, and semantic commit workflows
- **Project Structure Reorganization**: Moved configuration files to .githooks/ and scaffold/ directories for better organization
- **Branch Management Optimization**: Intelligent branch state management with automatic context detection and upstream push defaults
- **Metrics & Monitoring**: Implemented adaptive metrics system with platform-specific workflows and badge generation

#### Code Quality & Standards
- **Cursor Integration**: Enhanced Cursor IDE integration with dynamic commitlint support and MDC coding standards
- **Multi-language Standards**: Comprehensive coding rules for Bash, JavaScript, Python, and TypeScript
- **Header Standardization**: Unified header format across all script types with automatic date updates
- **Documentation Standards**: Google/PEP-257 docstring standards and improved code documentation

#### User Experience Enhancements
- **Improved CLI Interfaces**: Enhanced visualization for configuration tools with minimalist design
- **Better Error Handling**: Robust error handling and user feedback across all tools
- **Streamlined Workflows**: Simplified installation processes and improved command-line experiences

### ⚠️ Deprecated
- **Legacy File Cleanup**: Removed obsolete legacy files and backup systems in favor of new architecture

### 🐛 Fixed

#### Security & Authentication
- **Permission Corrections**: Fixed execution permissions and resolved false positives in secret detection
- **GPG Verification**: Centralized GPG verification in branch-workflow-validator with improved reliability

#### Core Functionality
- **Branch Protection**: Enhanced branch protection management with robust validation and configuration handling
- **Context Information**: Resolved KeyError in 'show_status' command by improving context data collection
- **Header Processing**: Fixed header validation and automatic date modification across all supported file types
- **Version Management**: Corrected --update-all logic for individual file processing with proper depth handling

#### Development Tools
- **Commitlint Robustness**: Improved commitlint validation with better configuration handling
- **File Processing**: Enhanced file detection and processing for header validation across Bash, Python, and JavaScript
- **Template Generation**: Fixed dynamic template generation and configuration file processing

### 💥 Breaking Changes
- **Branch State Management**: Complete redesign of branch state system with MERGED/WIP/DELETED states, --delete and --replace commands, and new git aliases
- **Repository Structure**: Major reorganization of configuration files and tool locations
- **API Changes**: Updated APIs for multi-platform integration with new authentication methods

---

## [v0.0.2] - 2025-05-13

### ⚡ Changed
- **CI Workflow Enhancement**: Introduced specialized flow for ci/* branches with updated development guides and tooling

---

## [v0.0.1] - 2025-05-13

### 🎉 Added

#### Core Development Tools
- **Python Environment Management**: Comprehensive pymanager.sh with virtual environment creation, package management, and global/local installation support
- **Project Management**: Introduced project_manager.py (later promanager.py) with TOML configuration support and automated project structure initialization
- **Git Workflow Tools**: Created wfwdevs.py for Git workflow management with interactive stash handling and develop branch synchronization

#### Infrastructure & Setup
- **Email Management**: Complete email_cleaner.py solution with documentation and configuration examples
- **Package Management**: Advanced packages.sh script with Snap support, package definitions, and colored UI
- **MCP Server Management**: Tools for Model Context Protocol server management and configuration

#### Documentation & Standards
- **Comprehensive Documentation**: Detailed guides for all tools including user manuals, contribution guidelines, and workflow documentation
- **Template System**: GitHub templates for issues, pull requests, and contributions
- **Code Standards**: Established .cursorrules for consistent coding practices and documentation standards

### ⚡ Changed

#### Project Evolution
- **Initial Setup**: Complete project foundation with scripts, documentation, and development environment
- **Tool Refinement**: Continuous improvement of package management, Python environment handling, and Git workflow tools
- **Structure Optimization**: Multiple reorganizations for better maintainability and user experience
- **Feature Enhancement**: Regular updates to functionality based on usage patterns and requirements

#### Development Workflow
- **Release Automation**: Implemented automated release workflows with proper versioning
- **Branch Protection**: Established branch protection rules and contribution workflows
- **CI/CD Integration**: Added continuous integration with commitlint validation and automated testing

### 🐛 Fixed
- **Environment Management**: Resolved package extraction issues and logging location problems in pymanager.sh
- **Git Workflow**: Fixed push logic for new tasks and improved error handling in wfwdevs.py
- **File Processing**: Corrected various file handling and processing issues across multiple tools

### 💥 Breaking Changes
- **Package Management**: Replaced --remove with --remove-global and interactive --remove-local commands
- **Environment Structure**: Changed virtual environment management approach with new global/local distinction
- **Tool Naming**: Renamed project_manager to promanager with updated functionality and interface

---

## Project Statistics
- **Total Commits**: 135
- **Major Versions**: 1
- **Breaking Changes**: Multiple architectural improvements
- **Security Enhancements**: Comprehensive token and authentication management
- **Documentation**: Extensive user guides and API documentation
