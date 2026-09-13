# ----- Modules -----
from dotenv import load_dotenv
import obsws_python as obs
import random
import time
import os

# ----- Global Variables -----
HOST = "localhost"
PORT = 4455
load_dotenv(".env")
PASSWORD = os.getenv("OBS_PASSWORD")
if not PASSWORD:
    raise ValueError("OBS_PASSWORD missing in .env!")

SCENE_NAME = "Yuri" # Name of the Scene where the Yuri spawn
IMAGE_LIFETIME = 10  # How long until the Image disappears

active_sources = {}  # {source_name: spawn_timestamp}

# ----- Connect to OBS -----
def connect_to_obs():
    try:
        client = obs.ReqClient(host=HOST, port=PORT, password=PASSWORD)
        return client
    except Exception as e:
        print(f"ERROR CONNECTING TO OBS: {e}")
        return None

# ----- Create a new Image Source for the Yuri -----
def create_image_source(client, image_path, source_name):
    try:
        response = client.create_input(
            SCENE_NAME,
            source_name,
            "image_source",
            {"file": image_path},
            True
        )
        return response
    except Exception as e:
        print(f"ERROR CREATING IMAGE SOURCE: {e}")
        return None

# ----- Remove the Image Source again -----
def remove_image_source(client, source_name):
    try:
        client.remove_input(source_name)
        return True
    except Exception as e:
        print(f"ERROR REMOVING IMAGE SOURCE: {e}")
        return False

# ----- Randomly Place the Image on Screen -----
def randomize_position(client, item_id, canvas_width=1920, canvas_height=1080, target_size=400):
    try:
        x = random.randint(0, canvas_width - target_size)
        y = random.randint(0, canvas_height - target_size)
        transform = {
            "positionX": x,
            "positionY": y,
            "boundsType": "OBS_BOUNDS_SCALE_INNER",
            "boundsWidth": target_size,
            "boundsHeight": target_size
        }
        client.set_scene_item_transform(SCENE_NAME, item_id, transform)
        return (x, y)
    except Exception as e:
        print(f"ERROR SETTING POSITION: {e}")
        return None

# ----- The COMPLETE Algorithm to spawn 1 single Yuri Image -----
def spawn_yuri_image(client, image_path):
    source_name = f"yuri_{int(time.time() * 1000)}"
    response = create_image_source(client, os.path.abspath(image_path), source_name)
    if response is None:
        return None
    item_id = response.scene_item_id
    randomize_position(client, item_id)
    active_sources[source_name] = time.time()
    return source_name

# ----- Delete Every Image Source which is older than IMAGE_LIFETIME -----
def cleanup_old_sources(client):
    now = time.time()
    to_remove = [name for name, spawn_time in active_sources.items() if now - spawn_time > IMAGE_LIFETIME]
    for name in to_remove:
        if remove_image_source(client, name):
            del active_sources[name]
    
# ----- Testing -----
if __name__ == '__main__':
    client = connect_to_obs()
    spawn_yuri_image(client, "temp_images/7101745.gif") # Get path with yuri code later
    print(active_sources)
    time.sleep(5)
    cleanup_old_sources(client)
    print(active_sources)
    time.sleep(7) 
    cleanup_old_sources(client)
    print(active_sources)