import tkinter as tk
import json


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("400x500")
        self.genres = list(self.get_genres())
        self.subgenres = self.get_subgenres(self.genres[0])
        self.master.resizable(0, 0)
        self.master.title("Radio Recorder for SHOUTcast")
        self.pack()
        self.create_widgets()

    def update_subgenres(self, genre):
        # taken from fhdrsdg on stackoverflow
        self.subgenres = self.get_subgenres(genre)
        menu = self.subgenre_menu["menu"]
        menu.delete(0, "end")
        for string in self.subgenres:
            menu.add_command(
                label=string, command=lambda value=string: self.vari2.set(value)
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

    def create_widgets(self):
        self.label_search = tk.LabelFrame(self, text="Search")
        self.label_search.pack(pady=10)
        self.search_bar = tk.Entry(
            self.label_search, width=50, borderwidth=10, relief=tk.FLAT
        )
        self.search_bar.pack(padx=10)

        # read genres and subgenres

        self.label_filters = tk.LabelFrame(self.label_search, text="Filter by")
        self.label_filters.pack(padx=10, pady=10, side=tk.LEFT)

        self.vari1 = tk.StringVar(self)
        self.vari1.set("Genre")
        self.genre_menu = tk.OptionMenu(
            self.label_filters,
            self.vari1,
            *self.genres,
            command=lambda _: self.update_subgenres(self.vari1.get())
        )
        self.genre_menu.pack(side=tk.LEFT)

        self.search_btn = tk.Button(self.label_search, text="Search", height=2)
        self.search_btn.pack(side=tk.RIGHT, padx=10)

        self.vari2 = tk.StringVar(self)
        self.vari2.set("Subgenre")

        self.subgenre_menu = tk.OptionMenu(
            self.label_filters, self.vari2, *self.subgenres
        )
        self.subgenre_menu.pack(side=tk.RIGHT)

        self.stations_frame = tk.LabelFrame(self, text="Radio Stations")
        self.stations_frame.pack()
        stations = ["Radio1", "Radio2", "Radio3"]
        self.stations_list = tk.Listbox(
            self.stations_frame, width=54, borderwidth=10, relief=tk.FLAT
        )
        for entry in stations:
            self.stations_list.insert(tk.END, entry)

        self.stations_list.pack()

        self.record_btn = tk.Button(self, text="Record")
        self.record_btn.pack(side=tk.LEFT, pady=10)

        self.play_btn = tk.Button(self, text="Select Save Folder")
        self.play_btn.pack(side=tk.RIGHT, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
