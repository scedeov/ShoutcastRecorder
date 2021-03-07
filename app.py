from tkinter import *
import shoutcast
import threading

root = Tk()

station_entry = Entry(root, width=50)
station_entry.pack()


def record():
    station_id = station_entry.get()
    shoutcast.record_radio(station_id)


def record_thread():
    threading.Thread(target=record).start()


record_btn = Button(root, text="Grabar\nRadio", command=record_thread)
record_btn.pack()

if __name__ == "__main__":
    root.mainloop()
