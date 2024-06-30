import os
import requests
import json
import pandas as pd
from requests import get, post
from urllib.parse import urlencode
from dotenv import load_dotenv
import webbrowser
import base64

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

def get_spotify_token():
    auth_url = "https://accounts.spotify.com/authorize"
    token_url = "https://accounts.spotify.com/api/token"

    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": "user-library-read user-read-recently-played playlist-read-private",
        "show_dialog": "true"
    }
    auth_request_url = f"{auth_url}?{urlencode(params)}"
    webbrowser.open(auth_request_url)
    redirect_response = input("Paste the full redirect URL here: ")

    code = redirect_response.split("?code=")[1]

    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI
    }
    response = post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Failed to get Spotify token.")
        return None

def get_recently_played_tracks(token):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("items")
    else:
        print("Failed to get recently played tracks.")
        return []

def get_saved_tracks(token):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("items")
    else:
        print("Failed to get saved tracks.")
        return []

def get_user_playlists(token):
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("items")
    else:
        print("Failed to get user playlists.")
        return []

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("items")
    else:
        print(f"Failed to get tracks for playlist {playlist_id}.")
        return []

def gather_user_data():
    token = get_spotify_token()
    if not token:
        return None

    user_id = 'example_user_id'  # Replace with actual user_id

    recently_played = get_recently_played_tracks(token)
    saved_tracks = get_saved_tracks(token)
    playlists = get_user_playlists(token)

    user_data = []
    
    # Recently played tracks
    for item in recently_played:
        track = item['track']
        user_data.append((user_id, track['id'], 'recently_played'))

    # Saved tracks
    for item in saved_tracks:
        track = item['track']
        user_data.append((user_id, track['id'], 'saved'))

    # Playlists
    for playlist in playlists:
        playlist_id = playlist['id']
        playlist_tracks = get_playlist_tracks(token, playlist_id)
        for item in playlist_tracks:
            track = item['track']
            user_data.append((user_id, track['id'], 'playlist'))

    return pd.DataFrame(user_data, columns=['user_id', 'song_id', 'interaction'])

if __name__ == "__main__":
    user_data = gather_user_data()
    if user_data is not None:
        user_data.to_csv('data/user_song_interaction_data.csv', index=False)
        print("User data saved to 'user_song_interaction_data.csv'")
