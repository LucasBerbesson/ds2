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
    
    """
    # consumptions
    consumption =  pd.read_csv(consumption_csv, delimiter=";",parse_dates=["Date - Heure"], usecols = ["Date - Heure","Consommation (MW)"])
    consumption.drop_duplicates(inplace=True,subset='Date - Heure')
    consumption.columns = ['Date', 'Conso']
    # half hours
    start_date = consumption['Date'].min()
    dates = []
    for i in range(90000):
        start_date += timedelta(minutes=30)
        dates.append(start_date)
    half_hours = pd.DataFrame(dates,columns=['Date'])
    # weather
    weather = pd.read_csv(weather_csv,usecols=['dt','temp'])
    weather['dt'] = pd.to_datetime(weather['dt'],unit='s')
    weather.columns = ['Date', 'Temp']
    weather.drop_duplicates(inplace=True,subset='Date')
    # Merging
    df1 = pd.merge(consumption,weather,on='Date',how="left")
    df2 = pd.merge(half_hours,df1,on='Date',how="left")
    df2.interpolate('linear',limit=4,inplace=True)
    return df2.dropna()


def compute_day_off(date):
    if is_day_off(date):
        return 1
    return 0


def is_weekend(date):
    if date.weekday() >=5:
        return 1
    return 0



def get_data_with_features(consumption_csv="./data/eco2mix_regional_cons_def.csv",weather_csv="./data/meteo-paris.csv"):
    """
    A function to get consumption and weather data
    Do the wrangling
    Add interesting features
    
    """
    df = get_data(consumption_csv,weather_csv)
    df['is_day_off'] = df['Date'].apply(compute_day_off)
    df['conso_24_lag'] = df['Conso'].shift(48)
    df['conso_7_days_lag'] = df['Conso'].shift(336)
    df['is_weekend'] = df['Date'].apply(is_weekend)
    df['day_of_week']=df['Date'].dt.weekday
    df.set_index("Date",inplace=True)
    return df.dropna()