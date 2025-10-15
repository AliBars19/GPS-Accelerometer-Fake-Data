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

##THINGS TO ASK FOR TOMORROW
# how precise is the canGPS. if its total 8 digits(52.072501) then is that 1 can frame, then the other frame sends teh long
# if the precision is 6 didgits(52.0725) then what do we do with the other 2 digits, do we just add 00 at the end or smth


import struct
import time
import json



can_stream = [] #the list of can frames
base_time = 1700000000000000000  #epoch time in nanoseconds

with open('gps_silverstone.json', 'r') as f:
    gps_data = json.load(f)

for point in gps_data:
    lat = float(point['lat'])
    long = float(point['long'])
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

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ this is a can to JSON converter now we are gonna combine this with JSON to MCAP

















import json
from time import time_ns
from mcap.writer import Writer
from mcap.reader import make_reader
import requests

# Get CAN data from URL
url = "C:\\Users\\aliba\\Downloads\\UNI\\Formula Student\\GPS Fake Data\\GPS-Accelerometer-Fake-Data\\GPS-Accelerometer-Fake-Data\\can_gps_stream.json"
can_data = requests.get(url, stream=True)
can_data.raise_for_status()  # check if request was successful


can_data_json = can_data.json()  

with open("candata.mcap", "wb") as stream:
    writer = Writer(stream)
    writer.start()

    # Register schema for CAN message format
    schema_id = writer.register_schema(
        name="can_data",
        encoding="jsonschema",
        data=json.dumps({
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "time": {"type": "number"},
                "data": {
                    "type": "array",
                    "items": {"type": "integer"}
                }
            }
        }).encode(),
    )
    
    # Register channel
    channel_id = writer.register_channel(
        schema_id=schema_id,
        topic="can_messages",
        message_encoding="json",
    )

    for entry in can_data_json:
        # Convert time to nanoseconds for MCAP log-time
        log_time = int(entry["time"] * 1e9)
        
        
        entry_json = json.dumps(entry).encode("utf-8")
        
        # Add message to MCAP file
        writer.add_message(
            channel_id=channel_id,
            log_time=log_time,
            data=entry_json,
            publish_time=time_ns()
        )

    writer.finish()

print("Reading MCAP file contents:")
print("=" * 50)

with open("candata.mcap", "rb") as f:
    reader = make_reader(f)
    
    message_count = 0
    for schema, channel, message in reader.iter_messages():
        try:
            json_data = json.loads(message.data.decode("utf-8"))
            print(f"Message {message_count + 1}:")
            print(f"  Topic: {channel.topic}")
            print(f"  Log Time: {message.log_time}")
            print(f"  Data: {json_data}")
            print("-" * 30)
            message_count += 1
            
            
            if message_count >= 5:
                print(f"... (showing first 5 messages out of total)")
                break
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error in topic '{channel.topic}': {e}")
            print(f"Raw data: {message.data}")