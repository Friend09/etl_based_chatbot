#!/usr/bin/env python3
"""
Utility script to identify potentially unused or redundant files in the project.
Helps maintain a clean project structure.
"""

import os
import sys
from pathlib import Path
import importlib
import re
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def find_imports(file_path):
    """Find import statements in a Python file."""
    imports = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()

            # Find import statements
            import_pattern = r'(?:from\s+([\w.]+)\s+import|import\s+([\w.,\s]+))'
            for match in re.finditer(import_pattern, content):
                modules = match.group(1) or match.group(2)
                for module in re.split(r',\s*', modules):
                    module = module.strip()
                    if module and not module.startswith('.'):
                        imports.append(module.split('.')[0])
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return set(imports)

def find_file_references(file_path, all_files):
    """Find references to a file in other files (beyond imports)."""
    filename = os.path.basename(file_path)
    module_name = os.path.splitext(filename)[0]
    refs = []

    try:
        for other_file in all_files:
            if other_file == file_path:
                continue

            with open(other_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Look for usage as module reference
                if f"'{module_name}'" in content or f'"{module_name}"' in content:
                    refs.append(other_file)
                    continue

                # Look for references as a file path
                if filename in content:
                    refs.append(other_file)
                    continue
    except Exception as e:
        print(f"Error checking references for {file_path}: {e}")

    return refs

def is_entry_point(file_path):
    """Check if a file is likely an entry point."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Check for common entry point patterns
        if "__name__" in content and "__main__" in content:
            return True
        if "sys.exit" in content or "argparse" in content:
            return True
    return False

def check_package_structure():
    """Check that each package has an __init__.py file."""
    print("\nChecking package structure...")
    issues = []

    for root, dirs, files in os.walk(project_root):
        if "__pycache__" in root or ".git" in root or "venv" in root:
            continue

        py_files = [f for f in files if f.endswith('.py')]
        if py_files and '__init__.py' not in files:
            rel_path = os.path.relpath(root, project_root)
            if rel_path != '.':  # Skip project root
                issues.append(f"Directory '{rel_path}' contains Python files but no __init__.py")

    if issues:
        print("\nPackage structure issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Package structure looks good - all Python directories have __init__.py files.")

    return issues

def find_dangling_files():
    """Find potentially unused Python files in the project."""
    print("Scanning for potentially dangling files...")

    # Get all Python files
    python_files = []
    for root, _, files in os.walk(project_root):
        if "__pycache__" in root or ".git" in root or "venv" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    # Get all files (to check for references beyond imports)
    all_files = []
    for root, _, files in os.walk(project_root):
        if "__pycache__" in root or ".git" in root or "venv" in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            # Skip binary files and very large files
            if os.path.getsize(file_path) < 1000000:  # 1MB limit
                all_files.append(file_path)

    # Build import map
    imports_map = {}
    for py_file in python_files:
        imports_map[py_file] = find_imports(py_file)

    # Find files not imported anywhere
    potentially_dangling = []
    for py_file in python_files:
        rel_path = os.path.relpath(py_file, project_root)
        if os.path.basename(py_file) == "__init__.py":
            continue

        module_name = os.path.splitext(os.path.basename(py_file))[0]
        is_imported = False
        is_referenced = False

        # Check if it's imported
        for other_file, imports in imports_map.items():
            if other_file != py_file and module_name in imports:
                is_imported = True
                break

        # If not imported, check for other forms of references
        if not is_imported:
            refs = find_file_references(py_file, all_files)
            if refs:
                is_referenced = True

        # If neither imported nor referenced, check if it's an entry point
        if not is_imported and not is_referenced:
            entry_point = is_entry_point(py_file)

            # Skip if it's a possible entry point, test file, or common utility
            if (entry_point or
                "test_" in module_name or
                module_name == "test" or
                os.path.basename(os.path.dirname(py_file)) == "tests" or
                module_name in ["main", "app", "setup", "config", "settings", "cleanup", "init_db", "run"]):
                continue

            potentially_dangling.append(rel_path)

    # Print results
    if potentially_dangling:
        print("\nPotentially unused files (not imported or referenced elsewhere):")
        for file in sorted(potentially_dangling):
            print(f"  - {file}")
    else:
        print("No potentially unused files found.")

    return potentially_dangling

def find_duplicate_functionality():
    """Find files with potentially duplicate functionality."""
    print("\nChecking for files with potentially duplicate functionality...")

    # Patterns to look for
    patterns = {
        "database tests": r"test.*database|database.*test",
        "connectors": r"connector|connection",
        "utilities": r"util|helper",
        "loggers": r"log(ger)?",
        "models": r"model",
        "settings": r"config|setting",
    }

    # Group files by pattern
    grouped_files = {k: [] for k in patterns}
    for root, _, files in os.walk(project_root):
        if "__pycache__" in root or ".git" in root or "venv" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)

                for category, pattern in patterns.items():
                    if re.search(pattern, file, re.IGNORECASE):
                        grouped_files[category].append(rel_path)

    # Print groups with multiple files
    found_duplication = False
    for category, files in grouped_files.items():
        if len(files) > 1:
            found_duplication = True
            print(f"\nPotential duplicate {category} files:")
            for file in sorted(files):
                print(f"  - {file}")

    if not found_duplication:
        print("No obvious duplicate functionality detected.")

def check_for_removed_files():
    """Check for references to files that have been moved or renamed."""
    print("\nChecking for references to removed or renamed files...")

    # Updated mapping of moved files
    known_renames = {
        # This file has already been moved
        "tests/test_database.py": "tests/test_database.py",
    }

    issues = []
    all_files = []

    # Get all files
    for root, _, files in os.walk(project_root):
        if "__pycache__" in root or ".git" in root or "venv" in root:
            continue
        for file in files:
            if os.path.getsize(os.path.join(root, file)) < 1000000:  # 1MB limit
                all_files.append(os.path.join(root, file))

    # Check for references to moved/renamed files
    for old_path, new_path in known_renames.items():
        old_filename = os.path.basename(old_path)
        for file_path in all_files:
            if os.path.exists(os.path.join(project_root, old_path)):
                issues.append(f"File {old_path} has been moved to {new_path} but still exists")
                break

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if old_path in content or old_filename in content:
                        issues.append(f"File {file_path} contains reference to {old_path} which has been moved to {new_path}")
            except Exception as e:
                print(f"Error checking file {file_path}: {e}")

    if issues:
        print("\nPotential issues with moved/renamed files:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("No references to moved or renamed files found.")

    return issues

def generate_report():
    """Generate a comprehensive report of potential project issues."""
    report = {
        "dangling_files": find_dangling_files(),
        "duplicate_functionality": {},
        "package_issues": check_package_structure(),
        "moved_file_references": check_for_removed_files(),
    }

    # Add duplicate functionality info
    print("\nGenerating comprehensive report...")
    report_file = os.path.join(project_root, "reports", "cleanup_report.json")

    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to {report_file}")

if __name__ == "__main__":
    print(f"Project root: {project_root}")

    # Run all checks
    dangling_files = find_dangling_files()
    find_duplicate_functionality()
    check_package_structure()
    check_for_removed_files()

    # Generate report
    # generate_report()  # Uncomment to save full report

    if dangling_files:
        print("\nReminder: Use this output as a guide only. Manually verify before deleting any files.")
        print("Some files may be used in ways not detected by this script.")
