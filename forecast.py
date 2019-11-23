import config
import pandas as pd
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
import plotly.offline as py
import time
import datetime
import sys
import csv
import os
import mysql.connector
import argparse
from tqdm import tqdm

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-Methods-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def selectFrequency(freq):
    switcher = {
        "seconds": "S",
        "minutes": "min",
        "hours": "H",
        "days": "D"
    }
    return switcher.get(freq, "D")

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-Main Program-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# Constants
YEAR_IN_MILLIS = 31540000000

# Initialize script
current_millis = int(round(time.time() * 1000))

# Initialize argparse
parser = argparse.ArgumentParser(os.path.splitext(__file__)[0], description="Script to forecast particulate matter values based on ai.")
parser.add_argument("-s", "--sensor", help="The chip id for the sensor, whose date is to be consumed.", type=int, required=True)
parser.add_argument("-f", "--from", help="The timestamp in milliseconds, where we have to beginn loading the data. Leave blank / not set this argument to provide the data from 1 year.", type=int, dest="date_from", default=(current_millis - YEAR_IN_MILLIS))
parser.add_argument("-t", "--to", help="The timestamp in milliseconds, where we have to stop loading the data. Leave blank / not set this argument to provide the data till now.", type=int, dest="date_to", default=current_millis)
parser.add_argument("-freq", "--frequency", help="The unit for the period which will be predicted. Use on of the following: seconds, minutes, hours, days. Example: Pass -freq hours and -p 10 to get the prediction for the next 10 hours after the specified to datetime.", choices=['seconds', 'minutes', 'hours', 'days'], type=str.lower, default="minutes")
parser.add_argument("-p", "--periods", help="The periods which will be predicted. Example: Pass -freq days and -p 10 to get the prediction for the next 10 days after the specified to datetime.", type=int, default=7200)
args = parser.parse_args()

# Start parameters
data_sensor = args.sensor
data_from = args.date_from
data_to = args.date_to
frequency = selectFrequency(args.frequency) #args.frequency[0].upper()
periods = args.periods

# Get start and end of date range
start = datetime.datetime.fromtimestamp(data_from / 1000.0)
end = datetime.datetime.fromtimestamp(data_to / 1000.0)

# Get required values
year_start = int(start.strftime('%Y'))
month_start = int(start.strftime('%m'))
year_end = int(end.strftime('%Y'))
month_end = int(end.strftime('%m'))

# Delete old files
if os.path.exists("tmp.csv"): os.remove("tmp.csv")
if os.path.exists("tmp_clean.csv"): os.remove("tmp_clean.csv")
if os.path.exists("model.pkl"): os.remove("model.pkl")
if os.path.exists("temp_plot.html"): os.remove("temp_plot.html")

# Get data for the sensor from the db and export it to a temporary csv file
print("Loading data records ...")
first = True
for year in range(year_start, year_end +1):
    for month in range((month_start if year == year_start else 1), (month_end if year == year_end else 12) +1):
        # Get name of database
        db_name = "data_" + str(year) + "_" + (str(month) if(month > 9) else "0" + str(month))
        try:
            db = config.connectToDb(db_name)
            query = "SELECT time as t, pm10 as p1, pm2_5 as p2 FROM data_" + str(data_sensor) + " WHERE UNIX_TIMESTAMP(STR_TO_DATE(time, '%Y/%m/%d %T')) >= " + str(time.mktime(start.timetuple())) + " AND UNIX_TIMESTAMP(STR_TO_DATE(time, '%Y/%m/%d %T')) < " + str(time.mktime(end.timetuple())) + " ORDER BY UNIX_TIMESTAMP(STR_TO_DATE(time, '%Y/%m/%d %T')) ASC"
            # Request data from the db
            cursor = db.cursor()
            cursor.execute(query)
            # Write to csv file
            rows = cursor.fetchall()
            cursor.close()
            column_names = [i[0] for i in cursor.description]
            fp = open('tmp.csv', 'a')
            csv_file = csv.writer(fp, delimiter=';')
            if first:
                csv_file.writerow(column_names) 
                first = False 
            csv_file.writerows(rows)
            fp.close()
        except mysql.connector.Error as err:
            print(db_name + " not found. Skipping this db.")

# Read in csv to pandas
print("Crop data to the selected columns ...")
df = pd.read_csv('tmp.csv', parse_dates=[0], sep=';')
df_new = df.rename(columns={'t': 'ds', 'p1': 'y'})
df_final = pd.DataFrame(df_new, columns=['ds', 'y'])

# Analyze the data
print(df_final.describe())

# Save cropped data to another csv file
print("Exporting clean csv ...")
df_final.to_csv('tmp_clean.csv', sep=';')

# Initialize prophet
print("Feeding prophet ...")
m = Prophet()
# Train the ai model
print("Training ai model ...")
m.fit(df_final)
future = m.make_future_dataframe(periods=periods, freq=frequency)
print("Pedicting ...")
forecast = m.predict(future)
print("Saving ai model ...")
forecast.to_pickle("model.pkl")
print("Predicted values:")
forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)

# Dump the predicing result to a html file
#print("Saving dump ...")
#fig = plot_plotly(m=m, fcst=forecast)
#fig.write_image("prediction.png")

# Save predicted records to seperate databases
print("Saving prediction to databases ...")
db = config.connectToDbServer()
for i in tqdm(range(periods)):
    row = forecast_data.iloc[i]
    # Get name of database
    year = int(row.ds.strftime('%Y'))
    month = int(row.ds.strftime('%m'))
    db_name = "forecast_" + str(year) + "_" + (str(month) if(month > 9) else "0" + str(month))
    try:
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + db_name + ";")
        cursor.close()
        db = config.connectToDb(db_name)
        cursor = db.cursor()
        # print("CREATE TABLE IF NOT EXISTS forecast_" + str(data_sensor) + " (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, time VARCHAR(20), pm2_5 FLOAT, pm10 FLOAT, temp FLOAT, humidity FLOAT, pressure FLOAT, p1_limit_lower FLOAT, p1_limit_upper FLOAT);")
        cursor.execute("CREATE TABLE IF NOT EXISTS forecast_" + str(data_sensor) + " (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, time VARCHAR(20), pm10 FLOAT, pm2_5 FLOAT, temp FLOAT, humidity FLOAT, pressure FLOAT, p1_limit_lower FLOAT, p1_limit_upper FLOAT);")
        cursor.execute("INSERT INTO forecast_" + str(data_sensor) + " (time, pm10, pm2_5, temp, humidity, pressure, p1_limit_lower, p1_limit_upper) VALUES ('" + row.ds.strftime('%Y-%m-%d %H:%M:%S') + "', " + str(round(row.yhat, 2)) + ", 0, 0, 0, 0, " + str(round(row.yhat_lower, 2)) + ", " + str(round(row.yhat_upper, 2)) + ");")
        cursor.close()
    except mysql.connector.Error as err:
        print("Exception during the writing process: " + str(err))

# Finished
print("Finished.")