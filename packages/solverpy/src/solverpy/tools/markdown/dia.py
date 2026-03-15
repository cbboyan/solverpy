import os
import subprocess
import logging
import inspect

# from markdown.extensions import Extension
# from pymdownx.superfences import SuperFencesCodeExtension
# from markdown.preprocessors import Preprocessor

# def custom_formatter(source, language, css_class, options, md, **kwargs):
# def custom_formatter(source, language, css_class, options, md, classes=None, id_value='', attrs=None, **kwargs):

logger = logging.getLogger(__name__)

def frame_filename():
   for frame_info in inspect.stack():
      frame = frame_info.frame
      if 'page' in frame.f_locals:
         page = frame.f_locals['page']
         #if hasattr(page, 'file') and hasattr(page.file, 'src_path'):
         if hasattr(page, 'file') and hasattr(page.file, 'dest_uri'):
            #filename = page.file.src_path
            filename = page.file.dest_uri
            break
   else:
      filename = "unknown"
   return filename


OPTIONS = ["name"]

ROOT = "docs"

def validator(language, inputs, options, attrs, md):
   okay = True
   for (k, v) in inputs.items():
      if k in OPTIONS:
         options[k] = v
      else:
         attrs[k] = v
   return okay


# def link(code, language, options, md, **kwargs):
def link(code, language, css_class, options, md, **kwargs):
   image_name = code.strip()
   image_path = os.path.join('diagrams/out', f'{image_name}.svg')
   d_src = os.path.dirname(frame_filename())
   rel_path_html = os.path.relpath(image_path, d_src)

   print("LINK(dia): ", code, language, options, image_path, rel_path_html,
         os.getcwd())

   return f'''
<div class="image-container">
  <img src="{rel_path_html}" alt="{image_name}" class="clickable-image">
</div>
'''

def linkhtml(src: str, alt: str) -> str:
   return f'''
<div class="image-container">
  <img src="{src}" alt="{alt}" class="clickable-image">
</div>
'''

def buildsvg(f_puml):
   subprocess.run(["plantuml", "-tsvg", f_puml])
   print(f"Generated diagram {f_puml}")

def plantuml(code, language, css_class, options, md, **kwargs):
   assert "name" in options
   f_puml = f"{options['name']}.puml"
   f_puml = os.path.join(ROOT, "dia", f_puml)
   os.makedirs(os.path.dirname(f_puml), exist_ok=True)
   with open(f_puml, "w") as f:
      f.write("@startuml\n")
      f.write("skinparam backgroundColor transparent\n\n")
      f.write(code)
      f.write("\n@enduml\n")
   buildsvg(f_puml)
   f_svg = f"{options['name']}.svg"
   f_svg = os.path.join("dia", f_svg) # relative to `ROOT`
   alt = options["desc"] if "desc" in options else options["name"]
   f_rel = os.path.relpath(f_svg, os.path.dirname(frame_filename()))
   return linkhtml(f_rel, alt)


# def custom(source, language, css_class, options, md, **kwargs):
#
#    def printdir(obj):
#       for x in dir(obj):
#          print(x, type(getattr(obj, x)))  # ,
#          print(getattr(obj, x, "?"))
#          print()
#          # print(x, type(x), getattr(obj, x, "?"))
#
#    print(f"CUSTOM: {source} {options} {md} {kwargs}")
#    #printdir(md)
#    print("PARSER")
#    #printdir(md.parser)
#
#
#    print("FILENAME", filename)
#
#    return "CUSTUOM"
#
#
#
# # Preprocessor to inject current file dir and docs root
# class DiaFileInjector(Preprocessor):
#
#    def __init__(self, md, filepath, docs_dir):
#       super().__init__(md)
#       self.filepath = filepath
#       self.docs_dir = docs_dir
#
#    def run(self, lines):
#       self.md.current_file_dir = os.path.dirname(self.filepath)
#       self.md.docs_dir = self.docs_dir
#       return lines
#
#
# # The Extension
# class DiaExtension(Extension):
#
#    def __init__(self, **kwargs):
#       self.config = {
#          'filepath': ['', 'Path to current Markdown file'],
#          'docs_dir': ['docs', 'Path to the docs root folder']
#       }
#       super().__init__(**kwargs)
#
#    def extendMarkdown(self, md):
#       filepath = self.getConfig('filepath')
#       docs_dir = self.getConfig('docs_dir')
#
#       # Register superfences custom fence
#       SuperFencesCodeExtension(custom_fences=[{
#          'name': 'dia',
#          'class': 'dia',
#          'format': "dia_processor"
#       }]).extendMarkdown(md)
#
#       # Inject current file info
#       md.preprocessors.register(DiaFileInjector(md, filepath, docs_dir),
#                                 'dia_file_injector', 0)
#
#       print("YAN: ...")
#
#
# def makeExtension(**kwargs):
#    return DiaExtension(**kwargs)
