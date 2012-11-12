"""flog.

Usage:
  flog.py
  flog.py [options]
  flog.py --serve [--port=<port>] [--host=<host>]...

  flog.py -h | --help
  flog.py --version

Options:
  -h --help     Show this screen.

  --serve        Run a HTTP server and rebuild rebuilds automatically.
  --port=<port>  Set the port for the dev server [default: 8000].
  --host=<host>  Set the host for the dev server [default: 0.0.0.0].

  -c --content=<content_path>    Set path for content [default: ./content].
  -o --output=<output_path>      Set path for output [default: ./public].
  -t --template=<template_path>  Set the template path [default: ./templates].
  -d --default=<default>         Set default template [default: _default.html].
"""
import sys
from docopt import docopt
from flog import SiteBuilder

if __name__ == "__main__":
    args = docopt(__doc__, version=1.0)

    sb = SiteBuilder(
        content_path = args['--content'],
        output_path = args['--output'],
        template_path = args['--template'],
        default_template = args['--default']
    )

    if args['--serve']:
        port = int(args['--port'])
        print("Starting dev server on port: {0}".format(port))
        sb.start_dev_server(args['--host'], port)
    else:
        print("Building site...")
        sb.build()
        print("done")





