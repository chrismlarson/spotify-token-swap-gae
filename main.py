# !/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import urllib
import json
from google.appengine.api import urlfetch


# CHANGE these values to your own
k_client_id = "spotify-ios-sdk-beta"
k_client_secret = "ba95c775e4b39b8d60b27bcfced57ba473c10046"
k_client_callback_url = "spotify-ios-sdk-beta://callback"


class SpotifyTokenSwap(webapp2.RequestHandler):
    def get(self):
        code = self.request.get('code')
        url = 'https://ws.spotify.com/oauth/token'
        params = {
            'grant_type': 'authorization_code',
            'client_id': k_client_id,
            'client_secret': k_client_secret,
            'redirect_uri': k_client_callback_url,
            'code': code
        }

        encoded_params = urllib.urlencode(params)
        response = urlfetch.fetch(url=url,
                                  payload=encoded_params,
                                  method=urlfetch.POST)

        self.response.headers.add_header("Access-Control-Allow-Origin", '*')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.status = response.status_code
        self.response.write(json.dumps(response.content))


app = webapp2.WSGIApplication([
                                  ('/swap', SpotifyTokenSwap)
                              ], debug=False)