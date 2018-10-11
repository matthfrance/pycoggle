# -*- coding: utf-8 -*-

from pycoggle.pycoggle import *


username='xxx'
password='xxx'

oauth_code='xxx'

access_token = CoggleApi.get_access_token(oauth_code, username, password, 'http://localhost:8080')
