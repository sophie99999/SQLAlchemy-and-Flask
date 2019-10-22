import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import numpy as numpy
import datetime as dt

#Database Setup:
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#Flask Setup
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    return(
        f"Here are some available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Query all precipitation
    results=session.query(Measurement.date,Measurement.prcp).all()
    
    #Create a dictionary from the row data and append to a list of all precipitation (Jsonify can only take one list of dictionaries at a time, so you need to wrap it)
    all_precipitation=[]
    for date,prcp in results:
        precipitation_dict={}
        precipitation_dict["date"]=date
        precipitation_dict["precipitation"]=prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    #Query all the staions
    all_stations=session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    #Create a dictionary from the row data and append to a list of all stations
    all_station=[]
    for station,name,latitude,longitude,elevation in all_stations:
        all_station_dict={}
        all_station_dict["station"]=station
        all_station_dict["name"]=name
        all_station_dict["latitude"]=latitude
        all_station_dict["longitude"]=longitude
        all_station_dict["elevation"]=elevation
        all_station.append(all_station_dict)

    return jsonify(all_station)


@app.route("/api/v1.0/tobs")
def tobs():
    #Query for the dates and temperature observations from a year from the last data point
    tobs_query=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>="2016-08-22").all()
    #Create a dictionary from the row data and append to a list of all tobs
    all_tobs=[]
    for date,tobs in tobs_query:
        all_tobs_dict={}
        all_tobs_dict["date"]=date
        all_tobs_dict["tobs"]=tobs
        all_tobs.append(all_tobs_dict)

    return jsonify(all_tobs)


@app.route('/api/v1.0/<start>')
def startdate(start):

    #Formatting the date
    canonicalized_search=dt.datetime.strptime(start, "%Y-%m-%d")
    #Query the information after that date
    start_query=session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
                filter(Measurement.date>canonicalized_search).all()
    #Create dictionaries to put into one list
    start_stats=[]
    for maximum, minimum,average in start_query:
        start_stats_dict={}
        start_stats_dict["Maximum temp"]=maximum
        start_stats_dict["Minimum temp"]=minimum
        start_stats_dict["Average temp"]=average
        start_stats.append(start_stats_dict)

    return jsonify(start_stats)


@app.route("/api/v1.0/<start>/<end>")
def daterange(start,end):

    #Query
    daterange_results=session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
                        filter(Measurement.date.between(start,end)).all()
    
    #Creating a list and the dictionaries within the list
    range_list=[]
    for maximum, minimum,average in daterange_results:
        range_dict={}
        range_dict["Maximum temp"]=maximum
        range_dict["Minimum temp"]=minimum
        range_dict["Average temp"]=average
        range_list.append(range_dict)

    return jsonify(range_list)

  


if __name__=='__main__':
    app.run(debug=True)