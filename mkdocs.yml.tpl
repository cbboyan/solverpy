site_name: SolverPy
site_url: https://cbboyan.github.io/solverpy/

theme: 
  name: material

markdown_extensions:
  #- markdown.extensions.attr_list
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
          paths: [src]
          options:
            show_source: true
            show_root_heading: true
            show_root_full_path: true
            show_signature_annotations: true
  - autorefs: {}


nav:
  - Home: index.md
  - Tutorial: tutorial.md
  - Options: options.md
  - Markdown: markdown.md
  - Test: test.md
