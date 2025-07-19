from meteostat import Stations

stations = Stations()
stations = stations.region('IN')  # India
all_indian_stations = stations.fetch()

# Print all stations
for index, row in all_indian_stations.iterrows():
    print(f"{row['name']}: ({row['latitude']}, {row['longitude']})")
