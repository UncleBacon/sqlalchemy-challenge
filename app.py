from flask import Flask, jsonify
import datetime as dt
from datetime import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#Access DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")

# * Home page.

#   * List all routes that are available.
def welcome():
    return (
        f"<h1>Welcome to the Weather App Home Page!</h1><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"

    )


@app.route("/api/v1.0/precipitation")

def precipitation():
    """Convert the query results to a Dictionary using `date` as the 
    key and `prcp` as the value"""
    
    session = Session(engine)
    max_date = max(session.query(measurement.date))[0]
    start_date = datetime.strptime(max_date, '%Y-%m-%d').date()
    year_ago = start_date - dt.timedelta(days=365)
    data = session.query(measurement.date,measurement.prcp).filter(measurement.prcp!='None').filter(measurement.date > year_ago).filter(measurement.date < start_date).all()
    session.close()
    prcp = pd.DataFrame(data).set_index('date')  
    prcp = prcp.rename(columns = {'prcp':'Precipitation'})
    prcp = prcp.sort_values('date')
    prcpavg = prcp.groupby('date')['Precipitation'].mean()
    prcpdf = pd.DataFrame(prcpavg)
    prcp_dict = prcpdf.to_dict('index')
    

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")

def stations():
    """Return a JSON list of stations from the dataset, or a 404 if not."""
    
    session = Session(engine)
    stations = session.query(measurement.station, station.name).filter(measurement.station==station.station).group_by('station').order_by(func.count(measurement.date).desc()).all()
    station_dict = pd.DataFrame(stations).set_index('station').to_dict('index')
    session.close()
    return(jsonify(station_dict))
    

@app.route("/api/v1.0/tobs")
def temperature():
    """query for the dates and temperature observations from a year from the last data point. 
    Return a JSON list of Temperature Observations (tobs) for the previous year, or a 404 if not."""
    
    session = Session(engine)
    max_date = max(session.query(measurement.date))[0]
    start_date = datetime.strptime(max_date, '%Y-%m-%d').date()
    year_ago = start_date - dt.timedelta(days=365)

    stations = session.query(measurement.station, func.count(measurement.date)).group_by('station').order_by(func.count(measurement.date).desc()).all()
    mactive = stations[0][0]
    
    temp_LastYear = session.query(measurement.date,measurement.tobs).filter(measurement.station == mactive).filter(measurement.date>year_ago).filter(measurement.date<max_date).all()

    temp_dict = pd.DataFrame(temp_LastYear,columns = ['Date','Temp']).set_index('Date').to_dict('index')
    session.close()
    return(jsonify(temp_dict))

@app.route("/api/v1.0/<start>")
# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
    

def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range.
     When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
     or a 404 if not."""
# Set the start and end date of the trip
    start_date = datetime.strptime(start, '%Y-%m-%d').date()   
    print(type(start_date))
    # Use the start and end date to create a range of dates

    session = Session(engine) 
    dates = session.query(measurement.date).filter(measurement.date >= start_date).all()
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

    return jsonify(temp_dict), 404
    
@app.route("/api/v1.0/<start>/<end>")

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
    dates = session.query(measurement.date).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
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
    temp_df_SE = pd.DataFrame(data).set_index('date').groupby('date').agg('mean')
    

    temp_dict_SE = temp_df_SE.to_dict('index')

    return jsonify(temp_dict_SE), 404

if __name__ == "__main__":
    app.run(debug=True)


# ## Hints

# * You will need to join the station and measurement tables for some of the analysis queries.

# * Use Flask `jsonify` to convert your API data into a valid JSON response object.
