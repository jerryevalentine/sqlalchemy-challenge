# Import the dependencies.
from flask import Flask, render_template
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
from io import BytesIO
import base64
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import func
from flask import jsonify
from sqlalchemy.orm import scoped_session, sessionmaker



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a scoped session
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

# Query all records from the Measurement table
all_measurement_data = session.query(Measurement).all()

# Convert the query results to a list of dictionaries containing all attributes
measurement_data_dicts = [measurement.__dict__ for measurement in all_measurement_data]

# Drop the unnecessary '__sa_instance_state' key from each dictionary
for measurement_dict in measurement_data_dicts:
    measurement_dict.pop('_sa_instance_state', None)

# Convert the list of dictionaries to a DataFrame
df_measurement = pd.DataFrame(measurement_data_dicts)

# Convert the 'date' column to datetime format
df_measurement['date'] = pd.to_datetime(df_measurement['date'])

# Define start and end date for the last 12 months
end_date = df_measurement['date'].max()
start_date = end_date - dt.timedelta(days=365)

# Filter data for the last 12 months
df_last_12_months = df_measurement[(df_measurement['date'] >= start_date) & (df_measurement['date'] <= end_date)]

# Your previous code for calculating other dataframes goes here...

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

### Page names and their corresponding URLs
pages = [
    {'name': 'Home', 'url': '/'},
    {'name': 'Precipitation_for_All_Dates', 'url': '/Precipitation_for_All_Dates'},
    {'name': 'Histogram_SC00519281_12_months', 'url': '/Histogram_SC00519281_12_months'},
    {'name': 'Precipitation', 'url': '/api/v1.0/precipitation'},
    {'name': 'Stations', 'url': '/api/v1.0/stations'}
]

# Define routes for different pages
@app.route('/')
def index():
    return render_template('index.html', pages=pages)

@app.route('/Precipitation_for_All_Dates')
def Precipitation_for_All_Dates():
    # Plot the graph
    plt.figure(figsize=(10, 6))
    plt.bar(df_last_12_months['date'], df_last_12_months['prcp'], width=0.5)  # Adjust the width as needed
    plt.xticks(rotation=45)
    plt.title('Precipitation for All Dates in the Last 12 Months')
    plt.xlabel('Date')
    plt.ylabel('Precipitation (inches)')
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('Precipitation_for_All_Dates.html', pages=pages, plot_url=plot_url)

@app.route('/Histogram_SC00519281_12_months')
def Histogram_SC00519281_12_months():
    # Plot the histogram
    plt.figure(figsize=(8, 6))
    plt.hist(df_last_12_months['tobs'], bins=12, edgecolor='black')
    plt.xlabel('Temperature')
    plt.ylabel('Frequency')
    plt.title('Histogram of USC00519281 for the Last 12 Months')
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('Histogram_SC00519281_12_months.html', pages=pages, plot_url=plot_url)

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Convert df_last_12_months to a dictionary using date as the key and prcp as the value
    precipitation_data = df_last_12_months.set_index('date')['prcp'].to_dict()
    
    # Convert keys (dates) to strings
    precipitation_data = {str(key): value for key, value in precipitation_data.items()}
    
    # Return the JSON representation of the dictionary
    return jsonify(precipitation_data)




@app.route('/api/v1.0/stations')
def stations():
    # Create a new session for the current thread
    session = Session()

    # Query all records from the Station table
    all_stations = session.query(Station.station, Station.name).all()
    
    # Close the session
    session.close()
    
    # Convert the query results to a list of dictionaries
    station_data = []
    for station in all_stations:
        station_dict = {}
        station_dict['station'] = station.station
        station_dict['name'] = station.name
        station_data.append(station_dict)
    
    # Return the JSON representation of the list of dictionaries
    return jsonify(station_data)


if __name__ == "__main__":
    app.run(debug=True)
