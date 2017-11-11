#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import re
import logging
import signal

import tornado.web
import tornado.template
import tornado.ioloop
import tornado.httpserver
import json
from tornado.options import options, define

logging.basicConfig(level=logging.INFO)

define("port", default=8080, help="TCP port to connect to")
define("dir", default=None, help="Directory from which to serve files")

#------------------------------------------------------------------------------
class IndexHandler(tornado.web.RequestHandler):

    def get(self, path):
        """ GET method to list contents of directory or
        write index page if index.html exists."""

        # remove heading slash
        path = path[1:]

        for index in ['index.html', 'index.htm']:
            index = os.path.join(path, index)
            if os.path.exists(index):
                with open(index, 'rb') as f:
                    self.write(f.read())
                    self.finish()
                    return
        html = self.generate_index(path)
        self.write(html)
        self.finish()

    def generate_index(self, path):
        """ generate index html page, list all files and dirs.
        """
        if path:
            files = os.listdir(path)
        else:
            files = os.listdir('.')
        files = [filename + '/'
                if os.path.isdir(os.path.join(path, filename))
                else filename
                for filename in files]
        html_template = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>
        <title>Directory listing for /{{ path }}</title>
        <body>
        <h2>Directory listing for /{{ path }}</h2>
        <hr>
        <ul>
        {% for filename in files %}
        <li><a href="{{ filename }}">{{ filename }}</a>
        {% end %}
        </ul>
        <hr>
        </body>
        </html>
        """
        t = tornado.template.Template(html_template)
        return t.generate(files=files, path=path)


#------------------------------------------------------------------------------
class StaticFileHandler(tornado.web.StaticFileHandler):
    def write(self, chunk):
        super(StaticFileHandler, self).write(chunk)
        logging.info('write called')
        self.flush()

#------------------------------------------------------------------------------
def stop_server(signum, frame):
    tornado.ioloop.IOLoop.instance().stop()
    logging.info('Stopped!')

#------------------------------------------------------------------------------
def loadHandlers(app):
    logging.info('load handler:')
    files = os.listdir(".")
    fh = []
    for f in files:
        m=re.search(".*handler.py$", f)
        if m!=None:
            logging.info('-> {}...'.format(f))
            modulename=re.sub('.py', '', f)
            classname=re.sub('handler', 'Handler', modulename)
            c = classname.split()[0][0]
            classname=re.sub(c, c.upper(), classname)

            module = __import__(modulename)
            route = module.getroute()
            class_ = getattr(module, classname)
            print classname, modulename, "route:", route
            
            app.add_handlers(
                r".*",  # match any host
                [
                    (
                        r"/"+route,
                        class_
                    )    
                ]
            )
  
#------------------------------------------------------------------------------
def run():
    options.parse_command_line()

    if options.dir != None:
        logging.info('dir location: %s' % options.dir)
        os.chdir(options.dir)
        application = tornado.web.Application([
            (r'(.*)/$', IndexHandler,),
            (r'/(.*)$', StaticFileHandler, {'path': options.dir}),
        ])
    else:
        application = tornado.web.Application()

    loadHandlers(application)

    signal.signal(signal.SIGINT, stop_server)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    logging.info('Serving HTTP on 0.0.0.0 port %d ...' % options.port)
    tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    run()

