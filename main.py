import spotipy
from spotipy.oauth2 import SpotifyOAuth

# fill out from the spotify dev dashboard
CLIENTID=""
CLIENTSECRET=""

if CLIENTID == "" or CLIENTSECRET == "":
    print("Go to the spotify dashboard and put in your client ids and whatnot")
    exit(1)

artistID = input("Artist ID: ")
playlistName = input("Playlist Name: ")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENTID,
    client_secret=CLIENTSECRET,
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-library-read playlist-modify-public playlist-modify-private"
))
results = sp.artist_albums(artistID, 'album,single')

albums = results['items']
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

foundSongs = set()

artRes = sp.artist(artistID)
theArt = artRes['name']
user_id = sp.me()["id"]

playlist = sp.user_playlist_create(user=user_id, name=playlistName, public=True, description= f"all songs from {theArt}")
for album in reversed(albums):
    print(album['name'], "-", album['release_date'])
    songRes = sp.album_tracks(album['uri'])
    songs = []
    for song in songRes['items']:
        uri = song['uri']
        artists = [artist["name"] for artist in song["artists"]]
        foundArtist = False
        for artist in artists:
            if theArt in artist:
                foundArtist = True;

        if uri not in foundSongs and foundArtist:
            foundSongs.add(uri)
            songs.append(uri)
            print("\t",song['name'], artists)
    if len(songs) != 0:
        sp.playlist_add_items(playlist['id'], songs)

