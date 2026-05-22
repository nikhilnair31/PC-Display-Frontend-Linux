# E-Ink Dashboard — RPI Frontend

Raspberry Pi side of the e-paper dashboard. Fetches a rendered PNG from the backend server and writes it to a Waveshare 7.5" V2 e-paper display.

**Backend (server):** [PC-Display-Backend-Linux](https://github.com/nikhilnair31/PC-Display-Backend-Linux)

## How It Works

`refresh_dashboard.py` polls `GET /get_dashboard_image` from the backend on a configurable interval, converts the image to 1-bit, and pushes it to the e-paper via SPI. Full refreshes happen every N cycles to clear ghosting.

## Setup

### 1. Clone the e-Paper library

```bash
cd /home/nikhil
git clone https://github.com/waveshareteam/e-Paper.git
```

### 2. Clone this repo

```bash
cd /home/nikhil/Projects
git clone <this-repo> E_Dashboard
cd E_Dashboard
```

### 3. Install dependencies

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Also install Flask for the receiver service:

```bash
pip install flask
```

### 4. Configure environment

Create `.env` in the project root:

```
SERVER=http://<backend_ip>:5001
FAST_INTERVAL=1200
FULL_REFRESH_EVERY=10
FULL_REFRESH_MAX_TIME=21600
```

### 5. Enable the service

```bash
sudo cp refresh_dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now refresh_dashboard.service
```

### 6. Verify

```bash
sudo systemctl status refresh_dashboard.service
journalctl -u refresh_dashboard -f
```

## Files

| File | Description |
|---|---|
| `refresh_dashboard.py` | Main polling loop — fetches image from server, updates e-paper |
| `receiver.py` | Alternative: Flask server that被动receives images pushed from the backend |
| `refresh_dashboard.service` | Systemd unit for the polling script |
| `dashboard_reciever.service` | Systemd unit for the receiver script |
| `Helmet-Regular.ttf` | Display font |

## Troubleshooting

- **GPIO busy**: `sudo pkill -9 -f python` then restart the service
- **Ghosting persists**: Check `waveshare_epd/lib/epdconfig.py` — lower `SPI.max_speed_hz` from 4000000 to 1000000
- **Fading after full refresh**: Normal for partial updates; full refresh clears it
