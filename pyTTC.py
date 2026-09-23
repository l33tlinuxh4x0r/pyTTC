import os
import sys
import time
import zipfile
import datetime
import platform
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

#How often to run!
dl_interval = 300

#Selenium vars
options = Options()
options.add_argument("--headless")
options.add_argument('--log-level=3')

#Fix Gentoo binary location/nomenclature and still allow to run on other distros correctly.
info = platform.freedesktop_os_release()
try:
    if info.get("ID") == "gentoo":
        options.binary_location = "/usr/bin/firefox-bin"
        service = Service(executable_path="/usr/bin/geckodriver")
        driver = webdriver.Firefox(options=options, service=service)
    else:
        driver = webdriver.Firefox(options=options)
except:
    driver = webdriver.Firefox(options=options)
    
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
    #Use selenium to control webclient to upload to TTC

    #Upload data
    driver.get("https://us.tamrieltradecentre.com/pc/Trade/WebClient")
    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(file_path)

    #Check that upload completed sucessfully
    runs = 0
    msgs = driver.find_elements(By.ID, "web-client-console-panel")
    for msg in msgs:
        if "Upload Completed" in msg.text:
            pass
        elif runs == 5:
            print("Upload Failed.")
        else:
            time.sleep(5)
            runs +=1
        print("Upload Completed.")
        offset = runs
        runs = 0

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
    driver.quit()
    sys.exit(0)  # Exit cleanly
