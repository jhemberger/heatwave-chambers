import os
import time
from datetime import datetime, timedelta
import subprocess

# -------------------------
# CONFIGURATION
# -------------------------

CAMERA_INDEX = 0
SEGMENT_DURATION_MS = 5 * 60 * 1000   # 5 minutes 
WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 20
BITRATE = 1000000

MAIN_DIR = '/home/bombus/chamber-01/videos'
PARENT_DIR = os.path.join(MAIN_DIR, 'forage-cam')
os.makedirs(PARENT_DIR, exist_ok=True)

RECORD_START_HOUR = 18   # 6 PM
RECORD_END_HOUR = 10     # 10 AM

# -------------------------
# LOG FUNCTION
# -------------------------

def log(path, message):
    with open(path, 'a') as log_file:
        log_file.write(f"{datetime.now().isoformat()} - {message}\n")

# -------------------------
# TIME WINDOW CHECK
# -------------------------

def in_recording_window(now):
    return now.hour >= RECORD_START_HOUR or now.hour < RECORD_END_HOUR

def seconds_until_6pm(now):
    today_6pm = now.replace(hour=18, minute=0, second=0, microsecond=0)
    if now >= today_6pm:
        today_6pm += timedelta(days=1)
    return (today_6pm - now).total_seconds()

print(f'Starting overnight recordings (Camera {CAMERA_INDEX})')

# -------------------------
# MAIN LOOP
# -------------------------

try:
    while True:
        now = datetime.now()

        # ---------- ONLY RECORD DURING WINDOW ----------
        if not in_recording_window(now):
            sleep_time = seconds_until_6pm(now)
            print(f"Outside recording window. Sleeping {int(sleep_time/60)} minutes.")
            time.sleep(sleep_time)
            continue

        # Date-based folder
        date = now.strftime("%Y-%m-%d")
        outDir = os.path.join(PARENT_DIR, date)
        os.makedirs(outDir, exist_ok=True)

        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_cam{CAMERA_INDEX}_nest"

        video_path = os.path.join(outDir, filename + '.h264')
        image_path = os.path.join(outDir, filename + '.jpg')
        log_path = os.path.join(outDir, 'log.txt')

        log(log_path, f"=== Starting new 5-min recording (Camera {CAMERA_INDEX}) ===")
        log(log_path, f"Video path: {video_path}")

        # RECORD VIDEO
        try:
            subprocess.run([
                'rpicam-vid',
                '--camera', str(CAMERA_INDEX),
                '-t', str(SEGMENT_DURATION_MS),
                '--codec', 'h264',
                '--width', str(WIDTH),
                '--height', str(HEIGHT),
                '--framerate', str(FRAMERATE),
                '--bitrate', str(BITRATE),
                '-o', video_path
            ], check=True)

            log(log_path, "Video recording completed successfully.")

        except subprocess.CalledProcessError as e:
            log(log_path, f"ERROR during video recording: {e}")

        # EXTRACT FIRST FRAME
        try:
            subprocess.run([
                'ffmpeg',
                '-i', video_path,
                '-frames:v', '1',
                '-q:v', '2',
                image_path
            ], check=True)

            log(log_path, "Image extraction completed successfully.")

        except subprocess.CalledProcessError as e:
            log(log_path, f"ERROR during image extraction: {e}")

        print(f"Saved: {video_path}")
        log(log_path, "=== Segment complete ===\n")

        # SLEEP UNTIL NEXT 10-MINUTE BOUNDARY
        now = datetime.now()
        seconds_until_next_10 = 600 - (now.minute % 10) * 60 - now.second

        if seconds_until_next_10 <= 0:
            seconds_until_next_10 = 1

        time.sleep(seconds_until_next_10)

except KeyboardInterrupt:
    print('Interrupted by user, exiting.')
