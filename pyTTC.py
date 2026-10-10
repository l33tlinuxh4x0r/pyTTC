import os
import sys
import time
import zipfile
import datetime
import platform
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

#Setup paths
windows_dir = os.path.expanduser("~\\Documents\\" + "Elder Scrolls Online\\live\\AddOns\\TamrielTradeCentre\\")
linux_dir = os.path.expanduser("~/.steam/steam/steamapps/compatdata/306130/pfx/drive_c/users/steamuser/My Documents/Elder Scrolls Online/live/AddOns/TamrielTradeCentre/")

#Check for OS compatibility
if os.name == 'nt':
    extract_folder = os.path.abspath(windows_dir)
    up_file = os.path.abspath(os.path.expanduser("~\\Documents\\") + "Elder Scrolls Online\\live\\SavedVariables\\TamrielTradeCentre.lua")
else:
    extract_folder = os.path.abspath(linux_dir)
    up_file = os.path.abspath(os.path.expanduser("~/.steam/steam/steamapps/compatdata/306130/pfx/drive_c/users/steamuser/My Documents/Elder Scrolls Online/live/SavedVariables/TamrielTradeCentre.lua"))

dl_folder = os.path.expanduser("~/Downloads/")
dl_file = os.path.join(dl_folder + "PriceTable.zip")

def upload():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    driver.get("https://us.tamrieltradecentre.com/pc/Trade/WebClient")
    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(up_file)

    print("Waiting for upload to complete...")
    page_text = driver.find_element(By.TAG_NAME, "body").text
    while "UPLOADING..." in page_text:
        time.sleep(2)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
    print(time.strftime("%H:%M:%S", time.localtime()) + " Success! Data successfully sent to Tamriel Trade Centre.")
    driver.close()

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
        print(time.strftime("%H:%M:%S", time.localtime()) + " Finished Downloading! You have the latest version of the Price Table.")
    except:
        print("Corrupt download, removing.")
    #Delete Downloaded zip file
    if os.path.exists(dl_file):
        os.remove(dl_file)

#Download interval equals one hour
dl_interval = 3600
interval = dl_interval
last_modified_time = 0
page_text = ""

try:
    while True:
        if os.path.isfile(up_file):
            current_modified_time = os.path.getmtime(up_file)
            if current_modified_time != last_modified_time:
                upload()
                interval += 5
                last_modified_time = current_modified_time    
        if interval >= dl_interval:
            download()
            interval = 0
            
        time.sleep(1)
        interval += 1

except KeyboardInterrupt:
    print("\nCtrl+C pressed, exiting...")
    sys.exit(0)  # Exit cleanly

