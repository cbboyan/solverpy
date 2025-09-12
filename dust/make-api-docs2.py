#!/usr/bin/env python3
from pathlib import Path

SRC_DIR = Path("src")
DOCS_DIR = Path("docs/api")

def make_md_file(pyfile: Path):
    rel = pyfile.relative_to(SRC_DIR)

    if rel.name == "__init__.py":
        # package module: solverpy/foo/__init__.py → solverpy.foo
        module = ".".join(rel.parent.parts)
        md_path = DOCS_DIR / rel.parent / "index.md"
    else:
        # normal module: solverpy/foo/bar.py → solverpy.foo.bar
        module = ".".join(rel.with_suffix("").parts)
        md_path = DOCS_DIR / rel.with_suffix(".md")

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
        name = parts[-1].replace(".md", "")
        if name == "index":
            current["_self"] = str(Path("api") / path)
        else:
            current[name] = str(Path("api") / path)
    return nav

def dump_nav(nav, indent=0):
    """Pretty-print nav dict as YAML fragment."""
    lines = []
    for key, value in sorted(nav.items()):
        if isinstance(value, dict):
            # If this dict has a "_self", it's a package with a page
            self_page = value.get("_self")
            if self_page:
                lines.append("  " * indent + f"- {key.capitalize()}: {self_page}")
                # nest the children
                children = {k: v for k, v in value.items() if k != "_self"}
                if children:
                    lines.extend(dump_nav(children, indent + 1))
            else:
                lines.append("  " * indent + f"- {key.capitalize()}:")
                lines.extend(dump_nav(value, indent + 1))
        else:
            lines.append("  " * indent + f"- {key.capitalize()}: {value}")
    return lines

if __name__ == "__main__":
    py_files = [p for p in SRC_DIR.rglob("*.py")]
    md_files = [make_md_file(p) for p in py_files]

    nav = build_nav(md_files)
    print("\n# Paste this into mkdocs.yml under 'nav:'\n")
    for line in dump_nav(nav, indent=1):
        print(line)
