site_name: SolverPy
site_url: https://cbboyan.github.io/solverpy/

theme:
  name: material
  favicon: img/favicon.svg

markdown_extensions:
  #- markdown.extensions.attr_list
  - admonition
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.superfences:
      custom_fences:
        - name: plantuml
          class: plantuml
          format: !!python/name:solverpy.tools.markdown.plantuml.plantuml
          validator: !!python/name:solverpy.tools.markdown.plantuml.validator

extra_javascript:
  - js/solverpy.js

extra_css:
  - css/solverpy.css
  - css/heading.css
  - css/color.css

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [packages/solverpy/src, packages/solverpy-learn/src]
          options:
            show_source: true
            show_root_heading: true
            show_root_full_path: true
            show_signature_annotations: true
  - autorefs: {}


nav:
  - 🏠 Home: index.md
  - 📥 Install: install.md
  - 🧭 Usage: usage.md
  - 🎓 Tutorials:
      - 🧪 Evaluating E: tutorials/eval-eprover.md
      - ⚗️ Evaluating cvc5: tutorials/eval-cvc5.md
      - 🧠 Training ENIGMA: tutorials/enigma-training.md
      - 🐍 Python API:
          - 💡 Solving a problem: tutorials/python-solving.md
          - 🔧 Benchmark evaluation: tutorials/python-evaluation.md
  - ⌨️ Commands: commands.md
