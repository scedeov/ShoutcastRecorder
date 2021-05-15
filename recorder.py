import logging
import os

import requests

import shoutcast_api as sapi


def record_radio(station_id):
    content_url = sapi.get_content_url(station_id)
    radio = sapi.get_radio_info(station_id)
    radio_name = radio["Station"]["Name"]
    listeners = radio["Station"]["Listeners"]

    filename = "./mp3s/" + radio_name + sapi.EXT

    r = requests.get(content_url, stream=True)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        print("Recording... ")
        print(f"Station: {radio_name}\nListeners: {listeners}")
        print("Press Ctrl + C to stop.")
        for chunk in r.iter_content(chunk_size=sapi.CHUNK_SIZE):
            f.write(chunk)
