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
from UserToken import UserToken
from google.appengine.api import urlfetch

# CHANGE these values to your own
k_client_id = ""
k_client_secret = ""
k_client_callback_url = ""

# Spotify endpoints
k_spotify_accounts_endpoint = "https://accounts.spotify.com"
k_spotify_profile_endpoint = "https://api.spotify.com"


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
            profile_data = get_profile_data(token_data["access_token"])
            user_token_with_matching_username = UserToken.query(UserToken.username == profile_data["id"]).fetch(1)
            if user_token_with_matching_username:
                user_token_with_matching_username[0].key.delete()
            # Store user ID and refresh token in DB, so that we can retrieve it later.
            new_user_token = UserToken()
            new_user_token.username = profile_data["id"]
            new_user_token.refresh_token = token_data["refresh_token"]
            new_user_token.put()

        self.response.headers.add_header("Access-Control-Allow-Origin", '*')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.status = response.status_code
        self.response.write(response.content)


class SpotifyTokenRefresh(webapp2.RequestHandler):
    def post(self):
        spotify_id = self.request.get('id')
        auth_header = "Basic " + base64.b64encode(k_client_id + b":" + k_client_secret)
        user_token_with_matching_username = UserToken.query(UserToken.username == spotify_id).fetch(1)
        refresh_token = user_token_with_matching_username[0].refresh_token
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


def get_profile_data(access_token):
    response = urlfetch.fetch(url=k_spotify_profile_endpoint + "/v1/me",
                              method=urlfetch.GET,
                              headers={"Authorization": "Bearer " + access_token},
                              validate_certificate=True)
    return json.loads(response.content)


app = webapp2.WSGIApplication([
                                  ('/swap', SpotifyTokenSwap),
                                  ('/refresh', SpotifyTokenRefresh)
                              ], debug=False)