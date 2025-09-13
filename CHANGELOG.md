# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modular architecture with separate scripts for each maintenance task
- Python-based orchestrator for better error handling and reporting
- Comprehensive utils module with type annotations
- Folder structure organized by functionality (system, apps, cleanup, health)
- Documentation files (CHANGELOG.md, RULES.md, REPORT_SAMPLE.md)
- .gitignore file for proper version control hygiene
- Machine-readable rules in JSON format

### Changed
- Refactored monolithic bash script into modular Python components
- Improved error handling with user-friendly explanations
- Enhanced reporting with better formatting and progress tracking
- Migrated from single 1500+ line script to organized module structure

### Deprecated
- Original monolithic bash script (preserved as mint-maintainer-original.sh)

### Fixed
- Chapter 1 (Timeshift checkpoint) temporarily disabled due to issues with snapshot annotation

### Security
- All sudo commands now properly validated before execution
- Improved error handling prevents partial execution on failures

## [1.0.0] - 2024-01-01

### Added
- Initial release with comprehensive system maintenance features
- Support for APT, Flatpak, Snap, and Homebrew updates
- Disk cleanup and optimization features
- System health monitoring
- User-friendly reporting system
