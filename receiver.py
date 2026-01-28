# receiver.py

import sys
import os

# Set the pin factory for gpiozero before importing waveshare
os.environ['GPIOZERO_PIN_FACTORY'] = 'lgpio'

# Point to the 'lib' folder
sys.path.append('/home/nikhil/e-Paper/RaspberryPi_JetsonNano/python/lib')

import io
from flask import Flask, request
from PIL import Image
from waveshare_epd import epd7in5_V2
from waveshare_epd import epdconfig

app = Flask(__name__)
epd = epd7in5_V2.EPD()
# Create a lock to prevent multiple threads from talking to the screen at once
screen_lock = threading.Lock()

def update_display_task(img):
    """Internal task to handle the slow hardware refresh"""
    # Use a lock so if two requests come in fast, they don't corrupt the SPI bus
    if not screen_lock.acquire(blocking=False):
        print("Screen busy, skipping this update...")
        return

    try:
        print("Starting display refresh...")
        epd.init()
        epd.display(epd.getbuffer(img))
        epd.sleep()
        print("Display refresh complete.")
    except Exception as e:
        print(f"Hardware Error: {e}")
    finally:
        screen_lock.release()

@app.route("/receive_image", methods=["POST"])
def receive_image():
    try:
        if 'image' not in request.files:
            return "No image part", 400
        
        file = request.files['image']
        # Read the image into memory and convert it immediately
        img = Image.open(io.BytesIO(file.read())).convert("1")
        
        # Start the hardware refresh in a background thread
        thread = threading.Thread(target=update_display_task, args=(img,))
        thread.start()
        
        # Return immediately so the PC doesn't time out
        return "OK", 200
    except Exception as e:
        print(f"Request Error: {e}")
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, threaded=True)