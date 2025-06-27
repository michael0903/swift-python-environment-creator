# SPEC (Swift Python Environment Creator)

A modern, ultra-fast Python project setup and dependency management tool that leverages [uv](https://github.com/astral-sh/uv) as the backend for lightning-fast performance.

## 📖 Project Origins

This project began as a solution to a common developer frustration. When I started dabbling with Python programming, I found myself constantly switching between my Windows computer at home and my macOS laptop at work. Setting up my development environment manually every time I switched machines was tedious and error-prone, and I hadn't yet learned how to use GitHub effectively to sync my progress between environments.

Initially, I thought: "If I could create a script that handles all of this setup for me, it could also help my teammates get started on their Python programming journey more easily." What started as a personal productivity tool gradually evolved as I learned more about the Python ecosystem.

Over time, I incrementally added more sophisticated tools and libraries:

- **[Loguru](https://github.com/Delgan/loguru)** for better logging capabilities
- **[Pathvalidate](https://github.com/thombashi/pathvalidate)** for robust file path handling
- **[Pytest](https://docs.pytest.org/)** for comprehensive testing support
- **[uv](https://github.com/astral-sh/uv)** (most recently) when I discovered its incredible speed advantages while adopting ConPort for Roo Code

What you see today as SPEC represents the culmination of this journey - from a simple personal script to a comprehensive, modern Python environment management tool that solves real-world development workflow challenges.

## 🚀 Why SPEC?

SPEC modernizes Python project initialization by replacing traditional Python tooling with uv, providing:

- **⚡ Lightning-fast performance** - Up to 10-100x faster than pip for dependency resolution and installation
- **🔒 Lock file support** - Reproducible builds with uv.lock
- **📦 Modern project structure** - pyproject.toml-based configuration
- **🛠️ Simplified toolchain** - Single tool for virtual environments, dependency management, and project initialization
- **🔄 Better dependency resolution** - Advanced solver for consistent environments

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [File Structure](#file-structure)
- [Comparison with Original](#comparison-with-original)
- [Migration Guide](#migration-guide)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🔧 Installation

### Prerequisites

1. **Install uv** (if not already installed):

   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or via pip
   pip install uv
   ```

2. **Verify installation**:
   ```bash
   uv --version
   ```

### Get SPEC

```bash
# Clone the repository
git clone <repository-url>
cd spec

# Or download the files directly to your project directory
```

## ⚡ Quick Start

### Basic Project Setup

```bash
# Navigate to your project directory
cd my-python-project

# Run SPEC setup script
python create_project_structure.py

# Or specify a custom project name
python create_project_structure.py --project-name my-awesome-project
```

### Install Dependencies from Code

```bash
# Scan and install dependencies found in your Python files
python scan_and_install_packages.py

# Or scan a specific directory
python scan_and_install_packages.py --scan-dir ./src
```

## 🎯 Core Features

### 1. **Ultra-Fast Project Initialization**

- Creates `.venv` virtual environment using uv
- Generates modern `pyproject.toml` configuration
- Sets up VS Code integration (settings.json, launch.json)
- Configures environment variables (.env)

### 2. **Intelligent Dependency Management**

- AST-based import scanning (no code execution)
- Automatic dependency installation via `uv add`
- Support for development dependencies
- Lock file generation for reproducible builds

### 3. **Cross-Platform Compatibility**

- Windows, macOS, and Linux support
- Platform-specific path handling
- Consistent virtual environment naming (.venv)

### 4. **Modern Python Standards**

- pyproject.toml configuration
- Hatchling build backend
- PEP 621 compliant project metadata
- Type hints throughout codebase

### 5. **Enhanced Logging & Configuration**

- Structured logging with Loguru
- UV-specific configuration helpers
- Environment detection (dev/test/prod)
- Project introspection utilities

## 📁 File Structure

```
spec/
├── create_project_structure.py   # Main setup script (UV-powered)
├── scan_and_install_packages.py  # Dependency management (UV-powered)
├── project_settings.py           # UV-specific configuration
├── spec.code-workspace            # VS Code workspace file
└── README.md                      # This documentation
```

### Generated Project Structure

After running [`create_project_structure.py`](create_project_structure.py):

```
your-project/
├── .venv/                 # Virtual environment
├── pyproject.toml         # Project configuration
├── uv.lock               # Lock file (generated on first uv sync)
├── .env                  # Environment variables
├── logs/                 # Log directory
├── .vscode/              # VS Code configuration
│   ├── settings.json
│   └── launch.json
├── test/                 # Test directory
│   └── pytest_settings.py
└── src/                  # Source code directory
    └── __init__.py
```

## 🔄 Performance Benefits

SPEC leverages uv's high-performance capabilities to deliver exceptional speed improvements over traditional Python tooling:

### Performance Comparison vs Traditional Tools

| Operation               | Traditional (pip/venv) | SPEC   | Speedup       |
| ----------------------- | ---------------------- | ------ | ------------- |
| Virtual env creation    | ~5-10s                 | ~1-2s  | 3-5x faster   |
| Dependency installation | ~30-60s                | ~3-10s | 6-20x faster  |
| Dependency resolution   | ~10-30s                | ~1-3s  | 10-30x faster |
| Project sync            | N/A                    | ~2-5s  | New feature   |

### Feature Advantages

| Feature                   | Traditional Approach      | SPEC                             |
| ------------------------- | ------------------------- | -------------------------------- |
| **Virtual Environment**   | venv module               | uv venv (faster)                 |
| **Dependency Management** | pip                       | uv add/sync (10-100x faster)     |
| **Project Configuration** | setup.py/requirements.txt | pyproject.toml (modern standard) |
| **Lock Files**            | ❌ No lock files          | ✅ uv.lock for reproducibility   |
| **Dependency Resolution** | pip (basic)               | uv resolver (advanced)           |
| **Installation Speed**    | Standard pip speed        | Up to 100x faster                |
| **Build System**          | setuptools                | hatchling (modern)               |
| **Python Support**        | 3.7+                      | 3.8+ (following uv requirements) |
| **Configuration**         | Basic setup               | Enhanced project_settings.py     |

## 📖 Migration Guide

### From Traditional Python Setup

1. **Install uv** (see [Installation](#installation))

2. **Backup your current project**:

   ```bash
   cp -r your-project your-project-backup
   ```

3. **Copy SPEC files**:

   ```bash
   # Copy SPEC files to your project
   cp create_project_structure.py your-project/
   cp scan_and_install_packages.py your-project/
   cp project_settings.py your-project/
   ```

4. **Migrate environment**:

   ```bash
   # Remove old virtual environment
   rm -rf .win_env .mac_env venv

   # Run SPEC setup
   python create_project_structure.py
   ```

5. **Migrate dependencies**:

   ```bash
   # If you have requirements.txt
   uv add -r requirements.txt

   # Or scan your code
   python scan_and_install_packages.py
   ```

6. **Update imports** (if using config module):

   ```python
   # Traditional setup
   from config import get_logger

   # SPEC
   from project_settings import get_logger
   ```

### From requirements.txt to pyproject.toml

If you have existing requirements.txt files, you can migrate them:

```bash
# Install from requirements.txt
uv add -r requirements.txt

# For development dependencies
uv add --dev -r requirements-dev.txt
```

The dependencies will be automatically added to your pyproject.toml.

## 📚 Usage Examples

### Example 1: New Project Setup

```bash
# Create a new directory
mkdir my-ai-project
cd my-ai-project

# Initialize with SPEC
python ../create_project_structure.py --project-name my-ai-project

# Add some dependencies
uv add numpy pandas scikit-learn
uv add --dev pytest black

# Your project is ready!
```

### Example 2: Existing Project Migration

```bash
# In your existing project directory
python create_project_structure.py

# Scan existing code for dependencies
python scan_and_install_packages.py

# Sync environment
uv sync
```

### Example 3: Custom Configuration

```python
# In your code, use the enhanced config
from project_settings import get_logger, get_project_info

# Get a configured logger
logger = get_logger("my_module")
logger.info("Starting application")

# Get project information
info = get_project_info()
print(f"Project: {info['name']} v{info['version']}")
```

### Example 4: VS Code Integration

The setup automatically configures VS Code for your UV environment:

```json
// .vscode/settings.json (auto-generated)
{
  "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true
}
```

## ⚙️ Configuration

### project_settings.py Features

The enhanced configuration module provides:

```python
from project_settings import (
    get_logger,           # Enhanced Loguru logger
    check_uv_installation, # UV availability check
    get_uv_python_path,   # Path to UV Python executable
    is_uv_project,        # Check if current dir is UV project
    sync_uv_environment,  # Sync pyproject.toml with environment
    get_project_info,     # Comprehensive project information
    is_development_mode,  # Environment detection
)
```

### pyproject.toml Configuration

The generated pyproject.toml includes:

```toml
[project]
name = "your-project"
version = "0.1.0"
description = "Project description"
requires-python = ">=3.8"
dependencies = [
    # Your dependencies here
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    # Development dependencies
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

## 🔧 Troubleshooting

### Common Issues

1. **uv not found**

   ```bash
   # Ensure uv is in your PATH
   export PATH="$HOME/.cargo/bin:$PATH"
   # Or reinstall uv
   ```

2. **Permission errors on Windows**

   ```bash
   # Run PowerShell as administrator
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Virtual environment not activating**

   ```bash
   # Manually activate if needed
   # Windows
   .venv\Scripts\activate
   # Unix
   source .venv/bin/activate
   ```

4. **Dependencies not installing**
   ```bash
   # Check uv sync
   uv sync
   # Or force reinstall
   uv sync --reinstall
   ```

### Debug Mode

Enable debug logging:

```python
from project_settings import get_logger
logger = get_logger("debug", log_file_name_suffix="debug")
logger.debug("Debug information here")
```

### Check Installation

Verify your UV installation:

```bash
# Check UV version
uv --version

# Check project status
uv pip list

# Verify virtual environment
uv venv --help
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code passes linting (black, flake8)
5. Submit a pull request

### Development Setup

```bash
# Clone and setup for development
git clone <repository-url>
cd spec

# Create development environment
uv venv
uv sync
uv add --dev pytest black flake8 mypy

# Run tests
pytest

# Format code
black .
```

## 📜 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [Astral](https://astral.sh/) team for creating uv
- Python community for modern packaging standards
- Contributors to the Python packaging ecosystem

## 🔗 Related Projects

- [uv](https://github.com/astral-sh/uv) - Ultra-fast Python package manager
- [pyproject.toml specification](https://peps.python.org/pep-0621/) - Modern Python project metadata
- [Hatchling](https://hatch.pypa.io/latest/) - Modern Python build backend

---

**Ready to experience the speed of modern Python development? Try SPEC today! ⚡**
