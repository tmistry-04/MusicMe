# MusicMe 🎵

A full stack music recommendation web app — search any song and discover what to listen to next.

**Live demo:** [musicme-lb4z.onrender.com/app](https://musicme-lb4z.onrender.com/app)

---

## What it does

- 🔍 **Search** for any song by name
- 🎧 **Get recommendations** — 5 similar tracks powered by Last.fm
- ❤️ **Save favourites** to your personal list
- 📜 **Search history** automatically saved per session
- 🔐 **User accounts** with secure login and registration

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy ORM |
| Authentication | JWT tokens, bcrypt password hashing |
| Music Data | Last.fm REST API |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Deployment | Render |

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/search?track=` | Search for tracks by name | No |
| GET | `/recommend?track=&artist=` | Get 5 similar tracks | No |
| POST | `/favourite` | Save a track to favourites | Yes |
| GET | `/favourites` | Get all saved favourites | Yes |
| DELETE | `/favourite/{id}` | Remove a favourite | Yes |
| GET | `/history` | Get search history | Yes |
| POST | `/register` | Create a new account | No |
| POST | `/login` | Login and receive JWT token | No |

---

## Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/tmistry-04/MusicApp.git
cd MusicApp
```

**2. Create a virtual environment and install dependencies**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Set up environment variables**

Create a `.env` file in the project root:
```
LASTFM_API_KEY=your_lastfm_api_key
LASTFM_SECRET=your_lastfm_secret
SECRET_KEY_JWT=your_secret_key
```

Get a free Last.fm API key at [last.fm/api](https://www.last.fm/api).

**4. Run the server**
```bash
uvicorn main:app --reload
```

**5. Open the app**

Visit `http://127.0.0.1:8000/app` in your browser, or use the interactive API docs at `http://127.0.0.1:8000/docs`.

---

## Project Structure

```
MusicApp/
├── main.py          # FastAPI app and all endpoints
├── database.py      # SQLAlchemy database connection
├── models.py        # Database table definitions
├── auth.py          # JWT token and password hashing logic
├── index.html       # Frontend UI
├── requirements.txt # Python dependencies
└── .env             # Secret keys (not committed to GitHub)
```

---

## Future Features

- **Multi-seed recommendations** — select multiple tracks or artists and receive recommendations based on their combined profile
- **Album art** — integrate MusicBrainz and Cover Art Archive APIs to display album artwork alongside results
- **Spotify OAuth** — log in with Spotify and get recommendations based on your personal listening history
- **User-specific data** — link favourites and history to individual user accounts with foreign keys
- **PostgreSQL** — migrate from SQLite to PostgreSQL for production-grade persistence

---

## Author

Tanisha Mistry · [github.com/tmistry-04](https://github.com/tmistry-04) · tanisha.p.mistry@gmail.com
