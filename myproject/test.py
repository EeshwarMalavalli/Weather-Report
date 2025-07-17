from meteostat import Point, Daily
from datetime import datetime
import pandas as pd
import numpy as np

# Define the location (Mumbai, India)
mumbai = Point(19.0760, 72.8777)

# Set the date range (last 3 years)
start = datetime(2022, 1, 1)
end = datetime(2024, 12, 31)

# Fetch daily weather data
data = Daily(mumbai, start, end)
data = data.fetch()


# Show sample data
data.index = data.index.strftime('%d-%m')
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

data.drop(['snow', 'wdir','wpgt','tsun'], axis=1, inplace=True)

print(data.head())

# Taking care of missing data
data['prcp'].fillna(data['prcp'].mean(),inplace=True)


# Separating features and dependent variable
X = data.loc[:, ['tavg','tmin','tmax','wspd','pres']].values
y = data.loc[:, 'prcp'].values



# Training the Random Forest Regression model on the whole dataset
from sklearn.ensemble import RandomForestRegressor

regressor = RandomForestRegressor(n_estimators = 100, random_state = 0)
regressor.fit(X, y)


## Predicting a new result
input_date = input('Enter the date in DD-MM-YYYY - ')

print(regressor.predict([[input_date[:4]]]))

