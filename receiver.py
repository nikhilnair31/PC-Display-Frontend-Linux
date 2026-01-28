# receiver.py

import sys
import os
# Adds the current directory to the path so waveshare_epd can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import io
from flask import Flask, request
from PIL import Image
from waveshare_epd.lib.waveshare_epd import epd7in5_V2
from waveshare_epd.lib.waveshare_epd import epdconfig

app = Flask(__name__)
epd = epd7in5_V2.EPD()

@app.route("/receive_image", methods=["POST"])
def receive_image():
    try:
        file = request.files['image']
        img = Image.open(io.BytesIO(file.read())).convert("1")
        
        # Display logic
        epd.init() # Or init_fast() if you prefer
        epd.display(epd.getbuffer(img))
        epd.sleep()
        
        return "Display Updated", 200
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)