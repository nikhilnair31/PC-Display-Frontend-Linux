# refresh_dashboard.py

import sys
import os
import io
import time
import requests
import logging
from dotenv import load_dotenv
from PIL import Image
from waveshare_epd.lib.waveshare_epd import epd7in5_V2
from waveshare_epd.lib.waveshare_epd import epdconfig

# --- LOGGING SETUP ---
# Forces logs to show up in journalctl -u refresh_dashboard.service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# --- CONST ---
load_dotenv()
SERVER = os.getenv("SERVER")
# We do a full refresh on startup, then every 100 fast cycles
FULL_REFRESH_EVERY = int(os.getenv("FULL_REFRESH_EVERY", 10))
FULL_REFRESH_MAX_TIME = int(os.getenv("FULL_REFRESH_MAX_TIME", 21600)) 
FAST_INTERVAL = int(os.getenv("FAST_INTERVAL", 1200))

# --- HARDWARE INIT ---
# IMPORTANT: If fading persists, go to waveshare_epd/lib/epdconfig.py 
# and change self.SPI.max_speed_hz = 4000000 to 1000000
logger.info("Initializing EPD hardware...")
epd = epd7in5_V2.EPD()

def fetch_dashboard_image():
    try:
        logger.info(f"Fetching image from {SERVER}...")
        r = requests.get(f"{SERVER}/get_dashboard_image", timeout=15)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("1")
        logger.info("Image fetched and converted successfully.")
        return img
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return None

# --- MAIN ---
if __name__ == "__main__":
    fast_count = 0
    last_full_refresh = time.time()
    
    # Force a Full Refresh on the very first loop after script start
    # to clear any ghosting or partial-init artifacts.
    first_run = True 
    
    logger.info("--- Dashboard Service Started ---")
    logger.info(f"Settings: Full every {FULL_REFRESH_EVERY} cycles. Fast interval: {FAST_INTERVAL}s")

    try:
        while True:
            now = time.time()
            img = fetch_dashboard_image()

            if img:
                time_since_full = now - last_full_refresh
                
                # Logic to decide between Full or Fast
                do_full = first_run or \
                          (fast_count >= FULL_REFRESH_EVERY) or \
                          (time_since_full >= FULL_REFRESH_MAX_TIME)

                if do_full:
                    reason = "Initial Startup" if first_run else "Cycle/Time Limit"
                    logger.info(f">>> FULL REFRESH (Reason: {reason})")
                    
                    # 1. Initialize for full refresh
                    epd.init()
                    
                    # 2. REMOVE epd.Clear() - This causes the unnecessary extra flashing
                    # epd.Clear() 
                    
                    # 3. Just display the image. This command performs 
                    # its own clear/draw cycle.
                    logger.info("Writing buffer (Full Refresh)...")
                    epd.display(epd.getbuffer(img))
                    
                    logger.info("Putting display to sleep...")
                    epd.sleep()
                    
                    # Reset counters
                    fast_count = 0
                    last_full_refresh = now
                    first_run = False
                else:
                    logger.info(f">>> FAST REFRESH (Cycle: {fast_count + 1}/{FULL_REFRESH_EVERY})")
                    
                    # Fast init does not sleep, keeping the LUT active in controller RAM
                    epd.init_fast()
                    epd.display(epd.getbuffer(img))
                    epd.sleep()
                    fast_count += 1
            else:
                # Failure! Sleep for only 30 seconds and try again
                logger.warning("No image received. Retrying in 30 seconds...")
                time.sleep(30)

            logger.info(f"Cycle complete. Sleeping for {FAST_INTERVAL} seconds...")
            time.sleep(FAST_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Service interrupted by user.")
    except Exception as e:
        logger.error(f"Critical error in main loop: {e}", exc_info=True)
    finally:
        # This only runs if the service is stopped or crashes
        logger.info("Shutting down GPIO via module_exit().")
        epdconfig.module_exit()
