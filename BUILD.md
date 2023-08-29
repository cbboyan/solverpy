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

