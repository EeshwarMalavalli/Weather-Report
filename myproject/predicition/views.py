from django.shortcuts import render
from meteostat import Point, Daily
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Create your views here.
def weather_prediction_model(request):
    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude") 
        date = request.POST.get("date") 
        print(date)
        output = ml_output(longitude,latitude, date)
        
        return render(request, "forecast.html", {"output": output})

    
    return render(request, "forecast.html")


def ml_output(longitude,latitude,date):
    print(longitude,latitude)
    longitude = int(longitude)
    latitude = int(latitude)
    location = Point(longitude, latitude)

    # Set the date range (last 3 years)
    start = datetime(2022, 1, 1)
    end = datetime(2024, 12, 31)

    # Fetch daily weather data
    data = Daily(location, start, end)
    data = data.fetch()


    # Show sample data
    data.index = data.index.strftime('%d-%m')
    data['date'] = data.index

    print(data.head())

    print(data.info())
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

    #
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    x = le.fit_transform(X)

    # Training the Random Forest Regression model on the whole dataset
    from sklearn.ensemble import RandomForestRegressor

    regressor = RandomForestRegressor(n_estimators = 100, random_state = 0)
    regressor.fit(x.reshape(-1, 1), y.reshape(-1, 1))


    ## Predicting a new result

    print(regressor.predict([le.transform([[date[:5]]])]))

    # Step 5: Plot average temperature
    # plt.figure(figsize=(12, 5))
    plt.scatter(le.transform([[date[:5]]]),regressor.predict([le.transform([[date[:5]]])]),color='green')
    plt.plot(np.arange(0,365).reshape(-1,1), regressor.predict(np.arange(0,365).reshape(-1,1)), label='Average Temp (°C)', color='orange')
    plt.xlabel('No.of days')
    plt.ylabel('Temperature (°C)')
    plt.title(f'Yearly Average Temperature ({date[6:]})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
