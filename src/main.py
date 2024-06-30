import os
from requests import post
import base64
from playlist_generator import PlaylistGenerator
from music_recommender import MusicRecommender
from queue_manager import QueueManager
from summarizer import Summarizer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from urllib.parse import urlencode
import webbrowser

# Initialize the console for rich text output
console = Console()

def get_spotify_token():
    """
    Authenticate with Spotify and get an access token using Authorization Code Flow.
    """
    clientID = os.getenv("SPOTIFY_CLIENT_ID")
    clientSECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    
    auth_url = "https://accounts.spotify.com/authorize"
    token_url = "https://accounts.spotify.com/api/token"

    # Step 1: Get authorization code
    params = {
        "client_id": clientID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "user-read-playback-state user-read-currently-playing",
        "show_dialog": "true"
    }
    auth_request_url = f"{auth_url}?{urlencode(params)}"
    webbrowser.open(auth_request_url)
    redirect_response = input("Paste the full redirect URL here: ")

    # Extract the authorization code from the redirect response
    code = redirect_response.split("?code=")[1]

    # Step 2: Exchange authorization code for access token
    auth_header = base64.b64encode(f"{clientID}:{clientSECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    response = post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Failed to get Spotify token.")
        return None

def main():
    # Create instances of the various classes
    playlist_gen = PlaylistGenerator()
    token = get_spotify_token()
    if not token:
        console.print("Failed to authenticate with Spotify.", style="bold red")
        return

    music_recommender = MusicRecommender(token)
    queue_manager = QueueManager()
    summarizer = Summarizer()

    # Main loop to handle user input and perform actions
    while True:
        console.clear()
        console.print(Panel("Welcome to [bold cyan]MusicPal[/bold cyan]", expand=False))
        
        table = Table(title="Menu")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        table.add_row("1", "Generate Playlist")
        table.add_row("2", "Recommend Songs")
        table.add_row("3", "Add to Queue")
        table.add_row("4", "Summarize Playlists")
        table.add_row("5", "Print Currently Playing Song")
        table.add_row("6", "Exit")

        console.print(table)
        
        # Get user choice
        choice = IntPrompt.ask("Choose an option (1-6)")

        if choice == 1:
            mood = Prompt.ask("Enter the mood for the playlist")
            playlist = playlist_gen.generate_playlist(mood)
            console.print(f"Generated Playlist: {playlist}", style="bold green")

        elif choice == 2:
            recommendations = music_recommender.recommend_based_on_current_song()
            console.print(f"Recommendations: {recommendations}", style="bold green")

        elif choice == 3:
            current_song_id = Prompt.ask("Enter the current song ID to add to queue")
            queue_manager.add_to_queue(current_song_id)
            console.print("Song added to queue.", style="bold green")

        elif choice == 4:
            user_id = Prompt.ask("Enter the user ID to summarize playlists")
            summary = summarizer.summarize(user_id)
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            with open(f"{output_dir}/{user_id}.txt", "w") as output_file:
                output_file.write(summary)
            console.print(f"Summary written to {output_dir}/{user_id}.txt", style="bold green")

        elif choice == 5:
            music_recommender.print_current_playing_track()

        elif choice == 6:
            console.print("Exiting...", style="bold red")
            break

        else:
            console.print("Invalid choice. Please try again.", style="bold red")
        
        Prompt.ask("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
