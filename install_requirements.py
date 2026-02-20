#!/usr/bin/env python3
"""
Install all requirements.txt files found in subdirectories

This script finds all requirements.txt files in the project and installs them.
It can either install them individually or merge them first (recommended).
"""

import os
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
import re


def find_requirements_files(root_dir: str = ".") -> list[Path]:
    """
    Find all requirements.txt files in subdirectories
    
    Args:
        root_dir: Root directory to search from
        
    Returns:
        List of Path objects pointing to requirements.txt files
    """
    root = Path(root_dir).resolve()
    requirements_files = []
    
    for req_file in root.rglob("requirements.txt"):
        # Skip common directories that shouldn't be installed
        if any(skip in str(req_file) for skip in ["node_modules", "__pycache__", ".git", ".venv", "venv"]):
            continue
        requirements_files.append(req_file)
    
    return sorted(requirements_files)


def parse_requirements_file(file_path: Path) -> list[str]:
    """
    Parse a requirements.txt file and return list of requirements
    
    Args:
        file_path: Path to requirements.txt file
        
    Returns:
        List of requirement strings
    """
    requirements = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            requirements.append(line)
    return requirements


def merge_requirements(requirements_files: list[Path]) -> dict[str, str]:
    """
    Merge multiple requirements.txt files, handling version conflicts
    
    Args:
        requirements_files: List of Path objects to requirements.txt files
        
    Returns:
        Dictionary mapping package names to their requirements
    """
    merged = {}
    conflicts = defaultdict(list)
    
    for req_file in requirements_files:
        requirements = parse_requirements_file(req_file)
        for req in requirements:
            # Extract package name (handle various formats: package==1.0.0, package>=1.0.0, etc.)
            match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)', req)
            if match:
                package_name = match.group(1).lower()
                
                # Check for conflicts
                if package_name in merged and merged[package_name] != req:
                    conflicts[package_name].append((req_file, req))
                
                # Use the most permissive version if there's a conflict
                # (e.g., >= takes precedence over ==)
                if package_name not in merged:
                    merged[package_name] = req
                elif '>=' in req and '==' in merged[package_name]:
                    # Prefer >= over ==
                    merged[package_name] = req
                elif '==' in req and '>=' in merged[package_name]:
                    # Keep >= if already set
                    pass
    
    return merged, conflicts


def install_requirements(requirements: list[str], method: str = "merge") -> bool:
    """
    Install requirements using pip
    
    Args:
        requirements: List of requirement strings
        method: Installation method ("merge" or "individual")
        
    Returns:
        True if successful, False otherwise
    """
    if not requirements:
        print("No requirements to install.")
        return True
    
    print(f"\nInstalling {len(requirements)} packages...")
    
    try:
        # Use pip install with the requirements
        cmd = [sys.executable, "-m", "pip", "install"] + requirements
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e.stderr}", file=sys.stderr)
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Install all requirements.txt files found in subdirectories"
    )
    parser.add_argument(
        "--method",
        choices=["merge", "individual"],
        default="merge",
        help="Installation method: 'merge' (recommended) or 'individual'"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without actually installing"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to search from (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Find all requirements.txt files
    print(f"Searching for requirements.txt files in {args.root}...")
    requirements_files = find_requirements_files(args.root)
    
    if not requirements_files:
        print("No requirements.txt files found.")
        return 1
    
    print(f"\nFound {len(requirements_files)} requirements.txt file(s):")
    for req_file in requirements_files:
        print(f"  - {req_file}")
    
    if args.method == "merge":
        # Merge all requirements
        print("\nMerging requirements...")
        merged, conflicts = merge_requirements(requirements_files)
        
        if conflicts:
            print("\n⚠️  Version conflicts detected:")
            for package, conflict_list in conflicts.items():
                print(f"  {package}:")
                for req_file, req in conflict_list:
                    print(f"    - {req_file}: {req}")
            print("\nUsing the most permissive version for conflicts.")
        
        requirements_list = list(merged.values())
        
        if args.dry_run:
            print("\n📦 Would install the following packages:")
            for req in sorted(requirements_list):
                print(f"  {req}")
            return 0
        
        print(f"\n📦 Merged {len(requirements_list)} unique packages")
        return 0 if install_requirements(requirements_list) else 1
    
    else:  # individual
        # Install each requirements.txt individually
        if args.dry_run:
            print("\n📦 Would install requirements from:")
            for req_file in requirements_files:
                requirements = parse_requirements_file(req_file)
                print(f"  {req_file} ({len(requirements)} packages)")
            return 0
        
        success = True
        for req_file in requirements_files:
            print(f"\n📦 Installing requirements from {req_file}...")
            requirements = parse_requirements_file(req_file)
            if not install_requirements(requirements):
                success = False
                print(f"⚠️  Failed to install requirements from {req_file}")
        
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
