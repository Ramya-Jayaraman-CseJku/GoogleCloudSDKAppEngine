# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 15:07:15 2021

@author: ramya
"""

import pandas as pd
import flask
from flask import request, jsonify
import requests
import json

# setttingcopywithwarning remove
pd.options.mode.chained_assignment = None  # default='warn'

# =============================================================================
# district data url
districtDataUrl = pd.read_csv(
    'https://covid19-dashboard.ages.at/data/CovidFaelle_Timeline_GKZ.csv', sep=";")
districtDataUrl.info(verbose=False)
districtDataUrl.info()
districtDataUrl.dtypes
print('count of nan values')
print(districtDataUrl.isna().sum())
print(districtDataUrl.isnull().sum(axis=0))

importantColumns = districtDataUrl[[
    'Time', 'Bezirk', 'AnzahlFaelle']]
# check if the rows contain value zero
print(importantColumns == 0)
# non zero value rows
importantColumns = importantColumns[~(importantColumns == 0).any(axis=1)]
importantColumns.info(verbose=False)
importantColumns.info()
importantColumns.dtypes
# convert to datetime format of time column for grouping by week,month,year dayfirst=true for correct conversion format(yyyy-mm-dd)
importantColumns['Time'] = pd.to_datetime(
    districtDataUrl['Time'], dayfirst=True)

# =============================================================================

# R VALUE url

rValueUrl = pd.read_csv(
    'https://www.ages.at/fileadmin/AGES2015/Wissen-Aktuell/COVID19/R_eff.csv', sep=";", decimal=',')
rValueUrl.info(verbose=False)
rValueUrl.info()
rValueUrl.dtypes

importantColumnsREFF = rValueUrl[['Datum', 'R_eff']]
importantColumnsREFF['Datum'] = pd.to_datetime(rValueUrl['Datum'])

# =============================================================================
# Vaccination Districts Url
vaccinationDistrictsDataUrl = pd.read_csv(
    'https://info.gesundheitsministerium.gv.at/data/COVID19_vaccination_municipalities.csv', sep=';')

colVaccDist = vaccinationDistrictsDataUrl[[
    "date", "municipality_id", "municipality_name", "municipality_population", "dose_1", "dose_2", "dose_3"]]
colVaccDist.dropna(axis=0)
colVaccDist.info(verbose=False)
colVaccDist.info()
colVaccDist.dtypes

colVaccDist = colVaccDist[~(
    colVaccDist == 0).any(axis=1)]

colVaccDist['date'] = pd.to_datetime(
    colVaccDist['date'], utc=True)
colVaccDist['date'] = colVaccDist['date'].dt.tz_convert(
    'CET')
colVaccDist.loc[(colVaccDist.municipality_id == 90101),
                'municipality_name'] = 'Wien Innere Stadt'
colVaccDist.loc[(colVaccDist.municipality_id == 90201),
                'municipality_name'] = 'Wien Leopoldstadt'
colVaccDist.loc[(colVaccDist.municipality_id == 90301),
                'municipality_name'] = 'Wien Landstraße'
colVaccDist.loc[(colVaccDist.municipality_id == 90401),
                'municipality_name'] = 'Wien Wieden'
colVaccDist.loc[(colVaccDist.municipality_id == 90501),
                'municipality_name'] = 'Wien Margareten'
colVaccDist.loc[(colVaccDist.municipality_id == 90601),
                'municipality_name'] = 'Wien Mariahilf'
colVaccDist.loc[(colVaccDist.municipality_id == 90701),
                'municipality_name'] = 'Wien Neubau'
colVaccDist.loc[(colVaccDist.municipality_id == 90801),
                'municipality_name'] = 'Wien Josefstadt'
colVaccDist.loc[(colVaccDist.municipality_id == 90901),
                'municipality_name'] = 'Wien Alsergrund'
colVaccDist.loc[(colVaccDist.municipality_id == 91001),
                'municipality_name'] = 'Wien Favoriten'
colVaccDist.loc[(colVaccDist.municipality_id == 91101),
                'municipality_name'] = 'Wien Simmering'
colVaccDist.loc[(colVaccDist.municipality_id == 91201),
                'municipality_name'] = 'Wien Meidling'
colVaccDist.loc[(colVaccDist.municipality_id == 91301),
                'municipality_name'] = 'Wien Hietzing'
colVaccDist.loc[(colVaccDist.municipality_id == 91401),
                'municipality_name'] = 'Wien Penzing'
colVaccDist.loc[(colVaccDist.municipality_id == 91501),
                'municipality_name'] = 'Wien Rudolfsheim-Fünfhaus'
colVaccDist.loc[(colVaccDist.municipality_id == 91601),
                'municipality_name'] = 'Wien Ottakring'
colVaccDist.loc[(colVaccDist.municipality_id == 91701),
                'municipality_name'] = 'Wien Hernals'
colVaccDist.loc[(colVaccDist.municipality_id == 91801),
                'municipality_name'] = 'Wien Währing'
colVaccDist.loc[(colVaccDist.municipality_id == 91901),
                'municipality_name'] = 'Wien Döbling'
colVaccDist.loc[(colVaccDist.municipality_id == 92001),
                'municipality_name'] = 'Wien Brigittenau'
colVaccDist.loc[(colVaccDist.municipality_id == 92101),
                'municipality_name'] = 'Wien Floridsdorf'
colVaccDist.loc[(colVaccDist.municipality_id == 92201),
                'municipality_name'] = 'Wien Donaustadt'
colVaccDist.loc[(colVaccDist.municipality_id == 92301),
                'municipality_name'] = 'Wien Liesing'
# =============================================================================
# read json file for warn level
response = requests.get(
    "https://corona-ampel.gv.at/sites/corona-ampel.gv.at/files/assets/Warnstufen_Corona_Ampel_aktuell.json", timeout=5)
# response.close()
entiredata = json.loads(response.text)

finallist = []
# read loacl csv file for coordinates
df = pd.read_csv(r'AustrianCitiesWithCoordinates.csv')

# =============================================================================


def getMarkerColor(i):
    switcher = {
        '1': 'green',
        '2': 'yellow',
        '3': 'orange',
        '4': 'red',
    }
    return switcher.get(i, "Invalid number")


# =============================================================================
# API
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    sample = "Welcome to the home page of flask API try following routes to see covid related information <br/>1./api/positivecasesbydistrict/<br/>2./api/VaccinationDistricts/<br/>3./api/R_eff_Austria/</p>"
    return sample

# A route to return all the json data.


@app.route('/api/positivecasesbydistrict/', methods=['GET'])
def api_DistrictPositiveCases_Filter():
    districtname = ''
    interval = ''
    # get query parameters
    query_parameters = request.args
    # assign param to filter data
    districtname = query_parameters.get('districtname')

    interval = query_parameters.get('interval')

    if 'districtname' in query_parameters:
        districtnametofilter = districtname
        filteredDistrict = importantColumns[importantColumns['Bezirk']
                                            == districtnametofilter]

    else:
        return 'Error:No district name provided. Please choose a district name.'

    if 'interval' in query_parameters:
        dataintervaltofilter = interval
    else:
        return 'Error:No interval provided. Please choose a interval .'

    if(dataintervaltofilter == 'Daily'):

        districtDataByDay = filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'], Interval=filteredDistrict['Time'].dt.strftime('%d %b %Y'), Year=filteredDistrict['Time'].dt.strftime(
            '%Y').sort_index()).groupby(['DistrictName', 'Interval', 'Year'], sort=False)['AnzahlFaelle'].sum()
        convertedJson = districtDataByDay.to_json(orient="table")

    elif(dataintervaltofilter == 'Weekly'):
        districtDataByWeek = filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'], Interval='week '+filteredDistrict['Time'].dt.strftime(
            '%W %Y'), Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName', 'Interval', 'Year'], sort=False)['AnzahlFaelle'].sum()
        convertedJson = districtDataByWeek.to_json(orient="table")

    elif(dataintervaltofilter == 'Monthly'):

        districtDataByMonth = filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'], Interval=filteredDistrict['Time'].dt.strftime('%b %Y'), Year=filteredDistrict['Time'].dt.strftime(
            '%Y').sort_index()).groupby(['DistrictName', 'Interval', 'Year'], sort=False)['AnzahlFaelle'].sum()
        convertedJson = districtDataByMonth.to_json(orient="table")

    elif(dataintervaltofilter == 'Yearly'):

        districtDataByYear = filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'], Interval=filteredDistrict['Time'].dt.strftime(
            '%Y').sort_index()).groupby(['DistrictName', 'Interval'])['AnzahlFaelle'].sum()
        convertedJson = districtDataByYear.to_json(orient="table")

    else:
        return 'Error: Interval type provided is mismatched  . Please choose one of the data interval Daily,Weekly,Monthly or Yearly.'

    #convertedJson = districtDataByMonth.to_json(orient="table")
    # de-serialize into python obj
    parsedJson = json.loads(convertedJson)
    # serialize into json
    json.dumps(parsedJson)
    # json op to mime-type application/json
    return jsonify(parsedJson)

# =============================================================================


@app.route('/REff', methods=['GET'])
def REffhome():
    return "<p>R_Effective data: R effective value for austria grouped by week month and year</p>"

# A route to return all the json data.


@app.route('/api/R_eff_Austria/', methods=['GET'])
def api_REffectiveValue_Filter():

    interval = ''
    # get query parameters
    query_parameters = request.args
    # assign param to filter data

    interval = query_parameters.get('interval')

    if 'interval' in query_parameters:
        dataintervaltofilter = interval
    else:
        return 'Error:No interval provided. Please choose a interval .'

    if(dataintervaltofilter == 'Daily'):
        REffDataEveryday = importantColumnsREFF.assign(Interval=importantColumnsREFF['Datum'].dt.strftime(
            '%d %b %Y'), Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index())
        convertedJsonREff = REffDataEveryday.to_json(orient="table")

    else:
        return 'Error:Interval type provided is mismatched  . Please choose one of the data interval Weekly,Monthly.'

    parsedJsonREff = json.loads(convertedJsonREff)
    json.dumps(parsedJsonREff)
    return jsonify(parsedJsonREff)


# =============================================================================

@app.route('/VaccinationDistricts', methods=['GET'])
def VaccinationDistricts():
    return "<p>Vaccination data: Vaccination data for districts for particular date</p>"

# A route to return all the json data.


@app.route('/api/VaccinationDistricts/', methods=['GET'])
def api_VaccinationDistricts_Filter():
    districtname = ''

    query_parameters = request.args

    districtname = query_parameters.get('districtname')

    if 'districtname' in query_parameters:
        districtnametofilter = districtname
        filteredDistrictVacc = colVaccDist[colVaccDist['municipality_name']
                                           == districtnametofilter]

    else:
        return 'Error:No districtname provided. Please choose a districtname.'

    VaccData = filteredDistrictVacc.assign(
        Interval=filteredDistrictVacc['date'].dt.strftime('%d %b %Y'), Dose=filteredDistrictVacc['dose_1'], Type="Dose_1")
    VaccDataDose_2 = filteredDistrictVacc.assign(
        Interval=filteredDistrictVacc['date'].dt.strftime('%d %b %Y'),
        Dose=filteredDistrictVacc['dose_2'], Type="Dose_2")
    VaccDataDose_3 = filteredDistrictVacc.assign(
        Interval=filteredDistrictVacc['date'].dt.strftime('%d %b %Y'),
        Dose=filteredDistrictVacc['dose_3'], Type="Dose_3")
    data = [VaccData, VaccDataDose_2, VaccDataDose_3]
    ddf = pd.concat(data)
    convertedJsonVaccDist = ddf.to_json(
        orient="table")

    parsedJsonVaccDist = json.loads(convertedJsonVaccDist)
    json.dumps(parsedJsonVaccDist)
    return jsonify(parsedJsonVaccDist)

# =============================================================================


@app.route('/api/warnLevelRegion/', methods=['GET'])
def api_warningLevelRegion():

    date = ''
    query_parameters = request.args
    date = query_parameters.get('date')
    if 'date' in query_parameters:
        datetofilter = date
    else:
        return 'Error:No date provided. Please choose a date.'
    citiesWithCoordinatesByDate = []

    for warnLevelObjects in entiredata:
        warnLevelObjects['Stand'] = warnLevelObjects['Stand'][0:10]
        if warnLevelObjects['Stand'] == datetofilter:
            for region in warnLevelObjects['Warnstufen']:
                if region['Name'] is not None:
                    for entry in df.iterrows():
                        if entry[1]['cityName'] == region['Name']:
                            citiesDict = {}

                            citiesDict['cityName'] = region['Name']
                            citiesDict['Latitude'] = entry[1]['Latitude']
                            citiesDict['Longitude'] = entry[1]['Longitude']
                            citiesDict['Warnstufe'] = region['Warnstufe']
                            citiesDict['MarkerColor'] = getMarkerColor(
                                citiesDict['Warnstufe'])
                            citiesWithCoordinatesByDate.append(citiesDict)
    print(citiesWithCoordinatesByDate)
    responseWarnLevel = jsonify(citiesWithCoordinatesByDate)
    return responseWarnLevel


if __name__ == '__main__':
    app.run(port=8080, debug=True)
