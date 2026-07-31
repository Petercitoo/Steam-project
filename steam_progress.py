import time
import json
import os
from utils import get_steam_path, get_lib_path, get_manifests, get_download_data

steam_path = get_steam_path()
lib_paths = get_lib_path(steam_path)
manifests = get_manifests(lib_paths)
progress_f = os.path.join(os.environ.get("TEMP"), "dl_progress.json")
last_reading = None

while True:
    current = get_download_data(manifests)

    if isinstance(current, Exception):
        print(current)
        last_reading = None  
        with open(progress_f, "w") as f:
            progress_string =  json.dumps({"idle": True})
            f.write(progress_string)
    else:
        now = time.time()
        if last_reading is not None:
            prev_data, prev_time = last_reading

            if prev_data["appid"] == current["appid"]:
                elapsed = now - prev_time
                
                download_diff = current["bd"] - prev_data["bd"]
                speed = download_diff / elapsed if elapsed > 0 else 0

                percentage = (current["bd"] / current["btd"]) * 100 if current["btd"] else 0
                remaining = current["btd"] - current["bd"]
                eta_seconds = remaining / speed if speed > 0 else None

                with open(progress_f, "w") as f:
                    progress_string = json.dumps({"appid": current["appid"],"percentage": percentage, "remaining": remaining, "eta_seconds": eta_seconds})
                    f.write(progress_string)
        last_reading = (current,now)
    time.sleep(1)



