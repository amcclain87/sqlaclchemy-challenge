# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.inspection import inspect

from flask import Flask, jsonify, request

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Date format for -start- and -end-: yyyy-mm-dd<br/>"
        f"/api/v1.0/-start-<br/>"
        f"/api/v1.0/-start-/-end-<br/>"
        )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #calculation 1 year prior to most recent date
    one_year = dt.date(2017,8,23) - timedelta(days = 365)
    # Perform a query to retrieve the data and precipitation scores
    last_twelve = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date > one_year).all()
    
    #create the dictionary
    all_precip = []
    for date, prcp in last_twelve:
        precip_dict = {}
        precip_dict[date] = prcp
        all_precip.append(precip_dict)

    #jsonify dictionary
    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    #query for stations
    station_query = session.execute('select * from Station')
    #create station dictionary
    stations = []
    for id,station,name,latitude, longitude, elevation in station_query:
        station_dict = {}
        station_dict['id'] = id
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        stations.append(station_dict)

    #jsonify dictionary
    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def tobs():
    #query stations and the amount of measurements they recorded
    stations = session.query(Measurement.station, func.count(Measurement.station).label('count')).order_by(func.count(Measurement.station).desc()).group_by(Measurement.station).all()
    
    #most active station
    most_active = stations[0][0]
    #one year prior to most recent date
    one_year = dt.date(2017,8,23) - timedelta(days = 365)

    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    temp = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == most_active).filter(Measurement.date > one_year).all()


    #create dictionary for temps
    all_tobs = []
    for date, tobs in temp:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)

    #jsonify dictionary
    return jsonify(all_tobs)



@app.route("/api/v1.0/<string:start>")
def start_date(start):
    
    #query
    temp = session.query(Measurement.tobs).\
        filter(Measurement.date >= start).all()

    #temperature list
    temps = []
    for t in temp:
        temps.append(t[0])
    #summary information for given range
    max_t = max(temps)
    min_t = min(temps)
    count = len(temps)
    total = sum(temps)
    average = total/count
    #summary dictionary
    summary = [{'Start date': start, 'max temp': max_t, 'min temp': min_t, 'avg temp': average}]
    #jsonify dictionary    
    return jsonify(summary)

@app.route("/api/v1.0/<string:start>/<string:end>")
def search_date(start=None,end=None):
    
    #query
    temp2 = session.query(Measurement.tobs).\
        filter(Measurement.date<= end).filter(Measurement.date >= start).all()
    
    #list of temps for date range
    temps2 = []
    for t2 in temp2:
        temps2.append(t2[0])


    #summary stats
    max_t2 = max(temps2)
    min_t2 = min(temps2)
    count2 = len(temps2)
    total2 = sum(temps2)
    average2 = total2/count2
    #summary dictionary
    summary2 = [{'Start date': start, 'end date': end, 'max temp': max_t2, 'min temp': min_t2, 'avg temp': average2}]
    #jsonify dictionary    
    return jsonify(summary2)




if __name__ == "__main__":
    # @TODO: Create your app.run statement here
    # YOUR CODE GOES HERE
    app.run(debug=True)