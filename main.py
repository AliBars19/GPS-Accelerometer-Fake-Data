#------------------

import json
from time import time_ns
from mcap.writer import Writer
from mcap.reader import make_reader
 
#------------------
#MCAP WRITER FOR GPS DATA, EDITED FOR GPS SCHEMA (check gps-corrected-schema.json for reference)
#------------------

can_data = "gokart_silverstonelap_fakedata.json"

# get json data from file 
with open(can_data, "r") as f:
    gps_data = json.load(f)

with open("gpsfakedata.mcap", "wb") as stream:
    writer = Writer(stream)
    writer.start()

    # Register schema for CAN message format
    schema_position = writer.register_schema(
        name="gps.Position",
        encoding="jsonschema",
        data=json.dumps({
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "altitude": {"type": "number"},
            },
            "required": ["latitude", "longitude", "altitude"]
        }).encode("utf-8"),
    )
    schema_velocity = writer.register_schema(
        name="gps.Velocity",
        encoding="jsonschema",
        data=json.dumps({
            "type": "object",
            "properties": {
                "speed": {"type": "number"},
                "heading": {"type": "number"},
            },
            "required": ["speed", "heading"]
        }).encode("utf-8"),
    )
    schema_status = writer.register_schema(
        name="gps.Status",
        encoding="jsonschema",
        data=json.dumps({
            "type": "object",
            "properties": {
                "num_satellites": {"type": "integer"},
                "fix_type": {"type": "integer"},
            },
            "required": ["num_satellites", "fix_type"]
        }).encode("utf-8"),
    )
    
    # Register channel
    channels = {
        "/vehicle/gps/position": writer.register_channel(
            schema_id=schema_position,
            topic="/vehicle/gps/position",
            message_encoding="json",
        ),
        "/vehicle/gps/velocity": writer.register_channel(
            schema_id=schema_velocity,
            topic="/vehicle/gps/velocity",
            message_encoding="json",
        ),
        "/vehicle/gps/status": writer.register_channel(
            schema_id=schema_status,
            topic="/vehicle/gps/status",
            message_encoding="json",
        ),
    }
    

    for entry in gps_data:
        topic = entry["topic"]
        log_time = int(entry["timestamp"])
        data_json = json.dumps(entry["data"]).encode("utf-8")
        
        # Add message to MCAP file
        writer.add_message(
            channel_id=channels[topic],
            log_time=log_time,
            publish_time=time_ns(),
            data=data_json,
        )

    writer.finish()

print("Reading MCAP file contents:")
print("=" * 50)

with open("gpsfakedata.mcap", "rb") as f:
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

# """