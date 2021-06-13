import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("400x500")
        self.master.resizable(0, 0)
        self.master.title("Radio Recorder for SHOUTcast")
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.label_search = tk.LabelFrame(self, text="Search")
        self.label_search.pack(pady=10)
        self.search_bar = tk.Entry(
            self.label_search, width=50, borderwidth=10, relief=tk.FLAT
        )
        self.search_bar.pack(padx=10)

        self.label_filters = tk.LabelFrame(self.label_search, text="Filter by")
        self.label_filters.pack(padx=10, pady=10, side=tk.LEFT)
        genres = ("Trance", "Electronica", "Salsa")
        vari1 = tk.StringVar(self)
        vari1.set("Genre")
        self.genre = tk.OptionMenu(self.label_filters, vari1, *genres)
        self.genre.pack(side=tk.LEFT)

        self.search_btn = tk.Button(self.label_search, text="Search", height=2)
        self.search_btn.pack(side=tk.RIGHT, padx=10)

        vari2 = tk.StringVar(self)
        vari2.set("Subgenre")
        self.subgenre = tk.OptionMenu(self.label_filters, vari2, *genres)
        self.subgenre.pack(side=tk.RIGHT)

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
