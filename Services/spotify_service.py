import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ.get("CLIENT_ID_SPOTIFY"),
    client_secret=os.environ.get("CLIENT_SECRET_SPOTIFY"),
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-modify-playback-state user-read-playback-state"
))


def play_music(query):
    results = sp.search(q=query, limit=1, type='track')

    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        uri = track['uri']

        devices = sp.devices()
        if not devices['devices']:
            print("Abre Spotify en tu PC primero")
            return "No se pudo reproducir porque no hay dispositivos activos. Pídele al usuario que abra Spotify en su PC."

        device_id = devices['devices'][0]['id']

        sp.start_playback(device_id=device_id, uris=[uri])

        mensaje = f"Reproduciendo: {track['name']} - {track['artists'][0]['name']} en Spotify."
        print(mensaje)
        return mensaje
    else:
        mensaje = "No se encontró ninguna canción en Spotify con ese nombre."
        print(mensaje)
        return mensaje