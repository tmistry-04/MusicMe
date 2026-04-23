from dotenv import load_dotenv
import pylast
import os
import requests
from fastapi import FastAPI, Depends, HTTPException
from auth import hash_password, verify_password, create_token, decode_token
from models import Favourite, History, User
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models
# creates tables in db:
models.Base.metadata.create_all(bind=engine)
# fix SSL certificate verification on Mac:
import ssl
import certifi
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

load_dotenv()

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Last.fm connection object (object network represents authenticated connection to Last.fm's API):
network = pylast.LastFMNetwork(
    api_key=os.getenv("LASTFM_API_KEY"),
    api_secret=os.getenv("LASTFM_SECRET"),
)

# to interact with the database in each of the endpoints: GET /favourites, GET /history, POST /favourite, DELETE /favourite
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
use FastAPI's OAuth2 scheme to extract JWT tokens from request headers
decode the token to get the user's identity and verify they exist in the database
Protect endpoints use FastAPI's dependency injection to enforce authentication
"""
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        print("payload:", payload)
        email = payload.get("sub")
        print("email:", email)
        user = db.query(User).filter(User.email == email).first()
        print("user:", user)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception as e:
        print("error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
def read_root():
    return {"message": "MusicMe is alive!"}


@app.get("/search") # ← decorator: "when someone hits GET /search..."
def search(track: str, db: Session = Depends(get_db)): # ← "...run this function"
    # build URL
    response = requests.get(
        "https://ws.audioscrobbler.com/2.0/",
        params={
            "method": "track.search",
            "track": track,
            "api_key": os.getenv("LASTFM_API_KEY"),
            "format": "json",
            "limit": 5
        }
    )

    data = response.json()
    tracks = []
    for result in data["results"]["trackmatches"]["track"]:
        tracks.append({
            "name": result["name"],
            "artist": result["artist"],
        })

    history_entry = History(
        track_name=track,
        artist=tracks[0]["artist"] if tracks else ""  # save top artist from results since we don't have the artist yet.
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
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

from pydantic import BaseModel

# DATABASE ENDPOINTS:

# POST /favourite:
# create a Pydantic class for POST /favourite HTTP method since parameters come from request body (not URL) to send data that is to be saved, therefore need to define shape of request body
# GET methods don't need a class since params come from URL
class FavouriteRequest(BaseModel):
    track_name: str
    artist: str

# when the track is favourited, it will take information from request body, and then create a new favourite object extracting data from request body, then commit that to database:
@app.post("/favourite")
def add_favourite(request: FavouriteRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favourite_track = Favourite(
        track_name = request.track_name,
        artist = request.artist,
    )
    db.add(favourite_track)
    db.commit()

    # we are sending the db the favourite track's track name and artist, but we don't have id or saved_at,
    # so we are asking database to pass us the values it auto generated using db.refresh, to then return final favourite_track object with all 4 fields filled out:
    db.refresh(favourite_track)
    return favourite_track

@app.delete("/favourite/{favourite_id}")
def delete_favourite(favourite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favourite = db.query(Favourite).filter(Favourite.id == favourite_id).first()
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite not found")
    db.delete(favourite)
    db.commit()
    return {"message": "Removed from favourites"}

# GET /favourites:
@app.get("/favourites")
def get_favourites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favourites = db.query(Favourite).all()
    return favourites

# GET /history:
@app.get("/history")
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history = db.query(History).all()
    return history

# AUTHORIZATION ENDPOINTS:

# POST /register:
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    hashed_pw = hash_password(request.password)
    # check if user already registered with this email before:
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # otherwise create new user:
    new_user = User(
        username = request.username,
        email = request.email,
        hashed_password = hashed_pw,
    )
    db.add(new_user)
    db.commit()
    # refresh to fill out created_at and id fields for User class (defined in models.py)
    db.refresh(new_user)
    return new_user


# POST /login:
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # find user object inside database that matches request.email that user passed when making login in request:
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # call create token with data = {"sub": user.email} which is a dictionary with data["exp"] added automatically as part of create_token function:
    return {"token": create_token({"sub": user.email})}

