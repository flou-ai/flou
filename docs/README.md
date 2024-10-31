# Flou documentation

Created with MkDocs[0].

## Installing and running locally

Inside your virtualenv:

``` bash
% cd docs
% pip install -r requirements.txt
% mkdocs serve -a 0.0.0.0:8002
```

Visit `http://localhost:8002/` to preview the docs.

## Building locally

If you want to build the docs locally you can run:

``` bash
% mkdocs build
```

And to upload them to a server run:

``` bash
% scp -r ./build/* user@host:/path/to/server/root
```

[0] https://www.mkdocs.org/