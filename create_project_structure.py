#!/usr/bin/env python3
"""
SPEC - Swift Python Environment Creator
Create Project Structure Script

This script automates the creation and configuration of a modern Python project
structure using uv (ultrafast Python package manager) for both Windows and macOS/Linux.
It performs the following steps:

1.  **OS Detection:** Identifies the current operating system (Windows, macOS, Linux).
2.  **Project Initialization:** Uses uv to initialize a new Python project with pyproject.toml.
3.  **Directory Structure Creation:** Creates standard project directories:
    *   `scripts`
    *   `src/package` (with `__init__.py`)
    *   `tests`
4.  **Virtual Environment Setup:** Creates a uv-managed virtual environment (.venv).
    If an environment already exists, it is removed and recreated.
5.  **Core Dependency Installation:** Installs essential testing packages (`pytest`,
    `pytest-html`, `pytest-mock`, `loguru`, `pathvalidate`) using uv.
6.  **Configuration File Generation:** Creates dynamic configuration files tailored
    to the environment:
    *   `tests/conftest.py`: Provides pytest fixtures and configuration for testing.

**Key Features:**

*   **UV-Based:** Uses uv for ultra-fast dependency resolution and installation.
*   **Modern Project Structure:** Creates pyproject.toml-based project layout.
*   **Cross-Platform:** Works on Windows, macOS, and Linux.
*   **Automated Virtual Environment:** Creates and configures uv-managed .venv.
*   **Modern Testing Setup:** Installs `pytest` with consolidated configuration in pyproject.toml.

**Assumptions:**

*   uv is installed and accessible in the system PATH.
*   Python 3.8+ is available on the system.
*   The script is executed from the directory where the project should be created.

**Exclusions:**

*   This script does **not** create static project files like `.gitignore`, `README.md`,
    license files, or specific project code templates. These are expected to be
    added separately or extracted from an archive.

**Usage:**

1.  Ensure uv is installed: `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
2.  Navigate to the desired parent directory for your new project in the terminal.
3.  Run the script: `python create_project_structure.py`
4.  Follow the post-setup instructions printed to the console.

Author: Michael Fu
Date: 2025/06/27
Release: 1.0
"""

import os
import platform
import subprocess
import sys
import shutil
import logging
import datetime
import inspect
import json

# --- Attempt to import loguru, fallback to standard logging if not available ---
try:
    from loguru import logger
    from project_settings import get_logger

    logger = get_logger(__name__)
    logger.info("Using loguru for logging.")
except ImportError:
    # Custom logging setup to mimic loguru style
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with colors and loguru-style formatting"""

        # ANSI color codes
        COLORS = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[34m",  # Blue
            "SUCCESS": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow/Orange
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[41m\033[37m",  # White on Red background
            "RESET": "\033[0m",  # Reset
            "TIMESTAMP": "\033[32m",  # Green for timestamp
            "SOURCE": "\033[36m",  # Cyan for source
        }

        def format(self, record):
            # Get calling frame info
            frame = inspect.currentframe().f_back
            while frame:
                if frame.f_code.co_filename != __file__:
                    break
                frame = frame.f_back

            module_name = record.module
            func_name = record.funcName
            lineno = record.lineno

            # Format timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Get log level with consistent padding (8 chars)
            level_name = record.levelname
            level_padded = f"{level_name:<8}"

            # Source info
            source = f"{module_name}:{func_name}:{lineno}"

            # Format the message with colors
            color = self.COLORS.get(level_name, self.COLORS["RESET"])
            message = record.getMessage()

            # Construct the formatted log message
            formatted_message = (
                f"{self.COLORS['TIMESTAMP']}{timestamp}{self.COLORS['RESET']} | "
                f"{color}{level_padded}{self.COLORS['RESET']} | "
                f"{self.COLORS['SOURCE']}{source}{self.COLORS['RESET']} - "
                f"{color}{message}{self.COLORS['RESET']}"
            )

            return formatted_message

    # Set up the custom logger
    def setup_logger():
        # Add SUCCESS level between INFO and WARNING
        logging.SUCCESS = 25  # Between INFO(20) and WARNING(30)
        logging.addLevelName(logging.SUCCESS, "SUCCESS")

        # Add success method to Logger class
        def success(self, message, *args, **kwargs):
            if self.isEnabledFor(logging.SUCCESS):
                self._log(logging.SUCCESS, message, args, **kwargs)

        # Add the success method to the Logger class
        logging.Logger.success = success

        # Create logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = ColoredFormatter()
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

        return logger

    # Initialize logger
    logger = setup_logger()
    logger.warning("loguru not found. Using standard logging as fallback.")

# --- Constants and Configuration ---
# These files will be created by the script
DYNAMIC_FILES = [
    "pyproject.toml",
    "tests/conftest.py",
]

# --- Helper Functions ---


def check_uv_installed():
    """Check if uv is installed and accessible."""
    try:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, check=True
        )
        logger.info(f"Found uv: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("uv is not installed or not accessible in PATH.")
        logger.error("Please install uv first:")
        logger.error("  pip install uv")
        logger.error("  or visit: https://github.com/astral-sh/uv")
        return False


def create_directory(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.success(f"Created directory: {path}")
    else:
        logger.info(f"Directory already exists: {path}")


def create_file(path, content):
    """Create a file with the given content."""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.success(f"Created file: {path}")
    else:
        logger.info(f"File already exists: {path}. Skipping creation.")


def check_venv_exists():
    """Check if the .venv virtual environment exists and is valid."""
    venv_path = ".venv"
    if not os.path.exists(venv_path):
        return False

    if platform.system() == "Windows":
        python_exec = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_exec = os.path.join(venv_path, "bin", "python")

    return os.path.exists(python_exec)


def setup_uv_project():
    """Initialize uv project and virtual environment."""
    # Remove existing .venv if it exists
    if os.path.exists(".venv"):
        logger.warning("Removing existing virtual environment '.venv'...")
        shutil.rmtree(".venv")

    try:
        # Initialize uv project (creates pyproject.toml if it doesn't exist)
        logger.info("Initializing uv project...")
        subprocess.run(["uv", "init", "--no-readme"], check=True, capture_output=True)
        logger.success("UV project initialized!")

        # Create virtual environment
        logger.info("Creating virtual environment with uv...")
        subprocess.run(["uv", "venv"], check=True, capture_output=True)
        logger.success("Virtual environment created successfully!")

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to setup uv project: {e}")
        return False


def install_core_dependencies():
    """Install core development dependencies using uv."""
    # List all core dependencies here
    core_deps = ["pytest", "pytest-html", "pytest-mock", "loguru", "pathvalidate"]

    try:
        logger.info(f"Installing core dependencies: {', '.join(core_deps)}...")

        # Use uv add to install dependencies
        for dep in core_deps:
            subprocess.run(
                ["uv", "add", dep],
                check=True,
                capture_output=True,
                text=True,
            )

        logger.success(
            f"Core dependencies installed successfully: {', '.join(core_deps)}!"
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install core dependencies: {e}")
        if hasattr(e, "stdout") and e.stdout:
            logger.error(f"UV stdout: {e.stdout}")
        if hasattr(e, "stderr") and e.stderr:
            logger.error(f"UV stderr: {e.stderr}")
        return False


def update_pyproject_toml():
    """Update pyproject.toml with project structure and build settings."""
    pyproject_path = "pyproject.toml"

    # Read existing pyproject.toml if it exists
    config = {}
    if os.path.exists(pyproject_path):
        try:
            import tomli

            with open(pyproject_path, "rb") as f:
                config = tomli.load(f)
        except ImportError:
            # Fallback: try to read as text and update manually
            logger.warning(
                "tomli not available. Creating basic pyproject.toml structure."
            )

    # Update project configuration
    if "project" not in config:
        config["project"] = {}

    project_name = os.path.basename(os.getcwd())
    config["project"].update(
        {
            "name": project_name,
            "version": "0.1.0",
            "description": "Python project created with SPEC (Swift Python Environment Creator)",
            "requires-python": ">=3.8",
        }
    )

    # Update build system
    config["build-system"] = {
        "requires": ["hatchling"],
        "build-backend": "hatchling.build",
    }

    # Add tool configurations
    if "tool" not in config:
        config["tool"] = {}

    # Add pytest configuration
    config["tool"]["pytest"] = {
        "ini_options": {
            "testpaths": ["tests"],
            "python_files": ["test_*.py", "*_test.py"],
            "python_classes": ["Test*"],
            "python_functions": ["test_*"],
            "addopts": "--html=reports/report.html --self-contained-html",
        }
    }

    # Write updated pyproject.toml
    try:
        import tomli_w

        with open(pyproject_path, "wb") as f:
            tomli_w.dump(config, f)
        logger.success("Updated pyproject.toml with project configuration")
    except ImportError:
        # Fallback: create basic pyproject.toml manually
        basic_pyproject = f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = "Python project created with SPEC (Swift Python Environment Creator)"
requires-python = ">=3.8"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--html=reports/report.html --self-contained-html"
"""
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(basic_pyproject)
        logger.success("Created basic pyproject.toml")


def create_conftest():
    """Create the tests/conftest.py file with basic pytest fixtures and configuration."""

    conftest_content = '''# tests/conftest.py
"""
Pytest configuration file for shared fixtures and test settings.
All test files in this directory and subdirectories can use these fixtures.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# --- Common Fixtures ---

@pytest.fixture
def project_root():
    """Return the project root directory path."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_data():
    """Provide common test data."""
    return {
        "id": 123,
        "name": "Test Item",
        "value": 99.9,
        "active": True
    }


# --- Example Fixtures (uncomment and modify as needed) ---

# @pytest.fixture(scope="session")
# def database_connection():
#     """Create a database connection for the test session."""
#     # Setup code here
#     connection = create_test_db_connection()
#     yield connection
#     # Teardown code here
#     connection.close()

# @pytest.fixture
# def temp_file(tmp_path):
#     """Create a temporary file for testing."""
#     file_path = tmp_path / "test_file.txt"
#     file_path.write_text("test content")
#     return file_path

# @pytest.fixture
# def mock_api_response():
#     """Mock API response for testing."""
#     return {
#         "status": "success",
#         "data": {"message": "Test response"}
#     }
'''

    create_file(os.path.join("tests", "conftest.py"), conftest_content)


# Main function
def main():
    # Check if uv is installed
    if not check_uv_installed():
        sys.exit(1)

    # Detect the operating system
    system = platform.system()
    logger.info(f"Setting up Python project for {system} using SPEC and uv")

    # Determine project root
    project_root = os.getcwd()  # Current working directory

    # Create the project structure directories
    create_directory("scripts")
    create_directory("src/package")
    create_directory("tests")
    create_directory("reports")  # For test reports

    # Create __init__.py in package
    create_file("src/package/__init__.py", "")

    # Initialize uv project and virtual environment
    if not setup_uv_project():
        logger.critical("Failed to set up uv project")
        sys.exit(1)

    # Install core dependencies
    if not install_core_dependencies():
        logger.critical("Failed to install core dependencies.")
        sys.exit(1)

    # Update pyproject.toml with project configuration
    update_pyproject_toml()

    # Create dynamic files
    create_conftest()

    # Display helpful messages on what to do next
    logger.success("SPEC project setup complete!")

    logger.info(
        f"Your project is using uv with a .venv virtual environment on {system}."
    )
    logger.info("To activate the virtual environment:")
    if system == "Windows":
        logger.info("  .venv\\Scripts\\activate")
    else:
        logger.info("  source .venv/bin/activate")

    logger.info("To add new dependencies:")
    logger.info("  uv add <package-name>")
    logger.info("To add development dependencies:")
    logger.info("  uv add --dev <package-name>")

    logger.info("To migrate an existing project:")
    logger.info("1. Copy your project's main script file to the `scripts` directory")
    logger.info("2. Copy your project's package files to the `src/package` directory")
    logger.info(
        "3. Add dependencies using `uv add <package>` or run the `scan_and_install_packages.py` script"
    )
    logger.info("4. Update pyproject.toml with your project details")

    logger.info("Project files created:")
    logger.info(
        "  - pyproject.toml: Modern Python project configuration with pytest settings"
    )
    logger.info("  - .venv/: Virtual environment managed by uv")
    logger.info("  - src/package/: Your main package source code")
    logger.info("  - tests/conftest.py: Pytest configuration and shared fixtures")
    logger.info("  - reports/: Test report output directory")


if __name__ == "__main__":
    # Add a debug message to demonstrate all log levels
    logger.debug("Starting SPEC-based project environment setup")
    main()
