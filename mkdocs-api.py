#!/usr/bin/env python3
"""
Generate API documentation structure from Python module hierarchy.

This script traverses a Python module structure in 'src' directory and creates
a corresponding file hierarchy in 'docs/api' with .py files converted to .md files.
Each .md file contains a reference line in the format '::: a.b.c' where a.b.c
is the qualified module name. __init__.py files become index.md files.
Finally, it outputs a YAML navigation structure compatible with MkDocs.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Union


def get_qualified_name(file_path: Path, src_root: Path) -> str:
   """Convert file path to qualified Python module name."""
   # Get relative path from src root
   rel_path = file_path.relative_to(src_root)

   # Remove .py extension
   if rel_path.suffix == '.py':
      rel_path = rel_path.with_suffix('')

   # Convert path separators to dots
   parts = list(rel_path.parts)

   # Handle __init__.py files (they represent the parent module)
   if parts[-1] == '__init__':
      parts = parts[:-1]

   return '.'.join(parts) if parts else ''


def create_md_file(py_file: Path, docs_root: Path, src_root: Path) -> Path | None:
   """Create corresponding .md file for a Python file."""
   # Get relative path from src
   rel_path = py_file.relative_to(src_root)

   # Convert to docs path
   if rel_path.name == '__init__.py':
      # __init__.py becomes index.md
      md_rel_path = rel_path.parent / 'index.md'
   else:
      # Regular .py files become .md files
      md_rel_path = rel_path.with_suffix('.md')

   md_file = docs_root / md_rel_path

   # Create directory if it doesn't exist
   md_file.parent.mkdir(parents=True, exist_ok=True)

   # Get qualified name for the reference
   qualified_name = get_qualified_name(py_file, src_root)

   # Create content
   if qualified_name:
      if rel_path.name == "__init__.py":
         # check file empty
         if py_file.stat().st_size == 0:
            return None
         content = f"::: {qualified_name}\n"
         content = f"# {rel_path.parent.name.capitalize()} Overview \n\n" + content
      else:
         content = f"::: {qualified_name}\n"
         content = f"# module {rel_path.name[:-3]}\n\n" + content
   else:
      # Root __init__.py case
      content = "# SolverPy Overview\n"

   # Write the file
   with open(md_file, 'w') as f:
      f.write(content)

   return md_file


def traverse_module(src_dir: Path, docs_dir: Path) -> List[Path]:
   """Traverse module structure and create corresponding .md files."""
   created_files = []

   for root, dirs, files in os.walk(src_dir):
      root_path = Path(root)

      # Process Python files
      for file in files:
         if file.endswith('.py'):
            py_file = root_path / file
            md_file = create_md_file(py_file, docs_dir, src_dir)
            if md_file:
               created_files.append(md_file)

   return created_files


def build_nav_structure(
      docs_dir: Path,
      created_files: List[Path]) -> Dict[str, Union[str, List, Dict]]:
   """Build navigation structure for MkDocs."""
   nav = {}

   for md_file in sorted(created_files):
      # Get relative path from docs/api
      rel_path = md_file.relative_to("docs")
      parts = list(rel_path.parts)

      # Navigate through the structure
      current_nav = nav
      for i, part in enumerate(parts[:-1]):  # All parts except the last
         if part not in current_nav:
            current_nav[part] = {}
         current_nav = current_nav[part]

      # Handle the final part (the file)
      final_part = parts[-1]
      file_key = final_part[:-3]  # Remove .md extension

      # Special handling for index.md
      if file_key == 'index':
         file_key = 'Overview'

      # Store the relative path for MkDocs
      current_nav[file_key] = str(rel_path)

   return nav


def dict_to_mkdocs_nav(nav_dict: Dict,
                       level: int = 0) -> List[Union[str, Dict]]:
   """Convert nested dictionary to MkDocs nav format."""
   nav_list = []
   indent = "  " * level

   # First, add Overview if it exists
   if 'Overview' in nav_dict:
      nav_list.append({'ℹ️ Overview': nav_dict['Overview']})

   # Then add all other items in sorted order
   for key, value in sorted(nav_dict.items()):
      if key == 'Overview':
         continue  # Already added
      if isinstance(value, dict):
         # It's a nested structure
         if len(value) == 1 and 'Overview' in value:
            # If there's only an Overview, flatten it
            nav_list.append({key: value['Overview']})
         else:
            # Create nested structure
            nested_nav = dict_to_mkdocs_nav(value, level + 1)
            nav_list.append({f"📁 {key}": nested_nav})

   # Then add all other items in sorted order
   for key, value in sorted(nav_dict.items()):
      if key == 'Overview':
         continue  # Already added
      if isinstance(value, dict):
         continue
      if isinstance(value, str):
         # It's a file reference
         nav_list.append({f"🤖 {key}": value})
   return nav_list


def main():
   """Main function to generate documentation structure."""
   # Define paths
   src_dir = Path('src')
   docs_api_dir = Path('docs/api')

   # Check if src directory exists
   if not src_dir.exists():
      print(f"Error: {src_dir} directory not found!")
      return

   # Create docs/api directory
   docs_api_dir.mkdir(parents=True, exist_ok=True)

   print(
      f"Traversing {src_dir} and creating documentation in {docs_api_dir}...")

   # Traverse and create files
   created_files = traverse_module(src_dir, docs_api_dir)

   print(f"Created {len(created_files)} documentation files:")
   for file in sorted(created_files):
      print(f"  {file}")

   # Build navigation structure
   nav_structure = build_nav_structure(docs_api_dir, created_files)
   nav_list = dict_to_mkdocs_nav(nav_structure)

   # Create the final YAML structure
   assert len(nav_list) == 1
   api = nav_list[0]
   assert type(api) == dict and type(api["📁 api"]) == list
   api['📦 API 🚧'] = api["📁 api"][0]["📁 solverpy"]
   del api["📁 api"]
   nav_list = [api]
   mkdocs_nav = nav_list
   
   # Output YAML
   print("\nGenerated MkDocs navigation YAML:")
   print("=" * 50)
   yaml_output = yaml.dump(
      mkdocs_nav,
      default_flow_style=False,
      sort_keys=False,
   )
   # add spaces at the beginning of each line
   yaml_output = '  ' + yaml_output.replace('\n', '\n  ')

   nav_file = Path('mkdocs.yml')
   with open(nav_file, 'w') as f:
      f.write(open(Path("mkdocs.yml.tpl")).read())
      f.write(yaml_output)
   print(f"Navigation YAML saved to: {nav_file}")


if __name__ == '__main__':
   main()
