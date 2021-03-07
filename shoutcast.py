import requests
import json
import os

CHUNK_SIZE = 256
EXT = ".mp3"

API_PLAYER = "http://directory.shoutcast.com/Player/"
API_HOME = "http://directory.shoutcast.com/Home/"

HOME_TOP_RADIOS = "Top"
HOME_BROWSE_GENRE = "BrowseByGenre"
PLAYER_STREAM_URL = "GetStreamUrl"
PLAYER_TRACK_NAME = "GetCurrentTrack"

AMSTERDAM_TRANCE = "1821355"


def get_radio_info(station_id):
    api = API_PLAYER + PLAYER_TRACK_NAME
    data = {"stationID": station_id}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    r = requests.post(api, data=data, headers=headers)
    r_json = json.loads(r.text)
    return r_json


def get_radio_name(station_id):
    name = get_radio_info(station_id)["Station"]["Name"]
    return name


def get_radio_listeners(station_id):
    listeners = get_radio_info(station_id)["Station"]["Listeners"]
    return listeners


def get_song_name(station_id):
    song_name = get_radio_info(station_id)["Station"]["CurrentTrack"]
    return song_name


def get_content_url(station_id):
    api = API_PLAYER + PLAYER_STREAM_URL
    data = f"station={station_id}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "directory.shoutcast.com",
        "Content-Length": "15",
    }

    r = requests.post(api, data=data, headers=headers)

    content_url = r.text.strip('"')
    return content_url


def record_radio(station_id):
    content_url = get_content_url(station_id)
    radio = get_radio_info(station_id)
    radio_name = radio["Station"]["Name"]
    listeners = radio["Station"]["Listeners"]

    filename = "./mp3s/" + radio_name + EXT

    r = requests.get(content_url, stream=True)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        print("Recording... ")
        print(f"Station: {radio_name}\nListeners: {listeners}")
        print("Press Ctrl + C to stop.")
        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)
