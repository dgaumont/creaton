import logging
import tornado.web
import torndb
import json

logging.basicConfig(level=logging.INFO)

def getroute():
    return "hello"

#------------------------------------------------------------------------------
class HelloHandler(tornado.web.RequestHandler):

    def get(self):
        logging.info("Hello GET")
        self.write('OK')

    def post(self):
        logging.info("Hello POST")
        self.write('OK')
    
