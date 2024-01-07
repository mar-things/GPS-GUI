import serial
import time
import re

def read_nmea_from_com_port():
    serialPort = serial.Serial(port = "/dev/ttyUSB0", baudrate = 4800,timeout=2000)
    serialString = ""  # Used to hold data coming over UART
    while 1:
        # Wait until there is data waiting in the serial buffer
        if serialPort.in_waiting > 0:

            # Read data out of the buffer until a carraige return / new line is found
            serialString = serialPort.readline()

            # Print the contents of the serial data
            try:
                sentence = serialString.decode("Ascii")
                return sentence
            except:
                pass


def extract_gpgll(sentence):
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

'''# Example usage:
gpgll_sentence = "$GPGLL,4916.45,N,12311.12,W,225444,A,*1D"'''
gpgll_sentence = read_nmea_from_com_port()
coordinates = extract_gpgll(gpgll_sentence)

if coordinates:
    print(f"Latitude: {coordinates[0]}, Longitude: {coordinates[1]}")


