"""
    spotify.py
    ~~~~~~~~~~~~
    This file contains functions that communicate with the Spotify API.

    :copyright: 2019 Moodify (High-Mood)
    :authors:
           "Stan van den Broek",
           "Mitchell van den Bulk",
           "Mo Diallo",
           "Arthur van Eeden",
           "Elijah Erven",
           "Henok Ghebrenigus",
           "Jonas van der Ham",
           "Mounir El Kirafi",
           "Esmeralda Knaap",
           "Youri Reijne",
           "Siwa Sardjoemissier",
           "Barry de Vries",
           "Jelle Witsen Elias"
"""

import requests
from requests.auth import HTTPBasicAuth

from app.utils.exceptions import StatusCodeError
from app.utils.models import User
from config import SPOTIFY_CLIENT, SPOTIFY_SECRET


def get_artists(access_token, artistids):
    """
    Gets Spotify catalog information for several artists based on their Spotify IDs.
    :param access_token: A valid access token from the Spotify Accounts service.
    :param artistids: A list of the Spotify IDs for the artists.
    :return: Response body which contains a list of object whose key is "artists" and
             whose value is an array of artist objects in JSON format.
    """
    url = "https://api.spotify.com/v1/artists?ids={}".format(",".join(artistids))

    return _get_basic_request(access_token, url)


def get_audio_features(access_token, trackids):
    """
    Gets Spotify catalog information for several artists based on their Spotify IDs.
    :param access_token: A valid access token from the Spotify Accounts service.
    :param trackids: A list of the Spotify IDs for the artists.
    :return: Response body contains an object whose key is "artists" and
             whose value is an array of artist objects in JSON format.
    """
    url = "https://api.spotify.com/v1/audio-features/?ids={}".format(",".join(trackids))

    return _get_basic_request(access_token, url)


def get_recently_played(access_token, limit=50):
    """
    Gets tracks from the current user’s recently played tracks.
    :param access_token: A valid access token from the Spotify Accounts service.
    :param limit: The maximum number of items to return.
    :return: Response body contains an array of play history objects
            (wrapped in a cursor-based paging object) in JSON format.
    """
    url = "https://api.spotify.com/v1/me/player/recently-played?limit={}".format(limit)

    return _get_basic_request(access_token, url)


def get_user_info(access_token):
    """
    Gets detailed profile information about the current user.
    :param access_token: A valid access token from the Spotify Accounts service.
    :return: Response body contains a user object in JSON format.
    """
    url = "https://api.spotify.com/v1/me"

    return _get_basic_request(access_token, url)


def get_recommendations(access_token, recommendation_count, track_string, param_string):
    """
    Gets song recommendations based on the given parameters.
    :param access_token: A valid access token from the Spotify Accounts service.
    :param recommendation_count: The target size of the list of recommended tracks.
    :param track_string: A comma separated list of Spotify IDs for a seed track.
    :param param_string: For each tunable track attribute, a range on the
                         selected track attribute’s value can be provided.
    :return: A response body contains a recommendations response object in JSON format.
    """
    url = "https://api.spotify.com/v1/recommendations?limit=" + \
          f"{recommendation_count}&seed_tracks={track_string}{param_string}"

    return _get_basic_request(access_token, url)


def _get_basic_request(access_token, url):
    """ Handles basic requests to the Spotify API. """
    headers = {'Authorization': "Bearer {}".format(access_token)}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 429:
            __import__('time').sleep(int(response.headers['Retry-After']))
        else:
            raise StatusCodeError(response)

    return response.json()


def get_access_token(refresh_token):
    """
    Gets a new access token for the user.
    :param refresh_token: The refresh token returned from the authorization code exchange.
    :return: Response body contains the new access token for the user in JSON format.
    """
    url = "https://accounts.spotify.com/api/token"

    body = {"grant_type": "refresh_token",
            "refresh_token": refresh_token}

    response = requests.post(url, data=body, auth=HTTPBasicAuth(SPOTIFY_CLIENT, SPOTIFY_SECRET))

    if response.status_code != 200:
        raise StatusCodeError(response)

    return response.json()["access_token"]


def get_playlists(userid, url=None, output=[]):
    access_token = get_access_token(User.get_refresh_token(userid))
    if not url:
        url = "https://api.spotify.com/v1/me/playlists"
    headers = {'Authorization': "Bearer {}".format(access_token)}
    response = requests.get(url, headers=headers)

    json_data = response.json()

    for item in json_data["items"]:
        resp = {"name": item['name'],
                "id": item['id'],
                'href': item['href'],
                'public': item['public'],
                'track_href': item['tracks']['href'],
                'track_count': item['tracks']['total'], }
        output.append(resp)

    if json_data['next']:
        return get_playlists(userid, json_data['next'], output)

    return output
