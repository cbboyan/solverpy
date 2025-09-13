import os
import subprocess
import hashlib
import inspect

OPTIONS = ["name", "alt"]

ROOT = "docs"


def frame_filename():
   for frame_info in inspect.stack():
      frame = frame_info.frame
      if 'page' in frame.f_locals:
         page = frame.f_locals['page']
         if hasattr(page, 'file') and hasattr(page.file, 'dest_uri'):
            filename = page.file.dest_uri
            break
   else:
      filename = "unknown"
   return filename


def validator(language, inputs, options, attrs, md):
   okay = True
   for (k, v) in inputs.items():
      if k in OPTIONS:
         options[k] = v
      else:
         attrs[k] = v
   return okay


def linkhtml(src: str, alt: str) -> str:
   return f'''
<div class="image-container">
  <img src="{src}" alt="{alt}" class="clickable-image">
</div>
'''


def buildsvg(f_puml):
   subprocess.run(["plantuml", "-tsvg", f_puml])
   print(f"Generated diagram: {f_puml}")


def plantuml(code, language, css_class, options, md, **kwargs):
   if "name" in options:
      name = options["name"]
   else:
      name = hashlib.md5(code.encode("utf-8")).hexdigest()
   f_puml = os.path.join(ROOT, "dia", f"{name}.puml")
   os.makedirs(os.path.dirname(f_puml), exist_ok=True)
   with open(f_puml, "w") as f:
      f.write("@startuml\n")
      f.write("skinparam backgroundColor transparent\n\n")
      f.write(code)
      f.write("\n@enduml\n")
   buildsvg(f_puml)
   f_svg = os.path.join("dia", f"{name}.svg")
   alt = options["alt"] if "alt" in options else name
   f_rel = os.path.relpath(f_svg, os.path.dirname(frame_filename()))
   return linkhtml(f_rel, alt)
