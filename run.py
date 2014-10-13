# -*- coding: utf-8 -*-

import urllib
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

define('port', default=3000, help='run on the given port', type=int)
define('debug', default=False, help='run in debug mode')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/translate", TranslateHandler)
        ]
        settings = dict(
            debug=options.debug
        )
        super(Application, self).__init__(handlers, **settings)


class TranslateApiRequest(tornado.httpclient.HTTPRequest):
    def __init__(self, query, *arg, **kargs):
        lang = kargs.get('lang', "zh")
        url = "http://translate.google.com/translate_tts"
        url += "?tl=%s&q=%s" % (lang, query)
        user_agent = '"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS' + \
            'X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) ' + \
            'Chrome/18.0.1025.163 Safari/535.19'
        headers = {
            'Host': "translate.google.com",
            'Referer': "http://www.gstatic.com/translate/sound_player2.swf",
            'User-Agent': user_agent
        }
        super(TranslateApiRequest, self).__init__(url, headers=headers)


class TranslateHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        query = self.get_argument('q')
        http_client = AsyncHTTPClient()
        req = TranslateApiRequest(query)
        resp = yield http_client.fetch(req)
        self.set_header("Content-Type", 'audio/mpeg')
        self.set_header("Content-Disposition", 'filename="music.mp3"')
        self.write(resp.body)


def main():
    tornado.options.parse_command_line()
    httpserver = tornado.httpserver.HTTPServer(Application())
    httpserver.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
