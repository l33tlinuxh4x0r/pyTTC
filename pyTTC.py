import os
import sys
import time
import zipfile
import datetime
import platform
import requests

UPLOAD_URL = f"https://us.tamrieltradecentre.com"

#Setup paths
windows_dir = os.path.expanduser("~\\Documents\\" + "Elder Scrolls Online\\live\\AddOns\\TamrielTradeCentre\\")
linux_dir = os.path.expanduser("~/.steam/steam/steamapps/compatdata/306130/pfx/drive_c/users/steamuser/My Documents/Elder Scrolls Online/live/AddOns/TamrielTradeCentre/")

dl_folder = os.path.expanduser("~/Downloads/")
dl_file = os.path.join(dl_folder + "PriceTable.zip")

#Check for OS compatibility
if os.name == 'nt':
    extract_folder = os.path.abspath(windows_dir)
    file_path = os.path.abspath(os.path.expanduser("~\\Documents\\") + "Elder Scrolls Online\\live\\SavedVariables\\TamrielTradeCentre.lua")
else:
    extract_folder = os.path.abspath(linux_dir)
    file_path = os.path.abspath(os.path.expanduser("~/.steam/steam/steamapps/compatdata/306130/pfx/drive_c/users/steamuser/My Documents/Elder Scrolls Online/live/SavedVariables/TamrielTradeCentre.lua"))

def download():
    #Download Price Table from TTC
    with open(dl_file, 'wb') as fd:
        for chunk in requests.get("https://us.tamrieltradecentre.com/download/PriceTable").iter_content(chunk_size=128):
            fd.write(chunk)
    #Extract Price Table and keep modification timestamp
    try:
        with zipfile.ZipFile(dl_file, 'r') as zipped:
            for file in zipped.infolist():
                zipped.extract(file, extract_folder)
                timestamp = time.mktime(file.date_time + (0, 0, -1))
                unzipped_file = os.path.join(extract_folder, file.filename)
                os.utime(unzipped_file, (timestamp, timestamp))
    except:
        print("Corrupt download, removing.")
    #Delete Downloaded zip file
    if os.path.exists(dl_file):
        os.remove(dl_file)

def upload(): 
    with open(file_path, 'rb') as f:
        files = {
            'FileUpload': ('TamrielTradeCentre.lua', f, 'application/octet-stream')
        }

        try:
            # Post the multipart form data
            response = requests.post(UPLOAD_URL, files=files)
            
            if response.status_code == 200:
                print(time.strftime("%H:%M:%S", time.localtime()) + " Success! Data successfully sent to Tamriel Trade Centre.")
            else:
                print(f"Failed to upload. Server responded with status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while connecting to TTC: {e}")

#Main loop
download()
print(time.strftime("%H:%M:%S", time.localtime()) + " Finished Downloading, try to only do this once a day.\nNote: This runs once every time the script is launched.")
last_modified_time = 0
try:
    while True:
        #Upload portion of loop (only upload if needed.)
        if os.path.isfile(file_path):
            current_modified_time = os.path.getmtime(file_path)
            if current_modified_time != last_modified_time:
                upload()
                last_modified_time = current_modified_time
        time.sleep(1)
except KeyboardInterrupt:
    print("\nCtrl+C pressed, exiting...")
    sys.exit(0)  # Exit cleanly
