import spotipy
import sys
import os
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

CLIENTID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENTSECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

if CLIENTID == "" or CLIENTSECRET == "" or CLIENTID == None or CLIENTSECRET == None:
    print(
        "Go to the spotify dashboard and put in your client id and secret into the .env file"
    )
    with open(".env", "w") as f:
        f.write("SPOTIPY_CLIENT_ID=\nSPOTIPY_CLIENT_SECRET=")
    exit(1)

if len(sys.argv) == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
    print('Usage:\n  python main.py "artist_id" "playlist_name"')
    print("\nParameters: ")
    print(
        "  artist_id: The link/id to the artist you want to make the playlist about. (open.spotify.com/artist/5L15t6I0PQS9SBXbiklPEN) (5L15t6I0PQS9SBXbiklPEN) "
    )
    exit(1)

artistsID = []
playlistName = ""

if len(sys.argv) > 2:
    artistsID.append(sys.argv[1])
    playlistName = sys.argv[2]
    for i in range(3, len(sys.argv)):
        artistsID.append(sys.argv[i])

else:
    artistsID.append(input("Artist ID: "))
    playlistName = input("Playlist Name: ")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENTID,
        client_secret=CLIENTSECRET,
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-library-read playlist-modify-public playlist-modify-private",
    )
)

albums = []

for artist in artistsID:
    results = sp.artist_albums(artist, "album,single")
    albums.extend(results["items"])

while results["next"]:
    results = sp.next(results)
    albums.extend(results["items"])

for i in range(len(albums)):
    albums[i]["release_date"] += "2020-06-15"[len(albums[i]["release_date"]) :]
albums.sort(key=lambda x: datetime.strptime(x["release_date"], "%Y-%m-%d"))

foundSongs = set()
theArts = set()

for artist in artistsID:
    artRes = sp.artist(artist)
    theArts.add(artRes["name"])

user_id = sp.me()["id"]

playlist = sp.user_playlist_create(
    user=user_id,
    name=playlistName,
    public=True,
    description=f"all songs from {", ".join(theArts)}",
)

for album in albums:
    print(album["name"], "-", album["release_date"])
    songRes = sp.album_tracks(album["uri"])
    songs = []
    for song in songRes["items"]:
        uri = song["uri"]
        artists = [artist["name"] for artist in song["artists"]]
        foundArtist = False
        for artist in artists:
            if artist in theArts:
                foundArtist = True

        if uri not in foundSongs and foundArtist:
            foundSongs.add(uri)
            songs.append(uri)
            print("\t", song["name"], artists)
    if len(songs) != 0:
        sp.playlist_add_items(playlist["id"], songs)
