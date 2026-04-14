# Tuya Dashboard

A Flask web app to monitor and control your Tuya devices from a Raspberry Pi.

## Project Structure

```
tuya_dashboard/
├── app.py              ← Flask backend (API + routes)
├── devices.json        ← Your tinytuya device list
├── requirements.txt
├── devices/            ← Your Python device classes
│   ├── __init__.py
│   ├── breaker.py
│   ├── consumption_breaker.py
│   ├── contact_sensor.py
│   ├── esmax.py
│   ├── general_circuit_breaker.py
│   ├── heater.py
│   ├── locks.py
│   ├── presence_sensor.py
│   ├── smart_bulb.py
│   ├── smart_ir.py
│   ├── smart_lock.py
│   ├── smart_plug.py
│   └── smart_tv.py
└── templates/
    └── index.html      ← Dashboard frontend
```

## Setup on Raspberry Pi

### 1. Install dependencies

```bash
cd tuya_dashboard
pip install -r requirements.txt
```

### 2. Make sure devices.json is up to date

If devices show "No IP", run the tinytuya wizard again:

```bash
python -m tinytuya wizard
```

Then copy the updated `devices.json` into this folder.

### 3. Run the app

```bash
python app.py
```

The dashboard will be available at:
- **http://localhost:5000** (on the Pi itself)
- **http://<pi-ip-address>:5000** (from any device on your network)

To find your Pi's IP: `hostname -I`

### 4. Run on startup (optional)

Create a systemd service so it starts automatically:

```bash
sudo nano /etc/systemd/system/tuya-dashboard.service
```

Paste:
```ini
[Unit]
Description=Tuya Dashboard
After=network.target

[Service]
WorkingDirectory=/home/pi/tuya_dashboard
ExecStart=/usr/bin/python3 app.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable tuya-dashboard
sudo systemctl start tuya-dashboard
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/devices` | List all devices from devices.json |
| GET | `/api/device/<id>/status` | Poll live status from device |
| POST | `/api/device/<id>/command` | Send a DPS command |

### Command example

```bash
curl -X POST http://localhost:5000/api/device/DEVICE_ID/command \
  -H "Content-Type: application/json" \
  -d '{"dps": "1", "value": true}'
```

## Notes

- Devices without an IP address cannot be polled live. Run the tinytuya wizard on the same network as the devices.
- The dashboard auto-detects device type from the `category` field in devices.json.
- Live polling connects directly to devices over your local network (no cloud needed).
