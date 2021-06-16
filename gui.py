from tkinter import filedialog, messagebox
import tkinter as tk
import requests
import logging
import threading
import json
import os

import shoutcast_api as sapi
from radio import Radio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Application(tk.Frame):

    NO_RESULTS = "..."
    SEARCH_BAR_MESSAGE = "search for a radio station"

    def __init__(self, master=None, session=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("400x500")
        self.genres = list(self.get_genres())
        self.subgenres = self.get_subgenres(self.genres[0])
        self.stations = {}
        self.threads = []
        self.directory = None
        self.session = session
        self.master.resizable(0, 0)
        self.master.title("Radio Recorder for SHOUTcast")
        self.pack()
        self.create_widgets()

    def update_subgenres(self, genre):
        # taken from fhdrsdg on stackoverflow https://stackoverflow.com/a/28412967
        self.subgenres = self.get_subgenres(genre)
        menu = self.subgenre_menu["menu"]
        menu.delete(0, "end")
        for string in self.subgenres:
            menu.add_command(
                label=string, command=lambda value=string: self.subgenre_var.set(value)
            )

    def get_genres(self):
        with open("stations.json", "r") as f:
            data = json.load(f)

        return data.keys()

    def get_subgenres(self, genre):
        with open("stations.json", "r") as f:
            data = json.load(f)
            data = dict(data)

        return data[genre]

    def update_stations(self):
        self.stations_listbox.delete(0, "end")
        self.stations = sapi.get_stations(self.subgenre_var.get(), self.session)
        result = self.search_bar_var.get()
        for station in self.stations:
            if (
                result == ""
                or result == self.SEARCH_BAR_MESSAGE
                or result in station.name.lower()
            ):
                self.stations_listbox.insert(tk.END, station.name)
            else:
                self.stations_listbox.insert(tk.END, self.NO_RESULTS)
                logging.info(f"No results found for {result}...")
                break

    def search(self):
        if self.genre_var.get() == "Genre" or self.subgenre_var.get() == "Subgenre":
            messagebox.showerror(
                title="Error~! :(", message="You need to select a Genre and a Subgenre."
            )
        else:
            self.update_stations()

    def clear(self, event):
        self.search_bar_var.set("")

    def save_folder(self):
        self.directory = filedialog.askdirectory()

    def get_station(self, name) -> Radio:
        for station in self.stations:
            if station.name == name:
                return station

    def record(self):
        current_station_name = self.stations_listbox.get(
            self.stations_listbox.curselection()
        )
        station = self.get_station(current_station_name)
        content_url = sapi.get_content_url(station.id, self.session)
        # listeners = station.listeners

        filename = self.directory + "/" + station.name + sapi.EXT
        try:
            station.r = self.session.get(content_url, stream=True)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                logging.info(f"Recording {station.name}...")
                while not station.stop:
                    chunk = station.r.iter_content(chunk_size=sapi.CHUNK_SIZE)
                    f.write(next(chunk))
                logging.info(f"Stopped Recording for {station.name}.")
        except requests.exceptions.MissingSchema:
            logging.error(f"Invalid URL received for {station.name}")
        except Exception as e:
            logging.error(f" Exception Found {e}")
        finally:
            station.stop = True
            logging.info(f"Threads {len(self.threads)}")
            logging.info("Marked to STOP")

    def add_record(self):
        current_selection = self.stations_listbox.get(
            self.stations_listbox.curselection()
        )

        station = self.get_station(current_selection)

        if current_selection == self.NO_RESULTS:
            logging.info("No results found.")
            return

        if station.stop != None:
            logging.info(f"You are currently recording this station {station.name}")
            return

        if not self.directory:
            logging.info("You did not select a save folder.")
            self.save_folder()

        thread = threading.Thread(target=self.record)
        self.threads.append(thread)
        thread.name = current_selection
        thread.start()
        logging.info(f"Thread {thread.name} started")
        logging.info(f"Threads {len(self.threads)}")

    def stop_record(self):
        current_name = self.stations_listbox.get(self.stations_listbox.curselection())
        for thread in self.threads:
            if thread.name == current_name:
                radio = self.get_station(current_name)
                radio.stop = True
                logging.info("Sent signal to stop recording...")
                radio.r.close()
                logging.info(f"Response for {radio.name} closed!")
                logging.info(f"Threads {len(self.threads)}")
            else:
                logging.info(f"Thread does not exist for {current_name}")

    def create_widgets(self):
        self.label_search = tk.LabelFrame(self, text="Search")
        self.label_search.pack(pady=10)

        self.search_bar_var = tk.StringVar()
        self.search_bar_var.set(self.SEARCH_BAR_MESSAGE)

        self.search_bar = tk.Entry(
            self.label_search,
            textvariable=self.search_bar_var,
            width=50,
            borderwidth=10,
            relief=tk.FLAT,
        )
        self.search_bar.bind("<Button-1>", self.clear)
        self.search_bar.pack(padx=10)

        self.label_filters = tk.LabelFrame(self.label_search, text="Filter by")
        self.label_filters.pack(padx=10, pady=10, side=tk.LEFT)

        self.genre_var = tk.StringVar(self)
        self.genre_var.set("Genre")

        self.genre_menu = tk.OptionMenu(
            self.label_filters,
            self.genre_var,
            *self.genres,
            command=lambda _: self.update_subgenres(self.genre_var.get()),
        )
        self.genre_menu.pack(side=tk.LEFT)

        self.search_btn = tk.Button(
            self.label_search, text="Search", height=2, command=self.search
        )
        self.search_btn.pack(side=tk.RIGHT, padx=10)

        self.subgenre_var = tk.StringVar(self)
        self.subgenre_var.set("Subgenre")

        self.subgenre_menu = tk.OptionMenu(
            self.label_filters, self.subgenre_var, *self.subgenres
        )
        self.subgenre_menu.pack(side=tk.RIGHT)

        self.stations_frame = tk.LabelFrame(self, text="Radio Stations")
        self.stations_frame.pack()

        self.stations_listbox = tk.Listbox(
            self.stations_frame, width=54, borderwidth=10, relief=tk.FLAT
        )

        self.stations_listbox.pack()

        self.record_btn = tk.Button(self, text="Record", command=self.add_record)
        self.record_btn.pack(side=tk.LEFT, pady=10)

        self.stop_btn = tk.Button(self, text="Stop", command=self.stop_record)
        self.stop_btn.pack(side=tk.LEFT, pady=10)

        self.save = tk.Button(self, text="Select Save Folder", command=self.save_folder)
        self.save.pack(side=tk.RIGHT, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    with requests.Session() as session:
        session.get("http://directory.shoutcast.com")
        app = Application(master=root, session=session)
        app.mainloop()
