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

import json
import string
import struct
import time
from time import time_ns
from mcap.writer import Writer
from mcap.reader import make_reader
from numpy import double

can_stream = [] #the list of can frames

with open('gps_silverstone.json', 'r') as f:
    gps_data = json.load(f)

def make_frame(id, values,timestamp, fmt='>f'):  #packs data into can frame, if not full 8 bytes is ysed, fills rest with 0

        values_bytes = struct.pack(fmt, values)
        if len(values_bytes) < 8:
            values_bytes += b'\x00' * (8 - len(values_bytes))
        elif len(values_bytes) > 8:
            values_bytes = values_bytes[:8]  # Truncate to 8 bytes
        return {
            "id": id,
            "timestamp": timestamp,
            "data": list(values_bytes)
        }


for point in gps_data:
   timestamp = int(point['timestamp'])  # convert to nanoseconds
   data = point.get('data',{})
   topic = str(point.get('topic'))

   lat = float(data.get('latitude'))
   lon = float(data.get('longitude', 0.0))
   alt = float(data.get('altitude', 0.0))
   speed = float(data.get('speed', 0.0))
   heading = float(data.get('heading', 0.0))
   fix_type = float(data.get('fix_type', 0.0))
   num_satellites = float(data.get('num_satellites', 0.0))

   can_stream.append(make_frame(501, lat,timestamp,fmt=">d"))
   can_stream.append(make_frame(502, lon,timestamp,fmt=">d"))
   can_stream.append(make_frame(503, alt,timestamp,fmt=">d"))
   can_stream.append(make_frame(504, speed,timestamp,fmt=">d"))
   can_stream.append(make_frame(505, heading,timestamp,fmt=">d"))
   can_stream.append(make_frame(506, fix_type,timestamp,fmt=">d"))
   can_stream.append(make_frame(507, num_satellites,timestamp,fmt=">d"))

   can_frame = {
           "topic": topic,
           "timestamp": timestamp, 
           "data":{
               "latitude": lat,
               "longitude": lon,
               "altitude": alt,
               "speed": speed,
               "heading": heading,
               "fix_type": fix_type,
               "num_satellites": num_satellites
           }  
       }

   can_stream.append(can_frame)

with open('can_gps_stream.json', 'w') as f:
    json.dump(can_stream, f, indent=4)

with open('can_gps_stream.json', 'r') as f:
    can_stream = json.load(f)  
#------------------
#MCAP WRITER
#------------------




can_data = "can_gps_stream.json"

# get json data from file 
with open(can_data, "r") as f:
    can_data_json = json.load(f)

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
                "timestamp": {"type": "number"},
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

    for entry_idx, entry in enumerate(can_data_json):
        if "time" in entry:
            time_s = float(entry["time"])
            log_time = int(time_s * 1_000_000_000)
        elif "timestamp" in entry:
            ts = entry["timestamp"]
            if isinstance(ts, int) or (isinstance(ts, float) and ts > 1e12):
                log_time = int(ts)
            else:
                log_time = int(float(ts) * 1_000_000_000)
        else:
            print(f"Warning: Entry {entry_idx} has no 'time' or 'timestamp'; using current time")
            log_time = time_ns()

        log_time = log_time
        
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
            
            
            # if message_count >= 5:
            #     print(f"... (showing first 5 messages out of total)")
            #     break
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error in topic '{channel.topic}': {e}")
            print(f"Raw data: {message.data}")