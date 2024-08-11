* to build:

    $ python3 -m build

* to upload:

    $ twine upload dist/* 

* to generate requirements.txt of the package

    $ pipreqs 

* to see the current version string

    $ setuptools-git-versioning

* to update the version tags

    $ ./version-tags.py

  and run the commands outputed;
  and then push the tags:

    $ git push --tags

* to update the CHANGELOG.md run:

    $ ./change-log.sh

+ stuff about git amend: https://www.atlassian.com/git/tutorials/rewriting-history

```bash
# Edit hello.py and main.py
git add hello.py
git commit 
# Realize you forgot to add the changes from main.py 
git add main.py 
git commit --amend --no-edit
```

+ git hooks: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks


+ automatically push tags for this repo
   
   $ git config push.followTags true

  or for all the repos globally:

   $ git config --global push.followTags true


