#General MCAP Format (for reference(help i wanna kms))

#Header
#Schema
#Channel
#Message
#Footer

#Were gna make the fake/raw data in JSON format

#ID: 501 , CANgps (lat/long)
#ID: 502 , IMU (accel,speed)

#IMPORTANT, CAN SENDS TWO AT A TIME SO MAKE SURE TO PAIR THEM

#------------------

#CANGPS
#Usually Broadcasted in NMEA 0183 Format which is in ASCII
#But canGPS automatically encapsulates it in can frames which we can use
#We will be using the SilverStone Circuit to simulate the GPS Data

#So I couldnt get the nmea injector working so were gna do smth different instead

#were gna pick 5 corners on the track and have the gps go to them in straight lines

import struct
import time
import json

track_corners = [
    {"lat": 52.072501, "long": -1.013343},
    {"lat": 52.075815, "long": -1.020988},
    {"lat": 52.078746, "long": -1.011508},
    {"lat": 52.063531, "long": -1.017886},
    {"lat": 52.069230, "long": -1.022263}
] #village,luffield,copse,stowe,mainstraight

can_stream = [] #the list of can frames
base_time = 1700000000000000000  #epoch time in nanoseconds

for i, corner in enumerate(track_corners):
    lat = float(corner['lat'])
    long = float(corner['long'])
    lat_bytes = struct.pack('>f', lat)  # Convert latitude to 4 bytes
    long_bytes = struct.pack('>f', long)  # Convert longitude to 4 bytes

    can_frame = {
        "timestamp": base_time + i * 1000000000,  # Increment time
        "id": 501,
        "data": list(lat_bytes + long_bytes)  # Combine lat and long bytes
    }

    can_stream.append(can_frame)

with open('can_gps_stream.json', 'w') as f:
    json.dump(can_stream, f, indent=4)

with open('can_gps_stream.json', 'r') as f:
    can_stream = json.load(f)   

