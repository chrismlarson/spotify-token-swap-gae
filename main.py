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
import base64
import urllib
import json
import simplecrypt
from google.appengine.api import urlfetch

# CHANGE these values to your own that come from Spotify Dev
k_client_id = ""
k_client_secret = ""
k_client_callback_url = ""

# CHANGE this to a random value that you create of reasonable length for security
k_encryption_secret = ""

# Spotify endpoints
k_spotify_accounts_endpoint = "https://accounts.spotify.com"


class SpotifyTokenSwap(webapp2.RequestHandler):
    def post(self):
        auth_code = self.request.get('code')
        auth_header = "Basic " + base64.b64encode(k_client_id + b":" + k_client_secret)
        params = {
            "grant_type": "authorization_code",
            "redirect_uri": k_client_callback_url,
            "code": auth_code
        }
        encoded_params = urllib.urlencode(params)

        response = urlfetch.fetch(url=k_spotify_accounts_endpoint + "/api/token",
                                  payload=encoded_params,
                                  method=urlfetch.POST,
                                  headers={"Authorization": auth_header},
                                  validate_certificate=True)

        if response.status_code == 200:
            token_data = json.loads(response.content)
            refresh_token = token_data["refresh_token"]
            encrypted_token = simplecrypt.encrypt(k_encryption_secret, refresh_token)
            base64_encrypted_token = base64.encodestring(encrypted_token)
            token_data["refresh_token"] = base64_encrypted_token
            response.content = json.dumps(token_data)

        self.response.headers.add_header("Access-Control-Allow-Origin", '*')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.status = response.status_code
        self.response.write(response.content)


class SpotifyTokenRefresh(webapp2.RequestHandler):
    def post(self):
        base64_encrypted_token = self.request.get('refresh_token')
        auth_header = "Basic " + base64.b64encode(k_client_id + b":" + k_client_secret)

        encrypted_token = base64.decodestring(base64_encrypted_token)
        refresh_token = simplecrypt.decrypt(k_encryption_secret, encrypted_token)

        params = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        encoded_params = urllib.urlencode(params)

        response = urlfetch.fetch(url=k_spotify_accounts_endpoint + "/api/token",
                                  payload=encoded_params,
                                  method=urlfetch.POST,
                                  headers={"Authorization": auth_header},
                                  validate_certificate=True)

        self.response.headers.add_header("Access-Control-Allow-Origin", '*')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.status = response.status_code
        self.response.write(response.content)


app = webapp2.WSGIApplication([
                                  ('/swap', SpotifyTokenSwap),
                                  ('/refresh', SpotifyTokenRefresh)
                              ], debug=False)