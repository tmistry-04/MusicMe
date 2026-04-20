from fastapi import FastAPI
from dotenv import load_dotenv
import pylast
import os

# fix SSL certificate verification on Mac:
import ssl
import certifi
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

load_dotenv()

app = FastAPI()

# Last.fm connection object (object network represents authenticated connection to Last.fm's API):
network = pylast.LastFMNetwork(
    api_key=os.getenv("LASTFM_API_KEY"),
    api_secret=os.getenv("LASTFM_SECRET"),
)

@app.get("/")
def read_root():
    return {"message": "MusicMe is alive!"}


@app.get("/search") # ← decorator: "when someone hits GET /search..."
def search(track: str): # ← "...run this function"
    # results holds 5 tracks that matched query q:
    results = network.search_for_track(track_name=track, artist_name="")
    tracks = []
    # we want to iterate through results to abstract data into only what we need, and put data in tracks list
    # (get rid of excess data like album art, artists etc):
    page = results.get_next_page()[:5]  # gives you a list of tracks, limit to 5
    for track in page:
        tracks.append({
            "name": track.get_name(),
            "artist": track.get_artist().get_name(),
        })
    return {"results": tracks}
