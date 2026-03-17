---
name: document-code
description: Use this skill when the user asks to add, fix, or audit documentation (docstrings) in the solverpy codebase. Triggers on requests like "document this module", "add docstrings", "fix missing documentation", "what is undocumented", "audit docstrings".
---

# document-code

Adds or audits Python docstrings in the solverpy package following the project's
mkdocstrings + mkdocs-material conventions.

## Audit first

Before writing anything, read every target file fully and produce a table:

| File | Module docstring | Class docstring | Missing methods |
|---|---|---|---|
| ... | ✓/✗ | ✓/✗ | list of names |

Report this to the user and confirm before proceeding.

## Priority order

1. Module-level docstrings (missing = entire page is blank in docs)
2. Abstract methods and properties (contract for subclasses)
3. `__init__` with non-trivial parameters
4. Public methods and properties
5. Dunder helpers (`__str__`, `__repr__`, `__hash__`, `__eq__`)

## Module docstrings

Use a Markdown `# Title` heading followed by a prose description.
Cross-link to important classes with mkdocstrings syntax:

```python
"""
# Short title describing the module's role

One or two sentences.  Cross-link with
[`ClassName`][solverpy.module.path.ClassName].

Optionally include a PlantUML diagram (see below).
"""
```

## Class docstrings

Every class (except simple helpers and data containers) should include a
PlantUML class hierarchy diagram showing the class in context — its superclass
and direct subclasses.  Use the `name=` attribute so the SVG gets a stable
filename:

```python
class Foo(Bar):
   """
   Short description.

   ```plantuml name="module-classname"
   abstract class solverpy.module.Bar
   abstract class solverpy.module.Foo extends solverpy.module.Bar {
      {abstract} + abstract_method() : ReturnType
      + concrete_method() : ReturnType
   }
   abstract class solverpy.module.Child extends solverpy.module.Foo
   ```

   Longer prose explaining responsibilities, key invariants, etc.
   """
```

**What to show in the diagram:**
- The class itself with its key fields and methods
- Its direct superclass (as a plain declaration, no body needed)
- Its known direct subclasses (as plain declarations)
- Mark abstract classes with `abstract class`
- Mark abstract members with `{abstract}`
- Use `--` separator between fields and methods in the class body

**What to skip PlantUML for:**
- Pure data containers / TypedDicts with no behaviour
- Small helper classes with no inheritance (e.g. `SolverPyObj`)
- Private / internal classes not exposed in the public API

## Method docstrings

### Abstract / interface methods — explain the contract:

```python
def process(self, output: str) -> "Result":
   """
   Parse raw solver output and return a Result dict.

   Args:
       output: combined stdout/stderr from the solver run.

   Returns:
       dict with at least ``status`` (str) and ``runtime`` (float).
   """
   raise NotImplementedError()
```

### `__init__` with meaningful parameters — use Args section:

```python
def __init__(self, cmd: str, limit: str, plugins: list["Plugin"] = []):
   """
   Args:
       cmd: base shell command (e.g. ``/usr/bin/eprover``).
       limit: resource limit string (e.g. ``"T10"``).
       plugins: extra plugins registered before the built-in limit plugins.
   """
```

### Properties — single line is fine:

```python
@property
def name(self) -> str:
   """Solver name including the resource limit, e.g. ``E:T10``."""
```

### Delegation methods — keep it short:

```python
def process(self, output: str) -> "Result":
   """Delegate output parsing to the wrapped solver."""
   return self.solver.process(output)
```

### Simple helpers — one line:

```python
def __str__(self) -> str:
   """Return the solver name."""
```

## Class variable docstrings

Inline docstrings directly after the assignment:

```python
class ShellSolver(SolverPy):
   _binary: str = ""
   """Default solver binary name looked up via ``shutil.which``."""
```

## Style rules

- **3-space indent** (project standard — do not use 4 spaces)
- Use backtick-quoted names inside docstrings: `` `ClassName` `` for prose,
  `[`ClassName`][module.path]` for hyperlinks in module/class docstrings
- Double backticks inside docstrings for inline code: `` ``T10`` ``
- No period at end of single-line docstrings; period at end of multi-line
  closing sentences
- Do not add docstrings to private helpers that are self-evident from the code
- Do not add `Returns:` sections for `-> None` methods
- Keep Args/Returns sections only where the signature alone is not self-documenting

## PlantUML tips

- Use fully-qualified class names: `solverpy.solver.solver.Solver`
- Use `extends` for inheritance, `o--` / `*--` for aggregation/composition
- Mark abstract members with `{abstract}`
- Add `--` separator between fields and methods
- Keep diagrams in class docstrings (not module docstrings) unless the module
  overview diagram shows multiple classes
