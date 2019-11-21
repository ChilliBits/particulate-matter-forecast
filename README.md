# Particulate Matter Forecast Script
AI based forecast script for predicting the particulate matter values of the future 🔮

## How to setup the dependencies for this script (tested for Ubuntu 16.04)
1. Install facebook prophet (https://facebook.github.io/prophet/docs/installation.html#python)
   * `$ apt-get update; apt-get upgrade -y`
   * `$ pip install fbprophet`
2. Install pandas library (https://pandas.pydata.org/pandas-docs/stable/install.html):
   * `$ pip install pandas`
3. Install plotly library for creating graphs:
   * `$ pip install plotly==4.3.0`
4. Finished!

If something doesn't work, feel free to write us an email: mrgames@outlook.de

## How to use this script
In the default configuration, the script loads the pm measurement data from 2018/11/15 to the current date from a specific sensor which can be defined by setting the command line argument to the chip id of the sensor.

Example:
`$ python forecast.py -s 27645785`

You can use following command to get advice, which parameters there are and how to use them:
`$ python forecast.py --help`

The algorithm takes the loaded data and merges it in a single csv file. This csv file will be dropped to `tmp.csv` in the same directory. Later on, the algorithm cropps the file to only the required columns. In the default configuration: the time and the PM10 value. The output is `tmp_clean.csv`
After this, we feed the data to our machine learning library (prophet) and start the learning cycle. This can take very long, depending on the number of selected data records. After this, the model for the nural network will be saved to `model.pkl`.
At last, we plot the whole forecast to a html file - `temp-plot.html`.

© M&R Games 2019 (Designed and developed by Marc Auberer in 2019)
