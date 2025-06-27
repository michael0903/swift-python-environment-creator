# project_settings.py
"""
SPEC Project Configuration File

This file centralizes project-wide settings and configurations for uv-managed SPEC projects, including:
- Loguru logger setup for consistent logging across multiple modules.
- Path validation using the pathvalidate library.
- UV-specific project configuration helpers.
- Modern Python project structure support.

SPEC (Swift Python Environment Creator) is a modern Python project setup tool that leverages
uv for ultra-fast dependency management and creates professional project structures.

This file is designed to be easily understood and extended by both humans and AI code assistants.
It's optimized for projects using uv as the package manager and pyproject.toml for configuration.

Author: Michael Fu
Date: 2025/06/27
Release: 1.0
"""
import os
import sys
import subprocess
from pathlib import Path
from loguru import logger
from pathvalidate import sanitize_filepath, sanitize_filename

# --- Project Root and Path Setup ---
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# --- UV Configuration ---
UV_CONFIG = {
    "venv_path": PROJECT_ROOT / ".venv",
    "pyproject_path": PROJECT_ROOT / "pyproject.toml",
    "lock_file_path": PROJECT_ROOT / "uv.lock",
    "cache_dir": PROJECT_ROOT / ".uv-cache",
}

# --- Loguru Logger Configuration ---
# Default settings (can be overridden)
DEFAULT_LOG_FILE_NAME = "spec_project.log"
DEFAULT_TEST_FILE_NAME = "spec_project_file"
LOG_DIR = PROJECT_ROOT / "logs"  # Define a log directory

# Ensure the log directory exists
LOG_DIR.mkdir(exist_ok=True)


def get_logger(
    module_name: str,
    log_file_name_suffix: str = None,
    test_file_name: str = DEFAULT_TEST_FILE_NAME,
) -> logger:
    """Creates and configures a Loguru logger for a specific module in a SPEC project.

    Args:
        module_name: The name of the module (used for the logger name and log file).
        log_file_name_suffix: Optional suffix for the log file name.
        test_file_name: The name of the test file for filtering.

    Returns:
        A configured Loguru logger object.
    """
    # Create a named logger
    module_logger = logger.bind(name=module_name)

    # Remove any existing handlers from the module logger (if any)
    module_logger.remove()

    # Construct the log file name
    if log_file_name_suffix:
        log_file_name = LOG_DIR / f"{module_name}_{log_file_name_suffix}.log"
    else:
        log_file_name = LOG_DIR / f"{module_name}.log"

    # Add a file handler for this module
    module_logger.add(
        str(log_file_name),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}",
        level="DEBUG",
        rotation="10 MB",
        enqueue=True,
        filter=lambda record: record["extra"].get("test_file") == test_file_name,
    )

    # Add a console handler (optional, but useful for development)
    module_logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        level="INFO",
        enqueue=True,
        filter=lambda record: record["extra"].get("test_file") == test_file_name,
    )

    # Add the test_file filter to the logger
    module_logger = module_logger.bind(test_file=test_file_name)

    return module_logger


# --- UV Helper Functions ---

def check_uv_installation() -> bool:
    """Check if uv is installed and accessible."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_uv_python_path() -> Path:
    """Get the path to the Python executable in the uv virtual environment."""
    venv_path = UV_CONFIG["venv_path"]
    if os.name == "nt":  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Unix-like systems
        return venv_path / "bin" / "python"


def get_uv_pip_path() -> Path:
    """Get the path to the pip executable in the UV virtual environment."""
    venv_path = UV_CONFIG["venv_path"]
    if os.name == "nt":  # Windows
        return venv_path / "Scripts" / "pip.exe"
    else:  # Unix-like systems
        return venv_path / "bin" / "pip"


def is_uv_project() -> bool:
    """Check if the current directory is a uv-managed project."""
    return UV_CONFIG["pyproject_path"].exists()


def get_project_dependencies():
    """Get project dependencies from pyproject.toml."""
    pyproject_path = UV_CONFIG["pyproject_path"]
    if not pyproject_path.exists():
        return {}
    
    try:
        import tomli
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
        
        dependencies = {}
        if "project" in data and "dependencies" in data["project"]:
            dependencies["main"] = data["project"]["dependencies"]
        
        if "project" in data and "optional-dependencies" in data["project"]:
            dependencies["optional"] = data["project"]["optional-dependencies"]
            
        return dependencies
    except ImportError:
        logger.warning("tomli not available. Cannot parse pyproject.toml")
        return {}
    except Exception as e:
        logger.error(f"Error reading pyproject.toml: {e}")
        return {}


def sync_uv_environment():
    """Sync the uv environment with pyproject.toml."""
    try:
        subprocess.run(["uv", "sync"], check=True, cwd=PROJECT_ROOT)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to sync uv environment: {e}")
        return False


# --- pathvalidate Configuration ---
# How to use:
# 1. Import: `from project_settings import sanitize_filepath, sanitize_filename`
# 2. Use: `safe_path = sanitize_filepath(user_input_path)`
#         `safe_filename = sanitize_filename(user_input_filename)`
#
# AI Code Assistant Note:
# - The `sanitize_filepath` and `sanitize_filename` functions are imported directly.
# - They can be used to validate and sanitize file paths and names.

# pathvalidate functions are directly imported and ready to use.

# --- Modern Python Project Configuration ---
# How to use:
# 1. Add your configuration variables as constants (uppercase with underscores).
# 2. Add any functions that help set up or manage these configurations.
# 3. Add a comment block above each configuration section to explain its purpose.
#
# AI Code Assistant Note:
# - This section is for adding modern Python project configurations.
# - Configurations should be defined as constants (e.g., `MY_SETTING = "value"`).
# - Functions related to these configurations should be defined here.
# - Each configuration section should have a clear comment block.

# Example: Development Configuration
# How to use:
# 1. Import: `from project_settings import DEV_SERVER_HOST, DEV_SERVER_PORT`
# 2. Use: `print(f"Development server: {DEV_SERVER_HOST}:{DEV_SERVER_PORT}")`
#
# AI Code Assistant Note:
# - These constants are examples of development settings for SPEC projects.
# - You can add more development-related settings here.
DEV_SERVER_HOST = "localhost"
DEV_SERVER_PORT = 8000

# Example: Testing Configuration
# How to use:
# 1. Import: `from project_settings import TEST_OUTPUT_DIR, COVERAGE_THRESHOLD`
# 2. Use: `generate_test_report(TEST_OUTPUT_DIR)`
#
# AI Code Assistant Note:
# - These constants configure testing behavior in SPEC projects.
# - Paths use pathlib.Path for better cross-platform support.
TEST_OUTPUT_DIR = PROJECT_ROOT / "reports"
COVERAGE_THRESHOLD = 80  # Minimum coverage percentage

# Example: Build Configuration
# How to use:
# 1. Import: `from project_settings import BUILD_OUTPUT_DIR, DIST_FORMAT`
# 2. Use: `build_project(BUILD_OUTPUT_DIR, DIST_FORMAT)`
#
# AI Code Assistant Note:
# - These constants configure build behavior for SPEC projects.
# - Uses modern Python packaging standards.
BUILD_OUTPUT_DIR = PROJECT_ROOT / "dist"
DIST_FORMAT = "wheel"  # or "sdist"

# Example: SPEC-Specific Helper Function
# How to use:
# 1. Import: `from project_settings import get_project_info`
# 2. Use: `info = get_project_info()`
#
# AI Code Assistant Note:
# - This function provides SPEC project information.
# - Useful for build scripts and project introspection.
def get_project_info() -> dict:
    """Get comprehensive project information from pyproject.toml and uv environment."""
    info = {
        "project_root": str(PROJECT_ROOT),
        "has_uv": check_uv_installation(),
        "is_uv_project": is_uv_project(),
        "venv_exists": UV_CONFIG["venv_path"].exists(),
        "python_path": str(get_uv_python_path()) if UV_CONFIG["venv_path"].exists() else None,
        "dependencies": get_project_dependencies(),
    }
    
    # Add pyproject.toml metadata if available
    try:
        import tomli
        pyproject_path = UV_CONFIG["pyproject_path"]
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomli.load(f)
            if "project" in data:
                info.update({
                    "name": data["project"].get("name", "unknown"),
                    "version": data["project"].get("version", "0.0.0"),
                    "description": data["project"].get("description", ""),
                    "python_requires": data["project"].get("requires-python", ">=3.8"),
                })
    except Exception as e:
        logger.debug(f"Could not read project metadata: {e}")
    
    return info


# Example: Environment Detection
# How to use:
# 1. Import: `from project_settings import is_development_mode, get_environment`
# 2. Use: `if is_development_mode(): ...`
#
# AI Code Assistant Note:
# - These functions help detect the current runtime environment.
# - Useful for conditional behavior in development vs production.
def is_development_mode() -> bool:
    """Check if the project is running in development mode."""
    # Check for common development indicators
    dev_indicators = [
        os.getenv("DEBUG") == "1",
        os.getenv("ENVIRONMENT") == "development",
        (PROJECT_ROOT / ".git").exists(),  # Git repository
        not (PROJECT_ROOT / "dist").exists(),  # No built distribution
    ]
    return any(dev_indicators)


def get_environment() -> str:
    """Get the current environment (development, testing, production)."""
    env = os.getenv("ENVIRONMENT")
    if env:
        return env.lower()
    
    if is_development_mode():
        return "development"
    elif os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        return "testing"
    else:
        return "production"


# Initialize project-level logger
project_logger = get_logger("project_settings")
project_logger.info(f"SPEC project configuration loaded from {PROJECT_ROOT}")
project_logger.debug(f"Environment: {get_environment()}")