from dotenv import load_dotenv
import os
from requests import get
import base64
import json

load_dotenv()

clientID = os.getenv("SPOTIFY_CLIENT_ID")
clientSECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
username = os.getenv("SPOTIFY_USERNAME")

# Scopes required for accessing user playback information and recommendations
scopes = "user-read-playback-state user-read-currently-playing"

class MusicRecommender:
    def __init__(self, token):
        self.token = token

    def get_current_playing_track(self):
        """
        Get the currently playing track.
        """
        url = "https://api.spotify.com/v1/me/player/currently-playing"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = get(url, headers=headers)
        if response.status_code == 200 and response.content:
            return response.json().get("item")
        else:
            print("Failed to get current playing track.")
            return None

    def get_recommendations(self, seed_tracks):
        """
        Get song recommendations based on seed tracks.
        """
        url = f"https://api.spotify.com/v1/recommendations?seed_tracks={seed_tracks}&limit=10"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("tracks")
        else:
            print("Failed to get recommendations.")
            return []

    def recommend_based_on_current_song(self):
        """
        Recommend songs based on the currently playing song.
        """
        current_track = self.get_current_playing_track()
        if current_track:
            seed_track_id = current_track.get("id")
            recommendations = self.get_recommendations(seed_track_id)
            return [track.get("name") for track in recommendations]
        else:
            return []

    def print_current_playing_track(self):
        """
        Print details of the currently playing track.
        """
        current_track = self.get_current_playing_track()
        if current_track:
            track_name = current_track.get("name")
            artist_name = ", ".join(artist.get("name") for artist in current_track.get("artists"))
            album_name = current_track.get("album").get("name")
            print(f"Currently Playing: {track_name} by {artist_name} from the album {album_name}")
        else:
            print("No track is currently playing.")
