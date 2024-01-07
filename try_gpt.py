import serial
import re
import folium

def nmea_to_lat_lon(nmea_sentence):
    # Regular expression to match GPGGA NMEA sentences
    pattern = re.compile(r'\$GPGGA,(\d+\.\d+),([NS]),(\d+\.\d+),([EW]),.*')

    match = pattern.match(nmea_sentence)
    print(match)
    
'''    if match:
        # Extracting relevant information
        time, lat, lat_direction, lon, lon_direction = match.groups()

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
        print("Invalid NMEA sentence format")
        return None'''

def read_nmea_from_com_port(port, baudrate=4800, timeout=5):
    m = folium.Map(location=[0, 0], zoom_start=2)  # Initial map centered at (0, 0)

    ser = serial.Serial(port, baudrate, timeout=timeout)

    try:
        while True:
            # Read a line from the serial port
            nmea_sentence = ser.readline().decode('Ascii').strip()
            #print(nmea_sentence)
            # Check if the line is a valid NMEA sentence
            if nmea_sentence.startswith('$GPGGA'):
                lat_lon = nmea_to_lat_lon(nmea_sentence)
                
                if lat_lon:
                    latitude, longitude = lat_lon

                    # Add marker to the map
                    folium.Marker([latitude, longitude], popup=f'Lat: {latitude}, Lon: {longitude}').add_to(m)

                    # Save the map to an HTML file (optional)
                    m.save('gps_map.html')

    except KeyboardInterrupt:
        # Close the serial port when the program is interrupted
        ser.close()
        print("Serial port closed.")

if __name__ == "__main__":
    # Replace 'COMx' with the actual COM port your GPS module is connected to
    com_port = "/dev/ttyUSB0"
    read_nmea_from_com_port(com_port)
