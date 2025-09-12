#!/usr/bin/env python3
import os
from pathlib import Path

SRC_DIR = Path("src")
DOCS_DIR = Path("docs/api")


def make_md_file(pyfile: Path):
   rel = pyfile.relative_to(SRC_DIR)
   module = ".".join(rel.with_suffix("").parts)

   # Special case for __init__.py → module is its parent
   if rel.name == "__init__.py":
      module = ".".join(rel.parent.parts)

   # docs/api/solverpy/foo/bar.md
   md_name = "index.md" if rel.name == "__init__.py" else rel.with_suffix(
      ".md").name
   md_path = DOCS_DIR / rel.parent / md_name
   md_path.parent.mkdir(parents=True, exist_ok=True)

   with open(md_path, "w") as f:
      f.write(f"::: {module}\n")

   return md_path.relative_to(DOCS_DIR)


def build_nav(md_files):
   """Build nested nav dict from md file paths."""
   nav = {}
   for path in sorted(md_files):
      parts = path.parts
      current = nav
      for p in parts[:-1]:
         current = current.setdefault(p, {})
      current[parts[-1].replace(".md", "")] = str(Path("api") / path)
   return nav


def dump_nav(nav, indent=0):
   """Pretty-print nav dict as YAML fragment."""
   lines = []
   for key, value in nav.items():
      if isinstance(value, dict):
         lines.append("  " * indent + f"- {key}:")
         lines.extend(dump_nav(value, indent + 1))
      else:
         lines.append("  " * indent + f"- {key}: {value}")
   return lines


if __name__ == "__main__":
   py_files = [p for p in SRC_DIR.rglob("*.py")]
   md_files = [make_md_file(p) for p in py_files]

   nav = build_nav(md_files)
   print("\n# Paste this into mkdocs.yml under 'nav:'\n")
   print("  - Documentation:")
   for line in dump_nav(nav, indent=2):
      print(line)
