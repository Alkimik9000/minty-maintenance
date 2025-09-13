# 🖥️ Mint Maintenance Script

A comprehensive system maintenance tool for Linux Mint 22 that keeps your system clean, updated, and running smoothly.

## ✨ Features

- **System Updates**: APT packages, security patches, and kernel management
- **Application Updates**: Flatpak, Snap, Homebrew, and Python tools
- **Cleanup Operations**: Logs, caches, Docker containers, orphaned packages
- **Health Monitoring**: Disk health, system services, GPU status
- **Space Recovery**: Typically frees 5-30GB through intelligent cleanup
- **User-Friendly Reports**: Clear explanations of every action taken

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/minty-maintenance.git
cd minty-maintenance

# Run full maintenance
bash mint-maintainer.sh

# Run in test mode (no changes made)
bash mint-maintainer.sh dry-run
```

## 📋 What It Does

The script performs 20+ maintenance tasks organized into categories:

### 🔧 System Maintenance
- Creates safety checkpoint (Timeshift)
- Updates core system packages (APT)
- Manages old kernels
- Updates device firmware
- Optimizes SSD performance

### 📱 Application Management  
- Updates Flatpak applications
- Updates Snap packages
- Checks Homebrew tools
- Updates Python packages
- Identifies standalone apps needing manual updates

### 🧹 Cleanup Operations
- Removes orphaned packages
- Cleans system logs
- Cleans Docker containers and images
- Performs deep clean with BleachBit
- Updates file search database

### 🏥 Health Checks
- Monitors disk health
- Checks system services
- Verifies GPU status
- Confirms automatic updates are enabled

## 📊 Sample Output

A typical run might free up significant space:

```
📊 Space Summary:
   🎉 Freed up approximately 27,263MB!
   Available space: 142G

📋 Overall Assessment:
   🌟 Your system is in excellent shape!
   All maintenance tasks completed successfully.
```

See [REPORT_SAMPLE.md](REPORT_SAMPLE.md) for a complete example.

## 🏗️ Architecture

The project uses a modular Python architecture:

```
minty-maintenance/
├── mint-maintainer.sh          # Main entry point (bash wrapper)
├── mint-maintainer-modular.py  # Python orchestrator
├── scripts/
│   ├── system/                 # System updates and maintenance
│   ├── apps/                   # Application updates
│   ├── cleanup/                # Cleanup operations
│   ├── health/                 # Health checks
│   └── utils/                  # Common utilities
└── reports/                    # Generated maintenance reports
```

## 🛠️ Requirements

- Linux Mint 22 (or Ubuntu 24.04 base)
- Python 3.x
- Administrator (sudo) access
- ~30 minutes for full maintenance

## 📖 Documentation

- [CHANGELOG.md](CHANGELOG.md) - Version history
- [RULES.md](RULES.md) - Development guidelines
- [MIGRATIONS.md](MIGRATIONS.md) - Upgrade instructions
- [REPORT_SAMPLE.md](REPORT_SAMPLE.md) - Example output

## 🤝 Contributing

Contributions are welcome! Please:

1. Follow the coding standards in [RULES.md](RULES.md)
2. Use conventional commits
3. Test in dry-run mode first
4. Update documentation as needed

## ⚠️ Safety

- Always backs up current state before making changes
- Dry-run mode available for testing
- Detailed logging of all operations
- Safe defaults for all cleanup operations

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built for the Linux Mint community to make system maintenance accessible to everyone.