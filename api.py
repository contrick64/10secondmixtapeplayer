import requests
import json

api_url = "https://p.jasperstephenson.com/ld51/api"

def load_song_by_id(song_id):
    url = f"{api_url}/songs/byIdFragment/{song_id}"
    response = requests.get(url)

    if not response.ok:
        raise Exception(f"Failed to load song with ID {song_id}")
    if response.text == 'null':
        raise Exception(f"Song with ID {song_id} not found")
    song = json.loads(response.text)
    return song

def load_page_of_songs(page=10):
    url = f"{api_url}/songs/top/{page}"
    response = requests.get(url)

    if not response.ok:
        raise Exception(f"Failed to load page {page}")
    page = json.loads(response.text)
    return page
