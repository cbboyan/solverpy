rm -rf docs/api
python3 mkdocs-api.py

# Regenerate docs/api/*.md and mkdocs.yml whenever a source file changes, so
# new/removed/renamed modules show up without restarting `mkdocs serve`
# (mkdocs itself only re-renders already-known pages from watched paths; it
# does not run mkdocs-api.py for us). Editing mkdocs.yml.tpl itself is rare
# enough that it still needs a manual rerun (or restart).
watchmedo shell-command \
   --patterns="*.py" \
   --recursive \
   --ignore-directories \
   --command='python3 mkdocs-api.py' \
   packages/solverpy/src packages/solverpy-learn/src &
WATCHER_PID=$!
trap 'kill $WATCHER_PID 2>/dev/null' EXIT

# --watch makes mkdocs reload when a .py file's docstrings change even
# though no page under docs/ changed. (mkdocs.yml is rewritten above on
# every source change, but per mkdocs's own limitation, a *nav-structure*
# change there -- new/removed module, or editing mkdocs.yml.tpl -- still
# needs a manual restart of this script; only *content* changes reload live.)
mkdocs serve --watch packages/solverpy/src --watch packages/solverpy-learn/src
