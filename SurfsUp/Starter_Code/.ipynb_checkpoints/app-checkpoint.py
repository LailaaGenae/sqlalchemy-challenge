# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(autoload_with=engine)

# # Save references to tables in the database
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#list all available routes
@app.route("/")
def homepage():
    """ List all available routes"""
    return(
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start>'
        f'/api/v1.0/<start>/<end>'
    )
#precipitation past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session link from Python to the DB
    session= Session(engine)
    #query the last 12 months of precip data
    cutoff_date = '2016-08-23'
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > cutoff_date).all()
    session.close()

    #create a dictionary and append to list of precipitation data
    precip_data = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)

 #stations list route
@app.route("/api/v1.0/stations")
def stations():
    #create session link
    session = Session(engine)
    #query the names of all stations in the list
    results = session.query(Measurement.station).distinct().all()
    session.close()

    #dictionary of active stations and counts
    station_data = []
    for station in results:
        station_dict = {}
        station_dict["station name"] = station[0]
        station_data.append(station_dict)

    return jsonify(station_data)

#route for tobs in past 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    #create session link
    session = Session(engine)
    #query most active observation station of the last 12 months of temp data 
    cutoff_date_12month = '2016-08-23'
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == 'USC00519281') & (Measurement.date > cutoff_date_12month)).all()
    session.close()

    #dictionary of tobs data for the most active station
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Oberved Temperature"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

#min, max, avg temp from start date
@app.route("/api/v1.0/<start_date>")
def temps_start(start_date):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    temp_data = []
    for tobs in results:
        temp_dict = {}
        temp_dict["Average"] = results[0][0]
        temp_dict["Minimum"] = results[0][1]
        temp_dict["Maximum"] = results[0][2]
        temp_data.append(temp_dict)

    return jsonify(temp_data)

#min, max, avg temp from end date
@app.route("/api/v1.0/<start_date>/<end_date>")
def temps_start_end(start_date=None, end_date=None):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((Measurement.date >= start_date)&(Measurement.date <= end_date)).\
        all()

    temp_data = []
    for tobs in results:
        temp_dict = {}
        temp_dict["Average"] = results[0][0]
        temp_dict["Minimum"] = results[0][1]
        temp_dict["Maximum"] = results[0][2]
        temp_data.append(temp_dict)

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)
