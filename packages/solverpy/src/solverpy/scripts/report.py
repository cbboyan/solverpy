import os
import sys


HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
* {{ box-sizing: border-box; }}
body {{
   font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
   font-size: 15px;
   line-height: 1.6;
   color: #333;
   max-width: 960px;
   margin: 0 auto;
   padding: 2rem 1.5rem;
   background: #fff;
}}
h1, h2, h3, h4 {{ margin-top: 1.4em; margin-bottom: 0.4em; font-weight: 600; }}
h1 {{ font-size: 1.8em; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.3em; }}
h2 {{ font-size: 1.4em; border-bottom: 1px solid #e0e0e0; padding-bottom: 0.2em; }}
h3 {{ font-size: 1.15em; }}
table {{
   border-collapse: collapse;
   width: 100%;
   margin: 1em 0;
   font-size: 0.9em;
}}
th, td {{
   border: 1px solid #d0d0d0;
   padding: 0.4em 0.75em;
   text-align: left;
}}
th {{ background: #f4f4f4; font-weight: 600; }}
tr:nth-child(even) {{ background: #fafafa; }}
pre {{
   background: #f6f8fa;
   border: 1px solid #e0e0e0;
   border-radius: 4px;
   padding: 1em;
   overflow-x: auto;
   font-size: 0.85em;
   line-height: 1.5;
}}
code {{
   background: #f0f0f0;
   border-radius: 3px;
   padding: 0.1em 0.35em;
   font-size: 0.88em;
   font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}}
pre code {{
   background: none;
   padding: 0;
   font-size: inherit;
}}
blockquote {{
   border-left: 4px solid #ccc;
   margin: 0;
   padding: 0.5em 1em;
   color: #555;
   background: #f9f9f9;
}}
a {{ color: #0366d6; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.highlight {{ background: #f6f8fa; border-radius: 4px; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def convert(mdpath: str, htmlpath: str) -> None:
   import markdown

   extensions = [
      "pymdownx.highlight",
      "pymdownx.inlinehilite",
      "pymdownx.superfences",
      "tables",
   ]
   extension_configs = {
      "pymdownx.highlight": {
         "use_pygments": True,
         "noclasses": True,
      },
   }

   with open(mdpath) as f:
      text = f.read()

   md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
   body = md.convert(text)

   title = os.path.splitext(os.path.basename(mdpath))[0]
   html = HTML.format(title=title, body=body)

   with open(htmlpath, "w") as f:
      f.write(html)


def main(args):
   mdpath = args.mdfile
   if not os.path.isfile(mdpath):
      print(f"error: file not found: {mdpath}", file=sys.stderr)
      sys.exit(1)
   if args.output:
      htmlpath = args.output
   else:
      htmlpath = os.path.splitext(mdpath)[0] + ".html"
   convert(mdpath, htmlpath)
   print(f"Written: {htmlpath}")


def register(subparsers):
   p = subparsers.add_parser(
      "report",
      help="Convert a report .md file to an offline HTML page.",
      description="Convert a solverpy report Markdown file to a self-contained HTML page.",
   )
   p.add_argument("mdfile", metavar="FILE.md", help="Input Markdown report file.")
   p.add_argument("-o", "--output", metavar="FILE.html",
                  help="Output HTML file (default: same name with .html extension).")
   p.set_defaults(func=main)
