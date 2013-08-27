# -*- coding: utf8 -*-
import webbrowser
import socket

APP_KEY = '1234567' # app key
APP_SECRET = 'abcdefghijklmn' # app secret
CALLBACK_URL = 'http://www.example.com/callback' # callback url

class Crawler:
    def __init__(self):
        pass

    def get_sentence(self, body):
        pass

def gen_redirect_url(self):
    ip = socket.gethostbyname(socket.gethostname())
    url = 'http://' + ip + '/authorize_callback'
    return url

class Weibo:
    def __init__(self, token=None, app_key=None, secret_key=None, redirect_url=None):
        self.token = token
        self.app_key = app_key
        self.secret_key = secret_key
        self.redirect_url = redirect_url
        if token:
            pass
        else:
            self.authorize()

    def authorize(self):
        url = 'https://api.weibo.com/oauth2/authorize?%s'
        params = urllib.urlencode(dict(client_id=self.app_key, 
                        redirect_uri=self.redirect_url))
        url = url % params
        webbrowser.open_new(url)


