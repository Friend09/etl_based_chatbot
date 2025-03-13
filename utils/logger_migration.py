"""
Logger migration utility to help transition to the new logging system.

This script identifies existing logger usage in Python files and migrates them
to the new logging structure.
"""

import os
import re
import sys
from pathlib import Path

def find_python_files(start_dir):
    """Find all Python files in the directory tree."""
    py_files = []
    for root, dirs, files in os.walk(start_dir):
        # Skip virtual environment directories and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.venv' and d != 'venv']
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def analyze_file(filepath):
    """Analyze a Python file for logger usage."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Look for logger patterns
    old_logger_patterns = [
        r'logging\.getLogger\(',
        r'logger\s*=\s*logging\.getLogger',
        r'import\s+logging',
    ]

    has_old_logger = False
    for pattern in old_logger_patterns:
        if re.search(pattern, content):
            has_old_logger = True
            break

    # Check if already using new logger
    new_logger_pattern = r'from\s+utils\.logger\s+import'
    already_migrated = bool(re.search(new_logger_pattern, content))

    return {
        'filepath': filepath,
        'has_old_logger': has_old_logger,
        'already_migrated': already_migrated,
        'module_name': os.path.basename(filepath)[:-3]  # Remove .py extension
    }

def generate_migration_instructions(analysis):
    """Generate instructions for migrating logger usage."""
    instructions = []

    for file_info in analysis:
        if file_info['has_old_logger'] and not file_info['already_migrated']:
            instructions.append(f"File: {file_info['filepath']}")
            component_type = detect_component_type(file_info['filepath'])

            if component_type:
                instructions.append(f"  - Replace: import logging")
                instructions.append(f"  - With: from utils.logger import get_component_logger")
                instructions.append(f"  - Replace: logger = logging.getLogger(...)")
                instructions.append(f"  - With: logger = get_component_logger('{component_type}', '{file_info['module_name']}')")
            else:
                instructions.append(f"  - Replace: import logging")
                instructions.append(f"  - With: from utils.logger import setup_logger")
                instructions.append(f"  - Replace: logger = logging.getLogger(...)")
                instructions.append(f"  - With: logger = setup_logger(__name__)")

            instructions.append("")

    return instructions

def detect_component_type(filepath):
    """Detect the component type based on filepath."""
    if '/etl/' in filepath:
        return 'etl'
    elif '/web/' in filepath or '/api/' in filepath:
        return 'web'
    elif '/db/' in filepath or '/dao/' in filepath or '/repository/' in filepath:
        return 'db'
    else:
        return None

def main():
    """Main function to run the migration tool."""
    print("Logger Migration Utility")
    print("=======================")

    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")

    # Find Python files
    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files")

    # Analyze files
    analysis = [analyze_file(filepath) for filepath in python_files]

    # Filter for files with logger usage
    logger_files = [file for file in analysis if file['has_old_logger']]
    print(f"Found {len(logger_files)} files with logger usage")

    # Count already migrated files
    migrated_files = [file for file in analysis if file['already_migrated']]
    print(f"Found {len(migrated_files)} files already using new logger")

    # Get files that need migration
    needs_migration = [file for file in logger_files if not file['already_migrated']]
    print(f"Found {len(needs_migration)} files that need logger migration")

    if needs_migration:
        instructions = generate_migration_instructions(needs_migration)
        print("\nMigration Instructions:")
        print("======================")
        for instruction in instructions:
            print(instruction)
    else:
        print("\nNo logger migration needed. All files using the new logger system.")

if __name__ == "__main__":
    main()
