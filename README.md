# Clixel Blog

A Hugo version of [blog.clixel.com](https://blog.clixel.com) using a lightly modified theme, [cactus](https://github.com/monkeyWzr/hugo-theme-cactus).

## Install

`brew install hugo`
`python3 venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

## Dev (fires up local hugo server)

`fab dev`

## Deploy (build static files and rsyncs)

`fab deploy`
