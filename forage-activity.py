
from gpiozero import DigitalInputDevice
from signal import pause
from datetime import datetime
import csv
import os

# GPIO pin (BCM numbering)
beam = DigitalInputDevice(27, pull_up=True)

LOG_FILE = "beam_log.csv"

# Create file with header if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "event"])

def log_event(event_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, event_type])
    
    print(f"{timestamp} - {event_type}")

def beam_broken():
    log_event("BROKEN")

def beam_restored():
    log_event("RESTORED")

beam.when_deactivated = beam_broken
beam.when_activated = beam_restored

print("Logging IR break beam events to beam_log.csv...")
pause()
