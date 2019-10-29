## SET UP DATABASE

#  import dependencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


## SET UP APP

# flask set up
app = Flask(__name__)


# list all available api routes
@app.route("/")
def home_page():
    return (
        f"Welcome to Honolulu climate analysis API! <br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation   :-- returns all precipitation records by date<br/>"
        f"<br/>"
        f"/api/v1.0/stations    :-- returns all stations in Honolulu<br/>"
        f"<br/>"
        f"/api/v1.0/tobs    :-- returns the temperature records in the last 12 months<br/>"
        f"<br/>"
        f"/api/v1.0/start_date  :-- returns the minimum temperature, average temperature and maximum temperature between a start date and the most recent data recorded (input date in the link with the format yyyy-mm-dd)<br/>"
        f"<br/>"
        f"/api/v1.0/start_date/end_date :-- returns the minimum temperature, average temperature and maximum temperature between a start date and end date (input date in the link with the format yyyy-mm-dd)<br/>"
    )


# precipitation route - convert the query results to a Dictionary using date as the key and prcp as the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create session
    session = Session(engine)

    # query all date and prcp data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # create a dictionary
    all_precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

# station route - return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    # create session
    session = Session(engine)

    # query all date and prcp data
    results = session.query(Station.name).all()

    session.close()

    # convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# tobs route - query for the dates and temperature observations from a year from the last data point
@app.route("/api/v1.0/tobs")
def temperatures():
    # create session
    session = Session(engine)

    # data one year ago from latest data point (2017-08-23)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # query all date and prcp data
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).all()

    session.close()

    # create a dictionary
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


# start date route - given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route("/api/v1.0/<start_date>")
def calc_temps_start(start_date):

    # create session
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    session.close()

    # convert list of tuples into normal list
    temp_results = list(np.ravel(results))

    return jsonify(temp_results)

# start and end date route - given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_start_end(start_date, end_date):

    # create session
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()

    # convert list of tuples into normal list
    temp_results = list(np.ravel(results))

    return jsonify(temp_results)




if __name__ == '__main__':
    app.run(debug=True)




