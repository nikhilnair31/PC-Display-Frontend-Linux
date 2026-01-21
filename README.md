# Setup
- Download e-Paper at git URL ``
- Enter here `cd /home/nikhil/Projects/E_Dashboard`
- Run to create symlink `ln -s /home/nikhil/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd epaper_lib`
- Run `sudo systemctl enable refresh_dashboard`
- Run `sudo systemctl start refresh_dashboard`
- Run `sudo systemctl daemon-reload`
- Run `sudo systemctl status refresh_dashboard`
- Run `journalctl -u pingserver -f`
- Sometimes run `sudo pkill -9 -f python` to kill python and free up GPIO pins
