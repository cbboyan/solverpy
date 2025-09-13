site_name: SolverPy
site_url: https://cbboyan.github.io/solverpy/

theme: 
  name: material

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.superfences:
      custom_fences:
        - name: dia
          class: dia
          format: !!python/name:solverpy.tools.markdown.dia.link

extra_javascript:
  - js/solverpy.js

extra_css:
  - css/solverpy.css

plugins:
  - search
  - build_plantuml:
      render: 'local' # or "local" for local rendering
      bin_path: '/usr/bin/plantuml' # ignored when render: server
      #server: 'http://www.plantuml.com/plantuml' # official plantuml server
      #disable_ssl_certificate_validation: true # for self-signed and invalid certs
      output_format: 'svg' # or "png"
      allow_multiple_roots: false # in case your codebase contains more locations for diagrams (all ending in diagram_root)
      diagram_root: 'docs/diagrams' # should reside under docs_dir
      output_folder: 'out'
      input_folder: 'src'
      input_extensions: '' # comma separated list of extensions to parse, by default every file is parsed
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
  - autorefs: {}

nav:
  - Home: index.md
  - Tutorial: tutorial.md
  - Options: options.md
  - Markdown: markdown.md
