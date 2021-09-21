# Clixel Blog

A Hugo version of [blog.clixel.com](https://blog.clixel.com) using a lightly modified theme, [cactus](https://github.com/monkeyWzr/hugo-theme-cactus).

## Install

`brew install hugo`
`python3 venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

## Dev (fires up local hugo server)

`fab dev`

## Basics (because I have 5 minutes of memory at this point)

Edit various config in `/config.toml` such as theme and colortheme. Edit layouts and styles in `/themes/cactus/`. Add a new post in `/content/posts`.

## Deploy (build static files and rsyncs)

`fab deploy`
