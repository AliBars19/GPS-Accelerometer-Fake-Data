#General MCAP Format (for reference(help i wanna kms))

#Header
#Schema
#Channel
#Message
#Footer

#ID: 501 , latitude POSITION
#ID: 502 , Longitude

#ID: 503 , altitude VELOCITY
#ID: 504 , speed
#ID: 504 , Heading

#ID: 505 , num_sat & fix_type status



#the overview file is the general layout(schema) 
#but the indiviaul file (gps_silverstone.json) is what it actually looks like

#create a master schema file (.txt), seperate into diff channels
#raw data should still be in one json file but in different channels

#------------------

import json
import struct
from time import time_ns
from mcap.writer import Writer
from mcap.reader import make_reader
 
#------------------
#MCAP WRITER
#------------------

# """

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

    for entry in can_data_json:
        ts = entry["timestamp"]
        log_time = int(ts)

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

# """