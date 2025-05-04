import os
import time
import zipfile
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

#Selenium vars
options = webdriver.FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

#How often to run!
dl_interval = 300

#Setup paths
windows_dir = os.path.expanduser("~\\Documents\\" + "Elder Scrolls Online\\live\\AddOns\\TamrielTradeCentre\\")
linux_dir = "/home/$USER/.steam/steam/steamapps/compatdata/306130/pfx/drive_c/users/steamuser/My Documents/Elder Scrolls Online/live/AddOns/TamrielTradeCentre/"

dl_folder = os.path.expanduser("~/Downloads/")
dl_file = os.path.join(dl_folder + "PriceTable.zip")

#Check for OS compatibility
if os.name == 'nt':
    extract_folder = os.path.abspath(windows_dir)
    file_path = os.path.abspath(os.path.expanduser("~\\Documents\\") + "Elder Scrolls Online\\live\\SavedVariables\\TamrielTradeCentre.lua")
else:
    extract_folder = os.path.abspath(linux_dir)
    file_path = os.path.abspath("/home/$USER/.steam/steam/steamapps/compatdata/306130/pfx/drive_c/users/steamuser/My Documents/Elder Scrolls Online/live/SavedVariables/TamrielTradeCentre.lua")

def download():
    #Download Price Table from TTC
    with open(dl_file, 'wb') as fd:
        for chunk in requests.get("https://us.tamrieltradecentre.com/download/PriceTable").iter_content(chunk_size=128):
            fd.write(chunk)
    #Extract Price Table and keep modification timestamp
    with zipfile.ZipFile(dl_file, 'r') as zipped:
        for file in zipped.infolist():
            zipped.extract(file, extract_folder)
            timestamp = time.mktime(file.date_time + (0, 0, -1))
            unzipped_file = os.path.join(extract_folder, file.filename)
            os.utime(unzipped_file, (timestamp, timestamp))

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

    driver.quit()

#Main loop
interval = dl_interval
#Offset to compensate for upload time so that download time is accurate
offset = 0
last_modified_time = 0
while True:
    #Download portion of loop
    if interval == dl_interval:
        download()
        #Reset interval
        print("Done with this run, waiting " + str(interval) + " seconds.")
        interval = 0

    #Upload portion of loop (check every 5 minutes, only upload if needed.)
    if os.path.isfile(file_path):
        current_modified_time = os.path.getmtime(file_path)

        if current_modified_time != last_modified_time:
            upload()
            last_modified_time = current_modified_time
            interval += offset
    else:
        interval += 1
        time.sleep(1)
