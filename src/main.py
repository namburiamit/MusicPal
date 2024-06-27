import os
from playlist_generator import PlaylistGenerator
from music_recommender import MusicRecommender
from queue_manager import QueueManager
from summarizer import Summarizer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel

console = Console()

def main():
    playlist_gen = PlaylistGenerator()
    music_recommender = MusicRecommender()
    queue_manager = QueueManager()
    summarizer = Summarizer()

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
        table.add_row("5", "Exit")

        console.print(table)
        
        choice = IntPrompt.ask("Choose an option (1-5)")

        if choice == 1:
            mood = Prompt.ask("Enter the mood for the playlist")
            playlist = playlist_gen.generate_playlist(mood)
            console.print(f"Generated Playlist: {playlist}", style="bold green")

        elif choice == 2:
            current_song_id = Prompt.ask("Enter the current song ID")
            recommendations = music_recommender.recommend_songs(current_song_id)
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
            console.print("Exiting...", style="bold red")
            break

        else:
            console.print("Invalid choice. Please try again.", style="bold red")
        
        Prompt.ask("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
