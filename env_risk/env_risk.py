#python3
# -*- coding: utf-8 -*-

#See data_schema.txt for more details
standard_dict = {
    'last_update':None,
    'country_region-name':None,
    'country_region-ID':None,
    'province_state-name':None,
    'province_state-ID':None,
    'town_area_name':None,
    'town_area_ID':None,
    'total_population':None,
    'latitude':None,
    'longitude':None,
    'confirmed_cases':None,                #cumulative =(hospitalised_with_symptoms + intensive_care + quarantine_at_home)
    'new_confirmed_cases':None,            #current
    'hospitalised_all':None,               #current
    'hospitalised_with_symptoms':None,     #current
    'quarantine_at_home':None,             #current
    'intensive_care':None,                 #current
    'with_ventilation':None,               #current
    'deaths':None,                         #cumulative
    'recovered_out-of-hospital':None,      #cumulative
    'tested':None,                         #cumulative
    'average_velocity':None,
    }

def read_italy_official_situation(granularity='regioni'):
    '''
    Read Offical Data from the Italian Governement / Protezione Civile.
    Downloaded from GitHub in JSON format.
    Currently only province_state ("regioni") level is implemented

    Parameters
    ----------
        granularity: str
            spational resolution, either "regioni" or "provincie"

    Returns
    -------
        standardised_data_list: list
            Data at the "regioni" or "provincie" level
    '''
    italy_regioni_population_dict = {
        'Lombardia':10060574,
        'Lazio': 5879082,
        'Campania':5801692, 
        'Sicilia':4999891,
        'Veneto':4905854,
        'Emilia-Romagna':4459477,
        'Piemonte':4356406,
        'Puglia':4029053,
        'Toscana':3729641,
        'Calabria':1947131,
        'Sardegna':1639591,
        'Liguria':1550640,
        'Marche':1525271,
        'Abruzzo':1311580,
        'Friuli Venezia Giulia':1215220,
        #'Trentino-Alto Adige':1072276,
        'P.A. Trento': 538223,
        'P.A. Bolzano': 520891, 
        'Umbria':882015,
        'Basilicata':562869,
        'Molise':305617,
        "Valle d'Aosta":125666,
    }

    import json,sys,wget
    from copy import deepcopy
    
    print('Download')
    if granularity=='regioni':
        #TODO replace file if existing
        filename = wget.download('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json')
    elif granularity=='provincie':
        sys.exit('granularity="provincie" not implemented!')
    else:
        sys.exit('granularity {} not recognised'.format(granularity))
    with open(filename,'r') as f:
        data_list= json.load(f)

    
    standardised_data_list = []
    for county_dict in data_list:
        data_dict = deepcopy(standard_dict)
        data_dict['last_update'] = county_dict['data']
        data_dict['country_region-name'] = county_dict['stato']
        data_dict['province_state-name'] = county_dict['denominazione_regione']
        data_dict['province_state-ID'] = county_dict['codice_regione']
        if granularity=='provincie':
            data_dict['town_area-name'] = county_dict['denominazione_provincia']
            data_dict['town_area-ID'] = county_dict['codice_provincia']
        if granularity=='regioni':
            data_dict['total_population'] = italy_regioni_population_dict[data_dict['province_state-name']]
        elif granularity=='provincie':
            sys.exit('granularity="provincie" not implemented!')
            #data_dict['total_populaiton'] = italy_provincie_population_dict[data_dict['town_area-name']]
        data_dict['latitude'] = county_dict['lat']
        data_dict['longitude'] = county_dict['long']
        data_dict['confirmed_cases'] = county_dict['totale_positivi']
        data_dict['hospitalised_all'] = county_dict['totale_ospedalizzati']
        data_dict['hospitalised_with_symptoms'] = county_dict['ricoverati_con_sintomi']
        data_dict['quarantine_at_home'] = county_dict['isolamento_domiciliare']
        data_dict['intensive_care'] = county_dict['terapia_intensiva']
        data_dict['new_confirmed_cases'] = county_dict['variazione_totale_positivi']
        data_dict['deaths'] = county_dict['deceduti']
        data_dict['recovered_out-of-hospital'] = county_dict['dimessi_guariti']
        data_dict['tested'] = county_dict['tamponi']
        data_dict['average_velocity'] = None
        standardised_data_list.append(data_dict)
    return standardised_data_list


def read_switzerland_official_situation(granularity='cantons'):
    '''
    Read Offical Data from the Swiss Cantons and Principality of Liechtenstein (FL)
    Downloaded from GitHub in csv format.
    Currently only province_state ("cantons") level is implemented

    Parameters
    ----------
        granularity: str
            spational resolution, either "cantons" or TODO

    Returns
    -------
        standardised_data_list: list
            Data at the "regioni" or "provincie" level


    TODO |  new_hosp        | new hospitalisations since last date | Number     | Irrespective of canton of residence |
    '''

    import json,sys,wget
    from copy import deepcopy
    import pandas as pd

    print('Download')
    if granularity=='cantons':
        #TODO replace file if existing
        filename = wget.download('https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total_v2.csv')
        filename_demographics = wget.download('https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/demographics.csv')
    else:
        sys.exit('granularity {} not recognised'.format(granularity))
    
    data = pd.read_csv(filename)
    demographics_data = pd.read_csv(filename_demographics)
    last_date = data['date'].iloc[-1*(26*2+1)] 
    current_data = data.loc[data['date'] == last_date]
    #TODO implement a function that finds the most recent data where there is data for each canton


    standardised_data_list = []
    for index, row in current_data.iterrows():
        row_demographics = demographics_data.loc[demographics_data.Canton==row['abbreviation_canton_and_fl']]
        data_dict = deepcopy(standard_dict)
        data_dict['last_update'] = last_date
        data_dict['country_region-name'] = 'CH'
        data_dict['province_state-name'] = row['abbreviation_canton_and_fl'] # TODO implement cantons dict 
        data_dict['province_state-ID'] = row['abbreviation_canton_and_fl']
        if granularity=='cantons':
            data_dict['total_population'] = row_demographics['Population']
        else:
            sys.exit('granularity={} not implemented!'.format(granularity))
        data_dict['latitude'] = None
        data_dict['longitude'] = None
        data_dict['confirmed_cases'] = row['ncumul_conf']
    #TODO    data_dict['hospitalised_all'] = county_dict['totale_ospedalizzati']
    #TODO    data_dict['hospitalised_with_symptoms'] = county_dict['ricoverati_con_sintomi']
    #TODO    data_dict['quarantine_at_home'] = county_dict['isolamento_domiciliare']
        data_dict['intensive_care'] = row['current_icu']
        data_dict['with_ventilation'] = row['current_vent']
    #TODO    data_dict['new_confirmed_cases'] = county_dict['variazione_totale_positivi']
        data_dict['deaths'] = row['ncumul_deceased']
        data_dict['recovered_out-of-hospital'] = row['ncumul_released']
        data_dict['tested'] = row['ncumul_tested']
        data_dict['average_velocity'] = None
        standardised_data_list.append(data_dict)
    return standardised_data_list

def environmental_risk_factor_basicgasmodel(rho_eff_contagious,sigma=4,v_avg=1.157):
    '''
    Function to compute the environmental risk factor
    based on the collision frequency in the kinetic theory of gases.

        z = sigma * v_avg * rho_eff-contagious

    Parameters
    ----------
        rho_eff_contagious : float
            Estimated (effective) density of contagious individuals
        sigma : float
            "Cross section", 2*infection_radius for a purely 2D model
            Default is 4 meters
        v_avg : float
            Average mobility, expressed as a velocity (m/s)
            Default is 1km/day -> (1.157 1e-5 m/s)
    Returns
    -------
        z : float
            Environmental risk factor
    '''

    return rho_eff_contagious * sigma * v_avg


if __name__ == "__main__":
    print('Example - Italy Data')
    def run_example(data_list):
        print('\n')
        l = []
        for data_dict in data_list:
            rho_eff_contagious = data_dict['confirmed_cases']/float(data_dict['total_population'])
            risk = environmental_risk_factor_basicgasmodel(rho_eff_contagious,sigma=4,v_avg=1.157)
            l.append([data_dict['province_state-name'],risk])
            print('{} Environmental Risk Factor= {:f}'.format(data_dict['province_state-name'],risk))
        print('-----\nSorting\n-----')
        [print('{}: ERF={:f}'.format(i[0],i[1])) for i in sorted(l, key = lambda x: x[1])]
    
    run_example(read_italy_official_situation())
    run_example(read_switzerland_official_situation())
