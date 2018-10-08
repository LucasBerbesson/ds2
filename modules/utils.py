import pandas as pd
from datetime import timedelta, datetime

days_off = ['2013-01-01', '2013-01-06', '2013-02-12', '2013-02-14', '2013-03-31', '2013-03-31', '2013-04-01',
 '2013-05-01', '2013-05-08', '2013-05-09', '2013-05-19', '2013-05-19', '2013-05-20', '2013-07-14',
 '2013-08-15', '2013-11-01', '2013-11-11', '2013-12-25', '2013-12-31', '2014-01-01', '2014-01-06',
 '2014-02-14', '2014-03-04', '2014-04-20', '2014-04-20', '2014-04-21', '2014-05-01', '2014-05-08',
 '2014-05-29', '2014-06-08', '2014-06-08', '2014-06-09', '2014-07-14', '2014-08-15', '2014-11-01',
 '2014-11-11', '2014-12-25', '2014-12-31', '2015-01-01', '2015-01-06', '2015-02-14', '2015-02-17',
 '2015-04-05', '2015-04-05', '2015-04-06', '2015-05-01', '2015-05-08', '2015-05-14', '2015-05-24',
 '2015-05-24', '2015-05-25', '2015-07-14', '2015-08-15', '2015-11-01', '2015-11-11', '2015-12-25',
 '2015-12-31', '2016-01-01', '2016-01-06', '2016-02-09', '2016-02-14', '2016-03-27', '2016-03-27',
 '2016-03-28', '2016-05-01', '2016-05-05', '2016-05-08', '2016-05-15', '2016-05-15', '2016-05-16',
 '2016-07-14', '2016-08-15', '2016-11-01', '2016-11-11', '2016-12-25', '2016-12-31', '2017-01-01',
 '2017-01-06', '2017-02-14', '2017-02-28', '2017-04-16', '2017-04-16', '2017-04-17', '2017-05-01',
 '2017-05-08', '2017-05-25', '2017-06-04', '2017-06-04', '2017-06-05', '2017-07-14', '2017-08-15',
 '2017-11-01', '2017-11-11', '2017-12-25', '2017-12-31', '2018-01-01', '2018-01-06', '2018-02-13',
 '2018-02-14', '2018-04-01', '2018-04-01', '2018-04-02', '2018-05-01', '2018-05-08', '2018-05-10',
 '2018-05-20', '2018-05-20', '2018-05-21', '2018-07-14', '2018-08-15', '2018-11-01', '2018-11-11',
 '2018-12-25', '2018-12-31', '2019-01-01', '2019-01-06', '2019-02-14', '2019-03-05', '2019-04-21',
 '2019-04-21', '2019-04-22', '2019-05-01', '2019-05-08', '2019-05-30', '2019-06-09', '2019-06-09',
 '2019-06-10', '2019-07-14', '2019-08-15', '2019-11-01', '2019-11-11', '2019-12-25', '2019-12-31']

strikes = ['2013-01-13',
 '2013-03-24',
 '2013-05-26',
 '2014-02-02',
 '2014-10-05',
 '2015-01-10',
 '2015-01-11',
 '2016-03-31',
 '2016-06-14',
 '2017-12-09']


def is_day_off(date):
    """
    Function to tell if a day is off in France
    Only works from 2013 to 2020.
    """
    if date.strftime("%Y-%m-%d") in days_off:
        return True
    return False


def get_data(consumption_csv="./data/eco2mix_regional_cons_def.csv",weather_csv="./data/meteo-paris.csv"):
    """
    A function to get consumption and weather data
    Do the wrangling
    And return a nice & compact dataframe
    Temperatures are in °C
    
    """
    # consumptions
    consumption =  pd.read_csv(consumption_csv, delimiter=";", usecols = ["Date - Heure","Consommation (MW)"])
    consumption["Date - Heure"] = pd.to_datetime(consumption["Date - Heure"], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
    consumption.drop_duplicates(inplace=True,subset='Date - Heure')
    consumption.columns = ['Date', 'Conso']
    # weather
    weather = pd.read_csv(weather_csv,usecols=['dt','temp'])
    weather.columns = ['Date', 'Temp']
    weather.drop_duplicates(inplace=True,subset='Date')
    weather['Date'] = pd.to_datetime(weather['Date'],unit='s',utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)    
    # Merging
    df1 = pd.merge(consumption,weather,on='Date',how="left")
    df1["Temp"] = df1["Temp"] - 273.15
    # Half hours
    date_range = pd.date_range(start=df1['Date'].min(),end=df1['Date'].max(),freq='30min')
    half_hours = pd.DataFrame(date_range,columns=['Date'])
    df2 = pd.merge(half_hours,df1,on='Date',how="left")
    #Interpolation
    df2.interpolate('linear',limit=4,inplace=True)
    return df2.dropna()


def is_day_off(date):
    return int(date.strftime('%Y-%m-%D') in days_off)


def is_weekend(date):
    if date.weekday() >=5:
        return 1
    return 0

def heating_degrees(temperature):
    """
    A heating degree day (HDD) is a measurement designed 
    to quantify the demand for energy needed to heat a building. 
    It is the number of degrees a temperature is below 18°C,
    which is the temperature below which buildings need to be heated. 
    """
    return max(18-temperature,0)


def cooling_degrees(temperature):
    """
    A cooling degree day (CDD) is a measurement designed 
    to quantify the demand for energy needed to cool a building.
    It is the number of degrees that a temperature is above 24°C,
    """
    return max(temperature-24,0)

from datetime import datetime, timedelta

def is_bridge(date):
    """
    Check if a datetime is a holiday bridge 
    (friday with thursday off or mondy with tuesday off)
    """
    weekday = date.weekday()
    if weekday == 4:
        return is_day_off(date-timedelta(days=1))
    elif weekday == 0:
        return is_day_off(date+timedelta(days=1))
    return False

def get_data_with_features(consumption_csv="./data/eco2mix_regional_cons_def.csv",weather_csv="./data/meteo-paris.csv"):
    """
    A function to get consumption and weather data
    Do the wrangling
    Add interesting features
    
    """
    df = get_data(consumption_csv,weather_csv)
    df['is_day_off'] = df['Date'].apply(is_day_off)
    df['is_bridge'] = df['Date'].apply(is_bridge)
    df['conso_24_lag'] = df['Conso'].shift(48)
    df['temp_24_lag'] = df['Temp'].shift(48)
    df['conso_7_days_lag'] = df['Conso'].shift(48*7)
    df["heating_degrees"] = df["Temp"].apply(heating_degrees)
    df["cooling_degrees"] = df["Temp"].apply(cooling_degrees)
    df['is_weekend'] = df['Date'].apply(is_weekend)
    df['day_of_week']=df['Date'].dt.weekday
    df["temp_rolling_7_days"] = df["Temp"].rolling(window=336).mean()
    df['month']=df['Date'].dt.month
    df.set_index("Date",inplace=True)
    return df.dropna()