Hurdles
=======

some problems I had whilst working on this project;

ReadTheDocs;

someone forgot to add a database migration definition file, so I had to contact someone on IRC to fix it

ReadTheDocs uses Python 3.2, and they use by default a version of jinja2 with Unicode literals, which Python 3.2 does not support.
As such, I had to build in a virtalenv, and use the requirements.txt file we can provide to force a version of
jinja2 that doesn't use Unicode literals, and a version of `markupsafe` that doesn't either. This was corrected a few days later on
ReadTheDocs' end.
