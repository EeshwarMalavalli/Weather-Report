from django.shortcuts import render
from meteostat import Point, Daily
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import io
from django.http import HttpResponse

# Create your views here.
def weather_prediction_model(request):
    if request.method == "POST":
        global date_mm_dd_yyyy
        global date_dd_mm_yyyy

        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude") 
        date = request.POST.get("date")     #format - YYYY-MM-DD
        
        date_obj = datetime.strptime(date, "%Y-%m-%d")  # Convert to datetime object
        date_mm_dd_yyyy = date_obj.strftime("%m-%d-%Y")  # Convert to new format (MM-DD-YYYY)
        date_dd_mm_yyyy = date_obj.strftime("%d-%m-%Y")  # Convert to new format (MM-DD-YYYY)
        print(date_mm_dd_yyyy)

        try:
            output = weather_report(longitude,latitude, date_mm_dd_yyyy)
        except Exception as e:
            print(latitude)
            return render(request, "forecast.html", {"error": "I am sorry, I do not have a weather report for these coordinates", "latitude":latitude,"longitude":longitude,"date":date})
        
        return render(request, "forecast.html", {"output":output,"latitude":latitude,"longitude":longitude,"date":date})

    
    return render(request, "forecast.html")



def weather_report(latitude, longitude, date):
    global le 
    global regressor

    latitude = float(latitude)
    longitude = float(longitude)
    print(latitude,longitude)
    location = Point(latitude, longitude)   # Set the location using latitude and longitude
    

    # Set the date range (last 3 years)
    start = datetime(2022, 1, 1)
    end = datetime(2024, 12, 31)

    # Get the daily weather report between start and end days
    data = Daily(location, start, end)
    ''' Creates a Daily time series object from the meteostat library.
    This object represents daily weather data between start and end dates for a given location. '''
    data = data.fetch()
    ''' Executes the query prepared in the previous line. Fetches the actual weather data from the 
    Meteostat server. Converts the response into a Pandas DataFrame, where:
    Each row is a date (index).
    Columns include:
    - tavg = average temp
    - tmin = min temp
    - tmax = max temp
    - prcp = precipitation
    - wspd = wind speed, etc
    - wpgt = Wind gust speed 
    - pres = Air pressure at sea level (in hPa)
    - tsun: Sunshine duration (in minutes) '''


    ## Data Preprocessing
    
    # Fomratting the date in the index column for analysis (from DD-MM-YYYY to MM-DD)
    data.index = data.index.strftime('%m-%d')
    data['date'] = data.index       # Creating a new column with name 'date'
  
    #print(data.head())
    #print(data.info())
    ''' <class 'pandas.core.frame.DataFrame'>
    Index: 1096 entries, 01-01 to 31-12
    Data columns (total 10 columns):
    #   Column  Non-Null Count  Dtype
    ---  ------  --------------  -----
    0   tavg    1096 non-null   Float64
    1   tmin    1096 non-null   Float64
    2   tmax    1096 non-null   Float64
    3   prcp    1092 non-null   Float64
    4   snow    0 non-null      Float64
    5   wdir    0 non-null      Float64
    6   wspd    1096 non-null   Float64
    7   wpgt    0 non-null      Float64
    8   pres    1096 non-null   Float64
    9   tsun    0 non-null      Float64
    dtypes: Float64(10)
    memory usage: 104.9+ KB
    None '''

    # Taking care of missing data
    data.drop(['snow', 'wdir','wpgt','tsun'], axis=1, inplace=True)
    data['tavg'].fillna(data['tavg'].mean(),inplace=True)

    # Separating features and dependent variable
    X = data.loc[:, 'date'].values
    y = data.loc[:, 'tavg'].values

    # Label Encoding
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    x = le.fit_transform(X)
    x = np.array(x)

    ## Training the Random Forest Regression model on the whole dataset
    from sklearn.ensemble import RandomForestRegressor

    regressor = RandomForestRegressor(n_estimators = 100, random_state = 0)
    regressor.fit(x.reshape(-1, 1), y.reshape(-1, 1))


    ## Predicting the weather on the date
    print(le.transform([[date[:5]]]))
    print(regressor.predict([le.transform([[date[:5]]])]))

    return regressor.predict([le.transform([[date[:5]]])])
    
    
# Plotting the graph
def plot_png(request):
    fig, ax = plt.subplots()
    ax.plot(np.arange(0,365).reshape(-1,1), regressor.predict(np.arange(0,365).reshape(-1,1)), label='Average Temp (°C)', color='orange')
    ax.scatter(le.transform([[date_mm_dd_yyyy[:5]]]),regressor.predict([le.transform([[date_mm_dd_yyyy[:5]]])]),label=f'Temp on {date_dd_mm_yyyy}',color='green')
    ax.set_xlabel('No.of days')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title(f'Yearly Average Temperature')
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    
     # Save to in-memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)


    return HttpResponse(buf.read(), content_type='image/png')
