import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

#Home Page
@app.route("/")

def welcome():
    """List all the available routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"
        f"/api/v1.0/start_date/<start_date>/end_date/<end_date>"

    )


#Precipitation
@app.route("/api/v1.0/precipitation")

def prcp():

    session = Session(engine)

    # Calculate the date 1 year ago from the last date in the database
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    one_yr_b4 = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the precipitation data for the last 12 months
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_yr_b4).\
        order_by(measurement.date).all()

    # Create a dictionary from the query results
    prcp_data = {date: prcp for date, prcp in results}

    return jsonify(prcp_data)


#Stations
@app.route("/api/v1.0/stations")

def stations():

    session = Session(engine)
    station_rows = session.query(station.name).all()
    session.close()

    # Convert Row objects to dictionaries
    station_list = [row._asdict() for row in station_rows]

    return jsonify(station_list)


#Temperature over the last year for the most active station 
@app.route("/api/v1.0/tobs")

def temperatures():

    session = Session(engine)

    #Calculate the date 1 year ago from the last date in the database
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    one_yr_b4 = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    #query the most active station
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).\
        first()[0]

    #query the tobs for the most active station
    temp_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= one_yr_b4).\
        order_by(measurement.date).all()
    
    session.close()

    temp_dates = []

    for date, tobs in temp_data:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_dates.append(temp_dict)

    return jsonify(temp_dates)


#Temperature details for a Specific date
@app.route("/api/v1.0/start_date/<start_date>")

def calc_temp_single_date(start_date):

    session = Session(engine)
    #Max temperature
    temp_high = session.query(func.max(measurement.tobs)).\
    filter(measurement.date >= start_date)[0][0]
    #Min temperature
    temp_low = session.query(func.min(measurement.tobs)).\
    filter(measurement.date >= start_date)[0][0]
    #Avg temperature
    temp_avg = round(session.query(func.avg(measurement.tobs)).\
    filter(measurement.date >= start_date)[0][0],2)

    session.close()

    dt_temp_dict = {}
    dt_temp_dict["Maximum Temp"] = temp_high
    dt_temp_dict["Minimum Temp"] = temp_low
    dt_temp_dict["Average Temp"] = temp_avg

    return jsonify(dt_temp_dict)


#Temperature details for a date range
@app.route("/api/v1.0/start_date/<start_date>/end_date/<end_date>")

def calc_temp(start_date, end_date):

    session = Session(engine)
    #Max temperature
    temp_high_dates = session.query(func.max(measurement.tobs)).\
    filter(measurement.date >= start_date).\
    filter(measurement.date <= end_date)[0][0]
    #Min temperature
    temp_low_dates = session.query(func.min(measurement.tobs)).\
    filter(measurement.date >= start_date).\
    filter(measurement.date <= end_date)[0][0]
    #Avg temperature
    temp_avg_dates = round(session.query(func.avg(measurement.tobs)).\
    filter(measurement.date >= start_date).\
    filter(measurement.date <= end_date)[0][0],2)

    session.close()

    dtrange_temp_dict = {}
    dtrange_temp_dict["Maximum Temp"] = temp_high_dates
    dtrange_temp_dict["Minimum Temp"] = temp_low_dates
    dtrange_temp_dict["Average Temp"] = temp_avg_dates

    return jsonify(dtrange_temp_dict)

if __name__ == '__main__':
    app.run(debug=True)