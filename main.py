from fastapi import FastAPI
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

load_dotenv()

app = FastAPI()

# Spotify connection object (object sp represents MY authenticated connection to Spotify's API):
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

@app.get("/")
def read_root():
    return {"message": "MusicMe is alive!"}


@app.get("/search") # ← decorator: "when someone hits GET /search..."
def search(q: str): # ← "...run this function"
    # results holds 5 tracks that matched query q:
    results = sp.search(q=q, limit=5, type="track")
    print(results)
    tracks = []
    # we want to iterate through results to abstract data into only what we need, and put data in tracks list
    # (get rid of excess data like album art, artists etc):
    for track in results["tracks"]["items"]:
        tracks.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "spotify_id": track["id"]
        })
    return {"results": tracks}