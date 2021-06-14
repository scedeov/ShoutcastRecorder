import json


class Radio:
    def __init__(self, response: dict):
        response = json.load(response)
        self.id = response.get("ID")
        self.name = response.get("Name")
        self.stream_url = response.get("StreamUrl")
        self.listeners = response.get("Listeners")
        self.genre = response.get("Genre")
        self.current_track = response.get("CurrentTrack")
    