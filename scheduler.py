import config
import os
import mysql.connector
import time
from tqdm import tqdm

# Constants
table_sensors = "Sensors"
time_offset = 5 #  5 days
time_offset_millis = time_offset * 86400000

# Initialization
current_millis = int(round(time.time() * 1000))

# Connect to the database and get all sensors which are on the map
db = config.connectToDb("main")
cursor = db.cursor()
query = "SELECT chip_id FROM " + table_sensors + " WHERE last_update > " + str((current_millis - time_offset_millis) / 1000)
print(query)
cursor.execute(query)
rows = cursor.fetchall()
cursor.close()

for i in tqdm(range(len(rows) -1)):
    row = rows[i]
    # Get chip id
    chip_id = str(row[0])
    # Execute forecast script for this sensor without output
    print("Executing forecast for " + chip_id + " ...")
    os.system("python forecast.py -s " + chip_id + "  > /dev/null 2>&1")

# Finished
print("Finished!")