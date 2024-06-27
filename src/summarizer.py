from dotenv import load_dotenv
import os
from requests import post, get
import json
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress

load_dotenv()

clientID = os.getenv("SPOTIFY_CLIENT_ID")
clientSECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

main_genres = {
    "Pop": ["pop"],
    "Rock": ["rock"],
    "Hip Hop": ["hip hop", "rap"],
    "Electronic": ["electronic", "edm"],
    "Country": ["country"],
    "Jazz": ["jazz"],
    "Classical": ["classical"]
}

class Summarizer:
    def __init__(self):
        self.token = self.get_token()

    def get_token(self):
        auth = clientID + ":" + clientSECRET
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + base64.b64encode(auth.encode("utf-8")).decode("utf-8"),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token

    def get_playlist_tracks(self, playlist_id):
        tracks = []
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {"Authorization": "Bearer " + self.token}
        while url:
            result = get(url, headers=headers)
            json_result = json.loads(result.content)
            tracks.extend(json_result.get("items", []))
            url = json_result.get("next")
        return tracks

    def get_playlist_genre_percentages(self, playlist_id):
        tracks = self.get_playlist_tracks(playlist_id)
        all_genres = []

        for item in tracks:
            track = item.get("track", {})
            for artist in track.get("artists", []):
                artist_id = artist.get("id")
                artist_info = self.get_artist_info(artist_id)
                all_genres.extend(artist_info.get("genres", []))

        total_genres = len(all_genres)
        if total_genres == 0:
            return {"No genres found": 100}

        unique_genres = set(all_genres)
        categorized_genres = {self.categorize_genre(genre): 0 for genre in unique_genres}
        for genre in all_genres:
            categorized_genres[self.categorize_genre(genre)] += 1

        genre_percentages = {genre: count / total_genres * 100 for genre, count in categorized_genres.items()}
        return genre_percentages

    def get_artist_info(self, artist_id):
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        headers = {"Authorization": "Bearer " + self.token}
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        return json_result

    def categorize_genre(self, genre):
        return next((main_genre for main_genre, sub_genres in main_genres.items() if any(sub_genre in genre.lower() for sub_genre in sub_genres)), "Other")

    def get_user_playlists(self, user_id):
        playlists = []
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        headers = {"Authorization": "Bearer " + self.token}
        while url:
            result = get(url, headers=headers)
            json_result = json.loads(result.content)
            playlists.extend(json_result.get("items", []))
            url = json_result.get("next")
        return playlists

    def summarize_playlist(self, playlist):
        name = playlist.get("name", "")
        playlist_id = playlist.get("id")
        genre_percentages = self.get_playlist_genre_percentages(playlist_id)
        
        summary = f"Playlist: {name}\n"
        for genre, percentage in genre_percentages.items():
            summary += f"{genre}: {percentage:.2f}%\n"
        summary += "\n"
        
        return summary

    def summarize(self, user_id):
        playlists = self.get_user_playlists(user_id)
        summary = f"Summary for user {user_id}:\n\n"
        
        with Progress() as progress:
            task = progress.add_task("[green]Summarizing playlists...", total=len(playlists))
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(self.summarize_playlist, playlist): playlist for playlist in playlists}
                for future in as_completed(futures):
                    summary += future.result()
                    progress.update(task, advance=1)
        
        return summary
