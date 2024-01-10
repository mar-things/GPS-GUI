import serial
import re

def extract_gpgll(sentence):
    # Check if the sentence starts with "$GPGLL"
    if not sentence.startswith("$GPGLL"):
        #print("Not a GPGLL sentence")
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

def read_nmea_from_com_port(port, baudrate=4800, timeout=1):
    ser = serial.Serial(port, baudrate, timeout=timeout)

    try:
        while True:
            # Read a line from the serial port
            nmea_sentence = ser.readline().decode('Ascii').strip()

            # Check if the line is a valid NMEA sentence
            coordinates = extract_gpgll(nmea_sentence)
            if coordinates:
                print(f"Latitude: {coordinates[0]}, Longitude: {coordinates[1]}")
            
    except KeyboardInterrupt:
        # Close the serial port when the program is interrupted
        ser.close()
        print("Serial port closed.")

if __name__ == "__main__":
    # Replace 'COMx' with the actual COM port your GPS module is connected to
    com_port = "/dev/ttyUSB0"
    read_nmea_from_com_port(com_port)
