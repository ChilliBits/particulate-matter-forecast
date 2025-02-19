# Particulate Matter Forecast Script
AI based forecast script for predicting the particulate matter values of the future 🔮.

## How to setup the dependencies for this script (tested for Ubuntu 16.04)
1. Install facebook prophet machine learning framework (https://facebook.github.io/prophet/docs/installation.html#python)
   * `$ apt-get update; apt-get upgrade -y`
   * `$ pip install fbprophet`
2. Install other libraries:
   * Pandas (https://pandas.pydata.org/pandas-docs/stable/install.html): `$ pip install pandas`
   * Plotly (https://plot.ly/python/getting-started/): `$ pip install plotly==4.3.0`
   * Tqdm (https://github.com/tqdm/tqdm): `$ pip install tqdm`
3. Finished!

If something doesn't work, feel free to write us an email: contact@chillibits.com.

## How to use this script
In the default configuration, the script loads the pm measurement data from 2018/11/15 to the current date from a specific sensor which can be defined by setting the command line argument to the chip id of the sensor.

Example:
`$ python forecast.py -s 27645785`

You can use following command to get advice, which parameters there are and how to use them:
`$ python forecast.py --help`.

The algorithm takes the loaded data and merges it in a single csv file. This csv file will be dropped to `tmp.csv` in the same directory. Later on, the algorithm cropps the file to only the required columns. In the default configuration: the time and the PM10 value. The output is `tmp_clean.csv`.
After this, we feed the data to our machine learning library (prophet) and start the learning cycle. This can take very long, depending on the number of selected data records. After this, the model for the nural network will be saved to `model.pkl`.
At last, we plot the whole forecast to a html file - `temp-plot.html`.

## Customization options
There are some command line arguments to customize the input data, that will be used for training the algorithm as well as the ouput options:

| Short form | Long form | Description | Expecting | Default value |
|------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|-----------------------------|
| -s | --sensor | The chip id for the sensor, whose date is to be consumed. | Integer | - (required attrribute) |
| -f | --from | The timestamp in milliseconds, where we have to beginn loading the data. | Integer | Current datetime - one year |
| -t | --to | The timestamp in milliseconds, where we have to stop loading the data. | Integer | Current datetime |
| -freq | --frequency | The unit for the period which will be predicted. Use on of the following: seconds, minutes, hours, days. Example: Pass -freq hours and -p 10 to get the prediction for the next 10 hours after the specified to datetime. | String (seconds / minutes / hours / days) | minutes |
| -p | --periods | The periods which will be predicted. Example: Pass -freq days and -p 10 to get the prediction for the next 10 days after the specified to datetime. | Integer | 7200 (5 days) |

You also can look them up by entering: `$ python forecast.py -h` or `$ python forecast.py --help`.

**TODO**

- [ ] try out with OrientDB (cf. https://github.com/orientechnologies/orientdb-jupyter)

© ChilliBits 2019-2021 (Designed and developed by Marc Auberer in 2019 and 2020)
