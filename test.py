from flask import Flask, jsonify
import datetime as dt
from datetime import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

path = r"C:\Users\bastaw1\PycharmProjects\GitHub\Homework\sqlalchemy-challenge\Instructions\Resources\hawaii.sqlite"
engine = create_engine("sqlite:///"+path)
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

def start__end_date(start,end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range.
     When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
     or a 404 if not."""
# Set the start and end date of the trip
    start_date = datetime.strptime(start, '%Y-%m-%d').date()   
    end_date = datetime.strptime(end, '%Y-%m-%d').date()
    # Use the start and end date to create a range of dates
    print('Start Date:', start_date)
    print('End Date:', end_date)

    session = Session(engine) 
    dates = session.query(measurement.date).filter(measurement.date >= start_date).filter(measurement.date < end_date).all()
    print("passing Dates")


    def daily_normals(date):
        sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
        return session.query(*sel).filter(func.strftime("%m-%d", measurement.date) == date).all()
        session.close()

    # Strip off the year and save a list of %m-%d strings
    
    print("Collecting Datez")

    datez = [date[0] for date in dates]
    
    
    normals = [] 
    for date in datez:
        x = datetime.strptime(date,'%Y-%m-%d')
        normals.append(daily_normals(x.strftime('%m-%d')))

    tmin = [x[0][0] for x in normals]
    tavg = [x[0][1] for x in normals]
    tmax = [x[0][2] for x in normals]
    print("passing min/avg/max to lists")
    
    data = {'date':datez,
        'tmin':tmin,
        'tavg':tavg,
        'tmax':tmax}
    temp_df = pd.DataFrame(data).set_index('date').groupby('date').agg('mean')
    

    temp_dict = temp_df.to_dict('index')

    print(temp_dict)

start__end_date('2016-10-02','2016-10-10')