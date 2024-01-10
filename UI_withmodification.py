import sys
import tkinter
import tkinter.messagebox
from tkintermapview import TkinterMapView
import serial
import re
import threading
import queue
import time

class GPSReader:
    def __init__(self, port, baudrate=4800, timeout=1, stop_event=None, data_queue=None):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.stop_event = threading.Event() if stop_event is None else stop_event
        self.data_queue = data_queue

    def extract_gpgll(self, sentence):
        # Check if the sentence starts with "$GPGLL"
        if not sentence.startswith("$GPGLL"):
            # print("Not a GPGLL sentence")
            return None

        # Regular expression to match GPGLL NMEA sentences
        pattern = re.compile(r'\$GPGLL,(\d+\.\d+),([NS]),(\d+\.\d+),([EW]),.*')

        match = pattern.match(sentence)

        if match:
            # Extracting relevant information
            lat, lat_direction, lon, lon_direction = match.groups()

            # Convert latitude and longitude from degrees, minutes to decimal degrees
            latitude = float(lat[:2]) + float(lat[2:]) / 60.0
            longitude = float(lon[:3]) + float(lon[3:]) / 60.0

            # Adjusting for North/South and East/West directions
            if lat_direction == 'S':
                latitude = -latitude
            if lon_direction == 'W':
                longitude = -longitude

            return latitude, longitude
        else:
            print("Invalid GPGLL sentence format")
            return None

    def read_nmea_from_com_port(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

        try:
            while not self.stop_event.is_set():
                try:
                    # Read a line from the serial port
                    nmea_sentence = self.ser.readline().decode('ascii').strip()

                    # Check if the line is a valid NMEA sentence
                    coordinates = self.extract_gpgll(nmea_sentence)
                    if coordinates:
                        self.data_queue.put(coordinates)

                except serial.SerialException:
                    pass

        except KeyboardInterrupt:
            pass
        finally:
            self.ser.close()
            print("Serial port closed.")


class App(tkinter.Tk):

    APP_NAME = "GPS-Mapping.py"
    WIDTH = 800
    HEIGHT = 750

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.gps_stop_event = threading.Event()
        self.data_queue = queue.Queue()
        self.gps_reader = GPSReader(port="/dev/ttyUSB0", baudrate=4800, timeout=1)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Return>", self.search)

        if sys.platform == "darwin":
            self.bind("<Command-q>", self.on_closing)
            self.bind("<Command-w>", self.on_closing)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.search_bar = tkinter.Entry(self, width=50)
        self.search_bar.grid(row=0, column=0, pady=10, padx=10, sticky="we")
        self.search_bar.focus()

        self.search_bar_button = tkinter.Button(master=self, width=8, text="Search", command=self.search)
        self.search_bar_button.grid(row=0, column=1, pady=10, padx=10)

        self.search_bar_clear = tkinter.Button(master=self, width=8, text="Clear", command=self.clear)
        self.search_bar_clear.grid(row=0, column=2, pady=10, padx=10)

        self.map_widget = TkinterMapView(width=self.WIDTH, height=600, corner_radius=0)
        self.map_widget.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.marker_list_box = tkinter.Listbox(self, height=12)
        self.marker_list_box.grid(row=2, column=0, columnspan=1, sticky="ew", padx=10, pady=10)

        self.listbox_button_frame = tkinter.Frame(master=self)
        self.listbox_button_frame.grid(row=2, column=1, sticky="nsew", columnspan=2)

        self.listbox_button_frame.grid_columnconfigure(0, weight=1)

        self.save_marker_button = tkinter.Button(master=self.listbox_button_frame, width=20, text="Start",
                                                 command=self.start_gps)
        self.save_marker_button.grid(row=0, column=0, pady=10, padx=10)

        self.clear_marker_button = tkinter.Button(master=self.listbox_button_frame, width=20, text="Stop",
                                                  command=self.stop_gps)
        self.clear_marker_button.grid(row=1, column=0, pady=10, padx=10)

        self.connect_marker_button = tkinter.Button(master=self.listbox_button_frame, width=20, text="Save",
                                                    command=self.connect_marker)
        self.connect_marker_button.grid(row=2, column=0, pady=10, padx=10)

        self.connect_marker_button = tkinter.Button(master=self.listbox_button_frame, width=20, text="Open",
                                                    command=self.connect_marker)
        self.connect_marker_button.grid(row=3, column=0, pady=10, padx=10)

        self.map_widget.set_address("Kaunas")

        self.marker_list = []
        self.marker_path = None

        self.search_marker = None
        self.search_in_progress = False

        # Periodically check for new data
        self.after(100, self.process_gps_data)

    def start_gps(self):
        # Start reading GPS data
        self.gps_thread = threading.Thread(target=self.gps_reader.read_nmea_from_com_port)
        self.gps_thread.start()

    def stop_gps(self):
        # Stop reading GPS data
        if self.gps_thread and self.gps_thread.is_alive():
            self.gps_stop_event.set()
            self.gps_thread.join()

    def process_gps_data(self):
        try:
            while True:
                coordinates = self.data_queue.get_nowait()
                print(f"Latitude: {coordinates[0]}, Longitude: {coordinates[1]}")
                # Add your logic to update the GUI with the coordinates
        except queue.Empty:
            pass

        # Schedule the next check after 100 milliseconds
        self.after(100, self.process_gps_data)

    def search(self, event=None):
        if not self.search_in_progress:
            self.search_in_progress = True
            if self.search_marker not in self.marker_list:
                self.map_widget.delete(self.search_marker)

            address = self.search_bar.get()
            self.search_marker = self.map_widget.set_address(address, marker=True)
            if self.search_marker is False:
                # address was invalid (return value is False)
                self.search_marker = None
            self.search_in_progress = False

    def clear_marker_list(self):
        for marker in self.marker_list:
            self.map_widget.delete(marker)

        self.marker_list_box.delete(0, tkinter.END)
        self.marker_list.clear()
        self.connect_marker()

    def connect_marker(self):
        print(self.marker_list)
        position_list = []

        for marker in self.marker_list:
            position_list.append(marker.position)

        if self.marker_path is not None:
            self.map_widget.delete(self.marker_path)

        if len(position_list) > 0:
            self.marker_path = self.map_widget.set_path(position_list)

    def clear(self):
        self.search_bar.delete(0, last=tkinter.END)
        self.map_widget.delete(self.search_marker)

    def on_closing(self, event=0):
        self.destroy()
        exit()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()

    start_gps_button = tkinter.Button(master=app.listbox_button_frame, width=20, text="Start GPS", command=app.start_gps)
    start_gps_button.grid(row=4, column=0, pady=10, padx=10)

    stop_gps_button = tkinter.Button(master=app.listbox_button_frame, width=20, text="Stop GPS", command=app.stop_gps)
    stop_gps_button.grid(row=5, column=0, pady=10, padx=10)

    app.start()
