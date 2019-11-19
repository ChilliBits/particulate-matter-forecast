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

# Start parameters
data_sensor = sys.argv[1]
data_from = 1542236400000  # 15.11.2018
data_to = int(round(time.time() * 1000))

# Get start and end of date range
start = datetime.datetime.fromtimestamp(data_from / 1000.0)
end = datetime.datetime.fromtimestamp(data_to / 1000.0)

# Get required values
year_start = int(start.strftime('%Y'))
month_start = int(start.strftime('%m'))
year_end = int(end.strftime('%Y'))
month_end = int(end.strftime('%m'))

# Get data for the sensor from the db and export it to a temporary csv file
if os.path.exists("tmp.csv"): os.remove("tmp.csv")

print("Loading data records ...")
first = True
for year in range(year_start, year_end +1):
    for month in range((month_start if year == year_start else 1), (month_end if year == year_end else 12) +1):
        # Get name of database
        db_name = "data_" + str(year) + "_" + (str(month) if(month > 9) else "0" + str(month))
        try:
            db = config.connectToDb(db_name)
            query = "SELECT time as t, pm10 as p1, pm2_5 as p2 FROM data_" + data_sensor + " WHERE UNIX_TIMESTAMP(STR_TO_DATE(time, '%Y/%m/%d %T')) >= " + str(time.mktime(start.timetuple())) + " AND UNIX_TIMESTAMP(STR_TO_DATE(time, '%Y/%m/%d %T')) < " + str(time.mktime(end.timetuple())) + " ORDER BY UNIX_TIMESTAMP(STR_TO_DATE(time, '%Y/%m/%d %T')) ASC"
            # Request data from the db
            cursor = db.cursor()
            cursor.execute(query)
            # Write to csv file74
            rows = cursor.fetchall()
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
print("Feed prophet ...")
df = pd.read_csv('tmp.csv', parse_dates=[0], sep=';')
df_new = df.rename(columns={'t': 'ds', 'p1': 'y'})
df_final = pd.DataFrame(df_new, columns=['ds', 'y'])
print(df_final.describe())
df_final.to_csv('tmp_clean.csv', sep=';')

# Initialize prophet
m = Prophet(daily_seasonality=False)
m.fit(df_final)
future = m.make_future_dataframe(periods=10, freq='D')
forecast = m.predict(future)
forecast.to_pickle("model.pkl")
fig = plot_plotly(m=m, fcst=forecast)
py.plot(fig)
# forecast.head()