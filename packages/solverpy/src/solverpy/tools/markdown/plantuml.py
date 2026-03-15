import os
import subprocess
import hashlib
import inspect

from ..external import catching

OPTIONS = ["name", "alt"]

ROOT = "docs"

UML = """
@startuml
skinparam backgroundColor transparent

{code}
@enduml
"""

HTML = """
<div class="image-container">
   <img src="{src}" alt="{alt}" class="clickable-image">
</div>
"""


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
   del md
   assert language == "plantuml"
   okay = True
   for (k, v) in inputs.items():
      if k in OPTIONS:
         options[k] = v
      else:
         attrs[k] = v
   return okay


def buildsvg(f_puml: str, code: str) -> None:
   code = UML.format(code=code)
   f_svg = f_puml[:-5] + ".svg"  # strip ".puml"
   if os.path.isfile(f_puml) and os.path.isfile(f_svg):
      with open(f_puml) as f:
         oldcode = f.read()
      if oldcode == code:
         print(f"Skipped existing PlantUML diagram: {f_puml}")
         return
   with open(f_puml, "w") as f:
      f.write(code)
   subprocess.run(["plantuml", "-tsvg", f_puml])
   print(f"Generated PlantUML diagram: {f_puml}")


@catching
def plantuml(code, language, css_class, options, md, **kwargs):
   del css_class, md, kwargs
   assert language == "plantuml"
   if "name" in options:
      name = options["name"]
   else:
      name = hashlib.md5(code.encode("utf-8")).hexdigest()
   f_puml = os.path.join(ROOT, "dia", f"{name}.puml")
   os.makedirs(os.path.dirname(f_puml), exist_ok=True)
   buildsvg(f_puml, code)
   f_svg = os.path.join("dia", f"{name}.svg")
   alt = options["alt"] if "alt" in options else name
   f_rel = os.path.relpath(f_svg, os.path.dirname(frame_filename()))
   return HTML.format(src=f_rel, alt=alt)
