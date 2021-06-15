import os
from radio import Radio
import requests

CHUNK_SIZE = 256
EXT = ".mp3"

API_PLAYER = "http://directory.shoutcast.com/Player/"
API_HOME = "http://directory.shoutcast.com/Home/"

HOME_TOP_RADIOS = "Top"
PLAYER_STREAM_URL = "GetStreamUrl"
PLAYER_TRACK_NAME = "GetCurrentTrack"
BROWSE_BY_GENRE = "BrowseByGenre"

AMSTERDAM_TRANCE = "1821355"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "http://directory.shoutcast.com",
    "Connection": "keep-alive",
    "Referer": "http://directory.shoutcast.com/",
}


def get_radio_info(station_id):
    api = API_PLAYER + PLAYER_TRACK_NAME
    data = {"stationID": station_id}
    r = requests.post(api, data=data, headers=HEADERS)
    return r.json()


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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "directory.shoutcast.com",
        "Content-Length": "15",
    }

    r = requests.post(api, data=data, headers=headers)

    content_url = r.text.strip('"')
    return content_url


# I need to make it so that headers are in only one place and only one session is used
def get_stations(subgenre, session):
    api = API_HOME + BROWSE_BY_GENRE
    data = f"genrename={subgenre}"
    r = session.post(api, data=data, headers=HEADERS, timeout=5)
    r.raise_for_status()
    r = r.json()
    stations = {radio["Name"]: radio["ID"] for radio in r}
    return stations
