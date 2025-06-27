#!/usr/bin/env python3
"""
SPEC - Swift Python Environment Creator
Scan and Install Packages Script

This script automates the installation of project dependencies using uv (ultrafast Python package manager).
It performs the following steps:

1.  **pyproject.toml Processing:** If a `pyproject.toml` file is present in the project root,
    it syncs all dependencies listed within it using `uv sync`.
2.  **Source Code Scanning:** It scans all Python (`.py`) files within the `src/package` and `scripts`
    directories for `import` statements. It then extracts the top-level module names from these imports.
3.  **Dependency Installation:** For each identified module, it checks if it's already installed in the
    current Python environment. If not, it attempts to install the corresponding package using `uv add`.
    A mapping is used to handle cases where the import name differs from the PyPI package name.
4.  **Lock File Update:** Finally, it ensures the `uv.lock` file is up to date by running `uv sync`.

**Key Features:**

*   **UV-Based:** Uses uv for ultra-fast dependency resolution and installation.
*   **pyproject.toml Support:** Reads from and updates modern Python project configuration.
*   **Automatic Dependency Detection:** Scans source code to identify required modules.
*   **Handles Import/Package Name Differences:** Uses a mapping to resolve common discrepancies.
*   **Lock File Management:** Maintains uv.lock for reproducible builds.
*   **Robust Project Root Detection:** Attempts to find the project root even if the script is not run from there.
*   **Clear Logging:** Provides detailed logging output to track the installation process.

**Assumptions:**

*   The project root contains `scripts` and `src` directories.
*   The `src` directory contains a `package` subdirectory.
*   uv is installed and accessible in the system PATH.
*   The script is run within the project root directory.

**Limitations:**

*   This script uses a heuristic approach to identify dependencies, which may not be perfect.
*   Some complex import patterns or dynamic imports might not be detected.
*   Package names on PyPI may not always directly correspond to import names.

**Usage:**

1.  Ensure uv is installed: `pip install uv` or visit https://github.com/astral-sh/uv
2.  Place this script (`scan_and_install_packages.py`) in the root directory of your Python project.
3.  Run the script from VS Code or the command line: `python scan_and_install_packages.py`

Author: Michael Fu
Date: 2025/06/27
Release: 1.0
"""

import os
import ast
import sys
import subprocess
import importlib.util
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


def check_uv_installed():
    """Check if uv is installed and accessible."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
        logger.info(f"Found uv: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("uv is not installed or not accessible in PATH.")
        logger.error("Please install uv first:")
        logger.error("  pip install uv")
        logger.error("  or visit: https://github.com/astral-sh/uv")
        return False


def sync_dependencies(pyproject_file):
    """Sync dependencies from pyproject.toml using uv sync."""
    if os.path.isfile(pyproject_file):
        logger.info(f"Found pyproject.toml at {pyproject_file}. Syncing dependencies...")
        try:
            subprocess.check_call(["uv", "sync"])
            logger.success("Successfully synced dependencies from pyproject.toml")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error syncing from pyproject.toml: {e}")
    else:
        logger.info("No pyproject.toml file found. Will scan source files for imports.")


def get_top_level_imports(file_path):
    """Parse a Python source file and extract a set of top-level module names from import statements."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return set()

    try:
        tree = ast.parse(file_content, filename=file_path)
    except SyntaxError as e:
        logger.warning(f"Skipping {file_path} due to SyntaxError: {e}")
        return set()

    imports = set()
    for node in ast.iter_child_nodes(tree):
        # Handle "import foo, bar" statements.
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod_name = alias.name.split(".")[0]
                imports.add(mod_name)
        # Handle "from foo import bar" statements.
        elif isinstance(node, ast.ImportFrom):
            # Skip relative imports (e.g. "from .module import something")
            if node.level == 0 and node.module:
                mod_name = node.module.split(".")[0]
                imports.add(mod_name)
    return imports


def find_all_imports(src_dirs):
    """Walk through the src_dirs recursively, parse all .py files, and collect all top-level imports."""
    all_imports = set()
    python_files_found = 0

    for src_dir in src_dirs:
        if not os.path.exists(src_dir):
            logger.warning(f"Directory {src_dir} does not exist. Skipping.")
            continue
            
        logger.info(f"Scanning directory: {src_dir}")
        for root, dirs, files in os.walk(src_dir):
            python_files = [f for f in files if f.endswith(".py")]
            if python_files:
                logger.info(f"Found {len(python_files)} Python files in {root}")
                python_files_found += len(python_files)

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    logger.debug(f"Processing: {file_path}")
                    file_imports = get_top_level_imports(file_path)
                    if file_imports:
                        logger.debug(f"  - Found imports: {file_imports}")
                    all_imports.update(file_imports)

    logger.info(f"Total Python files processed: {python_files_found}")
    if python_files_found == 0:
        logger.warning("WARNING: No Python files were found to process!")

    return all_imports


def is_installed(module_name):
    """Check whether a module is installed using importlib.util.find_spec."""
    return importlib.util.find_spec(module_name) is not None


# Import name -> Package name mapping for common discrepancies
PACKAGE_IMPORT_MAP = {
    "bs4": "beautifulsoup4",
    "PIL": "pillow",
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "yaml": "pyyaml",
    "requests": "requests",  # Some mappings are identical
    "dotenv": "python-dotenv",
    "dateutil": "python-dateutil",
    "serial": "pyserial",
    "magic": "python-magic",
    # Add more as you discover them
}


def install_module_with_uv(module_name):
    """Attempt to install the module using uv add."""
    package_name = PACKAGE_IMPORT_MAP.get(module_name, module_name)
    logger.info(f"Installing module: {module_name} (package: {package_name})")
    try:
        subprocess.check_call(["uv", "add", package_name])
        logger.success(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install package '{package_name}' for module '{module_name}'.")
        return False


def check_project_has_uv_config():
    """Check if the project has uv configuration (pyproject.toml with uv settings)."""
    pyproject_path = "pyproject.toml"
    if not os.path.exists(pyproject_path):
        return False
    
    try:
        # Try to read pyproject.toml to check for project configuration
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Simple check for project configuration
            return "[project]" in content or "[build-system]" in content
    except Exception as e:
        logger.debug(f"Error reading pyproject.toml: {e}")
        return False


def main():
    """Main function."""
    # Check if uv is installed
    if not check_uv_installed():
        sys.exit(1)

    # Get the absolute path of the script
    script_path = os.path.abspath(__file__)
    logger.debug(f"Script is located at: {script_path}")

    # Determine project root directory based on the script's location
    # Start by assuming the script is in the project root
    project_root = os.path.dirname(script_path)

    # Check if we are in the correct directory by looking for a 'src' folder or pyproject.toml
    has_src = os.path.isdir(os.path.join(project_root, "src"))
    has_pyproject = os.path.isfile(os.path.join(project_root, "pyproject.toml"))
    
    if not has_src and not has_pyproject:
        logger.warning(
            f"Neither 'src' directory nor 'pyproject.toml' found in the same directory as the script. Attempting to find project root..."
        )
        # Try to find the project root by going up the directory tree
        current_dir = project_root
        while current_dir != os.path.dirname(current_dir):  # Stop at the root directory
            if (os.path.isdir(os.path.join(current_dir, "src")) or 
                os.path.isfile(os.path.join(current_dir, "pyproject.toml"))):
                project_root = current_dir
                logger.info(f"Found project root at: {project_root}")
                break
            current_dir = os.path.dirname(current_dir)
        else:
            logger.critical(
                "Could not determine project root. Please ensure the script is within the project directory or a subdirectory."
            )
            sys.exit(1)

    logger.debug(f"Project root determined as: {project_root}")

    # Change to project root directory for uv operations
    os.chdir(project_root)
    logger.debug(f"Changed working directory to: {project_root}")

    # List contents of project root to verify
    logger.debug(f"Contents of project root: {os.listdir(project_root)}")

    # Check for pyproject.toml and sync existing dependencies
    pyproject_file = os.path.join(project_root, "pyproject.toml")
    sync_dependencies(pyproject_file)

    # Check for src directory structure
    src_dir = os.path.join(project_root, "src")
    src_package_dir = os.path.join(src_dir, "package")
    scripts_dir = os.path.join(project_root, "scripts")

    # Prepare directories to scan
    scan_dirs = []
    
    if os.path.isdir(src_package_dir):
        scan_dirs.append(src_package_dir)
    elif os.path.isdir(src_dir):
        scan_dirs.append(src_dir)
    
    if os.path.isdir(scripts_dir):
        scan_dirs.append(scripts_dir)

    if not scan_dirs:
        logger.warning("No standard source directories found (src/package, src, scripts). Scanning current directory.")
        scan_dirs = [project_root]

    # Debug directory structure
    logger.debug(f"Directories to scan: {scan_dirs}")

    # Scan for additional dependencies in the source directories
    logger.info("Scanning for additional dependencies in source files...")
    modules = find_all_imports(scan_dirs)
    logger.info(f"Modules found in source files: {sorted(modules)}")

    # List of built-in or standard library modules that we skip installing.
    builtin_exceptions = {
        "sys", "os", "time", "math", "itertools", "functools", "subprocess", 
        "threading", "json", "re", "ast", "datetime", "logging", "random",
        "pathlib", "collections", "typing", "dataclasses", "enum", "abc",
        "contextlib", "warnings", "copy", "pickle", "tempfile", "shutil",
        "glob", "fnmatch", "argparse", "configparser", "urllib", "http",
        "email", "html", "xml", "csv", "sqlite3", "hashlib", "hmac",
        "secrets", "uuid", "base64", "binascii", "struct", "io", "gzip",
        "zipfile", "tarfile", "platform", "socket", "ssl", "ftplib",
        "unittest", "doctest", "pdb", "trace", "traceback", "inspect",
        "dis", "gc", "weakref", "ctypes", "multiprocessing", "concurrent",
        "queue", "threading", "asyncio", "signal", "errno", "stat"
    }

    # Process each module, checking if it's installed and attempting installation if not.
    modules_installed = 0
    modules_failed = 0
    
    for module in sorted(mod for mod in modules if mod not in builtin_exceptions):
        if not is_installed(module):
            logger.warning(f"Module '{module}' is not installed.")
            if install_module_with_uv(module):
                modules_installed += 1
            else:
                modules_failed += 1
        else:
            logger.info(f"Module '{module}' is already installed.")

    # Final sync to ensure lock file is up to date
    if modules_installed > 0:
        logger.info("Running final sync to update lock file...")
        try:
            subprocess.check_call(["uv", "sync"])
            logger.success("Lock file updated successfully!")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error updating lock file: {e}")

    # Summary
    logger.success("Dependency installation complete!")
    logger.info(f"Summary: {modules_installed} modules installed, {modules_failed} failed")
    
    if modules_failed > 0:
        logger.warning(f"{modules_failed} modules could not be installed. Check the logs above for details.")
    
    logger.info("Project dependencies are managed in pyproject.toml and uv.lock")
    logger.info("To add new dependencies: uv add <package-name>")
    logger.info("To add development dependencies: uv add --dev <package-name>")
    logger.info("To sync dependencies: uv sync")


if __name__ == "__main__":
    # Add a debug message to demonstrate all log levels
    logger.debug("Starting SPEC-based dependency installation")
    main()