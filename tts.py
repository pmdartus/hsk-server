import os
import tornado

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.options import options


class TranslateApiRequest(tornado.httpclient.HTTPRequest):
    """HTTPRequest for Google TTS API

    Inherit from tornado.httpclient.HTTPRequest

    Args:
      query (str): text to translate
      lang  (str): lang of text, default is set to 'zh'
    """
    def __init__(self, query, lang="zh"):
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


class TextToSpeach(object):
    """Helper to retrieve voice of a word / sentence

    Attributes:
      query (str): word / sentence to fetch
    """
    def __init__(self, query):
        self.query = query

    @gen.coroutine
    def fetch_voice(self):
        """Retrieve and cache the voice of the selected text

        Use coroutine to defer the execution

        Return:
          str: path to load the cached file
        """
        path = self._cache_path()
        if not os.path.exists(path):
            http_client = AsyncHTTPClient()
            req = TranslateApiRequest(self.query)
            resp = yield http_client.fetch(req)
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with open(path, 'w+') as f:
                f.write(resp.body)
        raise gen.Return(path)

    def _cache_path(self):
        """Return the possible path of the cache file"""
        root = os.path.dirname(__file__)
        relative_path = "%s/%s.mp3" % (options.tmp, self.query)
        path = os.path.join(root, relative_path)
        return path
