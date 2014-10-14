# -*- coding: utf-8 -*-

import os
import json
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

define('port', default=3000, help='run on the given port', type=int)
define('tmp', default='tmp', help='directory to store the downloaded data')
define('debug', default=False, help='run in debug mode')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/translate", TranslateHandler),
            (r"/hsk/([1-6])", HskHandler)
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
        root = os.path.dirname(__file__)
        relative_path = "%s/%s.mp3" % (options.tmp, query)
        path = os.path.join(root, relative_path)
        if not os.path.exists(path):
            http_client = AsyncHTTPClient()
            req = TranslateApiRequest(query)
            resp = yield http_client.fetch(req)
            if not os.path.exists(os.path.dirname(relative_path)):
                os.makedirs(os.path.dirname(relative_path))
            with open(relative_path, 'w+') as f:
                f.write(resp.body)
        with open(relative_path) as f:
            self.set_header("Content-Type", 'audio/mpeg')
            self.set_header("Content-Disposition", 'filename="music.mp3"')
            self.write(f.read())


class HskHandler(tornado.web.RequestHandler):
    def get_hsk(self, level):
        root = os.path.dirname(__file__)
        relative_path = "files/level{}.txt".format(level)
        path = os.path.join(root, relative_path)
        hsk = []
        with open(path) as f:
            for l in f:
                val = l.rstrip().split('\t')
                word = {
                    'traditional': val[0],
                    'simplified': val[1],
                    'vocal': val[2],
                    'pinyin': val[3],
                    'translation': val[4].split('; ')
                }
                hsk.append(word)
        return hsk

    def get(self, level):
        hsk = []
        for i in xrange(1, int(level) + 1):
            hsk.extend(self.get_hsk(i))
        self.write(json.dumps(hsk))


def main():
    tornado.options.parse_command_line()
    httpserver = tornado.httpserver.HTTPServer(Application())
    httpserver.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
