import os
import time
from datetime import datetime
import subprocess

# -------------------------
# CONFIGURATION
# -------------------------

CAMERA_INDEX = 1           # Change to 1 for second camera
SEGMENT_DURATION_MS = 30 * 1000   # 30 seconds
WIDTH = 2592
HEIGHT = 1080
FRAMERATE = 6
BITRATE = 1000000           # 1 Mbps

MAIN_DIR = '/home/bombus/chamber-01/videos'
PARENT_DIR = os.path.join(MAIN_DIR, 'nest-cam')
os.makedirs(PARENT_DIR, exist_ok=True)

# -------------------------
# LOG FUNCTION
# -------------------------

def log(path, message):
    with open(path, 'a') as log_file:
        log_file.write(f"{datetime.now().isoformat()} - {message}\n")

print(f'Starting 30-second recordings every 5 minutes (Camera {CAMERA_INDEX})')

# -------------------------
# MAIN LOOP
# -------------------------

try:
    while True:
        now = datetime.now()

        # Date-based folder (sortable format)
        date = now.strftime("%Y-%m-%d")
        outDir = os.path.join(PARENT_DIR, date)
        os.makedirs(outDir, exist_ok=True)

        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_cam{CAMERA_INDEX}_nest"

        video_path = os.path.join(outDir, filename + '.h264')
        image_path = os.path.join(outDir, filename + '.jpg')
        log_path = os.path.join(outDir, 'log.txt')

        log(log_path, f"=== Starting new 30-sec recording (Camera {CAMERA_INDEX}) ===")
        log(log_path, f"Video path: {video_path}")

        # -------------------------
        # RECORD VIDEO
        # -------------------------

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
            
        # -------------------------
        # EXTRACT FIRST FRAME
        # -------------------------

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

        # -------------------------
        # SLEEP UNTIL NEXT 5-MINUTE BOUNDARY
        # -------------------------

        now = datetime.now()
        seconds_until_next_5 = 300 - (now.minute % 5) * 60 - now.second

        # Prevent negative sleep in rare timing edge case
        if seconds_until_next_5 <= 0:
            seconds_until_next_5 = 1

        time.sleep(seconds_until_next_5)

except KeyboardInterrupt:
    print('Interrupted by user, exiting.')