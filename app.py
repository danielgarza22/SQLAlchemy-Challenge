#Import all dependencies
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

# SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

# Create engine to conect to sqlite file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Base
Base = automap_base()
Base.prepare(engine, reflect=True)

# Variables to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask
app = Flask(__name__)

year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"======================================<br/>"
        f"Welcome to Climate_App<br/>"
        f"======================================<br/>"
        f"Available Routes:<br/>"
        f"======================================<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date (format ""yyyy-mm-dd"")<br/>"
        f"/api/v1.0/start date/end date (format ""yyyy-mm-dd"")"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the database
    session = Session(engine)

    data_ps = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date.between('2016-08-23','2017-08-23')).order_by(Measurement.date).all()

    prcp = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=year_ago).all()

    measurement_df = pd.DataFrame(data_ps).set_index([0]).T.to_dict('list')
    
    session.close()

    return jsonify(measurement_df)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # List the stations 
    bystations = session.query(Station.station).order_by(Station.station).all()

    session.close()

    return jsonify(bystations)

@app.route("/api/v1.0/tobs")
def temps():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    bystations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc()).all()
    countstations=pd.DataFrame(bystations,columns=['Station','Count of Station'])

    station1=str(countstations['Station'][0])

    station1data=session.query(Measurement.station,
                            func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs))\
        .group_by(Measurement.station).filter(Measurement.station==station1).all()

    dict1= {'Station': station1data[0][0],
            'Min Temp': station1data[0][1],
            'Max Temp': station1data[0][2],
            'Avg Temp': station1data[0][3]}
    session.close()

    return jsonify(dict1)


@app.route("/api/v1.0/<start>")
def starttemps(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    tempdata=session.query(Measurement.date,
                            func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs))\
        .group_by(Measurement.date).filter(Measurement.date>=start).all()

    listofdicts=[]
    for date, min, max, avg in tempdata:
        dict1= {}
        dict1['date']=date
        dict1["Tmin"]=min
        dict1["Tmax"]=max
        dict1["Tavg"]=avg
        listofdicts.append(dict1)

    session.close()

    return jsonify(listofdicts)

@app.route("/api/v1.0/<start>/<end>")
def betweentemps(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    tempdata=session.query(Measurement.date,
                            func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs))\
        .group_by(Measurement.date).filter(Measurement.date.between(start,end)).all()

    listofdicts=[]
    for date, min, max, avg in tempdata:
        dict1= {}
        dict1['date']=date
        dict1["Tmin"]=min
        dict1["Tmax"]=max
        dict1["Tavg"]=avg
        listofdicts.append(dict1)

    session.close()

    return jsonify(listofdicts)

if __name__ == '__main__':
    app.run(debug=True)