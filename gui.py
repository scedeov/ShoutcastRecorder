from radio import Radio
from tkinter import filedialog
import tkinter as tk
import json
import os
import requests
import threading

import shoutcast_api as sapi


class Application(tk.Frame):
    def __init__(self, master=None, session=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("400x500")
        self.genres = list(self.get_genres())
        self.subgenres = self.get_subgenres(self.genres[0])
        self.stations = {}
        self.threads = []
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
            if result in station.name or result == "":
                self.stations_listbox.insert(tk.END, station.name)
            else:
                pass

    def clear(self, event):
        self.search_bar_var.set("")

    def save_folder(self):
        self.directory = filedialog.askdirectory()
        print(self.directory)

    def get_station(self, name) -> Radio:
        for station in self.stations:
            if station.name == name:
                return station

    def record(self):
        current_station_name = self.stations_listbox.get(
            self.stations_listbox.curselection()
        )
        station = self.get_station(current_station_name)
        content_url = sapi.get_content_url(station.id)
        listeners = station.listeners

        filename = self.directory + "/" + station.name + sapi.EXT

        station.r = self.session.get(content_url, stream=True)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            print("Recording... ")
            print(f"Station: {station.name}\nListeners: {listeners}")
            print("Press Ctrl + C to stop.")
            while not station.stop:
                chunk = station.r.iter_content(chunk_size=sapi.CHUNK_SIZE)
                f.write(next(chunk))

    def add_record(self):
        thread = threading.Thread(target=self.record)
        self.threads.append(thread)
        thread.name = self.stations_listbox.get(self.stations_listbox.curselection())
        thread.start()

    def stop_record(self):
        current_name = self.stations_listbox.get(self.stations_listbox.curselection())
        for thread in self.threads:
            if thread.name == current_name:
                radio = self.get_station(current_name)
                radio.stop = True
                print("Stopped While")
                print("Closing Resopnse")
                radio.r.close()
                print("Response Closed")

    # def cleanup(self):
    #     for thread in self.threads:
    #         thread.join()

    def create_widgets(self):
        self.label_search = tk.LabelFrame(self, text="Search")
        self.label_search.pack(pady=10)

        self.search_bar_var = tk.StringVar()
        self.search_bar_var.set("search for a radio station")

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
            self.label_search, text="Search", height=2, command=self.update_stations
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
