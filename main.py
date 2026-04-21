from fastapi import FastAPI
from dotenv import load_dotenv
import pylast
import os
import requests

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

# Note: pylast's get_similar() requires user authentication and returned
# empty results with API key only. Using requests to call Last.fm's REST
# API directly, which works with API key alone.
@app.get("/recommend")
def recommend(track: str, artist: str):
    # build URL
    response = requests.get(
        "https://ws.audioscrobbler.com/2.0/",
        params={
            "method": "track.getsimilar",
            "artist": artist,
            "track": track,
            "api_key": os.getenv("LASTFM_API_KEY"),
            "format": "json",
            "limit": 5
        }
    )
    # convert response to python dictionary:
    data = response.json()
    similar_tracks = []
    for track in data["similartracks"]["track"]:
        similar_tracks.append({
            "name": track["name"],
            "artist": track["artist"]["name"],
        })
    return {"results": similar_tracks}

# https://ws.audioscrobbler.com/2.0/?method=track.getsimilar&artist=Taylor+Swift&track=Shake+It+Off&api_key=440af6b966fb4c0a061e0f0643f3ae01&format=json
'''
json format of response:
{"similartracks":{"track":
                      [{"name":"Blank Space","playcount":28086292,"mbid":"5af020a5-adae-4a39-ba1e-74b79dc3b06e","match":1.0,"url":"https://www.last.fm/music/Taylor+Swift/_/Blank+Space","streamable":{"#text":"0","fulltrack":"0"},
                        "duration":231,"artist":{"name":"Taylor Swift","mbid":"20244d07-534f-4eff-b4d4-930878889970","url":"https://www.last.fm/music/Taylor+Swift"},
                        "image":[{"#text":"https://lastfm.freetls.fastly.net/i/u/34s/2a96cbd8b46e442fc41c2b86b821562f.png","size":"small"},
                                 {"#text":"https://lastfm.freetls.fastly.net/i/u/64s/2a96cbd8b46e442fc41c2b86b821562f.png","size":"medium"},
                                 {"#text":"https://lastfm.freetls.fastly.net/i/u/174s/2a96cbd8b46e442fc41c2b86b821562f.png","size":"large"},
                                 {"#text":"https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png","size":"extralarge"},
                                 {"#text":"https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png","size":"mega"},
                                 {"#text":"https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png","size":""}]},
                       {"name":"Bad Blood","playcount":14198282,"mbid":"7fad1aa3-d874-48d8-842a-9ca9afea068e","match":0.
'''